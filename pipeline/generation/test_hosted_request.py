import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

import common
import hosted_request as request


class HostedRequestTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hosted-request-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "2020-09-14.yml").write_bytes(b"reviewed public spec")
        self.settings = {"generation_mode": "fern-hosted", "cli_version": request.CLI_VERSION,
                         "cli_sha256": request.CLI_SHA256, "spec_path": "2020-09-14.yml",
                         "generator_image": "fernapi/fern-go-sdk", "generator_version": "1.70.3",
                         "generator_digest": "sha256:" + "c" * 64}
        self.plan = {"schema_version": 1, "source": {"repository": "plaid/plaid-openapi", "commit": "a" * 40,
            "path": "2020-09-14.yml", "sha256": common.sha256(b"reviewed public spec")},
            "config": {"repository": "plaid/plaid-openapi", "commit": "a" * 40, "sha256": "b" * 64},
            "generation": {"repository": "plaid/plaid-openapi", "workflow": ".github/workflows/generate-go-sdk.yml", "run_id": "123"},
            "sdk_base": "d" * 40, "baseline": None, "tags": ["v50.0.0"], "current_major": 50,
            "version": "50.1.0", "override": "", "rehearsal": True}
        self.event = self.root / "event.json"
        self.event.write_text(json.dumps({"inputs": {"rehearsal": True}}))

    def validate(self, plan=None, major=False, settings=None):
        with patch.dict(os.environ, {"GITHUB_EVENT_PATH": str(self.event), "GITHUB_EVENT_NAME": "workflow_dispatch"}), \
             patch.object(request.generate, "ROOT", self.root), \
             patch.object(request.generate, "check_context", return_value=("plaid/plaid-openapi", "a" * 40, "123")), \
             patch.object(request.generate, "config_digest", return_value="b" * 64):
            return request.validate_plan(plan or self.plan, settings or self.settings, major)

    def test_current_and_next_major_derive_from_verified_plan(self):
        self.assertEqual(self.validate(), "50.1.0")
        self.assertEqual(self.validate(major=True), "51.0.0")

    def test_changed_plan_launch_identity_inputs_or_version_rejected(self):
        for field in ("source", "config", "generation"):
            plan = copy.deepcopy(self.plan)
            key = "run_id" if field == "generation" else "sha256"
            plan[field][key] = "999"
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                self.validate(plan)
        for change in ({"version": "50.2.0"}, {"sdk_base": "master"}, {"current_major": True}, {"rehearsal": "true"}):
            with self.subTest(change=change), self.assertRaises(common.PipelineError):
                self.validate(dict(self.plan, **change))

    def test_major_generation_refuses_override_or_existing_next_major(self):
        for change in ({"override": "50.1.0"}, {"tags": ["v50.0.0", "v51.0.0"]}):
            with self.subTest(change=change), self.assertRaises(common.PipelineError):
                self.validate(dict(self.plan, **change), major=True)
        with self.assertRaises(common.PipelineError):
            self.validate(settings=dict(self.settings, generation_mode="local"))

    def test_machine_reader_credential_stays_out_of_git_arguments_and_storage(self):
        seen = []
        def command(argv, **kwargs):
            seen.append((list(argv), dict(kwargs["env"])))
            return b""
        token = "ghs_EXPLICIT_READER_TEST_ONLY"
        with patch.object(request, "private_command", side_effect=command):
            request.fetch_objects(self.root / "private.git", "example/private-sdk", ["a" * 40, "b" * 40], token)
        self.assertEqual(len(seen), 2)
        self.assertTrue(all(token not in " ".join(argv) for argv, _ in seen))
        self.assertIn("--no-write-fetch-head", seen[1][0])
        self.assertIn("http.followRedirects=false", seen[1][0])
        self.assertIn("fetch.fsckObjects=true", seen[1][0])
        self.assertEqual(seen[1][1]["GIT_CONFIG_KEY_0"], "http.https://github.com/.extraheader")
        self.assertNotIn("GIT_CONFIG_VALUE_0", seen[0][1])
        self.assertFalse((self.root / "private.git").exists())

    def test_private_target_records_fixed_identity_and_base_before_launch(self):
        metadata = {"id": 123, "full_name": "example/private-sdk", "private": True, "fork": False, "default_branch": "main"}
        branch = {"name": "main", "commit": {"sha": "a" * 40}}
        with patch.object(request.fern_delivery, "_get", side_effect=[metadata, branch]) as get:
            self.assertEqual(request.private_target("example/private-sdk", "123", "fixture-token"), (123, "main", "a" * 40))
        self.assertEqual(get.call_args_list[1].args[0], "repos/example/private-sdk/branches/main")
        for change in ({"private": False}, {"fork": True}, {"id": 456}):
            with patch.object(request.fern_delivery, "_get", return_value=dict(metadata, **change)), self.assertRaises(Exception):
                request.private_target("example/private-sdk", "123", "fixture-token")

    def test_renderer_has_only_private_pr_output_and_digests_exact_written_inputs(self):
        config = self.root / "config"
        def render(path, *_args):
            (path / "fern").mkdir(parents=True)
            (path / "2020-09-14.yml").write_bytes(b"reviewed public spec")
            (path / "fern/openapi-overlay.yml").write_bytes(b"overlay: 1.0.0\n")
            (path / "fern/fern.config.json").write_text(json.dumps({"version": request.CLI_VERSION}))
            document = {"replay": {"enabled": False}, "groups": {"go-pipeline": {"generators": [{
                "name": "fernapi/fern-go-sdk@" + self.settings["generator_digest"], "version": "1.70.3",
                "output": {"location": "local-file-system", "path": "../../unused"}, "config": {"maxRetries": 0}}]}}}
            (path / "fern/generators.yml").write_text(request.yaml.safe_dump(document))
        with patch.object(request.generate, "render_config", side_effect=render):
            inputs = request.render_request(config, b"reviewed public spec", "50.1.0", self.settings, "example/private-sdk")
        doc = request.yaml.safe_load((config / "fern/generators.yml").read_text())
        entry = doc["groups"]["go-pipeline"]["generators"][0]
        self.assertNotIn("output", entry)
        self.assertEqual(entry["github"], {"repository": "example/private-sdk", "mode": "pull-request", "workflows": False, "license": "MIT"})
        self.assertEqual(inputs["fern:generators.yml"], common.sha256((config / "fern/generators.yml").read_bytes()))
        self.assertEqual(inputs["fern:generators.yml#fernapi/fern-go-sdk"], common.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()))

    def test_launch_uses_own_job_and_private_pr_not_incoming_receipt(self):
        job = "11111111-1111-4111-8111-111111111111"
        token = "fern_fixture_token"
        use_stderr = False
        def run(argv, **kwargs):
            env = kwargs["env"]
            self.assertEqual(env["FERN_TOKEN"], token)
            self.assertNotIn("SDK_FERN_READ_TOKEN", env)
            self.assertNotIn("GITHUB_TOKEN", env)
            self.assertNotIn("--local", argv)
            self.assertEqual(env["FERN_USE_SDK_GEN_API"], "false")
            try:
                urllib.request.urlopen(urllib.request.Request(env["FERN_FDR_ORIGIN"] + "/registry/api/register", data=b"{}"), timeout=3)
            except urllib.error.HTTPError as error:
                self.assertEqual(error.code, 403)
            log = f"DEBUG now go-pipeline fernapi/fern-go-sdk Job ID: {job}\nINFO now go-pipeline fernapi/fern-go-sdk Created pull request: https://github.com/example/private-sdk/pull/17\n"
            if use_stderr:
                return subprocess.CompletedProcess(argv, 0, stdout="", stderr=log.replace("Created pull request:", "Reused existing pull request:"))
            return subprocess.CompletedProcess(argv, 0, stdout=log, stderr="")
        with patch.dict(os.environ, {"SDK_FERN_READ_TOKEN": "never-pass", "GITHUB_TOKEN": "never-pass"}), \
             patch.object(request.subprocess, "run", side_effect=run):
            for use_stderr in (False, True):
                with self.subTest(reused_pr_on_stderr=use_stderr):
                    self.assertEqual(request.launch(self.root, self.root / "cli.cjs", "50.1.0", token, "example/private-sdk"), (job, 17))

    def test_launch_rejects_ambiguous_identity_or_unobserved_registry_containment(self):
        result = subprocess.CompletedProcess([], 0, stdout="unexpected result", stderr="private details")
        with patch.object(request.subprocess, "run", return_value=result), self.assertRaises(common.PipelineError) as caught:
            request.launch(self.root, self.root / "cli.cjs", "50.1.0", "fern_fixture_token", "example/private-sdk")
        self.assertNotIn("private", str(caught.exception))

    def test_outer_failure_never_leaks_private_details_and_does_not_publish_files(self):
        prepared, output = self.root / "prepared", self.root / "output"
        prepared.mkdir()
        (prepared / "plan.json").write_text(json.dumps(self.plan))
        secrets = {"FERN_TOKEN": "fern_fixture", "SDK_FERN_READ_TOKEN": "reader_fixture",
                   "FERN_OUTPUT_REPOSITORY": "example/private-sdk", "FERN_OUTPUT_REPOSITORY_ID": "123"}
        with patch.dict(os.environ, secrets), patch.object(request.generate, "settings", side_effect=ValueError("reader_fixture example/private-sdk")), \
             self.assertRaises(common.PipelineError) as failure:
            request.request(prepared, output)
        self.assertNotIn("reader_fixture", str(failure.exception))
        self.assertNotIn("example/private-sdk", str(failure.exception))
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
