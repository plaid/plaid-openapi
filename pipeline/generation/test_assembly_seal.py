"""Sealed assembly tests mock only the gh cryptographic verification response."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import assembly_seal
import attestation
import common
import generate
import hosted_contract
import publish_pr
import test_hosted_contract
import test_pipeline


class AssemblySealTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="assembly-seal-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.values = generate.settings()
        self.repo, self.artifact, self.manifest, self.plan = test_pipeline.PipelineTests.fixture(self)
        metadata = json.loads((self.repo / ".fern/metadata.json").read_bytes())
        metadata["cliVersion"] = self.manifest["generator"]["cli_version"]
        common.save_json(self.repo / ".fern/metadata.json", metadata)
        common.git(self.repo, "add", "-A")
        self.fern_index = common.canonical([item for item in common.entries(self.repo)
                                           if item[0] in {".fern/metadata.json", "client.go"}])
        self.record = test_hosted_contract.record_fixture(self.manifest, sdk_base=self.plan["sdk_base"], index=self.fern_index)
        self.manifest.update(schema_version=2, fern=self.record)
        (self.repo / hosted_contract.FERN_INDEX).write_bytes(self.fern_index)
        (self.repo / hosted_contract.FERN_PROVENANCE).write_bytes(test_hosted_contract.portable_fixture(self.record))
        common.save_json(self.repo / hosted_contract.FERN_BUNDLE, {"fixture_type": hosted_contract.FERN_PREDICATE})
        self.refresh_artifact()
        common.save_json(self.artifact / assembly_seal.ASSEMBLY_BUNDLE, {"fixture_type": assembly_seal.ASSEMBLY_PREDICATE})
        self.event = self.root / "event.json"
        common.save_json(self.event, {"repository": {"full_name": attestation.CONFIG_REPO, "private": False,
                         "fork": False, "default_branch": "master"}, "inputs": {"rehearsal": False}})
        environment = {"GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_EVENT_PATH": str(self.event),
            "GITHUB_REPOSITORY": attestation.CONFIG_REPO, "GITHUB_REF": "refs/heads/master",
            "GITHUB_SHA": self.manifest["config"]["commit"], "GITHUB_RUN_ID": self.manifest["generation"]["run_id"]}
        env = patch.dict(os.environ, environment)
        env.start()
        self.addCleanup(env.stop)
        self.calls = []
        verifier = patch.object(attestation, "run", side_effect=self.verified_response)
        verifier.start()
        self.addCleanup(verifier.stop)
        settings = patch.object(generate, "settings", return_value={**self.values, "generation_mode": "fern-hosted"})
        settings.start()
        self.addCleanup(settings.stop)

    def refresh_artifact(self):
        common.git(self.repo, "add", "-A")
        content, digest = common.content(self.repo)
        self.manifest["content_sha256"] = digest
        common.save_json(self.repo / common.MANIFEST, self.manifest)
        common.save_json(self.artifact / "manifest.json", self.manifest)
        common.save_json(self.artifact / "plan.json", self.plan)
        (self.artifact / "content.json").write_bytes(content)
        common.git(self.repo, "add", "-A")
        common.archive_sdk(self.repo, self.artifact / "sdk.tar.gz")

    def verified_response(self, *args):
        self.calls.append(args)
        bundle = Path(args[args.index("--bundle") + 1])
        predicate_type = json.loads(bundle.read_bytes())["fixture_type"]
        result = test_hosted_contract.verification_fixture(self.record)
        if predicate_type != hosted_contract.FERN_PREDICATE:
            suffix = "assembly" if predicate_type == assembly_seal.ASSEMBLY_PREDICATE else "source"
            result[0]["verificationResult"]["statement"].update(
                predicateType=predicate_type, predicate=copy.deepcopy(self.sealed_manifest),
                subject=[{"name": "plaid-go-v" + self.sealed_manifest["sdk"]["version"] + "-" + suffix,
                          "digest": {"sha256": self.sealed_manifest["content_sha256"]}}])
        return common.canonical(result)

    def verify(self):
        return assembly_seal.verify_assembly_artifact(self.artifact, self.root / "verified")

    def test_valid_seal_is_distinct_from_final_generation(self):
        self.sealed_manifest = copy.deepcopy(self.manifest)
        manifest, plan = self.verify()
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(plan, self.plan)
        kinds = [args[args.index("--predicate-type") + 1] for args in self.calls]
        self.assertEqual(kinds, [hosted_contract.FERN_PREDICATE, assembly_seal.ASSEMBLY_PREDICATE])
        self.assertNotIn(b"sdk-assembly", (self.artifact / "generation.bundle.json").read_bytes())

    def test_no_generation_signature_cannot_publish(self):
        (self.artifact / "generation.bundle.json").unlink()
        with self.assertRaisesRegex(common.PipelineError, "generation bundle"):
            publish_pr.verify_artifact(self.artifact, self.root / "verified", signed=True)

    def test_assembly_signature_cannot_substitute_final_generation(self):
        self.sealed_manifest = copy.deepcopy(self.manifest)
        common.save_json(self.artifact / "generation.bundle.json", {"fixture_type": assembly_seal.ASSEMBLY_PREDICATE})
        with self.assertRaisesRegex(common.PipelineError, "statement type"):
            publish_pr.verify_artifact(self.artifact, self.root / "verified", signed=True)

    def test_generation_signature_cannot_substitute_assembly(self):
        self.sealed_manifest = copy.deepcopy(self.manifest)
        common.save_json(self.artifact / assembly_seal.ASSEMBLY_BUNDLE, {"fixture_type": common.PREDICATE})
        with self.assertRaisesRegex(common.PipelineError, "statement type"):
            self.verify()

    def test_production_missing_seal_fails(self):
        (self.artifact / assembly_seal.ASSEMBLY_BUNDLE).unlink()
        with self.assertRaisesRegex(common.PipelineError, "assembly signature"):
            self.verify()

    def test_modified_sdk_self_rehashed_after_sealing_is_rejected(self):
        self.sealed_manifest = copy.deepcopy(self.manifest)
        (self.repo / "client.go").write_text("package plaid\nconst ChangedAfterSeal = true\n")
        self.refresh_artifact()
        with self.assertRaisesRegex(common.PipelineError, "predicate differs"):
            self.verify()

    def test_seal_cannot_be_reused_for_another_workflow_source_or_run(self):
        for field in ("GITHUB_SHA", "GITHUB_RUN_ID"):
            with self.subTest(field=field), patch.dict(os.environ, {field: "0"}), self.assertRaisesRegex(common.PipelineError, "another workflow"):
                assembly_seal.require_context(self.manifest, self.plan)

    def test_unsigned_flag_cannot_weaken_production_request(self):
        self.plan["rehearsal"] = True
        (self.repo / hosted_contract.FERN_BUNDLE).unlink()
        (self.artifact / assembly_seal.ASSEMBLY_BUNDLE).unlink()
        self.refresh_artifact()
        with self.assertRaisesRegex(common.PipelineError, "actual workflow request"):
            self.verify()

    def test_rehearsal_requires_actual_manual_input_and_no_seal(self):
        event = json.loads(self.event.read_bytes())
        event["inputs"]["rehearsal"] = True
        common.save_json(self.event, event)
        self.plan["rehearsal"] = True
        (self.repo / hosted_contract.FERN_BUNDLE).unlink()
        (self.artifact / assembly_seal.ASSEMBLY_BUNDLE).unlink()
        self.refresh_artifact()
        self.verify()
        self.assertEqual(self.calls, [])
        common.save_json(self.artifact / assembly_seal.ASSEMBLY_BUNDLE, {"fixture_type": assembly_seal.ASSEMBLY_PREDICATE})
        with self.assertRaisesRegex(common.PipelineError, "Unsigned rehearsal"):
            assembly_seal.verify_assembly_artifact(self.artifact, self.root / "second")


if __name__ == "__main__":
    unittest.main()
