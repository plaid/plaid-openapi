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

    def test_git_fetch_is_public_and_credential_free(self):
        seen = []
        def command(argv, **kwargs):
            seen.append((list(argv), dict(kwargs["env"])))
            return b""
        with patch.dict(os.environ, {"FERN_TOKEN": "fixture-secret", "GITHUB_TOKEN": "fixture-gh-secret"}), \
             patch.object(request, "quiet_command", side_effect=command):
            request.fetch_public_base(self.root / "public.git", "a" * 40)
        self.assertEqual(len(seen), 2)
        self.assertIn("https://github.com/plaid/plaid-go.git", seen[1][0])
        self.assertIn("--no-write-fetch-head", seen[1][0])
        self.assertIn("http.followRedirects=false", seen[1][0])
        self.assertIn("fetch.fsckObjects=true", seen[1][0])
        for _, env in seen:
            self.assertNotIn("GIT_CONFIG_VALUE_0", env)
            self.assertNotIn("FERN_TOKEN", env)
            self.assertNotIn("GITHUB_TOKEN", env)
        self.assertFalse((self.root / "public.git").exists())

    def test_renderer_has_only_empty_download_output_and_digests_exact_written_inputs(self):
        config = self.root / "config"
        raw = self.root / "raw"
        raw.mkdir()
        def render(path, destination, *_args):
            (path / "fern").mkdir(parents=True)
            (path / "2020-09-14.yml").write_bytes(b"reviewed public spec")
            (path / "fern/openapi-overlay.yml").write_bytes(b"overlay: 1.0.0\n")
            (path / "fern/fern.config.json").write_text(json.dumps({"version": request.CLI_VERSION}))
            document = {"replay": {"enabled": False}, "groups": {"go-pipeline": {"generators": [{
                "name": "fernapi/fern-go-sdk@" + self.settings["generator_digest"], "version": "1.70.3",
                "output": {"location": "local-file-system", "path": os.path.relpath(destination, path / "fern")}, "config": {"maxRetries": 0}}]}}}
            (path / "fern/generators.yml").write_text(request.yaml.safe_dump(document))
        with patch.object(request.generate, "render_config", side_effect=render):
            inputs = request.render_request(config, raw, b"reviewed public spec", "50.1.0", self.settings)
        doc = request.yaml.safe_load((config / "fern/generators.yml").read_text())
        entry = doc["groups"]["go-pipeline"]["generators"][0]
        self.assertNotIn("github", entry)
        self.assertEqual(entry["output"]["location"], "local-file-system")
        self.assertEqual((config / "fern" / entry["output"]["path"]).resolve(), raw.resolve())
        self.assertEqual(inputs["fern:generators.yml"], common.sha256((config / "fern/generators.yml").read_bytes()))
        self.assertEqual(inputs["fern:generators.yml#fernapi/fern-go-sdk"], common.sha256(json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()))

    def test_launch_uses_own_job_without_a_git_reader_or_private_repository(self):
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
            log = f"DEBUG now go-pipeline fernapi/fern-go-sdk Job ID: {job}\nINFO now go-pipeline fernapi/fern-go-sdk Downloaded files\n"
            if use_stderr:
                return subprocess.CompletedProcess(argv, 0, stdout="", stderr=log)
            return subprocess.CompletedProcess(argv, 0, stdout=log, stderr="")
        with patch.dict(os.environ, {"SDK_FERN_READ_TOKEN": "never-pass", "GITHUB_TOKEN": "never-pass"}), \
             patch.object(request.subprocess, "run", side_effect=run):
            for use_stderr in (False, True):
                with self.subTest(log_on_stderr=use_stderr):
                    self.assertEqual(request.launch(self.root, self.root / "cli.cjs", "50.1.0", token), job)

    def test_launch_rejects_ambiguous_identity_or_unobserved_registry_containment(self):
        result = subprocess.CompletedProcess([], 0, stdout="unexpected result", stderr="private details")
        with patch.object(request.subprocess, "run", return_value=result), self.assertRaises(common.PipelineError) as caught:
            request.launch(self.root, self.root / "cli.cjs", "50.1.0", "fern_fixture_token")
        self.assertNotIn("private", str(caught.exception))

    def test_outer_failure_never_leaks_private_details_and_does_not_publish_files(self):
        prepared, output = self.root / "prepared", self.root / "output"
        prepared.mkdir()
        (prepared / "plan.json").write_text(json.dumps(self.plan))
        with patch.dict(os.environ, {"FERN_TOKEN": "fern_fixture", "GH_TOKEN": "", "GITHUB_TOKEN": "", "SSH_AUTH_SOCK": ""}), \
             patch.object(request.generate, "settings", side_effect=ValueError("fern_fixture secret-location")), \
             self.assertRaises(common.PipelineError) as failure:
            request.request(prepared, output)
        self.assertNotIn("fern_fixture", str(failure.exception))
        self.assertNotIn("secret-location", str(failure.exception))
        self.assertFalse(output.exists())

    def test_request_keeps_download_receipt_and_uses_no_private_git_handoff(self):
        prepared, output = self.root / "prepared", self.root / "output"
        prepared.mkdir()
        (prepared / "plan.json").write_text(json.dumps(self.plan))
        public_files = {"go.mod": ("100644", b"module github.com/plaid/plaid-go/v50\n")}
        job = "11111111-1111-4111-8111-111111111111"
        inputs = {"fern:../2020-09-14.yml": "a" * 64}
        receipt = b'{"payload":"fixture","payloadType":"fixture","signatures":[{"sig":"fixture"}]}'
        summary = {"receipt_sha256": common.sha256(receipt), "key_sha256": "b" * 64,
                   "output_mode": "downloadFiles", "git_tree": "c" * 40,
                   "inputs_sha256": "d" * 64, "job_id_sha256": "e" * 64}
        def export(**kwargs):
            self.assertEqual(kwargs["expected_tree"], summary["git_tree"])
            self.assertEqual(kwargs["forbidden_values"], (b"fern_fixture",))
            (kwargs["output"] / "fern-output.tar.gz").write_bytes(b"fixture archive")
            (kwargs["output"] / "fern-content.json").write_bytes(b"[]")
            return common.sha256(b"[]")
        with patch.dict(os.environ, {"FERN_TOKEN": "fern_fixture", "GH_TOKEN": "", "GITHUB_TOKEN": "", "SSH_AUTH_SOCK": ""}), \
             patch.object(request.generate, "ROOT", self.root), \
             patch.object(request.generate, "settings", return_value=self.settings), \
             patch.object(request, "validate_plan", return_value="50.1.0"), \
             patch.object(request, "fetch_public_base") as fetch, \
             patch.object(request, "git_files", return_value=public_files), \
             patch.object(request, "render_request", return_value=inputs), \
             patch.object(request.generate, "install_cli", return_value=self.root / "cli.cjs"), \
             patch.object(request, "launch", return_value=job) as launch, \
             patch.object(request.fern_provenance, "verify_download", return_value={"summary": summary, "receipt": receipt}) as verify, \
             patch.object(request, "export_verified_output", side_effect=export):
            request.request(prepared, output)
        fetch.assert_called_once()
        self.assertEqual(fetch.call_args.args[1], self.plan["sdk_base"])
        self.assertEqual(launch.call_args.args[-1], "fern_fixture")
        self.assertEqual(set(verify.call_args.args[2]), {"job_id", "sdk_version", "cli_version", "generator", "inputs"})
        self.assertEqual(verify.call_args.args[2]["job_id"], job)
        self.assertEqual(set(path.name for path in output.iterdir()),
                         {"fern-output.tar.gz", "fern-content.json", "fern-record.json", "fern-provenance.json"})
        self.assertEqual((output / "fern-provenance.json").read_bytes(), receipt)
        record = json.loads((output / "fern-record.json").read_text())
        self.assertEqual(record["schema_version"], 2)
        self.assertEqual(record["evidence"], summary)
        self.assertNotIn("git_commit", record["evidence"])


if __name__ == "__main__":
    unittest.main()
