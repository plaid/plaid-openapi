#!/usr/bin/env python3
"""Privileged Fern launch and receipt verification; never execute SDK output."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading

import yaml

import fern_provenance
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


def quiet_command(argv, *, cwd=None, env=None, timeout=300):
    try:
        result = subprocess.run(argv, cwd=cwd, env=env or clean_env(),
                                capture_output=True, timeout=timeout)
        require(result.returncode == 0, "SDK base operation failed")
        return result.stdout
    except (OSError, subprocess.TimeoutExpired):
        raise PipelineError("SDK base operation failed") from None


def fetch_public_base(destination: Path, commit: str):
    """Fetch the exact public SDK base without any GitHub credential."""
    check_sha(commit)
    require(not destination.exists(), "Refusing to reuse a Git directory")
    env = clean_env(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1")
    quiet_command(["git", "init", "--bare", "--template=", str(destination)], env=env)
    quiet_command(["git", "-c", "credential.helper=", "-c", "http.followRedirects=false",
                   "-c", "protocol.allow=never", "-c", "protocol.https.allow=always",
                   "-c", "fetch.fsckObjects=true", "fetch", "--no-tags", "--no-write-fetch-head", "--depth=1",
                   "https://github.com/plaid/plaid-go.git", commit], cwd=destination, env=env)


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


def render_request(config: Path, raw: Path, spec: bytes, version: str, settings: dict):
    require(raw.is_dir() and not raw.is_symlink() and not any(raw.iterdir()), "Expected an empty download directory")
    generate.render_config(config, raw, spec, version, settings)
    path = config / "fern/generators.yml"
    document = yaml.safe_load(path.read_text())
    require(set(document["groups"]) == {"go-pipeline"}, "Expected only the reviewed Go generator")
    entries = document["groups"]["go-pipeline"]["generators"]
    require(len(entries) == 1, "Expected one Go generator")
    entry = entries[0]
    require(entry["name"] == settings["generator_image"] + "@" + settings["generator_digest"]
            and entry["version"] == settings["generator_version"] and
            set(entry["output"]) == {"location", "path"} and entry["output"]["location"] == "local-file-system"
            and (config / "fern" / entry["output"]["path"]).resolve() == raw.resolve(), "Unexpected rendered generator")
    entry["name"] = settings["generator_image"]
    def no_publication(value):
        if isinstance(value, dict):
            require(not ({"github", "publish", "publishInfo", "publish-info", "publish-metadata"} & value.keys()),
                    "Download configuration contains a repository or publishing destination")
            for nested in value.values():
                no_publication(nested)
        elif isinstance(value, list):
            for nested in value:
                no_publication(nested)
    no_publication(document)
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


def launch(config, cli, version, token):
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
        log = (result.stdout or "") + "\n" + (result.stderr or "")
        jobs = set(re.findall(r"^DEBUG .* go-pipeline fernapi/fern-go-sdk Job ID: (" + UUID + r")\s*$", log, re.MULTILINE))
        require(len(jobs) == 1, "Fern did not return exactly one requested generation job")
        require(re.search(r"https://github\.com/[^/\s]+/[^/\s]+/pull/[1-9][0-9]*\b", log) is None,
                "Download generation unexpectedly reported a pull request")
        return jobs.pop()
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
    try:
        require(not any(os.environ.get(name) for name in ("GH_TOKEN", "GITHUB_TOKEN", "SSH_AUTH_SOCK")),
                "Hosted request received an unexpected credential")
        require(prepared.resolve() != output.resolve() and not output.exists(), "Hosted request needs a new output directory")
        plan = parse_json((prepared / "plan.json").read_bytes())
        settings = generate.settings()
        version = validate_plan(plan, settings, major)
        # Raw output and the original envelope stay disposable; only the filtered
        # SDK and the verifier's portable public receipt may leave this directory.
        with tempfile.TemporaryDirectory(prefix="sdk-fern-download-") as temporary:
            work = Path(temporary)
            public = work / "public.git"
            fetch_public_base(public, plan["sdk_base"])
            public_files = git_files(public, plan["sdk_base"])
            require(public_files["go.mod"][1].splitlines()[0] ==
                    f"module github.com/plaid/plaid-go/v{plan['current_major']}".encode(), "Plan differs from the public SDK base module")
            spec = (generate.ROOT / settings["spec_path"]).read_bytes()
            config = work / "config"
            raw = work / "raw"
            raw.mkdir()
            inputs = render_request(config, raw, spec, version, settings)
            cli = generate.install_cli(work, settings)
            job = launch(config, cli, version, fern_token)
            expected = {"job_id": job, "sdk_version": version, "cli_version": settings["cli_version"],
                        "generator": {"image": settings["generator_image"], "version": settings["generator_version"],
                                      "sha256": settings["generator_digest"].removeprefix("sha256:")}, "inputs": inputs}
            verified = fern_provenance.verify_download(raw, PUBLIC_KEY, expected)
            summary, receipt = verified["summary"], verified["receipt"]
            require(isinstance(receipt, bytes) and sha256(receipt) == summary["receipt_sha256"], "Portable Fern receipt differs from verified evidence")
            require(fern_token.encode() not in receipt, "Portable Fern receipt contains a credential")
            safe = work / "public-output"
            safe.mkdir()
            content_hash = export_verified_output(directory=raw, expected_tree=summary["git_tree"], public_files=public_files,
                version=version, settings=settings, output=safe, forbidden_values=(fern_token.encode(),))
            (safe / "fern-provenance.json").write_bytes(receipt)
            record = {"schema_version": 2, "sdk_version": version, "source": plan["source"], "config": plan["config"],
                      "sdk_base": plan["sdk_base"], "generator": expected["generator"],
                      "cli": {"version": settings["cli_version"], "sha256": settings["cli_sha256"]},
                      "evidence": {key: summary[key] for key in ("receipt_sha256", "key_sha256", "output_mode", "git_tree", "inputs_sha256", "job_id_sha256")},
                      "content_sha256": content_hash, "generation": plan["generation"]}
            save_json(safe / "fern-record.json", record)
            require(set(path.name for path in safe.iterdir()) == {"fern-output.tar.gz", "fern-content.json", "fern-record.json", "fern-provenance.json"},
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
