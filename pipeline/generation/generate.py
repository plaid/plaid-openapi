#!/usr/bin/env python3
"""Prepare and validate an SDK PR artifact. This process has no publishing credential."""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request

from attestation import parse_json, validate_manifest
from common import (BUNDLE, MANIFEST, WORKFLOW, PipelineError, archive_sdk, canonical,
                    check_sha, clean_env, content, entries, git, protected_state,
                    propose_version, public_get, require, run, save_json, sha256,
                    spec_version, version_tuple)
from harden_wire_tests import harden as harden_wire_tests

ROOT = Path(__file__).resolve().parents[2]
CALLER_HOOK = ("\tif err := checkDestination(req.URL, client); err != nil {\n"
               "\t\treturn nil, err\n\t}\n\tclient = withoutRedirects(client)\n\n")
CALLER_ANCHOR = "\tresp, err := c.retrier.Run("


def settings() -> dict:
    value = json.loads((ROOT / "pipeline/generation/settings.json").read_text())
    require(value["config_repository"] == "plaid/plaid-openapi" and value["config_branch"] == "master", "Unexpected production config repository")
    require(value["spec_repository"] == "plaid/plaid-openapi" and value["spec_path"] == "2020-09-14.yml", "Unexpected spec source")
    require(value["sdk_repository"] == "plaid/plaid-go", "Unexpected SDK destination")
    require(type(value["major"]) is int and value["major"] >= 49, "Configured major must be at least 49")
    require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["cli_version"]) is not None and
            re.fullmatch(r"[0-9a-f]{64}", value["cli_sha256"]) is not None, "Invalid CLI pin")
    require(value["generator_image"] == "fernapi/fern-go-sdk" and
            re.fullmatch(r"sha256:[0-9a-f]{64}", value["generator_digest"]) is not None, "Invalid generator image pin")
    return value


def event_request(event_name: str, event: dict, values: dict) -> tuple[str, bool]:
    require(event_name in {"workflow_dispatch", "push", "schedule"}, "Unsupported generation trigger")
    inputs = event.get("inputs") or {}
    require(isinstance(inputs, dict) and set(inputs) <= {"version", "rehearsal"}, "Unexpected generation input; spec and config always use the workflow commit")
    require(not inputs or event_name == "workflow_dispatch", "Only manual dispatch accepts generation inputs")
    requested_rehearsal = inputs.get("rehearsal", False)
    require(type(requested_rehearsal) is bool or requested_rehearsal in ("true", "false"), "Invalid rehearsal value")
    rehearsal = requested_rehearsal in (True, "true")
    version = inputs.get("version", "")
    if version:
        version_tuple(version)
    return version, rehearsal


def check_context(event: dict, values: dict, rehearsal: bool) -> tuple[str, str, str]:
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    require(os.environ.get("GITHUB_EVENT_NAME") in {"push", "schedule", "workflow_dispatch"}, "Unsupported generation context")
    require(repository == values["config_repository"], "Run only from the public OpenAPI repository")
    metadata = event.get("repository") or {}
    require(metadata.get("full_name") == repository and metadata.get("private") is False and metadata.get("fork") is False,
            "Generation requires the original public repository, not a fork")
    require(os.environ.get("GITHUB_REF") == "refs/heads/" + values["config_branch"], "Generation workflow must run from trusted master")
    require(metadata.get("default_branch") == values["config_branch"], "Unexpected config default branch")
    require(not rehearsal or os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch", "Rehearsal requires manual dispatch")
    require(rehearsal or os.environ.get("SDK_PIPELINE_ENABLED") == "true", "Production generation is disabled")
    commit = check_sha(os.environ.get("GITHUB_SHA", ""))
    require(git(ROOT, "rev-parse", "HEAD") == commit, "Checkout differs from workflow commit")
    require(not git(ROOT, "status", "--porcelain"), "Generation checkout must be clean")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    require(re.fullmatch(r"[1-9][0-9]*", run_id) is not None, "Missing GitHub run identity")
    return repository, commit, run_id


def fetch_repository(repository: str, branch: str, directory: Path) -> str:
    require(repository == "plaid/plaid-go", "Only the fixed public SDK repository may be fetched")
    require(branch == "master", "Unexpected SDK branch")
    metadata = public_get("https://api.github.com/repos/" + repository)
    require(isinstance(metadata, dict) and metadata.get("full_name") == repository and
            metadata.get("private") is False and metadata.get("default_branch") == branch,
            "Public repository identity or default branch changed; review configuration before continuing")
    run(["git", "clone", "--filter=blob:none", "--single-branch", "--branch", branch,
         "https://github.com/" + repository + ".git", str(directory)])
    return check_sha(git(directory, "rev-parse", "HEAD"))


def verified_spec(repo: Path, config_commit: str, values: dict, sdk: Path | None = None) -> tuple[str, bytes]:
    commit = check_sha(config_commit)
    require(git(repo, "rev-parse", "HEAD") == commit, "Spec and config must use the same checked-out workflow commit")
    data = run(["git", "show", commit + ":" + values["spec_path"]], repo)
    current_version = spec_version(data)
    if sdk and (sdk / MANIFEST).exists():
        prior = validate_manifest(parse_json((sdk / MANIFEST).read_bytes()))
        source = prior["source"]
        prior_commit = check_sha(source["commit"])
        run(["git", "merge-base", "--is-ancestor", prior_commit, commit], repo)
        previous = run(["git", "show", prior_commit + ":" + values["spec_path"]], repo)
        require(sha256(previous) == source["sha256"], "Previous SDK spec hash does not match its public commit")
        require(current_version >= spec_version(previous), "Public spec version is older than the published SDK")
    return commit, data


def config_digest(repo: Path) -> str:
    selected = []
    for path, mode, digest in entries(repo, ref="HEAD"):
        if path == "2020-09-14.yml" or path.startswith(("fern/", "pipeline/")) or path == WORKFLOW:
            selected.append([path, mode, digest])
    return sha256(canonical(selected))


def input_identity(version: str, source_hash: str, config_hash: str) -> str:
    return sha256(canonical([version, source_hash, config_hash]))[:20]


def published_baseline(sdk: Path, tags: list[str], major: int, destination: Path) -> str | None:
    stable = []
    for tag in tags:
        match = re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", tag)
        if match and int(match[1]) == major:
            stable.append((tuple(map(int, match.groups())), tag))
    if not stable:
        return None
    tag = max(stable)[1]
    git(sdk, "fetch", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
    commit = check_sha(git(sdk, "rev-parse", tag + "^{commit}"))
    run(["git", "clone", "--shared", str(sdk), str(destination)])
    git(destination, "checkout", "--detach", commit)
    return tag


def pending_release(sdk: Path, remote_tags: str) -> str | None:
    """Wait for the merged generation to publish before proposing another version."""
    if not (sdk / MANIFEST).is_file():
        return None
    manifest = validate_manifest(parse_json((sdk / MANIFEST).read_bytes()))
    version = manifest["sdk"]["version"]
    ref = "refs/tags/v" + version
    references = {}
    for line in remote_tags.splitlines():
        sha, name = line.split()
        if name in {ref, ref + "^{}"}:
            require(name not in references, "Duplicate SDK release tag reference")
            references[name] = check_sha(sha)
    if ref not in references:
        require(ref + "^{}" not in references, "Release tag object is missing")
        return version
    # The first-parent commit that introduced these manifest bytes is the release
    # commit. Later docs/control commits can carry the same published manifest.
    release_commit = check_sha(git(sdk, "rev-list", "--first-parent", "-1", "HEAD", "--", MANIFEST))
    git(sdk, "fetch", "origin", f"{ref}:{ref}")
    require(git(sdk, "rev-parse", ref) == references[ref], "SDK release tag changed while checking publication")
    require(git(sdk, "cat-file", "-t", ref) == "tag", "Automated SDK release tag must be annotated")
    tagged_commit = check_sha(git(sdk, "rev-parse", ref + "^{commit}"))
    require(references.get(ref + "^{}") == tagged_commit, "SDK release tag peeled commit differs from the remote listing")
    require(tagged_commit == release_commit, "SDK release tag conflicts with the merged generation commit")
    require(parse_json(run(["git", "show", tagged_commit + ":" + MANIFEST], sdk)) == manifest,
            "Published SDK manifest differs from the current generation")
    return None


def assert_sdk_bootstrap(sdk: Path, module: str) -> None:
    require((sdk / ".fernignore").is_file(), "SDK needs the reviewed v49 bootstrap before pipeline activation")
    require((sdk / "go.mod").read_text().splitlines()[0] == "module " + module, "SDK bootstrap/configured major/module do not agree")
    for name in ("internal/caller.go", "internal/destination.go", "core/custom_endpoint.go",
                 "option/custom_endpoint.go", "README.md", "CHANGELOG.md", "LICENSE"):
        require((sdk / name).is_file(), f"Reviewed SDK bootstrap is missing {name}")
    require((sdk / "scripts/release").is_dir(), "SDK bootstrap must include the reviewed public release scripts")
    require((sdk / ".github/CODEOWNERS").is_file(), "SDK bootstrap must include workflow/release-code ownership")
    require(not git(sdk, "status", "--porcelain"), "SDK checkout must start clean")
    entries(sdk)  # Reject unsupported paths/modes before any generation.


def render_config(destination: Path, sdk: Path, data: bytes, version: str, values: dict) -> None:
    destination.mkdir(parents=True)
    shutil.copytree(ROOT / "fern", destination / "fern")
    (destination / "2020-09-14.yml").write_bytes(data)
    text = (ROOT / "fern/generators.yml").read_text()
    match = re.search(r"^  go-sdk:\n(.*?)(?=^  [a-zA-Z0-9_-]+:|\Z)", text, re.MULTILINE | re.DOTALL)
    require(match is not None, "Expected one reviewed go-sdk group")
    block = match.group(0)
    require(block.count("      - name:") == 1 and "name: fernapi/fern-go-sdk" in block, "Unexpected Go generator structure")
    require(re.search(r"^        version: " + re.escape(values["generator_version"]) + r"\s*$", block, re.MULTILINE) is not None, "Reviewed generator version and digest settings disagree")
    block = block.replace("  go-sdk:", "  go-pipeline:", 1)
    block = block.replace("name: fernapi/fern-go-sdk", "name: " + values["generator_image"] + "@" + values["generator_digest"], 1)
    github = re.search(r"^        github:\n.*?(?=^        config:)", block, re.MULTILINE | re.DOTALL)
    require(github is not None, "Expected reviewed GitHub output configuration")
    output = "        output:\n          location: local-file-system\n          path: " + json.dumps(os.path.relpath(sdk, destination / "fern")) + "\n"
    block = block[:github.start()] + output + block[github.end():]
    module = "github.com/" + values["sdk_repository"] + "/v" + str(version_tuple(version)[0])
    block = re.sub(r"github\.com/plaid/plaid-go/v\d+", module, block)
    require(re.search(r"^          maxRetries: 0\s*$", block, re.MULTILINE) is not None, "Automatic retries must remain disabled")
    require("workflows:" not in block and "repository:" not in block and "token:" not in block,
            "Local generator group must not contain publishing settings")
    # Retain shared auth/overlay settings but include only the Go group.
    header = text[:text.index("groups:")]
    require(header.count("../2020-09-14.yml") == 1, "Expected the public repository spec path")
    header = re.sub(r"^default-group:.*$", "default-group: go-pipeline", header, flags=re.MULTILINE)
    (destination / "fern/generators.yml").write_text(header + "groups:\n" + block)
    cli_config = json.loads((destination / "fern/fern.config.json").read_text())
    require(cli_config["version"] == values["cli_version"], "CLI config and checksum pin disagree")


def install_cli(work: Path, values: dict) -> Path:
    url = "https://registry.npmjs.org/fern-api/-/fern-api-" + values["cli_version"] + ".tgz"
    with urllib.request.urlopen(url, timeout=60) as response:
        archive = response.read()
    require(sha256(archive) == values["cli_sha256"], "Fern CLI tarball checksum mismatch")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as source:
        member = source.getmember("package/cli.cjs")
        require(member.isfile() and member.size < 100_000_000, "Unexpected CLI archive member")
        cli = work / "fern-cli.cjs"
        cli.write_bytes(source.extractfile(member).read())
    return cli


def check_maintained_caller(sdk: Path, log: Path) -> None:
    lines = re.findall(r"^DEBUG .* go-pipeline fernapi/fern-go-sdk Will write output to: (.+)$", log.read_text(), re.MULTILINE)
    require(len(lines) == 1, "Could not identify the pinned CLI's raw output for caller reconciliation")
    raw = Path(lines[0])
    require(raw.is_absolute() and raw.name == "output" and raw.parent.name.startswith("fern-"), "Unexpected raw generator output directory")
    caller = (sdk / "internal/caller.go").read_text()
    require(caller.count(CALLER_HOOK) == 1, "Maintained caller must contain the reviewed destination/redirect hook")
    require(caller.replace(CALLER_HOOK, "", 1) == (raw / "internal/caller.go").read_text(),
            "Generator caller changed: reconcile its new runtime with the reviewed security hook before updating the generator pin")


def restore_published_multipart_field(sdk: Path, values: dict) -> bool:
    """Preserve the published enum-as-text fix until the pinned generator supports it."""
    require(values["generator_version"] == "1.70.3", "Review multipart preservation for the new generator version")
    path = sdk / "transfer/diligence/raw_client.go"
    require(path.is_file() and not path.is_symlink(), "Missing generated transfer diligence client")
    metadata = parse_json((sdk / ".fern/metadata.json").read_bytes())
    require(metadata.get("generatorVersion") == values["generator_version"], "Multipart fix requires the pinned generated version")
    text = path.read_text()
    signature = "func (r *RawClient) UploadDocument(\n"
    require(text.count(signature) == 1, "Unrecognized transfer diligence upload method")
    start = text.index(signature)
    next_method = text.find("\nfunc ", start + len(signature))
    end = len(text) if next_method < 0 else next_method
    method = text[start:end]
    old = '\tif err := writer.WriteJSON("purpose", string(request.Purpose)); err != nil {\n\t\treturn nil, err\n\t}\n'
    corrected = old.replace('writer.WriteJSON(', 'writer.WriteField(', 1)
    require("request *transfer.TransferDiligenceDocumentUploadRequest," in method and
            '"/transfer/diligence/document/upload"' in method and
            'writer.WriteFile("file", request.File)' in method and method.count('"purpose"') == 1 and
            method.count(old) + method.count(corrected) == 1,
            "Unrecognized multipart purpose serialization; review the generated shape")
    if corrected in method:
        return False
    path.write_text(text[:start] + method.replace(old, corrected, 1) + text[end:])
    return True


def generate_new_client(sdk: Path, config: Path, version: str, values: dict, work: Path) -> None:
    # Explicitly preserve the entire trusted automation surface, including future files.
    ignore = sdk / ".fernignore"
    updated = ignore.read_text()
    for pattern in (".github/", "scripts/release/"):
        if pattern not in updated.splitlines():
            updated += "\n" + pattern + "\n"
    ignore.write_text(updated)
    git(sdk, "add", ".fernignore")
    if git(sdk, "diff", "--cached", "--name-only"):
        git(sdk, "-c", "user.name=SDK generator", "-c", "user.email=sdk-generator@localhost",
            "-c", "commit.gpgsign=false", "commit", "-m", "Preserve reviewed release automation during generation")
    before = protected_state(sdk)
    cli = install_cli(work, values)
    reference = values["generator_image"] + "@" + values["generator_digest"]
    run(["docker", "pull", reference], log=work / "generator-pull.log")
    image = json.loads(run(["docker", "image", "inspect", reference]))[0]
    require(reference in image["RepoDigests"], "Pulled generator does not match the pinned digest")
    save_json(work / "generator-image.json", {key: image[key] for key in ("Id", "RepoDigests", "Architecture", "Os")})
    log = work / "fern-generation.log"
    run(["node", str(cli), "generate", "--group", "go-pipeline", "--local", "--no-prompt",
         "--force", "--version", "v" + version, "--log-level", "debug"], config, log=log)
    require(re.search(r"\+ docker run .* " + re.escape(reference) + r" /fern/config\.json", log.read_text()) is not None,
            "Generation log does not establish execution of the pinned image digest")
    # The pinned CLI can prepend a version-only changelog after .fernignore restoration.
    # The reviewed release text belongs to the SDK PR reviewer; restore it from the clean base.
    run(["git", "restore", "--source=HEAD", "--staged", "--worktree", "--", "CHANGELOG.md"], sdk)
    git(sdk, "add", "-A")
    after = protected_state(sdk)
    require(before == after, "Generation modified protected SDK files or release automation")
    check_maintained_caller(sdk, log)
    restore_published_multipart_field(sdk, values)
    save_json(work / "wire-test-hardening.json", harden_wire_tests(sdk))


def run_legacy(sdk: Path, spec: Path, module: str, values: dict, work: Path) -> dict:
    adapter = ROOT / "pipeline/legacy/generate.py"
    require(adapter.is_file(), "Portable same-spec legacy generator has not been installed")
    output = work / "legacy-manifest.json"
    run([sys.executable, str(adapter), "--spec", str(spec), "--sdk", str(sdk),
         "--module", module, "--manifest", str(output)], ROOT, timeout=1800, log=work / "legacy.log")
    legacy = json.loads(output.read_text())
    require(set(legacy) == {"source_commit", "spec_sha256", "tree_sha256", "generator_digest"}, "Unexpected legacy manifest schema")
    check_sha(legacy["source_commit"])
    require(legacy["spec_sha256"] == sha256(spec.read_bytes()), "Legacy was not generated from the same exact public spec")
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", legacy["generator_digest"]) is not None, "Legacy generator digest is missing")
    git(sdk, "add", "-A")
    actual = sha256(canonical([item for item in entries(sdk) if item[0].startswith("legacy/")]))
    require(actual == legacy["tree_sha256"], "Legacy manifest tree hash mismatch")
    return legacy


def verify_sdk(sdk: Path, values: dict, work: Path) -> None:
    run(["go", "mod", "tidy", "-go=1.21"], sdk, log=work / "tidy.log")
    run(["go", "build", "./..."], sdk,
        env=clean_env(GOTOOLCHAIN="go" + values["go_floor"]), log=work / "go-floor-build.log")
    # A unique, task-owned container; no compose file from generated output is executed.
    name = "plaid-sdk-wiremock-" + work.name.lower().replace("_", "-")[:30]
    mapping = sdk / "wiremock/wiremock-mappings.json"
    require(mapping.is_file(), "Generated WireMock mappings are missing")
    run(["docker", "run", "-d", "--name", name, "-p", "127.0.0.1::8080", "-v",
         str(mapping) + ":/home/wiremock/mappings/wiremock-mappings.json:ro", values["wiremock_image"]])
    try:
        import time
        port = run(["docker", "port", name, "8080"]).decode().strip().rsplit(":", 1)[1]
        url = "http://127.0.0.1:" + port
        for attempt in range(30):
            try:
                urllib.request.urlopen(url + "/__admin/health", timeout=2).close()
                break
            except OSError:
                if attempt == 29:
                    raise PipelineError("WireMock did not become healthy")
                time.sleep(1)
        run(["go", "test", "-count=1", "-timeout=180s", "./..."], sdk,
            env=clean_env(WIREMOCK_URL=url), timeout=1200, log=work / "sdk-tests.log")
    finally:
        run(["docker", "rm", "-f", name])


def compatibility_gate(old: Path, sdk: Path, module: str, published: bool, values: dict, work: Path) -> None:
    if not published:
        (work / "api-diff.txt").write_text("Initial configured major has no published stable tag; no within-major compatibility promise yet.\n")
        return
    binary = work / "bin"
    binary.mkdir()
    run(["go", "install", "golang.org/x/exp/cmd/apidiff@" + values["apidiff_version"]],
        env=clean_env(GOBIN=str(binary), GOTOOLCHAIN="go" + values["go_version"]), log=work / "apidiff-install.log")
    tool = str(binary / "apidiff")
    before, after = work / "before.api", work / "after.api"
    run([tool, "-m", "-w", str(before), module], old, timeout=1200)
    run([tool, "-m", "-w", str(after), module], sdk, timeout=1200)
    changes = run([tool, "-m", "-incompatible", str(before), str(after)], timeout=1200)
    (work / "api-diff.txt").write_bytes(changes)
    require(not changes.strip(), "Breaking SDK or legacy API change: review a new configured major instead of publishing a minor/patch")


def manifest_for(values: dict, *, version: str, source_commit: str, source_bytes: bytes,
                 config_repo: str, config_commit: str, config_hash: str, run_id: str,
                 legacy: dict, content_hash: str) -> dict:
    require(source_commit == config_commit and config_repo == values["spec_repository"],
            "Generation spec and config must come from the same public commit")
    return {"schema_version": 1,
            "sdk": {"repository": values["sdk_repository"], "version": version,
                    "module": "github.com/" + values["sdk_repository"] + "/v" + str(version_tuple(version)[0])},
            "source": {"repository": values["spec_repository"], "commit": source_commit,
                       "path": values["spec_path"], "sha256": sha256(source_bytes)},
            "config": {"repository": config_repo, "commit": config_commit, "sha256": config_hash},
            "generator": {"cli_version": values["cli_version"], "cli_sha256": values["cli_sha256"],
                          "image_digest": values["generator_digest"]},
            "legacy": legacy, "content_sha256": content_hash,
            "generation": {"repository": config_repo, "workflow": WORKFLOW, "run_id": run_id}}


def update_changelog(sdk: Path, version: str, spec: bytes, values: dict) -> None:
    path = sdk / "CHANGELOG.md"
    text = path.read_text()
    if re.search(r"^#{1,2} (?:\[)?v?" + re.escape(version) + r"(?:\])?(?:\s|$)", text, re.MULTILINE):
        return
    parts = spec_version(spec)
    spec_label = f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}_{parts[3]}.{parts[4]}.{parts[5]}"
    entry = (f"## [v{version}]\n\nRegenerate the new client and legacy package from OpenAPI `{spec_label}` "
             f"using Fern Go `{values['generator_version']}` for the new client.\n\n")
    path.write_text(entry + text)


def sanitize_metadata(sdk: Path, version: str, module: str, values: dict) -> None:
    path = sdk / ".fern/metadata.json"
    metadata = json.loads(path.read_text())
    expected = {"cliVersion": values["cli_version"], "generatorName": "fernapi/fern-go-sdk",
                "generatorVersion": values["generator_version"], "sdkVersion": "v" + version}
    require(all(metadata.get(key) == value for key, value in expected.items()), "Raw Fern metadata does not match the pinned generation")
    config = metadata.get("generatorConfig", {})
    require(config.get("module", {}).get("path") == module and config.get("importPath") == module,
            "Raw Fern metadata contains the wrong public module")
    require(type(config.get("maxRetries")) is int and config["maxRetries"] == 0, "Raw Fern metadata enables automatic retries")
    # Keep only version identity in SDK metadata; the manifest links the public config.
    save_json(path, expected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    values = settings()
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    override, rehearsal = event_request(os.environ["GITHUB_EVENT_NAME"], event, values)
    config_repo, config_commit, run_id = check_context(event, values, rehearsal)
    output = args.output.resolve()
    require(not output.exists(), "Output directory already exists; never overwrite run evidence")
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="sdk-generation-") as temporary:
        work = Path(temporary).resolve()
        sdk = work / "sdk"
        base = fetch_repository(values["sdk_repository"], values["sdk_branch"], sdk)
        tag_refs = git(sdk, "ls-remote", "--tags", "origin", "refs/tags/v*")
        waiting = pending_release(sdk, tag_refs)
        if waiting:
            save_json(output / "result.json", {"status": "awaiting-release", "sdk_base": base, "version": waiting})
            return
        source_commit, data = verified_spec(ROOT, config_commit, values, sdk)
        tags = [line.split("refs/tags/", 1)[1] for line in tag_refs.splitlines() if not line.endswith("^{}")]
        version = propose_version(tags, values["major"], override)
        config_hash = config_digest(ROOT)
        identity = input_identity(version, sha256(data), config_hash)
        # Read-only catch-up: the current manifest proves these exact inputs already reached master.
        prior = json.loads((sdk / MANIFEST).read_text()) if (sdk / MANIFEST).exists() else None
        unchanged = prior and not override and prior["source"]["sha256"] == sha256(data) and prior["config"]["sha256"] == config_hash
        if unchanged:
            save_json(output / "result.json", {"status": "unchanged", "sdk_base": base})
            return
        module = "github.com/" + values["sdk_repository"] + "/v" + str(values["major"])
        assert_sdk_bootstrap(sdk, module)
        old = work / "before"
        baseline_tag = published_baseline(sdk, tags, values["major"], old)
        # Old provenance must not survive into a newly generated PR.
        run(["git", "rm", "--ignore-unmatch", "--", MANIFEST, BUNDLE], sdk)
        if git(sdk, "diff", "--cached", "--name-only"):
            git(sdk, "-c", "user.name=SDK generator", "-c", "user.email=sdk-generator@localhost",
                "-c", "commit.gpgsign=false", "commit", "-m", "Replace prior generation evidence")
        local_config = work / "config"
        render_config(local_config, sdk, data, version, values)
        generate_new_client(sdk, local_config, version, values, work)
        before_legacy = protected_state(sdk)
        legacy = run_legacy(sdk, local_config / "2020-09-14.yml", module, values, work)
        require(protected_state(sdk) == before_legacy, "Legacy generator modified protected release/customization files")
        verify_sdk(sdk, values, work)
        compatibility_gate(old, sdk, module, baseline_tag is not None, values, work)
        update_changelog(sdk, version, data, values)
        sanitize_metadata(sdk, version, module, values)
        git(sdk, "add", "-A")
        index, digest = content(sdk)
        manifest = manifest_for(values, version=version, source_commit=source_commit, source_bytes=data,
                                config_repo=config_repo, config_commit=config_commit, config_hash=config_hash,
                                run_id=run_id, legacy=legacy, content_hash=digest)
        save_json(sdk / MANIFEST, manifest)
        git(sdk, "add", MANIFEST)
        archive_sdk(sdk, output / "sdk.tar.gz")
        (output / "content.json").write_bytes(index)
        save_json(output / "manifest.json", manifest)
        save_json(output / "plan.json", {"sdk_base": base, "branch": "sdk-generation/go-v" + str(values["major"]) + "-" + identity,
                                        "identity": identity, "rehearsal": rehearsal})
        save_json(output / "result.json", {"status": "generated", "content_sha256": digest,
                                           "subject_name": "plaid-go-v" + version + "-source", "rehearsal": rehearsal})


if __name__ == "__main__":
    try:
        main()
    except (PipelineError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
