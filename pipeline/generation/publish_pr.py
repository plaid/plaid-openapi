#!/usr/bin/env python3
"""Verify generation evidence, then open a ready PR without executing SDK code."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlencode

from attestation import parse_json, validate_manifest, verified_attestation
from common import (BUNDLE, MANIFEST, PREDICATE, WORKFLOW, PipelineError, canonical,
                    check_sha, clean_env, content, entries, extract_sdk, git,
                    protected_state, public_get, require, run, save_json, sha256)
from generate import event_request, input_identity, settings


def validate_pr(value: dict, repository: str, branch: str, base: str, sdk_base: str, bot_id: int) -> str:
    require(isinstance(value, dict), "Unexpected pull-request response")
    require(value.get("state") == "open" and value.get("draft") is False,
            "Generated PR is closed or a draft; refusing to change its state automatically")
    author, head, target = value.get("user") or {}, value.get("head") or {}, value.get("base") or {}
    require(author.get("type") == "Bot" and type(author.get("id")) is int and author["id"] == bot_id,
            "Generated PR was not created by the configured publishing App bot")
    require((head.get("repo") or {}).get("full_name") == repository and head.get("ref") == branch,
            "Generated PR has an unexpected source repository or branch")
    require((target.get("repo") or {}).get("full_name") == repository and target.get("ref") == base and
            target.get("sha") == sdk_base, "Generated PR base changed; refusing automatic rebasing")
    head_sha = check_sha(head.get("sha", ""))
    require(isinstance(value.get("html_url"), str) and
            re.fullmatch(r"https://github\.com/" + re.escape(repository) + r"/pull/[1-9][0-9]*", value["html_url"]),
            "PR response has an unexpected URL")
    return head_sha


def open_pr(repository: str, branch: str, base: str, manifest: dict, token: str, *,
            sdk_base: str, head: str, bot_id: int) -> str:
    body = ("Regenerate both Go clients from the published OpenAPI revision so they use the same API contract.\n\n"
            "Source: https://github.com/plaid/plaid-openapi/commit/" + manifest["source"]["commit"])
    result = public_get(f"https://api.github.com/repos/{repository}/pulls", token=token, method="POST",
                        payload={"title": "Update Go SDK to v" + manifest["sdk"]["version"], "head": branch,
                                 "base": base, "body": body, "draft": False})
    require(validate_pr(result, repository, branch, base, sdk_base, bot_id) == head,
            "Created PR head changed; inspect the pushed branch before retrying")
    return result["html_url"]


def recover_pushed_branch(repository: str, branch: str, manifest: dict, plan: dict, work: Path,
                          expected_head: str) -> None:
    """Verify an existing generation branch; never modify its ref or PR."""
    previous = work / "previous-push"
    run(["git", "clone", "--filter=blob:none", "--single-branch", "--branch", branch,
         "https://github.com/" + repository + ".git", str(previous)])
    parents = git(previous, "rev-list", "--parents", "-n", "1", "HEAD").split()
    require(len(parents) == 2 and parents[0] == check_sha(expected_head) and parents[1] == plan["sdk_base"],
            "Existing branch changed or has additional commits; refusing automatic changes")
    old = validate_manifest(parse_json((previous / MANIFEST).read_bytes()))
    require(input_identity(old["sdk"]["version"], old["source"]["sha256"], old["config"]["sha256"]) == plan["identity"],
            "Existing branch was generated from different inputs")
    data, digest = content(previous)
    require(digest == old["content_sha256"] == manifest["content_sha256"], "Existing branch was edited; refusing automatic changes")
    index = work / "previous-content.json"
    index.write_bytes(data)
    verified_attestation(index, previous / BUNDLE, repository=old["config"]["repository"], workflow=WORKFLOW,
                         ref="refs/heads/master", commit=old["config"]["commit"], predicate_type=PREDICATE,
                         predicate=old, subjects=[{"name": "plaid-go-v" + old["sdk"]["version"] + "-source",
                                                  "digest": {"sha256": digest}}],
                         run_id=old["generation"]["run_id"])


def verify_artifact(directory: Path, sdk: Path, *, signed: bool = True) -> tuple[dict, dict]:
    manifest = validate_manifest(parse_json((directory / "manifest.json").read_bytes()))
    extract_sdk(directory / "sdk.tar.gz", sdk)
    require(parse_json((sdk / MANIFEST).read_bytes()) == manifest, "Archive and standalone manifests differ")
    git(sdk, "init", "-q")
    git(sdk, "add", "-A")
    index, digest = content(sdk)
    require(digest == manifest["content_sha256"], "SDK content differs from signed manifest")
    require(index == (directory / "content.json").read_bytes(), "Canonical content index differs from SDK tree")
    legacy = [entry for entry in entries(sdk) if entry[0].startswith("legacy/")]
    require(legacy and sha256(canonical(legacy)) == manifest["legacy"]["tree_sha256"], "Legacy content digest mismatch")
    module_lines = re.findall(r"^module\s+(\S+)\s*$", (sdk / "go.mod").read_text(), re.MULTILINE)
    require(module_lines == [manifest["sdk"]["module"]], "Manifest module mismatch")
    require(not list((sdk / "legacy").rglob("go.mod")), "Legacy cannot create a nested module")
    metadata = parse_json((sdk / ".fern/metadata.json").read_bytes())
    require(set(metadata) == {"cliVersion", "generatorName", "generatorVersion", "sdkVersion"},
            "SDK metadata must contain only version identity")
    require(metadata.get("sdkVersion") == "v" + manifest["sdk"]["version"], "Generated SDK version mismatch")
    require(metadata.get("cliVersion") == manifest["generator"]["cli_version"], "Generated CLI version mismatch")
    plan = parse_json((directory / "plan.json").read_bytes())
    require(set(plan) == {"sdk_base", "branch", "identity", "rehearsal"}, "Unexpected PR plan fields")
    check_sha(plan["sdk_base"])
    require(type(plan["rehearsal"]) is bool, "Invalid rehearsal flag")
    identity = input_identity(manifest["sdk"]["version"], manifest["source"]["sha256"], manifest["config"]["sha256"])
    branch = "sdk-generation/go-v" + manifest["sdk"]["version"].split(".")[0] + "-" + identity
    require(plan["identity"] == identity and plan["branch"] == branch, "PR branch/input identity mismatch")
    if signed:
        require(not plan["rehearsal"], "Unsigned rehearsal artifacts cannot enter the publishing path")
        bundle = directory / "generation.bundle.json"
        require(bundle.is_file(), "Signed generation bundle is missing")
        verified_attestation(directory / "content.json", bundle,
                             repository=manifest["config"]["repository"], workflow=WORKFLOW,
                             ref="refs/heads/master", commit=manifest["config"]["commit"],
                             predicate_type=PREDICATE, predicate=manifest,
                             subjects=[{"name": "plaid-go-v" + manifest["sdk"]["version"] + "-source",
                                        "digest": {"sha256": digest}}],
                             run_id=manifest["generation"]["run_id"])
        (sdk / BUNDLE).write_bytes(bundle.read_bytes())
    return manifest, plan


def pending_pr(repository: str, branch: str, *, token: str) -> dict | None:
    pending = []
    for page in range(1, 101):
        results = public_get(f"https://api.github.com/repos/{repository}/pulls?state=open&per_page=100&page={page}", token=token)
        require(isinstance(results, list), "Unexpected pull-request response")
        for result in results:
            head = result.get("head", {})
            if head.get("repo", {}).get("full_name") == repository and head.get("ref", "").startswith("sdk-generation/go-v"):
                pending.append(result)
        if len(results) < 100:
            break
    else:
        raise PipelineError("Too many open PRs to safely establish generation idempotency")
    if pending:
        require(len(pending) == 1 and pending[0]["head"]["ref"] == branch,
                "Another generated SDK PR is pending; wait for automatic integration or investigate its failed checks")
        return pending[0]
    return None


def require_current_base(repository: str, branch: str, expected: str, token: str) -> None:
    ref = public_get(f"https://api.github.com/repos/{repository}/git/ref/heads/{branch}", token=token)
    require(isinstance(ref, dict) and ref.get("ref") == "refs/heads/" + branch and
            ref.get("object", {}).get("type") == "commit" and ref["object"].get("sha") == expected,
            "SDK master changed during generation; refusing automatic rebasing")


def require_no_closed_pr(repository: str, branch: str, base: str, token: str) -> None:
    query = urlencode({"state": "closed", "head": repository.split("/", 1)[0] + ":" + branch,
                       "base": base, "per_page": 100})
    previous = public_get(f"https://api.github.com/repos/{repository}/pulls?{query}", token=token)
    require(isinstance(previous, list), "Unexpected closed pull-request response")
    require(not previous, "This generation branch already had a closed or merged PR; refusing to recreate it automatically")


def publish(directory: Path, artifact: Path, manifest: dict, plan: dict, work: Path) -> str:
    values = settings()
    require(os.environ.get("GITHUB_REPOSITORY") == values["config_repository"] and
            os.environ.get("GITHUB_REF") == "refs/heads/master" and
            os.environ.get("SDK_PIPELINE_ENABLED") == "true", "Production PR publishing is disabled outside trusted public master")
    require(os.environ.get("GITHUB_SHA") == manifest["config"]["commit"] and
            os.environ.get("GITHUB_RUN_ID") == manifest["generation"]["run_id"], "Artifact is not from this workflow run")
    event = parse_json(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
    metadata = event.get("repository") or {}
    require(metadata.get("full_name") == values["config_repository"] and metadata.get("private") is False and metadata.get("fork") is False,
            "Publishing requires the original public OpenAPI repository")
    require(os.environ.get("GITHUB_EVENT_NAME") in {"push", "schedule", "workflow_dispatch"}, "Unsupported publishing context")
    _, rehearsal = event_request(os.environ["GITHUB_EVENT_NAME"], event, values)
    require(not rehearsal, "Manual rehearsal cannot publish even if artifact outputs are changed")
    require(not plan["rehearsal"], "Rehearsal cannot publish a PR")
    token = os.environ.get("SDK_PR_TOKEN", "")
    require(bool(token), "Repo-scoped PR App token is missing")
    bot = os.environ.get("SDK_PR_APP_BOT_ID", "")
    require(re.fullmatch(r"[1-9][0-9]*", bot) is not None, "Publishing App bot ID is missing or invalid")
    bot_id = int(bot)
    repository, branch = values["sdk_repository"], plan["branch"]
    existing = pending_pr(repository, branch, token=token)
    require_current_base(repository, values["sdk_branch"], plan["sdk_base"], token)
    if existing:
        head = validate_pr(existing, repository, branch, values["sdk_branch"], plan["sdk_base"], bot_id)
        recover_pushed_branch(repository, branch, manifest, plan, work, head)
        # Returning success means this ready PR still carries the exact signed content.
        # Never amend, rebase, reset, mark ready, or otherwise change an existing PR.
        return existing["html_url"]
    require_no_closed_pr(repository, branch, values["sdk_branch"], token)
    references = public_get(f"https://api.github.com/repos/{repository}/git/matching-refs/heads/{branch}", token=token)
    require(isinstance(references, list), "Unexpected branch lookup response")
    if references:
        require(len(references) == 1 and references[0]["ref"] == "refs/heads/" + branch,
                "Conflicting generation branch names")
        head = check_sha(references[0].get("object", {}).get("sha", ""))
        recover_pushed_branch(repository, branch, manifest, plan, work, head)
        require_current_base(repository, values["sdk_branch"], plan["sdk_base"], token)
        return open_pr(repository, branch, values["sdk_branch"], manifest, token,
                       sdk_base=plan["sdk_base"], head=head, bot_id=bot_id)
    sdk = work / "publish-sdk"
    run(["git", "clone", "--filter=blob:none", "--single-branch", "--branch", values["sdk_branch"],
         "https://github.com/" + repository + ".git", str(sdk)])
    require(git(sdk, "rev-parse", "HEAD") == plan["sdk_base"], "SDK master changed during generation; regenerate from the new reviewed base")
    before = protected_state(sdk)
    # README/release-history edits are producer-owned, visible SDK PR content. Workflows,
    # scripts and custom security files remain exactly the reviewed base versions.
    excluded = {"CHANGELOG.md", ".fernignore"}
    old = {path: value for path, value in before.items() if path not in excluded}
    proposed = {path: value for path, value in protected_state(artifact).items() if path not in excluded}
    require(old == proposed, "Artifact modifies trusted release automation or maintained customizations")
    run(["git", "rm", "-r", "--quiet", "--", "."], sdk)
    for record in run(["git", "ls-files", "-z"], artifact).split(b"\0"):
        if record:
            name = record.decode()
            destination = sdk / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(artifact / name, destination)
    # Bundle was added after the unsigned generation index was verified.
    shutil.copy2(artifact / BUNDLE, sdk / BUNDLE)
    git(sdk, "checkout", "-b", branch)
    git(sdk, "add", "-A")
    require(content(sdk)[1] == manifest["content_sha256"], "Publishing checkout differs from attested content")
    git(sdk, "-c", "user.name=Plaid SDK automation", "-c", "user.email=sdk-automation@users.noreply.github.com",
        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-m", "Update Go SDK to v" + manifest["sdk"]["version"])
    # Plain fast-forward-only push: no force, no tag, no retry that overwrites a ref.
    authentication = base64.b64encode(("x-access-token:" + token).encode()).decode()
    env = clean_env(GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                    GIT_CONFIG_VALUE_0="AUTHORIZATION: basic " + authentication,
                    GIT_CONFIG_KEY_1="core.hooksPath", GIT_CONFIG_VALUE_1="/dev/null")
    run(["git", "push", "https://github.com/" + repository + ".git", "HEAD:refs/heads/" + branch], sdk, env=env)
    require_current_base(repository, values["sdk_branch"], plan["sdk_base"], token)
    return open_pr(repository, branch, values["sdk_branch"], manifest, token,
                   sdk_base=plan["sdk_base"], head=git(sdk, "rev-parse", "HEAD"), bot_id=bot_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--unsigned", action="store_true", help="Validate pre-attestation output; never permits publishing")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    require(not (args.unsigned and args.publish), "Unsigned validation cannot publish")
    with tempfile.TemporaryDirectory(prefix="sdk-publish-verification-") as temporary:
        work = Path(temporary)
        sdk = work / "verified-sdk"
        manifest, plan = verify_artifact(args.artifact, sdk, signed=not args.unsigned)
        if args.publish:
            url = publish(args.artifact, sdk, manifest, plan, work)
            print(url)
        else:
            print("Generation artifact verified" if not args.unsigned else "Unsigned generation content verified; attestation still required")


if __name__ == "__main__":
    try:
        main()
    except (PipelineError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
