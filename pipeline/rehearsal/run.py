#!/usr/bin/env python3
"""Exercise real generation on a PR runner, without release records or credentials."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generation"))
import generate
from common import (BUNDLE, MANIFEST, archive_sdk, check_sha, content, git,
                    protected_state, propose_version, require, save_json, sha256)
from overlay_coverage import validate as validate_overlay

# Reviewed release controls from plaid/plaid-go#359, not a moving PR branch.
SDK_COMMIT = "257aa2c6382f737407986369cce22c87307ef2de"


def check_context(event: dict) -> str:
    repository = "plaid/plaid-openapi"
    require(os.environ.get("GITHUB_EVENT_NAME") == "pull_request", "Rehearsal requires a PR event")
    require(os.environ.get("GITHUB_REPOSITORY") == repository, "Unexpected rehearsal repository")
    metadata = event.get("repository") or {}
    require(metadata.get("full_name") == repository and metadata.get("private") is False
            and metadata.get("fork") is False, "Rehearsal requires the original public repository")
    head = (event.get("pull_request") or {}).get("head") or {}
    require((head.get("repo") or {}).get("full_name") == repository, "Fork rehearsals are not allowed")
    commit = check_sha(head.get("sha", ""))
    require(git(generate.ROOT, "rev-parse", "HEAD") == commit, "Checkout differs from PR head")
    require(not git(generate.ROOT, "status", "--porcelain"), "Rehearsal checkout must be clean")
    return commit


def sample_memory(report: dict, stop: threading.Event) -> None:
    """Whole-runner available memory includes Docker usage; samples may miss peaks."""
    while not stop.is_set():
        memory = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        available = int(memory["MemAvailable"].split()[0])
        report["memory_total_kib"] = int(memory["MemTotal"].split()[0])
        report["minimum_sampled_available_memory_kib"] = min(
            report.get("minimum_sampled_available_memory_kib", available), available)
        stop.wait(2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output.resolve()
    commit = check_context(json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()))
    require(not output.exists(), "Do not overwrite rehearsal evidence")
    output.mkdir(parents=True)
    values = generate.settings()
    report = {"rehearsal": True, "status": "running", "source_commit": commit,
              "sdk_base": SDK_COMMIT, "phases_seconds": {}, "cpu_count": os.cpu_count(),
              "disk_free_start_bytes": shutil.disk_usage(output).free}
    stop = threading.Event()
    sampler = threading.Thread(target=sample_memory, args=(report, stop), daemon=True)
    sampler.start()

    @contextmanager
    def phase(name):
        report["phase"] = name
        print(name, flush=True)
        start = time.monotonic()
        try:
            yield
        finally:
            report["phases_seconds"][name] = round(time.monotonic() - start, 2)
            save_json(output / "rehearsal.json", report)

    try:
        with tempfile.TemporaryDirectory(prefix="sdk-rehearsal-") as temporary:
            work = Path(temporary).resolve()
            sdk, old, config = work / "sdk", work / "before", work / "config"
            with phase("fetch-public-inputs"):
                generate.fetch_repository(values["sdk_repository"], values["sdk_branch"], sdk)
                git(sdk, "fetch", "origin", SDK_COMMIT)
                git(sdk, "checkout", "--detach", SDK_COMMIT)
                require(git(sdk, "rev-parse", "HEAD") == SDK_COMMIT, "SDK pin mismatch")
                # Defense in depth: even an accidental push has no configured destination.
                git(sdk, "remote", "set-url", "--push", "origin", "/dev/null")
                module = "github.com/" + values["sdk_repository"] + "/v" + str(values["major"])
                generate.assert_sdk_bootstrap(sdk, module)
                _, data = generate.verified_spec(generate.ROOT, commit, values, sdk)
                validate_overlay(data, (generate.ROOT / "fern/openapi-overlay.yml").read_bytes())
                tags = [line.split("refs/tags/", 1)[1] for line in
                        git(sdk, "ls-remote", "--tags", "--refs", "origin", "refs/tags/v*").splitlines()]
                version = propose_version(tags, values["major"])
                report.update(spec_sha256=sha256(data), candidate_version=version,
                              baseline_tag=generate.published_baseline(sdk, tags, values["major"], old))
                require(report["baseline_tag"] is not None, "Rehearsal needs a published comparison baseline")
                require(not (sdk / MANIFEST).exists() and not (sdk / BUNDLE).exists(),
                        "Rehearsal pin must not carry release evidence")
                generate.render_config(config, sdk, data, version, values)
            with phase("fern-generation"):
                generate.generate_new_client(sdk, config, version, values, work)
            with phase("legacy-generation"):
                before = protected_state(sdk)
                report["legacy"] = generate.run_legacy(sdk, config / "2020-09-14.yml", module, values, work)
                require(protected_state(sdk) == before, "Legacy changed protected SDK files")
            with phase("build-and-wire-tests"):
                generate.verify_sdk(sdk, values, work)
            with phase("compatibility"):
                generate.compatibility_gate(old, sdk, module, True, values, work, output=output)
                shutil.copyfile(work / "api-diff.txt", output / "api-diff.txt")
            with phase("unsigned-artifact"):
                generate.update_changelog(sdk, version, data, values)
                generate.sanitize_metadata(sdk, version, module, values)
                git(sdk, "add", "-A")
                require(not (sdk / MANIFEST).exists() and not (sdk / BUNDLE).exists(),
                        "Rehearsal must not emit production release evidence")
                _, report["content_sha256"] = content(sdk)
                archive_sdk(sdk, output / "unsigned-sdk.tar.gz")
                report["archive_sha256"] = sha256((output / "unsigned-sdk.tar.gz").read_bytes())
            report["status"] = "passed"
    finally:
        stop.set()
        sampler.join()
        if report["status"] != "passed":
            report["status"] = "failed"
        report["disk_free_end_bytes"] = shutil.disk_usage(output).free
        save_json(output / "rehearsal.json", report)


if __name__ == "__main__":
    main()
