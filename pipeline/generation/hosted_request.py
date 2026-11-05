#!/usr/bin/env python3
"""Privileged Fern launch and receipt verification; never execute SDK output."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import base64
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
from urllib.parse import quote

import yaml

import fern_delivery
import generate
from attestation import parse_json
from common import (PipelineError, check_sha, clean_env, propose_version,
                    require, save_json, sha256, version_tuple)
from hosted_output import export_verified_output, git_files

PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEQmN9BeIQlQwt58feCt19d4mXiClx
yjkXDbQGTiaSJs1q9gCUNCwkyTsEx2+ElqTkbbhD+YMz2XaXuNrrlAt/hg==
-----END PUBLIC KEY-----
"""
CLI_VERSION = "5.193.2"
CLI_SHA256 = "bf69ff492a3ab6bc5ff890eff0060fd59ef9612eb9d3b30697dfbe6c16fbd059"
UUID = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"


def private_command(argv, *, cwd=None, env=None, timeout=300):
    try:
        result = subprocess.run(argv, cwd=cwd, env=env or clean_env(),
                                capture_output=True, timeout=timeout)
        require(result.returncode == 0, "Private SDK operation failed")
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        raise PipelineError("Private SDK operation failed") from None


def fetch_objects(destination: Path, repository: str, commits: list[str], token: str | None = None):
    """Use transient HTTP auth; never put credentials in Git URLs, files or logs."""
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is not None
            and all(part not in {".", ".."} for part in repository.split("/")), "Invalid SDK repository setting")
    require(commits and all(check_sha(commit) for commit in commits), "Expected fixed Git commits")
    require(not destination.exists(), "Refusing to reuse a private Git directory")
    env = clean_env(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1")
    private_command(["git", "init", "--bare", "--template=", str(destination)], env=env)
    if token is not None:
        require(isinstance(token, str) and token and all(32 < ord(char) < 127 for char in token), "Missing SDK reader credential")
        authorization = base64.b64encode(("x-access-token:" + token).encode()).decode()
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                   GIT_CONFIG_VALUE_0="Authorization: Basic " + authorization)
    try:
        private_command(["git", "-c", "credential.helper=", "-c", "http.followRedirects=false",
                         "-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
                         "-c", "fetch.fsckObjects=true", "fetch", "--no-tags", "--no-write-fetch-head",
                         "--depth=2" if token is not None else "--depth=1",
                         "https://github.com/" + repository + ".git", *commits], cwd=destination, env=env)
    finally:
        env.pop("GIT_CONFIG_VALUE_0", None)


def validate_plan(plan: dict, settings: dict, major: bool) -> str:
    expected_keys = {"schema_version", "source", "config", "generation", "sdk_base", "baseline", "tags",
                     "current_major", "version", "override", "rehearsal"}
    require(isinstance(plan, dict) and set(plan) == expected_keys and type(plan["schema_version"]) is int
            and plan["schema_version"] == 1 and type(plan["rehearsal"]) is bool, "Invalid hosted generation plan")
    event = parse_json(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
    override, rehearsal = generate.event_request(os.environ.get("GITHUB_EVENT_NAME", ""), event, settings)
    require(plan["override"] == override and plan["rehearsal"] == rehearsal, "Plan differs from the workflow's requested version or mode")
    repository, commit, run_id = generate.check_context(event, settings, plan["rehearsal"])
    require(settings.get("generation_mode") == "fern-hosted" and settings["cli_version"] == CLI_VERSION
            and settings["cli_sha256"] == CLI_SHA256, "Hosted generation requires the reviewed CLI and mode")
    source = {"repository": repository, "commit": commit, "path": settings["spec_path"],
              "sha256": sha256((generate.ROOT / settings["spec_path"]).read_bytes())}
    require(plan["source"] == source and plan["config"] == {"repository": repository, "commit": commit,
            "sha256": generate.config_digest(generate.ROOT)}, "Plan differs from the reviewed source inputs")
    require(plan["generation"] == {"repository": repository, "workflow": ".github/workflows/generate-go-sdk.yml", "run_id": run_id},
            "Plan differs from this workflow invocation")
    check_sha(plan["sdk_base"])
    require(type(plan["current_major"]) is int and plan["current_major"] >= 49
            and isinstance(plan["tags"], list) and all(isinstance(tag, str) for tag in plan["tags"])
            and isinstance(plan["override"], str), "Invalid planned version inputs")
    require(plan["version"] == propose_version(plan["tags"], plan["current_major"], plan["override"]),
            "Planned SDK version differs from the release policy")
    if major:
        target = plan["current_major"] + 1
        require(not plan["override"] and not any(tag.startswith(f"v{target}.") for tag in plan["tags"]),
                "Cannot automatically regenerate an overridden or already published major")
        return f"{target}.0.0"
    version_tuple(plan["version"])
    return plan["version"]


def private_target(repository, repository_id, token):
    require(isinstance(repository, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            and all(part not in {".", ".."} for part in repository.split("/")), "Invalid private Fern output setting")
    require(isinstance(repository_id, str) and re.fullmatch(r"[1-9][0-9]*", repository_id), "Invalid private repository identity")
    repository_id = int(repository_id)
    metadata = fern_delivery._get("repos/" + repository, token)
    fern_delivery._repository(metadata, repository, repository_id)
    branch = metadata.get("default_branch")
    require(isinstance(branch, str) and branch and not any(ord(char) < 32 for char in branch), "Invalid private SDK default branch")
    current = fern_delivery._get("repos/" + repository + "/branches/" + quote(branch, safe=""), token)
    require(current.get("name") == branch and isinstance(current.get("commit"), dict), "Private SDK branch changed")
    return repository_id, branch, check_sha(current["commit"].get("sha", ""))


def render_request(config: Path, spec: bytes, version: str, settings: dict, repository: str):
    generate.render_config(config, config.parent / "unused-local-output", spec, version, settings)
    path = config / "fern/generators.yml"
    document = yaml.safe_load(path.read_text())
    require(set(document["groups"]) == {"go-pipeline"}, "Expected only the reviewed Go generator")
    entries = document["groups"]["go-pipeline"]["generators"]
    require(len(entries) == 1, "Expected one Go generator")
    entry = entries[0]
    require(entry["name"] == settings["generator_image"] + "@" + settings["generator_digest"]
            and entry["version"] == settings["generator_version"] and
            entry["output"]["location"] == "local-file-system", "Unexpected rendered generator")
    del entry["output"]
    entry["name"] = settings["generator_image"]
    entry["github"] = {"repository": repository, "mode": "pull-request", "workflows": False, "license": "MIT"}
    require(document.get("replay", {}).get("enabled") is False, "Hosted replay must remain disabled")
    path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True))
    inputs = {"fern:" + name: sha256((config / "fern" / name).read_bytes())
              for name in ("../" + settings["spec_path"], "openapi-overlay.yml", "generators.yml")}
    inputs["fern:generators.yml#" + settings["generator_image"]] = sha256(json.dumps(
        entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
    return inputs


class RegistrySink(http.server.BaseHTTPRequestHandler):
    """Contain CLI registry writes without retaining request headers or contents."""
    def log_message(self, *_args):
        pass

    def reject(self):
        if self.command == "POST" and self.path == "/registry/api/register":
            self.server.registration_blocked = True
        remaining = int(self.headers.get("Content-Length", "0"))
        while remaining > 0:
            chunk = self.rfile.read(min(remaining, 65536))
            if not chunk:
                break
            remaining -= len(chunk)
        self.close_connection = True
        response = b'{"message":"Registry writes are disabled"}'
        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(response)

    do_GET = reject
    do_POST = reject
    do_PUT = reject
    do_PATCH = reject
    do_DELETE = reject


def launch(config, cli, version, token, repository):
    require(isinstance(token, str) and token and all(32 < ord(char) < 127 for char in token), "Missing Fern credential")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), RegistrySink)
    server.registration_blocked = False
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = clean_env(FERN_TOKEN=token, FERN_FDR_ORIGIN=f"http://127.0.0.1:{server.server_port}",
                    FERN_USE_SDK_GEN_API="false", FERN_NO_VERSION_REDIRECTION="true",
                    NPM_CONFIG_USERCONFIG="/dev/null", NPM_CONFIG_REGISTRY="https://registry.npmjs.org/")
    try:
        result = subprocess.run(["node", str(cli), "generate", "--group", "go-pipeline", "--no-prompt", "--force",
                                 "--version", "v" + version, "--log-level", "debug"], cwd=config, env=env,
                                capture_output=True, timeout=2700, text=True)
        require(result.returncode == 0 and server.registration_blocked, "Hosted Fern generation failed or registry isolation was not observed")
        # Parse the CLI's own job identity, never copy it from the incoming receipt.
        jobs = set(re.findall(r"^DEBUG .* go-pipeline fernapi/fern-go-sdk Job ID: (" + UUID + r")\s*$", result.stdout, re.MULTILINE))
        pulls = set(re.findall(r"^INFO .* go-pipeline fernapi/fern-go-sdk Created pull request: https://github\.com/" +
                              re.escape(repository) + r"/pull/([1-9][0-9]*)\s*$", result.stdout, re.MULTILINE))
        require(len(jobs) == 1 and len(pulls) == 1, "Fern did not return exactly one requested job and private PR")
        return jobs.pop(), int(pulls.pop())
    except (OSError, subprocess.TimeoutExpired):
        raise PipelineError("Hosted Fern generation could not complete") from None
    finally:
        env.pop("FERN_TOKEN", None)
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(prepared: Path, output: Path, *, major=False):
    """Produce only public-safe generated bytes and a predicate for Plaid signing."""
    fern_token = os.environ.pop("FERN_TOKEN", "")
    reader = os.environ.pop("SDK_FERN_READ_TOKEN", "")
    repository = os.environ.pop("FERN_OUTPUT_REPOSITORY", "")
    repository_id = os.environ.pop("FERN_OUTPUT_REPOSITORY_ID", "")
    try:
        require(not any(os.environ.get(name) for name in ("GH_TOKEN", "GITHUB_TOKEN", "SSH_AUTH_SOCK")),
                "Hosted request received an unexpected credential")
        require(prepared.resolve() != output.resolve() and not output.exists(), "Hosted request needs a new output directory")
        plan = parse_json((prepared / "plan.json").read_bytes())
        settings = generate.settings()
        version = validate_plan(plan, settings, major)
        # Everything below runs in a disposable directory; none of it is uploaded.
        with tempfile.TemporaryDirectory(prefix="sdk-private-fern-") as temporary:
            work = Path(temporary)
            public = work / "public.git"
            fetch_objects(public, settings["sdk_repository"], [plan["sdk_base"]])
            public_files = git_files(public, plan["sdk_base"])
            require(public_files["go.mod"][1].splitlines()[0] ==
                    f"module github.com/plaid/plaid-go/v{plan['current_major']}".encode(), "Plan differs from the public SDK base module")
            public_ignore = public_files[".fernignore"][1]
            repository_id, branch, raw_base = private_target(repository, repository_id, reader)
            spec = (generate.ROOT / settings["spec_path"]).read_bytes()
            config = work / "config"
            inputs = render_request(config, spec, version, settings, repository)
            cli = generate.install_cli(work, settings)
            job, number = launch(config, cli, version, fern_token, repository)
            expected = {"repository": "https://github.com/" + repository, "job_id": job, "sdk_version": version,
                        "generator": {"image": settings["generator_image"], "version": settings["generator_version"],
                                      "sha256": settings["generator_digest"].removeprefix("sha256:")}, "inputs": inputs}
            snapshot = fern_delivery.fetch_snapshot(repository=repository, repository_id=repository_id, number=number,
                                                   expected_base=raw_base, machine_token=reader)
            require(snapshot.base_ref == branch, "Generated PR targets a different private branch")
            raw = work / "raw.git"
            fetch_objects(raw, repository, [raw_base, snapshot.head], reader)
            verified = fern_delivery.fetch_and_verify(repository=repository, repository_id=repository_id, number=number,
                expected_base=raw_base, expected_head=snapshot.head, machine_token=reader, sdk_repo=raw,
                public_key=PUBLIC_KEY, expected=expected)
            require(verified.snapshot == snapshot, "Private Fern candidate changed during retrieval")
            safe = work / "public-output"
            safe.mkdir()
            content_hash = export_verified_output(repo=raw, base=raw_base, commit=snapshot.head, public_ignore=public_ignore,
                public_paths=set(public_files), version=version, settings=settings, output=safe, private_repository=repository,
                forbidden_values=(fern_token.encode(), reader.encode()))
            summary = verified.public_summary
            record = {"schema_version": 1, "sdk_version": version, "source": plan["source"], "config": plan["config"],
                      "sdk_base": plan["sdk_base"], "generator": expected["generator"],
                      "cli": {"version": settings["cli_version"], "sha256": settings["cli_sha256"]},
                      "evidence": {key: summary[key] for key in ("receipt_sha256", "key_sha256", "git_commit", "git_tree", "inputs_sha256", "job_id_sha256")},
                      "content_sha256": content_hash, "generation": plan["generation"]}
            save_json(safe / "fern-record.json", record)
            require(set(path.name for path in safe.iterdir()) == {"fern-output.tar.gz", "fern-content.json", "fern-record.json"},
                    "Unexpected public hosted artifact")
            shutil.copytree(safe, output)
    except Exception:
        raise PipelineError("Hosted Fern request or verification failed; no public candidate was produced") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--major", action="store_true")
    args = parser.parse_args()
    try:
        request(args.prepared, args.output, major=args.major)
    except PipelineError as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
