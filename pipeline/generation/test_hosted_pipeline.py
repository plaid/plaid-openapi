"""Staged assembly uses real Git/artifacts; expensive generation and signatures are separate boundaries."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import common
import attestation
import generate
import hosted_contract
import hosted_pipeline as hosted
import publish_pr
from test_pipeline import commit, init, spec as empty_spec, write


def spec():
    return empty_spec().replace(b"paths: {}", b"paths:\n  /fixture:\n    get:\n      x-fern-sdk-group-name: fixture\n      x-fern-sdk-method-name: get")


class HostedPipelineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hosted-pipeline-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source, self.sdk = self.root / "source", self.root / "sdk"
        self.values = dict(generate.settings(), generation_mode="fern-hosted")
        init(self.source)
        write(self.source, "2020-09-14.yml", spec().decode())
        write(self.source, "fern/openapi-overlay.yml", "overlay: 1.0.0\nactions: []\n")
        common.save_json(self.source / "pipeline/generation/settings.json", self.values)
        self.source_commit = commit(self.source)
        init(self.sdk)
        for name, value in {
            "go.mod": "module github.com/plaid/plaid-go/v50\n\ngo 1.21\n", "go.sum": "",
            "client.go": "package plaid\n", "removed.go": "package plaid\n",
            "legacy/client.go": "package plaid\n", "legacy/configuration.go": "package plaid\n",
            "internal/caller.go": "package internal\n", "internal/destination.go": "package internal\n",
            "core/custom_endpoint.go": "package core\n", "option/custom_endpoint.go": "package option\n",
            "README.md": "github.com/plaid/plaid-go/v50\n", "CHANGELOG.md": "## v50.0.0\n",
            "MIGRATION.md": "Reviewed migration\n", "LICENSE": "MIT\n", ".circleci/config.yml": "reviewed: true\n",
            ".github/CODEOWNERS": "* @example/owners\n", "scripts/release/policy.py": "# reviewed\n",
            ".fernignore": "go.mod\ngo.sum\nREADME.md\nCHANGELOG.md\nMIGRATION.md\nlegacy/\n",
        }.items():
            write(self.sdk, name, value)
        self.sdk_commit = commit(self.sdk)
        common.git(self.sdk, "tag", "v50.0.0")
        event = self.root / "event.json"
        self.event = {"repository": {"full_name": "plaid/plaid-openapi", "private": False, "fork": False,
                                      "default_branch": "master"}, "inputs": {"rehearsal": False}}
        common.save_json(event, self.event)
        self.env = {"GITHUB_REPOSITORY": "plaid/plaid-openapi", "GITHUB_EVENT_NAME": "workflow_dispatch",
                    "GITHUB_REF": "refs/heads/master", "GITHUB_SHA": self.source_commit,
                    "GITHUB_RUN_ID": "123", "GITHUB_EVENT_PATH": str(event), "SDK_PIPELINE_ENABLED": "true"}
        self.addCleanup(patch.stopall)
        patch.object(generate, "ROOT", self.source).start()
        patch.dict(os.environ, {**common.clean_env(), **self.env}, clear=True).start()
        self.fetch = patch.object(generate, "fetch_repository", side_effect=self.fetch_sdk).start()
        self.legacy = patch.object(generate, "run_legacy", side_effect=self.legacy_generation).start()
        self.tests = patch.object(generate, "verify_sdk", side_effect=self.sdk_tests).start()
        self.compatibility = patch.object(generate, "compatibility_gate", side_effect=self.api_comparison).start()
        self.signature = patch.object(hosted_contract, "verify_fern_evidence").start()
        self.seal_signature = patch.object(attestation, "verified_attestation").start()
        patch.object(generate, "restore_published_multipart_field").start()
        patch.object(generate, "harden_wire_tests").start()
        patch.object(hosted, "run", side_effect=self.run_command).start()
        self.breaking = False
        self.prepared = self.root / "prepared"

    def run_command(self, args, *positional, **keywords):
        if args[:3] == ["go", "mod", "tidy"]:
            return b""  # Dependency execution is part of the mocked SDK boundary.
        return common.run(args, *positional, **keywords)

    def fetch_sdk(self, repository, branch, destination):
        self.assertEqual((repository, branch), ("plaid/plaid-go", "master"))
        common.run(["git", "clone", "--quiet", str(self.sdk), str(destination)])
        return common.git(destination, "rev-parse", "HEAD")

    def legacy_generation(self, sdk, source, module, values, work):
        self.assertEqual(common.sha256(source.read_bytes()), common.sha256(spec()))
        self.assertEqual(module, (sdk / "go.mod").read_text().splitlines()[0].removeprefix("module "))
        write(sdk, "legacy/client.go", "package plaid\n// regenerated " + module + "\n")
        common.git(sdk, "add", "-A")
        return {"source_commit": "b" * 40, "spec_sha256": common.sha256(spec()),
                "tree_sha256": common.sha256(common.canonical([item for item in common.entries(sdk) if item[0].startswith("legacy/")])),
                "generator_digest": "sha256:" + "c" * 64}

    def sdk_tests(self, sdk, values, work):
        self.assertNotIn("GH_TOKEN", os.environ)
        self.assertNotIn("FERN_TOKEN", os.environ)
        self.assertFalse((sdk / "removed.go").exists())

    def api_comparison(self, old, sdk, module, published, values, work, **kwargs):
        changes = b"removed exported API\n" if self.breaking and work.name == "comparison" else b""
        (work / "api-diff.txt").write_bytes(changes)
        common.require(not changes or kwargs.get("allow_breaking"), "Breaking explicit override")
        return changes

    def plan(self):
        hosted.prepare(self.prepared)
        return json.loads((self.prepared / "plan.json").read_text())

    def fern(self, plan, version=None, name="fern"):
        version = version or plan["version"]
        output, tree = self.root / name, self.root / (name + "-tree")
        output.mkdir()
        init(tree)
        write(tree, "client.go", "package plaid\n// generated github.com/plaid/plaid-go/v" + version.split(".")[0] + "\n")
        common.save_json(tree / ".fern/metadata.json", {
            "cliVersion": self.values["cli_version"], "generatorName": self.values["generator_image"],
            "generatorVersion": self.values["generator_version"], "sdkVersion": "v" + version})
        common.git(tree, "add", "-A")
        index, digest = common.content(tree)
        common.archive_sdk(tree, output / "fern-output.tar.gz")
        (output / "fern-content.json").write_bytes(index)
        record = {"schema_version": 1, "sdk_version": version, "sdk_base": plan["sdk_base"],
                  **{key: plan[key] for key in ("source", "config", "generation")},
                  "generator": {"image": self.values["generator_image"], "version": self.values["generator_version"],
                                "sha256": self.values["generator_digest"].removeprefix("sha256:")},
                  "cli": {"version": self.values["cli_version"], "sha256": self.values["cli_sha256"]},
                  "evidence": {"receipt_sha256": "d" * 64, "key_sha256": hosted_contract.FERN_KEY_SHA256,
                               "git_commit": "e" * 40, "git_tree": "f" * 40,
                               "inputs_sha256": "a" * 64, "job_id_sha256": "b" * 64}, "content_sha256": digest}
        common.save_json(output / "fern-record.json", record)
        if not plan["rehearsal"]:
            (output / "fern.bundle.json").write_text('{"fixture":true}')
        return output

    def seal(self, directory):
        if not json.loads((directory / "plan.json").read_text())["rehearsal"]:
            (directory / "assembly.bundle.json").write_text('{"fixture":true}')

    def test_prepare_local_mode_leaves_existing_local_path_in_charge(self):
        with patch.object(generate, "settings", return_value=dict(self.values, generation_mode="local")):
            result = hosted.prepare(self.prepared)
        self.assertEqual(result, {"status": "ready", "mode": "local", "rehearsal": False})
        self.fetch.assert_not_called()
        self.assertFalse((self.prepared / "plan.json").exists())

    def test_prepare_waits_for_unpublished_predecessor(self):
        with patch.object(generate, "pending_release", return_value="50.1.0"):
            result = hosted.prepare(self.prepared)
        self.assertEqual(result["status"], "awaiting-release")
        self.assertFalse((self.prepared / "plan.json").exists())

    def test_prepare_selects_minor_and_records_exact_public_inputs(self):
        plan = self.plan()
        self.assertEqual(plan["version"], "50.1.0")
        self.assertEqual(plan["current_major"], 50)
        self.assertEqual(plan["sdk_base"], self.sdk_commit)
        self.assertEqual(plan["baseline"], {"tag": "v50.0.0", "commit": self.sdk_commit})
        self.assertEqual(plan["source"]["sha256"], common.sha256(spec()))
        self.assertEqual(plan["source"]["commit"], plan["config"]["commit"])

    def test_published_same_input_candidate_is_a_noop(self):
        plan = self.plan()
        output = self.root / "candidate"
        hosted.assemble(self.prepared, self.fern(plan), output)
        extracted = self.root / "released"
        common.extract_sdk(output / "sdk.tar.gz", extracted)
        common.git(self.sdk, "rm", "-r", "--quiet", ".")
        shutil.copytree(extracted, self.sdk, dirs_exist_ok=True)
        commit(self.sdk, "Publish fixture")
        common.git(self.sdk, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                   "-c", "tag.gpgsign=false", "tag", "-a", "v50.1.0", "-m", "Fixture")
        result = hosted.prepare(self.root / "next-prepare")
        self.assertEqual(result["status"], "unchanged")
        self.assertEqual(self.legacy.call_count, 1)

    def test_passing_candidate_has_schema2_and_both_verified_proofs(self):
        plan = self.plan()
        fern, output = self.fern(plan), self.root / "candidate"
        with patch.dict(os.environ, {"GH_TOKEN": "read-only-fixture"}):
            result = hosted.assemble(self.prepared, fern, output)
        self.assertEqual(result["status"], "assembled")
        self.signature.assert_called_once()
        self.tests.assert_not_called()
        self.compatibility.assert_not_called()
        self.legacy.assert_called_once()
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(manifest["fern"]["sdk_base"], self.sdk_commit)
        tree = self.root / "extracted"
        common.extract_sdk(output / "sdk.tar.gz", tree)
        self.assertTrue((tree / hosted_contract.FERN_INDEX).is_file())
        self.assertTrue((tree / hosted_contract.FERN_BUNDLE).is_file())
        self.assertEqual((tree / "MIGRATION.md").read_text(), "Reviewed migration\n")
        self.assertFalse((tree / "removed.go").exists())
        self.seal(output)
        archive_hash = common.sha256((output / "sdk.tar.gz").read_bytes())
        validation = self.root / "validation"
        result = hosted.validate(self.prepared, output, validation)
        self.assertEqual(result["status"], "generated")
        self.tests.assert_called_once()
        self.assertEqual({path.name for path in validation.iterdir()}, {"result.json", "api-diff.txt"})
        self.assertEqual(common.sha256((output / "sdk.tar.gz").read_bytes()), archive_hash)

    def test_missing_or_failed_signature_blocks_before_sdk_execution(self):
        plan = self.plan()
        fern = self.fern(plan)
        for failure in ("missing", "invalid"):
            with self.subTest(failure=failure):
                if failure == "missing":
                    (fern / "fern.bundle.json").unlink()
                else:
                    (fern / "fern.bundle.json").write_text("fixture")
                self.signature.side_effect = common.PipelineError("bad signature")
                with self.assertRaises(common.PipelineError):
                    hosted.assemble(self.prepared, fern, self.root / ("failed-" + failure))
        self.legacy.assert_not_called()
        self.tests.assert_not_called()

    def test_wrong_record_run_or_sdk_base_blocks_before_tests(self):
        plan = self.plan()
        for key in ("sdk_base", "generation"):
            fern = self.fern(plan, name=key)
            record = json.loads((fern / "fern-record.json").read_text())
            if key == "sdk_base":
                record[key] = "c" * 40
            else:
                record[key]["run_id"] = "999"
            common.save_json(fern / "fern-record.json", record)
            with self.assertRaisesRegex(common.PipelineError, "prepared inputs"):
                hosted.assemble(self.prepared, fern, self.root / ("wrong-" + key))
        self.tests.assert_not_called()

    def test_rehearsal_is_event_bound_and_has_only_unsigned_evidence(self):
        self.event["inputs"]["rehearsal"] = True
        common.save_json(Path(self.env["GITHUB_EVENT_PATH"]), self.event)
        plan = self.plan()
        output = self.root / "rehearsal"
        result = hosted.assemble(self.prepared, self.fern(plan), output)
        self.assertTrue(result["rehearsal"])
        self.assertEqual(json.loads((output / "manifest.json").read_text())["schema_version"], 2)
        tree = self.root / "rehearsal-sdk"
        common.extract_sdk(output / "sdk.tar.gz", tree)
        self.assertTrue((tree / hosted_contract.FERN_INDEX).is_file())
        self.assertFalse((tree / hosted_contract.FERN_BUNDLE).exists())
        self.assertFalse((tree / common.BUNDLE).exists())
        publish_pr.verify_artifact(output, self.root / "unsigned-check", signed=False)
        with self.assertRaises(common.PipelineError):
            publish_pr.verify_artifact(output, self.root / "signed-check", signed=True)
        self.signature.assert_not_called()
        plan["rehearsal"] = False
        common.save_json(self.prepared / "plan.json", plan)
        with self.assertRaisesRegex(common.PipelineError, "trusted workflow inputs"):
            hosted.load_plan(self.prepared)

    def test_major_regenerates_both_clients_and_checks_both_namespace_directions(self):
        plan = self.plan()
        self.breaking = True
        probe = self.root / "probe"
        hosted.assemble(self.prepared, self.fern(plan), probe)
        self.seal(probe)
        result = hosted.validate(self.prepared, probe, self.root / "minor-validation")
        self.assertEqual((result["status"], result["next_version"]), ("needs-major", "51.0.0"))
        self.assertFalse((probe / "generation.bundle.json").exists())
        output = self.root / "major"
        hosted.assemble(self.prepared, self.fern(plan, "51.0.0", "fern-major"), output, major=True)
        self.seal(output)
        result = hosted.validate(self.prepared, output, self.root / "major-validation", probe)
        self.assertEqual((result["status"], result["version"]), ("generated", "51.0.0"))
        self.assertEqual(self.legacy.call_count, 2)
        self.assertEqual(self.tests.call_count, 2)
        self.assertEqual([call.args[5].name for call in self.compatibility.call_args_list], ["comparison", "comparison", "forward", "reverse"])
        tree = self.root / "major-sdk"
        common.extract_sdk(output / "sdk.tar.gz", tree)
        self.assertIn("module github.com/plaid/plaid-go/v51", (tree / "go.mod").read_text())
        self.assertEqual((tree / "README.md").read_text(), "github.com/plaid/plaid-go/v51\n")

    def test_failed_sdk_tests_never_choose_a_major(self):
        plan = self.plan()
        self.tests.side_effect = common.PipelineError("SDK tests failed")
        candidate = self.root / "candidate"
        hosted.assemble(self.prepared, self.fern(plan), candidate)
        self.seal(candidate)
        output = self.root / "failed-tests"
        with self.assertRaisesRegex(common.PipelineError, "SDK tests failed"):
            hosted.validate(self.prepared, candidate, output)
        self.compatibility.assert_not_called()
        self.assertFalse((output / "manifest.json").exists())

    def test_changed_base_or_tags_stop_before_generation(self):
        plan = self.plan()
        fern = self.fern(plan)
        write(self.sdk, "docs.txt", "new reviewed base\n")
        commit(self.sdk)
        with self.assertRaisesRegex(common.PipelineError, "master changed"):
            hosted.assemble(self.prepared, fern, self.root / "stale")
        self.legacy.assert_not_called()

    def test_explicit_override_cannot_turn_a_break_into_major(self):
        self.event["inputs"]["version"] = "50.0.1"
        common.save_json(Path(self.env["GITHUB_EVENT_PATH"]), self.event)
        plan = self.plan()
        self.breaking = True
        candidate = self.root / "candidate"
        hosted.assemble(self.prepared, self.fern(plan), candidate)
        self.seal(candidate)
        with self.assertRaisesRegex(common.PipelineError, "Breaking explicit override"):
            hosted.validate(self.prepared, candidate, self.root / "override")
        with self.assertRaisesRegex(common.PipelineError, "Explicit version"):
            hosted.major_version(plan)

    def test_changed_fern_archive_cannot_reach_legacy_or_tests(self):
        plan = self.plan()
        fern = self.fern(plan)
        tree = self.root / "substituted"
        common.extract_sdk(fern / "fern-output.tar.gz", tree)
        write(tree, "client.go", "package replaced\n")
        hosted.initialize_tree(tree)
        common.archive_sdk(tree, fern / "fern-output.tar.gz")
        with self.assertRaisesRegex(common.PipelineError, "verified content index"):
            hosted.assemble(self.prepared, fern, self.root / "substitution")
        self.legacy.assert_not_called()
        self.tests.assert_not_called()

    def test_new_published_tag_invalidates_preparation(self):
        plan = self.plan()
        common.git(self.sdk, "tag", "v50.0.1")
        with self.assertRaisesRegex(common.PipelineError, "tags changed"):
            hosted.assemble(self.prepared, self.fern(plan), self.root / "new-tag")
        self.legacy.assert_not_called()

    def test_tampered_major_probe_stops_before_sdk_execution(self):
        plan = self.plan()
        self.breaking = True
        probe = self.root / "probe"
        hosted.assemble(self.prepared, self.fern(plan), probe)
        self.seal(probe)
        (probe / "content.json").write_text("[]")
        candidate = self.root / "major"
        hosted.assemble(self.prepared, self.fern(plan, "51.0.0", "major-fern"), candidate, major=True)
        self.seal(candidate)
        with self.assertRaises(common.PipelineError):
            hosted.validate(self.prepared, candidate, self.root / "major-validation", probe)
        self.tests.assert_not_called()

    def test_privileged_credentials_are_rejected(self):
        for name in ("FERN_TOKEN", "SDK_FERN_READ_TOKEN", "SDK_PR_APP_PRIVATE_KEY"):
            with self.subTest(name=name), patch.dict(os.environ, {name: "fixture-secret"}), \
                 self.assertRaisesRegex(common.PipelineError, "privileged credentials"):
                hosted.prepare(self.prepared)
        self.fetch.assert_not_called()

    def test_sdk_execution_cannot_modify_files_before_attestation(self):
        plan = self.plan()
        self.tests.side_effect = lambda sdk, *_args: write(sdk, "client.go", "package replaced_by_test\n")
        candidate = self.root / "candidate"
        hosted.assemble(self.prepared, self.fern(plan), candidate)
        self.seal(candidate)
        original = (candidate / "sdk.tar.gz").read_bytes()
        output = self.root / "modified-by-tests"
        with self.assertRaisesRegex(common.PipelineError, "SDK execution modified"):
            hosted.validate(self.prepared, candidate, output)
        self.compatibility.assert_not_called()
        self.assertFalse((output / "manifest.json").exists())
        self.assertEqual((candidate / "sdk.tar.gz").read_bytes(), original)

    def test_validation_requires_assembly_seal_before_execution(self):
        plan = self.plan()
        candidate = self.root / "candidate"
        hosted.assemble(self.prepared, self.fern(plan), candidate)
        with self.assertRaises(common.PipelineError):
            hosted.validate(self.prepared, candidate, self.root / "unsealed")
        self.seal(candidate)
        self.seal_signature.side_effect = common.PipelineError("bad seal")
        with self.assertRaisesRegex(common.PipelineError, "bad seal"):
            hosted.validate(self.prepared, candidate, self.root / "bad-seal")
        self.tests.assert_not_called()

    def test_major_validation_rejects_compatible_minor_probe(self):
        plan = self.plan()
        probe, candidate = self.root / "minor", self.root / "major"
        hosted.assemble(self.prepared, self.fern(plan), probe)
        hosted.assemble(self.prepared, self.fern(plan, "51.0.0", "major-fern"), candidate, major=True)
        self.seal(probe)
        self.seal(candidate)
        with self.assertRaisesRegex(common.PipelineError, "breaking provisional"):
            hosted.validate(self.prepared, candidate, self.root / "major-validation", probe)


if __name__ == "__main__":
    unittest.main()
