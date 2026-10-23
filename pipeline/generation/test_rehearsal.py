"""The pre-merge rehearsal has no production identity or publishing permission."""

import copy
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from common import PipelineError
from publish_pr import verify_artifact

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("rehearsal", ROOT / "pipeline/rehearsal/run.py")
rehearsal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rehearsal)


class RehearsalTests(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 40
        self.event = {"repository": {"full_name": "plaid/plaid-openapi", "private": False, "fork": False},
                      "pull_request": {"head": {"sha": self.sha, "repo": {"full_name": "plaid/plaid-openapi"}}}}
        self.env = {"GITHUB_EVENT_NAME": "pull_request", "GITHUB_REPOSITORY": "plaid/plaid-openapi"}

    def check(self, event=None, head=None):
        with patch.dict(os.environ, self.env, clear=True), patch.object(rehearsal, "git", side_effect=[head or self.sha, ""]):
            return rehearsal.check_context(event or self.event)

    def test_exact_same_repository_pr_allowed(self):
        self.assertEqual(self.check(), self.sha)

    def test_fork_or_private_repository_rejected(self):
        for key in ("fork", "private"):
            event = copy.deepcopy(self.event)
            event["repository"][key] = True
            with self.subTest(key=key), self.assertRaises(PipelineError):
                self.check(event)
        event = copy.deepcopy(self.event)
        event["pull_request"]["head"]["repo"]["full_name"] = "someone/plaid-openapi"
        with self.assertRaises(PipelineError):
            self.check(event)

    def test_wrong_context_or_checkout_rejected(self):
        with self.assertRaises(PipelineError):
            self.check(head="b" * 40)
        for name in ("push", "pull_request_target", "workflow_dispatch"):
            self.env["GITHUB_EVENT_NAME"] = name
            with self.subTest(event=name), self.assertRaises(PipelineError):
                self.check()

    def test_unsigned_rehearsal_cannot_be_consumed_by_publisher(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / "rehearsal.json").write_text('{"rehearsal": true}')
            with self.assertRaises(FileNotFoundError):
                verify_artifact(path, path)

    def test_workflow_cannot_sign_or_publish(self):
        text = (ROOT / ".github/workflows/sdk-rehearsal.yml").read_text()
        workflow = yaml.safe_load(text)
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        # PyYAML's YAML 1.1 parser represents the key "on" as True.
        self.assertEqual(set(workflow[True]), {"pull_request"})
        self.assertEqual(set(workflow["jobs"]), {"rehearse"})
        job = workflow["jobs"]["rehearse"]
        self.assertNotIn("permissions", job)
        self.assertNotIn("environment", job)
        self.assertNotIn("secrets.", text)
        self.assertNotIn("github.token", text)
        allowed = {"actions/checkout", "actions/setup-go", "actions/upload-artifact"}
        for step in job["steps"]:
            if "uses" in step:
                self.assertIn(step["uses"].split("@")[0], allowed)
            if step.get("uses", "").startswith("actions/checkout@"):
                self.assertIs(step["with"]["persist-credentials"], False)
                self.assertEqual(step["with"]["ref"], "${{ github.event.pull_request.head.sha }}")


if __name__ == "__main__":
    unittest.main()
