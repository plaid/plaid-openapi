#!/usr/bin/env python3
"""Open or refresh one PR that adds the Fern overlay entries a spec change needs."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

from common import PipelineError, clean_env, git, public_get, require, run
from generate import ROOT, settings
import overlay_coverage

BRANCH = "fern-overlay-sync"
OVERLAY = "fern/openapi-overlay.yml"
AUTHOR_NAME, AUTHOR_EMAIL = "Plaid SDK automation", "sdk-automation@users.noreply.github.com"
TITLE = "Add Fern overlay entries for new endpoints"


def body(commit: str, suggested: list[str]) -> str:
    source = f"https://github.com/plaid/plaid-openapi/commit/{commit}"
    if not suggested:
        return f"The [spec change]({source}) needs Go SDK credential removals only; no new SDK names.\n"
    names = "\n".join(f"- `{name}`" for name in suggested)
    return (f"The [spec change]({source}) added endpoints the Go SDK overlay doesn't name yet. "
            "These names become public Go SDK methods, so check each one before merging:\n\n"
            f"{names}\n\nTo change a name, push a commit to this branch. Automation stops updating "
            "this PR once anyone else has committed to it.\n")


def open_sync_pr(repository: str, token: str) -> dict | None:
    query = urlencode({"state": "open", "head": repository.split("/")[0] + ":" + BRANCH, "base": "master"})
    results = public_get(f"https://api.github.com/repos/{repository}/pulls?{query}", token=token)
    require(isinstance(results, list) and len(results) <= 1, "Unexpected overlay sync PR lookup response")
    return results[0] if results else None


def automation_only(repository: str, pr: dict, token: str, bot_id: int) -> dict | None:
    """Return the PR's single automation commit, or None when someone else has committed to it."""
    require((pr.get("user") or {}).get("id") == bot_id, "Overlay sync PR was not opened by the publishing App")
    commits = public_get(f"https://api.github.com/repos/{repository}/pulls/{pr['number']}/commits", token=token)
    require(isinstance(commits, list), "Unexpected overlay sync PR commits response")
    if len(commits) == 1 and commits[0]["commit"]["author"]["email"] == AUTHOR_EMAIL:
        return commits[0]
    return None


def push(repository: str, token: str, commit: str, suggested: list[str]) -> None:
    git(ROOT, "checkout", "-q", "-B", BRANCH)
    git(ROOT, "-c", f"user.name={AUTHOR_NAME}", "-c", f"user.email={AUTHOR_EMAIL}", "-c", "commit.gpgsign=false",
        "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", TITLE, "-m", body(commit, suggested))
    authentication = base64.b64encode(("x-access-token:" + token).encode()).decode()
    env = clean_env(GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                    GIT_CONFIG_VALUE_0="AUTHORIZATION: basic " + authentication,
                    GIT_CONFIG_KEY_1="core.hooksPath", GIT_CONFIG_VALUE_1="/dev/null")
    # The branch only ever holds one automation commit on master; a PR with other commits is never reached here.
    run(["git", "push", "--force", "https://github.com/" + repository + ".git", "HEAD:refs/heads/" + BRANCH],
        ROOT, env=env)


def sync(env: dict[str, str]) -> str:
    repository = settings()["config_repository"]
    require(env.get("GITHUB_REPOSITORY") == repository and env.get("GITHUB_REF") == "refs/heads/master" and
            env.get("GITHUB_EVENT_NAME") in {"push", "workflow_dispatch"},
            "Overlay sync runs only from the public OpenAPI repository's master branch")
    metadata = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text()).get("repository") or {}
    require(metadata.get("full_name") == repository and metadata.get("private") is False and
            metadata.get("fork") is False, "Overlay sync requires the original public OpenAPI repository")
    token = env.get("OVERLAY_SYNC_TOKEN", "")
    require(bool(token), "Repo-scoped PR App token is missing")
    bot = env.get("SDK_PR_APP_BOT_ID", "")
    require(re.fullmatch(r"[1-9][0-9]*", bot) is not None, "Publishing App bot ID is missing or invalid")
    commit = env.get("GITHUB_SHA", "")
    require(git(ROOT, "rev-parse", "HEAD") == commit, "Checkout is not the commit that triggered this run")
    require(not git(ROOT, "status", "--porcelain"), "Overlay sync checkout must be clean")

    overlay = ROOT / OVERLAY
    original = overlay.read_text()
    text, suggested = overlay_coverage.fix((ROOT / "2020-09-14.yml").read_bytes(), original)
    existing = open_sync_pr(repository, token)
    if text == original:
        return "Overlay already covers the spec" + (f"; {existing['html_url']} can be closed" if existing else "")
    previous = automation_only(repository, existing, token, int(bot)) if existing else None
    if existing and not previous:
        return f"{existing['html_url']} has commits from someone else; leaving it for review"

    overlay.write_text(text)
    git(ROOT, "add", OVERLAY)
    if previous and previous["commit"]["tree"]["sha"] == git(ROOT, "write-tree"):
        return f"{existing['html_url']} already has these entries"
    push(repository, token, commit, suggested)
    if existing:
        public_get(f"https://api.github.com/repos/{repository}/pulls/{existing['number']}", token=token,
                   method="PATCH", payload={"body": body(commit, suggested)})
        return f"Updated {existing['html_url']}"
    created = public_get(f"https://api.github.com/repos/{repository}/pulls", token=token, method="POST",
                         payload={"title": TITLE, "head": BRANCH, "base": "master",
                                  "body": body(commit, suggested), "draft": False})
    require(isinstance(created, dict) and (created.get("user") or {}).get("id") == int(bot),
            "Created PR was not opened by the publishing App")
    return f"Opened {created['html_url']}"


if __name__ == "__main__":
    try:
        print(sync(dict(os.environ)))
    except (PipelineError, OSError) as exc:
        sys.exit(str(exc))
