"""Ready PR and retry policy; no network writes or generated-code execution."""

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import common
import generate
import publish_pr
import test_pipeline


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.values = generate.settings()
        self.repo, self.artifact, self.manifest, self.plan = test_pipeline.PipelineTests.fixture(self)
        event = self.root / "event.json"
        event.write_text('{"repository":{"full_name":"plaid/plaid-openapi","private":false,"fork":false}}')
        self.env = {"GITHUB_REPOSITORY": "plaid/plaid-openapi", "GITHUB_REF": "refs/heads/master",
                    "SDK_PIPELINE_ENABLED": "true", "GITHUB_SHA": self.manifest["config"]["commit"],
                    "GITHUB_RUN_ID": "123", "GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": "workflow_dispatch",
                    "SDK_PR_TOKEN": "fixture-token", "SDK_PR_APP_BOT_ID": "12345"}
        self.head = "f" * 40
        self.ready = {"html_url": "https://github.com/plaid/plaid-go/pull/1", "state": "open", "draft": False,
                      "user": {"type": "Bot", "id": 12345},
                      "head": {"repo": {"full_name": "plaid/plaid-go"}, "ref": self.plan["branch"], "sha": self.head},
                      "base": {"repo": {"full_name": "plaid/plaid-go"}, "ref": "master", "sha": self.plan["sdk_base"]}}
        self.ref = {"ref": "refs/heads/master", "object": {"type": "commit", "sha": self.plan["sdk_base"]}}

    def publish(self):
        return publish_pr.publish(self.artifact, self.repo, self.manifest, self.plan, self.root)

    def test_new_pr_is_ready_for_the_pinned_bot_and_exact_head(self):
        with patch.object(publish_pr, "public_get", return_value=self.ready) as api:
            url = publish_pr.open_pr("plaid/plaid-go", self.plan["branch"], "master", self.manifest, "fixture",
                                     sdk_base=self.plan["sdk_base"], head=self.head, bot_id=12345)
        self.assertEqual(url, self.ready["html_url"])
        self.assertEqual(api.call_args.kwargs["method"], "POST")
        self.assertIs(api.call_args.kwargs["payload"]["draft"], False)
        self.assertEqual(api.call_args.kwargs["payload"]["head"], self.plan["branch"])

    def test_existing_draft_wrong_author_target_or_head_is_not_reported_ready(self):
        changes = [lambda p: p.update(draft=True), lambda p: p.update(state="closed"),
                   lambda p: p["user"].update(id=999), lambda p: p["user"].update(type="User"),
                   lambda p: p["user"].update(id=True), lambda p: p["base"].update(ref="different"),
                   lambda p: p["base"].update(sha="a" * 40),
                   lambda p: p["head"]["repo"].update(full_name="other/plaid-go"),
                   lambda p: p["head"].update(sha="main")]
        for change in changes:
            existing = copy.deepcopy(self.ready)
            change(existing)
            with self.subTest(existing=existing), patch.dict(os.environ, self.env), \
                 patch.object(publish_pr, "pending_pr", return_value=existing), \
                 patch.object(publish_pr, "public_get", return_value=self.ref) as api, \
                 patch.object(publish_pr, "recover_pushed_branch") as recover, self.assertRaises(common.PipelineError):
                self.publish()
            recover.assert_not_called()
            self.assertTrue(all(call.kwargs.get("method", "GET") == "GET" for call in api.call_args_list))

    def test_base_advance_stops_pending_pr_without_rebasing_or_writes(self):
        moved = copy.deepcopy(self.ref)
        moved["object"]["sha"] = "a" * 40
        with patch.dict(os.environ, self.env), patch.object(publish_pr, "pending_pr", return_value=self.ready), \
             patch.object(publish_pr, "public_get", return_value=moved) as api, \
             patch.object(publish_pr, "recover_pushed_branch") as recover, \
             self.assertRaisesRegex(common.PipelineError, "rebasing"):
            self.publish()
        recover.assert_not_called()
        self.assertEqual(api.call_count, 1)

    def test_closed_pr_is_not_automatically_recreated(self):
        with patch.dict(os.environ, self.env), patch.object(publish_pr, "pending_pr", return_value=None), \
             patch.object(publish_pr, "public_get", side_effect=[self.ref, [{"state": "closed"}]]) as api, \
             patch.object(publish_pr, "run") as execute, self.assertRaisesRegex(common.PipelineError, "recreate"):
            self.publish()
        execute.assert_not_called()
        self.assertTrue(all(call.kwargs.get("method", "GET") == "GET" for call in api.call_args_list))
        self.assertIn("head=plaid%3A", api.call_args_list[-1].args[0])

    def test_successful_push_failed_pr_creation_is_recovered_without_another_push(self):
        references = [{"ref": "refs/heads/" + self.plan["branch"], "object": {"type": "commit", "sha": self.head}}]
        events = []
        responses = iter([self.ref, [], references, self.ref, self.ready])
        def api(*args, **kwargs):
            events.append(kwargs.get("method", "GET"))
            return next(responses)
        with patch.dict(os.environ, self.env), patch.object(publish_pr, "pending_pr", return_value=None), \
             patch.object(publish_pr, "public_get", side_effect=api), \
             patch.object(publish_pr, "recover_pushed_branch", side_effect=lambda *args: events.append("verify")) as recover, \
             patch.object(publish_pr, "run") as execute:
            self.assertEqual(self.publish(), self.ready["html_url"])
        execute.assert_not_called()
        recover.assert_called_once_with("plaid/plaid-go", self.plan["branch"], self.manifest, self.plan, self.root, self.head)
        self.assertEqual(events, ["GET", "GET", "GET", "verify", "GET", "POST"])

    def test_rehearsal_disabled_or_missing_bot_identity_stops_before_remote_access(self):
        cases = [("SDK_PIPELINE_ENABLED", "false"), ("SDK_PR_APP_BOT_ID", ""), ("SDK_PR_APP_BOT_ID", "bot-name")]
        for key, value in cases:
            with self.subTest(key=key, value=value), patch.dict(os.environ, {**self.env, key: value}), \
                 patch.object(publish_pr, "public_get") as api, \
                 patch.object(publish_pr, "pending_pr") as pending, self.assertRaises(common.PipelineError):
                self.publish()
            api.assert_not_called()
            pending.assert_not_called()
        self.plan["rehearsal"] = True
        with patch.dict(os.environ, self.env), patch.object(publish_pr, "public_get") as api, \
             patch.object(publish_pr, "pending_pr") as pending, self.assertRaisesRegex(common.PipelineError, "Rehearsal"):
            self.publish()
        api.assert_not_called()
        pending.assert_not_called()

    def test_trusted_rehearsal_input_overrides_changed_artifact_flag(self):
        event = Path(self.env["GITHUB_EVENT_PATH"])
        value = json.loads(event.read_text())
        value["inputs"] = {"rehearsal": "true"}
        event.write_text(json.dumps(value))
        self.assertFalse(self.plan["rehearsal"])
        with patch.dict(os.environ, self.env), patch.object(publish_pr, "pending_pr") as pending, \
             self.assertRaisesRegex(common.PipelineError, "Manual rehearsal"):
            self.publish()
        pending.assert_not_called()

    def test_pull_request_context_cannot_publish(self):
        with patch.dict(os.environ, {**self.env, "GITHUB_EVENT_NAME": "pull_request"}), \
             patch.object(publish_pr, "pending_pr") as pending, self.assertRaisesRegex(common.PipelineError, "context"):
            self.publish()
        pending.assert_not_called()

    def prepare_existing_branch(self):
        (self.repo / common.BUNDLE).write_text('{"fixture_only":true}')
        return test_pipeline.commit(self.repo, "Generated fixture")

    def clone_local(self, arguments, *args, **kwargs):
        self.assertEqual(arguments[:2], ["git", "clone"])
        return common.run(["git", "clone", str(self.repo), arguments[-1]])

    def test_existing_branch_rechecks_the_actual_commit_content_and_signature(self):
        head = self.prepare_existing_branch()
        with patch.object(publish_pr, "run", side_effect=self.clone_local), \
             patch.object(publish_pr, "verified_attestation") as verify:
            publish_pr.recover_pushed_branch("plaid/plaid-go", self.plan["branch"], self.manifest, self.plan, self.root, head)
        verify.assert_called_once()
        self.assertEqual(verify.call_args.kwargs["predicate"], self.manifest)
        self.assertEqual(verify.call_args.kwargs["run_id"], "123")
        self.assertEqual(common.git(self.root / "previous-push", "rev-parse", "HEAD"), head)

    def test_changed_branch_head_stops_before_signature_check(self):
        self.prepare_existing_branch()
        with patch.object(publish_pr, "run", side_effect=self.clone_local), \
             patch.object(publish_pr, "verified_attestation") as verify, self.assertRaisesRegex(common.PipelineError, "branch changed"):
            publish_pr.recover_pushed_branch("plaid/plaid-go", self.plan["branch"], self.manifest, self.plan, self.root, "a" * 40)
        verify.assert_not_called()

    def test_extra_commit_stops_before_signature_check(self):
        self.prepare_existing_branch()
        (self.repo / "extra.txt").write_text("human edit")
        head = test_pipeline.commit(self.repo, "Additional change")
        with patch.object(publish_pr, "run", side_effect=self.clone_local), \
             patch.object(publish_pr, "verified_attestation") as verify, self.assertRaisesRegex(common.PipelineError, "additional commits"):
            publish_pr.recover_pushed_branch("plaid/plaid-go", self.plan["branch"], self.manifest, self.plan, self.root, head)
        verify.assert_not_called()

    def test_edited_generation_commit_stops_before_signature_check(self):
        (self.repo / "client.go").write_text("package corrupted\n")
        head = self.prepare_existing_branch()
        with patch.object(publish_pr, "run", side_effect=self.clone_local), \
             patch.object(publish_pr, "verified_attestation") as verify, self.assertRaisesRegex(common.PipelineError, "edited"):
            publish_pr.recover_pushed_branch("plaid/plaid-go", self.plan["branch"], self.manifest, self.plan, self.root, head)
        verify.assert_not_called()

    def test_invalid_signature_is_not_treated_as_a_successful_retry(self):
        head = self.prepare_existing_branch()
        with patch.object(publish_pr, "run", side_effect=self.clone_local), \
             patch.object(publish_pr, "verified_attestation", side_effect=common.PipelineError("invalid signature")), \
             self.assertRaisesRegex(common.PipelineError, "invalid signature"):
            publish_pr.recover_pushed_branch("plaid/plaid-go", self.plan["branch"], self.manifest, self.plan, self.root, head)


if __name__ == "__main__":
    unittest.main()
