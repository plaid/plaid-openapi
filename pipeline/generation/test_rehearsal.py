"""The pre-merge rehearsal has no production identity or publishing permission."""

import copy
from contextlib import ExitStack
import json
import tarfile
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
import common
import test_pipeline
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

    def run_current_major_fixture(self, pending=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            upstream = root / 'upstream'
            test_pipeline.init(upstream)
            test_pipeline.write(upstream, 'go.mod', 'module github.com/plaid/plaid-go/v50\n')
            test_pipeline.write(upstream, common.MANIFEST, '{}')
            test_pipeline.write(upstream, common.BUNDLE, 'prior signature')
            base = test_pipeline.commit(upstream)
            common.git(upstream, '-c', 'tag.gpgsign=false', 'tag', 'v50.0.0')
            event = root / 'event.json'
            event.write_text('{}')
            output = root / 'output'
            def fetch(repository, branch, sdk):
                common.run(['git', 'clone', '--shared', str(upstream), str(sdk)])
                return base
            def candidate(sdk, old, data, tags, major, override, published, values, work, out):
                self.assertEqual(major, 50)
                self.assertEqual(tags, ['v50.0.0'])
                self.assertFalse((sdk / common.MANIFEST).exists())
                self.assertFalse((sdk / common.BUNDLE).exists())
                self.assertEqual(common.git(sdk, 'remote', 'get-url', '--push', 'origin'), '/dev/null')
                return '50.1.0', {}
            with ExitStack() as patches:
                patches.enter_context(patch.dict(os.environ, {'GITHUB_EVENT_PATH': str(event)}))
                patches.enter_context(patch('sys.argv', ['run.py', '--output', str(output)]))
                patches.enter_context(patch.object(rehearsal, 'check_context', return_value='a' * 40))
                patches.enter_context(patch.object(rehearsal, 'sample_memory'))
                patches.enter_context(patch.object(rehearsal, 'validate_overlay'))
                patches.enter_context(patch.object(rehearsal.generate, 'fetch_repository', side_effect=fetch))
                patches.enter_context(patch.object(rehearsal.generate, 'assert_sdk_bootstrap'))
                patches.enter_context(patch.object(rehearsal.generate, 'verified_spec', return_value=('a' * 40, b'spec')))
                patches.enter_context(patch.object(rehearsal.generate, 'pending_release', return_value=pending))
                patches.enter_context(patch.object(rehearsal.generate, 'published_baseline', return_value='v50.0.0'))
                generation = patches.enter_context(patch.object(rehearsal.generate, 'generate_versioned_candidate', side_effect=candidate))
                patches.enter_context(patch.object(rehearsal.generate, 'update_changelog'))
                patches.enter_context(patch.object(rehearsal.generate, 'sanitize_metadata'))
                if pending:
                    with self.assertRaisesRegex(PipelineError, 'unpublished candidate'):
                        rehearsal.main()
                    generation.assert_not_called()
                    self.assertFalse((output / 'unsigned-sdk.tar.gz').exists())
                else:
                    rehearsal.main()
                    report = json.loads((output / 'rehearsal.json').read_text())
                    self.assertEqual(report['sdk_base'], base)
                    self.assertEqual(report['candidate_version'], '50.1.0')
                    with tarfile.open(output / 'unsigned-sdk.tar.gz') as archive:
                        self.assertNotIn(common.MANIFEST, archive.getnames())
                        self.assertNotIn(common.BUNDLE, archive.getnames())

    def test_current_v50_master_rehearsal_excludes_prior_release_evidence(self):
        self.run_current_major_fixture()

    def test_pending_release_stops_rehearsal_before_generation(self):
        self.run_current_major_fixture(pending='50.0.0')

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
