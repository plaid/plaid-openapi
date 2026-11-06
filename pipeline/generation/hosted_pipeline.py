#!/usr/bin/env python3
"""Prepare, assemble and finalize hosted SDK candidates without generation secrets."""

import argparse
import os
from pathlib import Path
import re
import shutil
import tempfile

import generate
import hosted_contract
from attestation import parse_json, validate_manifest
from common import (BUNDLE, MANIFEST, WORKFLOW, archive_sdk, approved_generated_changes,
                    canonical, check_sha, content, entries, extract_sdk, git, protected,
                    protected_state, propose_version, require, run, save_json, sha256, version_tuple)

PROOFS = (MANIFEST, BUNDLE, hosted_contract.FERN_INDEX, hosted_contract.FERN_BUNDLE, hosted_contract.FERN_PROVENANCE)
PLAN_KEYS = {"schema_version", "source", "config", "generation", "sdk_base", "baseline", "tags",
             "current_major", "version", "override", "rehearsal"}


def context():
    require(not any(os.environ.get(key) for key in (
        "FERN_TOKEN", "SDK_FERN_READ_TOKEN", "SDK_PR_TOKEN", "SDK_PR_APP_PRIVATE_KEY", "SDK_INTEGRATION_APP_PRIVATE_KEY",
        "SDK_RELEASE_APP_PRIVATE_KEY", "SDK_RELEASE_SIGNING_PRIVATE_KEY", "GO_SDK_PUSH_KEY", "SSH_AUTH_SOCK")),
        "SDK assembly must not receive privileged credentials")
    values = generate.settings()
    event = parse_json(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
    override, rehearsal = generate.event_request(os.environ["GITHUB_EVENT_NAME"], event, values)
    repository, commit, run_id = generate.check_context(event, values, rehearsal)
    return values, repository, commit, run_id, override, rehearsal


def new_output(path):
    require(not path.exists(), "Output directory already exists")
    path.mkdir(parents=True)


def tags_from_refs(refs):
    return sorted(line.split("refs/tags/", 1)[1] for line in refs.splitlines() if not line.endswith("^{}"))


def major_version(plan):
    require(not plan["override"], "Explicit version overrides cannot select another major")
    major = plan["current_major"] + 1
    require(not any(re.fullmatch(r"v" + str(major) + r"\.[0-9]+\.[0-9]+", tag) for tag in plan["tags"]),
            "Next major already has published tags")
    return f"{major}.0.0"


def prepare(output):
    values, repository, commit, run_id, override, rehearsal = context()
    new_output(output)
    mode = values.get("generation_mode", "local")
    result = {"status": "ready", "mode": mode, "rehearsal": rehearsal}
    if mode == "local":
        save_json(output / "result.json", result)
        return result
    require(mode == "fern-hosted", "Unknown generation mode")
    with tempfile.TemporaryDirectory(prefix="sdk-hosted-plan-") as temporary:
        work, sdk = Path(temporary), Path(temporary) / "sdk"
        base = generate.fetch_repository(values["sdk_repository"], values["sdk_branch"], sdk)
        refs = git(sdk, "ls-remote", "--tags", "origin", "refs/tags/v*")
        waiting = generate.pending_release(sdk, refs)
        if waiting:
            result.update(status="awaiting-release", sdk_base=base, version=waiting)
        else:
            _, data = generate.verified_spec(generate.ROOT, commit, values, sdk)
            from overlay_coverage import validate
            validate(data, (generate.ROOT / "fern/openapi-overlay.yml").read_bytes())
            config_hash = generate.config_digest(generate.ROOT)
            prior = parse_json((sdk / MANIFEST).read_bytes()) if (sdk / MANIFEST).exists() else None
            if prior and not override and prior["source"]["sha256"] == sha256(data) and prior["config"]["sha256"] == config_hash:
                result.update(status="unchanged", sdk_base=base)
            else:
                major, tags = generate.current_major(sdk, values), tags_from_refs(refs)
                stable = [version_tuple(tag[1:])[0] for tag in tags if re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", tag)]
                require(major == max([item for item in stable if item >= values["major"]] or [values["major"]]),
                        "SDK module differs from the latest supported published major")
                version = propose_version(tags, major, override)
                generate.assert_sdk_bootstrap(sdk, f"github.com/plaid/plaid-go/v{major}")
                before = work / "baseline"
                tag = generate.published_baseline(sdk, tags, major, before)
                plan = {"schema_version": 1, "sdk_base": base, "tags": tags, "current_major": major,
                        "version": version, "override": override, "rehearsal": rehearsal,
                        "baseline": {"tag": tag, "commit": check_sha(git(before, "rev-parse", "HEAD"))} if tag else None,
                        "source": {"repository": repository, "commit": commit, "path": values["spec_path"], "sha256": sha256(data)},
                        "config": {"repository": repository, "commit": commit, "sha256": config_hash},
                        "generation": {"repository": repository, "workflow": WORKFLOW, "run_id": run_id}}
                save_json(output / "plan.json", plan)
                result["version"] = version
    save_json(output / "result.json", result)
    return result


def load_plan(directory):
    values, repository, commit, run_id, override, rehearsal = context()
    require(values.get("generation_mode") == "fern-hosted", "Hosted assembly requires reviewed hosted configuration")
    plan = parse_json((directory / "plan.json").read_bytes())
    require(isinstance(plan, dict) and set(plan) == PLAN_KEYS and type(plan["schema_version"]) is int
            and plan["schema_version"] == 1, "Unexpected preparation plan")
    _, data = generate.verified_spec(generate.ROOT, commit, values)
    require(plan["source"] == {"repository": repository, "commit": commit, "path": values["spec_path"], "sha256": sha256(data)}
            and plan["config"] == {"repository": repository, "commit": commit, "sha256": generate.config_digest(generate.ROOT)}
            and plan["generation"] == {"repository": repository, "workflow": WORKFLOW, "run_id": run_id},
            "Preparation plan is not from this source and workflow run")
    require(type(plan["rehearsal"]) is bool and plan["rehearsal"] == rehearsal and plan["override"] == override,
            "Preparation plan differs from the trusted workflow inputs")
    require(type(plan["current_major"]) is int and plan["current_major"] >= values["major"]
            and isinstance(plan["tags"], list) and all(isinstance(tag, str) for tag in plan["tags"])
            and plan["tags"] == sorted(set(plan["tags"])), "Invalid version plan")
    check_sha(plan["sdk_base"])
    require(plan["version"] == propose_version(plan["tags"], plan["current_major"], override), "Version plan changed")
    if plan["baseline"] is not None:
        require(set(plan["baseline"]) == {"tag", "commit"} and plan["baseline"]["tag"] in plan["tags"], "Invalid baseline")
        check_sha(plan["baseline"]["commit"])
    return plan, values, data


def verify_delivery(directory, plan, values, version):
    record = hosted_contract.validate_fern_record(parse_json((directory / "fern-record.json").read_bytes()))
    require(all(record[key] == plan[key] for key in ("source", "config", "generation", "sdk_base"))
            and record["sdk_version"] == version
            and record["cli"] == {"version": values["cli_version"], "sha256": values["cli_sha256"]}
            and record["generator"] == {"image": values["generator_image"], "version": values["generator_version"],
                                        "sha256": values["generator_digest"].removeprefix("sha256:")},
            "Fern evidence differs from the prepared inputs")
    index, bundle = directory / "fern-content.json", directory / "fern.bundle.json"
    hosted_contract.validate_fern_index(index.read_bytes(), record)
    provenance = directory / "fern-provenance.json"
    require(provenance.is_file() and not provenance.is_symlink(), "Portable Fern provenance is missing or unsafe")
    hosted_contract.validate_fern_provenance(provenance.read_bytes(), record)
    if plan["rehearsal"]:
        require(not bundle.exists(), "Unsigned rehearsal must not carry production signing evidence")
    else:
        require(bundle.is_file(), "Hosted candidate has no signed Fern verification")
        hosted_contract.verify_fern_evidence(index, bundle, record)
    return record


def initialize_tree(path):
    git(path, "init", "-q")
    git(path, "add", "-A")


def preserved_paths(sdk):
    ignored = []
    for line in (sdk / ".fernignore").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        require(not any(char in line for char in "*?![]\\") and not line.startswith("/")
                and ".." not in Path(line).parts, "Review unsupported .fernignore pattern")
        ignored.append(line)
    return lambda name: protected(name) or name.startswith("legacy/") or any(
        name == item or item.endswith("/") and name.startswith(item) for item in ignored)


def copy_generated(sdk, raw):
    preserved = preserved_paths(sdk)
    incoming = {name: (mode, digest) for name, mode, digest in entries(raw)}
    previous = {name: (mode, digest) for name, mode, digest in entries(sdk)}
    for name in incoming:
        require(not preserved(name), "Fern export contains maintained SDK content")
    for name in previous.keys() - incoming.keys():
        if not preserved(name) and re.fullmatch(r"(?:[a-z][a-z0-9_]*/)*[a-z][a-z0-9_]*\.go", name):
            (sdk / name).unlink()
    for name in incoming:
        target = sdk / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(raw / name, target)


def fetch_baseline(plan, values, work):
    sdk, old = work / "public-sdk", work / "baseline"
    base = generate.fetch_repository(values["sdk_repository"], values["sdk_branch"], sdk)
    require(base == plan["sdk_base"], "SDK master changed after preparation")
    refs = git(sdk, "ls-remote", "--tags", "origin", "refs/tags/v*")
    require(tags_from_refs(refs) == plan["tags"], "SDK tags changed after preparation")
    require(generate.current_major(sdk, values) == plan["current_major"], "SDK major changed after preparation")
    generate.assert_sdk_bootstrap(sdk, f"github.com/plaid/plaid-go/v{plan['current_major']}")
    tag = generate.published_baseline(sdk, plan["tags"], plan["current_major"], old)
    baseline = {"tag": tag, "commit": git(old, "rev-parse", "HEAD")} if tag else None
    require(baseline == plan["baseline"], "Published comparison baseline changed")
    return sdk, old


def assemble(prepared, fern, output, major=False):
    """Create a candidate using trusted transformations; never execute SDK code."""
    plan, values, data = load_plan(prepared)
    version = major_version(plan) if major else plan["version"]
    record = verify_delivery(fern, plan, values, version)
    new_output(output)
    with tempfile.TemporaryDirectory(prefix="sdk-hosted-assembly-") as temporary:
        work = Path(temporary)
        # The ordinary read token is used only for signature verification above.
        os.environ.pop("GH_TOKEN", None)
        sdk, _old = fetch_baseline(plan, values, work)
        base = plan["sdk_base"]
        run(["git", "rm", "--ignore-unmatch", "--", *PROOFS], sdk)
        if major:
            generate.rewrite_module(sdk, plan["current_major"], plan["current_major"] + 1)
        raw = work / "fern"
        extract_sdk(fern / "fern-output.tar.gz", raw)
        initialize_tree(raw)
        require(content(raw)[0] == (fern / "fern-content.json").read_bytes(), "Fern archive differs from verified content index")
        before = protected_state(sdk)
        copy_generated(sdk, raw)
        generate.restore_published_multipart_field(sdk, values)
        generate.harden_wire_tests(sdk)
        metadata = parse_json((sdk / ".fern/metadata.json").read_bytes())
        require(metadata == {"cliVersion": values["cli_version"], "generatorName": values["generator_image"],
                             "generatorVersion": values["generator_version"], "sdkVersion": "v" + version},
                "Fern metadata differs from the requested SDK")
        module = f"github.com/plaid/plaid-go/v{version_tuple(version)[0]}"
        legacy = generate.run_legacy(sdk, generate.ROOT / values["spec_path"], module, values, work)
        require(legacy["spec_sha256"] == plan["source"]["sha256"] and protected_state(sdk) == before,
                "Legacy input or maintained files changed")
        # Resolves dependencies without running generated SDK code. Execution
        # belongs to a separate job after this candidate receives its assembly seal.
        run(["go", "mod", "tidy", "-go=1.21"], sdk, log=work / "dependencies.log")
        generate.update_changelog(sdk, version, data, values)
        git(sdk, "add", "-A")
        approved_generated_changes(sdk, sdk, version_tuple(version)[0], base_ref=base)
        for name in ("fern-content.json", "fern-record.json", "fern.bundle.json", "fern-provenance.json"):
            if (fern / name).is_file():
                shutil.copy2(fern / name, output / name)
        proof_files = [("fern-content.json", hosted_contract.FERN_INDEX), ("fern-provenance.json", hosted_contract.FERN_PROVENANCE)]
        if not plan["rehearsal"]:
            proof_files.append(("fern.bundle.json", hosted_contract.FERN_BUNDLE))
        for source, destination in proof_files:
            target = sdk / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fern / source, target)
        git(sdk, "add", "-A")
        index, digest = content(sdk)
        manifest = generate.manifest_for(values, version=version, source_commit=plan["source"]["commit"], source_bytes=data,
            config_repo=plan["config"]["repository"], config_commit=plan["config"]["commit"], config_hash=plan["config"]["sha256"],
            run_id=plan["generation"]["run_id"], legacy=legacy, content_hash=digest)
        manifest.update(schema_version=2, fern=record)
        validate_manifest(manifest)
        hosted_contract.validate_fern_record(record, manifest)
        save_json(sdk / MANIFEST, manifest)
        save_json(output / "manifest.json", manifest)
        git(sdk, "add", MANIFEST)
        archive_sdk(sdk, output / "sdk.tar.gz")
        (output / "content.json").write_bytes(index)
        identity = generate.input_identity(version, plan["source"]["sha256"], plan["config"]["sha256"], base)
        save_json(output / "plan.json", {"sdk_base": base, "branch": f"sdk-generation/go-v{version_tuple(version)[0]}-" + identity,
                                        "identity": identity, "rehearsal": plan["rehearsal"]})
        result = {"status": "assembled", "content_sha256": digest, "subject_name": "plaid-go-v" + version + "-source",
                  "version": version, "rehearsal": plan["rehearsal"]}
        save_json(output / "result.json", result)
        return result


def verified_candidate(directory, tree, plan, values, version):
    from assembly_seal import verify_assembly_artifact
    manifest, publication = verify_assembly_artifact(directory, tree)
    require(manifest["schema_version"] == 2 and manifest["sdk"]["version"] == version
            and all(manifest[key] == plan[key] for key in ("source", "config", "generation"))
            and manifest["fern"]["sdk_base"] == plan["sdk_base"]
            and publication["sdk_base"] == plan["sdk_base"] and publication["rehearsal"] == plan["rehearsal"],
            "Sealed candidate differs from the trusted preparation")
    hosted_contract.validate_generation_mode(manifest, values)
    return manifest


def validate(prepared, candidate, output, probe=None):
    """Execute checks in an isolated job; emit decisions, never replacement SDK bytes."""
    plan, values, _data = load_plan(prepared)
    version = major_version(plan) if probe is not None else plan["version"]
    new_output(output)
    with tempfile.TemporaryDirectory(prefix="sdk-hosted-validation-") as temporary:
        work, sdk = Path(temporary), Path(temporary) / "candidate"
        manifest = verified_candidate(candidate, sdk, plan, values, version)
        probe_tree = None
        if probe is not None:
            probe_tree = work / "probe"
            verified_candidate(probe, probe_tree, plan, values, plan["version"])
        os.environ.pop("GH_TOKEN", None)
        public, old = fetch_baseline(plan, values, work)
        approved_generated_changes(public, sdk, version_tuple(version)[0])
        if probe_tree is not None:
            approved_generated_changes(public, probe_tree, plan["current_major"])
        before_tests = content(sdk)[0]
        probe_before = content(probe_tree)[0] if probe_tree is not None else None
        generate.verify_sdk(sdk, values, work)
        git(sdk, "add", "-A")
        require(content(sdk)[0] == before_tests, "SDK execution modified the sealed candidate")
        if probe_tree is not None:
            git(probe_tree, "add", "-A")
            require(content(probe_tree)[0] == probe_before, "SDK execution modified the sealed probe")
        comparison = work / "comparison"
        comparison.mkdir()
        module = f"github.com/plaid/plaid-go/v{plan['current_major']}"
        changes = generate.compatibility_gate(old, probe_tree if probe_tree is not None else sdk,
            module, plan["baseline"] is not None, values, comparison, allow_breaking=not plan["override"])
        if probe_tree is None:
            status = "needs-major" if changes.strip() else "generated"
            if status == "needs-major":
                major_version(plan)
        else:
            require(changes.strip(), "Major generation requires a breaking provisional candidate")
            normalized = work / "normalized"
            shutil.copytree(sdk, normalized)
            generate.rewrite_module(normalized, plan["current_major"] + 1, plan["current_major"])
            for label, a, b in (("forward", probe_tree, normalized), ("reverse", normalized, probe_tree)):
                stage = comparison / label
                stage.mkdir()
                generate.compatibility_gate(a, b, module, True, values, stage)
            status = "generated"
        (output / "api-diff.txt").write_bytes(changes)
        result = {"status": status, "content_sha256": manifest["content_sha256"],
                  "subject_name": "plaid-go-v" + version + "-source", "version": version, "rehearsal": plan["rehearsal"]}
        if status == "needs-major":
            result["next_version"] = major_version(plan)
        save_json(output / "result.json", result)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "assemble", "validate"))
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--fern", type=Path)
    parser.add_argument("--probe", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--major", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.output.resolve())
    elif args.mode == "assemble":
        require(args.prepared is not None and args.fern is not None, "Assembly needs preparation and Fern artifacts")
        require(args.probe is None, "Assembly does not execute probe comparisons")
        assemble(args.prepared.resolve(), args.fern.resolve(), args.output.resolve(), args.major)
    else:
        require(args.prepared is not None and args.candidate is not None and not args.major,
                "Validation needs preparation and a sealed candidate; majors also require a sealed probe")
        validate(args.prepared.resolve(), args.candidate.resolve(), args.output.resolve(), args.probe.resolve() if args.probe else None)


if __name__ == "__main__":
    main()
