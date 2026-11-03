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
                    propose_version, require, run, save_json, sha256)
from overlay_coverage import validate as validate_overlay


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
              "phases_seconds": {}, "cpu_count": os.cpu_count(),
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
            sdk, old = work / "sdk", work / "before"
            with phase("fetch-public-inputs"):
                base = generate.fetch_repository(values["sdk_repository"], values["sdk_branch"], sdk)
                report["sdk_base"] = base
                git(sdk, "checkout", "--detach", base)
                require(git(sdk, "rev-parse", "HEAD") == base, "SDK pin mismatch")
                # Defense in depth: even an accidental push has no configured destination.
                git(sdk, "remote", "set-url", "--push", "origin", "/dev/null")
                major = generate.current_major(sdk, values)
                module = "github.com/" + values["sdk_repository"] + "/v" + str(major)
                generate.assert_sdk_bootstrap(sdk, module)
                _, data = generate.verified_spec(generate.ROOT, commit, values, sdk)
                validate_overlay(data, (generate.ROOT / "fern/openapi-overlay.yml").read_bytes())
                tag_refs = git(sdk, "ls-remote", "--tags", "origin", "refs/tags/v*")
                require(generate.pending_release(sdk, tag_refs) is None,
                        "SDK master has an unpublished candidate; wait for its release before rehearsal")
                tags = [line.split("refs/tags/", 1)[1] for line in tag_refs.splitlines() if not line.endswith("^{}")]
                version = propose_version(tags, major)
                report.update(spec_sha256=sha256(data), candidate_version=version,
                              baseline_tag=generate.published_baseline(sdk, tags, major, old))
                require(report["baseline_tag"] is not None, "Rehearsal needs a published comparison baseline")
                # Preserve source ancestry validation above, but never repackage
                # an earlier production manifest or signature as rehearsal output.
                run(["git", "rm", "--ignore-unmatch", "--", MANIFEST, BUNDLE], sdk)
                if git(sdk, "diff", "--cached", "--name-only"):
                    git(sdk, "-c", "user.name=SDK rehearsal", "-c", "user.email=sdk-rehearsal@localhost",
                        "-c", "commit.gpgsign=false", "commit", "-m", "Remove prior release evidence from rehearsal")
            with phase("generation-and-validation"):
                version, report["legacy"] = generate.generate_versioned_candidate(
                    sdk, old, data, tags, major, "", True, values, work, output)
                module = "github.com/plaid/plaid-go/v" + str(generate.version_tuple(version)[0])
                report["candidate_version"] = version
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
