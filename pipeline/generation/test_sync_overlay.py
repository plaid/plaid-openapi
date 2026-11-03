"""Overlay sync PR policy against a local repository and a fake GitHub API."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common import PipelineError, git
import sync_overlay
from test_overlay_coverage import fixture, yaml_text
from test_pipeline import commit, init, write

BOT = 12345
URL = "https://github.com/plaid/plaid-openapi/pull/9"


class FakeGitHub:
    def __init__(self, prs=(), commits=()):
        self.prs, self.commits, self.calls = list(prs), list(commits), []

    def __call__(self, url, *, token=None, payload=None, method=None):
        self.calls.append((method or "GET", url, payload))
        if method == "POST":
            return {"html_url": URL, "user": {"id": BOT}}
        if method == "PATCH":
            return {}
        return self.commits if url.endswith("/commits") else self.prs


class SyncOverlayTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "openapi"
        init(self.repo)
        self.spec, overlay = fixture()
        write(self.repo, "2020-09-14.yml", json.dumps(self.spec))
        write(self.repo, sync_overlay.OVERLAY, yaml_text(overlay))
        self.head = commit(self.repo)
        event = self.root / "event.json"
        event.write_text('{"repository":{"full_name":"plaid/plaid-openapi","private":false,"fork":false}}')
        self.env = {"GITHUB_REPOSITORY": "plaid/plaid-openapi", "GITHUB_REF": "refs/heads/master",
                    "GITHUB_EVENT_NAME": "push", "GITHUB_EVENT_PATH": str(event), "GITHUB_SHA": self.head,
                    "OVERLAY_SYNC_TOKEN": "fixture-token", "OVERLAY_SYNC_APP_BOT_ID": str(BOT)}
        self.pushes = []

    def add_endpoint(self):
        self.spec["paths"]["/accounts/balance/get"] = {"post": {"requestBody": {"content": {"application/json": {
            "schema": {"$ref": "#/components/schemas/Input"}}}}}}
        write(self.repo, "2020-09-14.yml", json.dumps(self.spec))
        self.head = self.env["GITHUB_SHA"] = commit(self.repo)

    def sync(self, github):
        with patch.object(sync_overlay, "ROOT", self.repo), patch.object(sync_overlay, "public_get", github), \
                patch.object(sync_overlay, "run", lambda argv, cwd, env: self.pushes.append((argv, env))):
            return sync_overlay.sync(self.env)

    def automation_pr(self, tree, email=sync_overlay.AUTHOR_EMAIL, author=BOT):
        pr = {"number": 9, "html_url": URL, "user": {"id": author}}
        return FakeGitHub([pr], [{"commit": {"author": {"email": email}, "tree": {"sha": tree}}}])

    def test_covered_spec_makes_no_changes(self):
        github = FakeGitHub()
        self.assertEqual(self.sync(github), "Overlay already covers the spec")
        self.assertEqual([call[0] for call in github.calls], ["GET"])
        self.assertEqual(self.pushes, [])

    def test_new_endpoint_opens_one_ready_pr_with_names_to_review(self):
        self.add_endpoint()
        github = FakeGitHub()
        self.assertEqual(self.sync(github), "Opened " + URL)
        (argv, env), = self.pushes
        self.assertEqual(argv[:3], ["git", "push", "--force"])
        self.assertEqual(argv[-1], "HEAD:refs/heads/fern-overlay-sync")
        self.assertNotIn("fixture-token", " ".join(argv))
        method, url, payload = github.calls[-1]
        self.assertEqual((method, payload["head"], payload["base"], payload["draft"]),
                         ("POST", "fern-overlay-sync", "master", False))
        self.assertIn("`POST /accounts/balance/get: accounts.getBalance`", payload["body"])
        self.assertIn(self.head, payload["body"])
        self.assertEqual(git(self.repo, "rev-parse", "HEAD~1"), self.head)
        self.assertEqual(git(self.repo, "log", "-1", "--format=%ae"), sync_overlay.AUTHOR_EMAIL)
        self.assertEqual(git(self.repo, "diff", "--name-only", "HEAD~1"), sync_overlay.OVERLAY)

    def test_unchanged_automation_pr_is_not_pushed_again(self):
        self.add_endpoint()
        self.sync(FakeGitHub())
        tree = git(self.repo, "rev-parse", "HEAD^{tree}")
        git(self.repo, "checkout", "-q", "master")
        github = self.automation_pr(tree)
        self.assertEqual(self.sync(github), URL + " already has these entries")
        self.assertEqual(len(self.pushes), 1)
        self.assertNotIn("PATCH", [call[0] for call in github.calls])

    def test_stale_automation_pr_is_refreshed(self):
        self.add_endpoint()
        github = self.automation_pr("0" * 40)
        self.assertEqual(self.sync(github), "Updated " + URL)
        self.assertEqual(len(self.pushes), 1)
        self.assertEqual(github.calls[-1][0], "PATCH")

    def test_pr_with_someone_elses_commit_is_left_alone(self):
        self.add_endpoint()
        github = self.automation_pr("0" * 40, email="reviewer@example.invalid")
        self.assertIn("has commits from someone else", self.sync(github))
        self.assertEqual(self.pushes, [])
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_branch_pr_from_another_author_is_rejected(self):
        self.add_endpoint()
        with self.assertRaisesRegex(PipelineError, "not opened by the overlay sync App"):
            self.sync(self.automation_pr("0" * 40, author=999))
        self.assertEqual(self.pushes, [])

    def test_untrusted_context_fails_before_github_calls(self):
        for change in ({"GITHUB_EVENT_NAME": "pull_request"}, {"GITHUB_EVENT_NAME": "pull_request_target"},
                       {"GITHUB_REF": "refs/heads/feature"}, {"GITHUB_REPOSITORY": "fork/plaid-openapi"},
                       {"OVERLAY_SYNC_TOKEN": ""}, {"OVERLAY_SYNC_APP_BOT_ID": "bot"}, {"GITHUB_SHA": "0" * 40}):
            with self.subTest(change=change):
                github = FakeGitHub()
                original = dict(self.env)
                self.env.update(change)
                with self.assertRaises(PipelineError):
                    self.sync(github)
                self.env = original
                self.assertEqual(github.calls, [])

    def test_workflow_scopes_the_credential_to_this_repository(self):
        workflow = (Path(__file__).resolve().parents[2] / ".github/workflows/sync-fern-overlay.yml").read_text()
        self.assertIn("permissions:\n  contents: read\n", workflow)
        self.assertIn("repositories: plaid-openapi\n", workflow)
        self.assertNotIn("pull_request", workflow.split("permissions:", 1)[0])
        self.assertNotIn("SDK_PR_APP", workflow)
        self.assertIn("environment: overlay-sync-publishing\n", workflow)


if __name__ == "__main__":
    unittest.main()
