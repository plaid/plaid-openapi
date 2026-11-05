"""Public Fern handoff linkage; only the gh verification process is mocked."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import attestation
import common
import hosted_contract as hosted


def record_fixture(manifest=None, *, sdk_base="b" * 40, index=None):
    """Build a public-safe synthetic record; callers may supply their manifest/index."""
    index = index if index is not None else common.canonical([
        [".fern/metadata.json", "100644", "1" * 64], ["client/client.go", "100644", "2" * 64]])
    record = {"schema_version": 1, "sdk_version": "50.0.0",
        "source": {"repository": attestation.SPEC_REPO, "commit": "a" * 40, "path": "2020-09-14.yml", "sha256": "c" * 64},
        "config": {"repository": attestation.CONFIG_REPO, "commit": "a" * 40, "sha256": "d" * 64},
        "sdk_base": sdk_base, "generator": {"image": "fernapi/fern-go-sdk", "version": "1.70.3", "sha256": "e" * 64},
        "cli": {"version": "5.193.2", "sha256": "f" * 64},
        "evidence": {"receipt_sha256": "1" * 64, "key_sha256": hosted.FERN_KEY_SHA256,
                     "git_commit": "2" * 40, "git_tree": "3" * 40, "inputs_sha256": "4" * 64, "job_id_sha256": "5" * 64},
        "content_sha256": common.sha256(index),
        "generation": {"repository": attestation.CONFIG_REPO, "workflow": attestation.GEN_WORKFLOW, "run_id": "123"}}
    if manifest is not None:
        record.update(sdk_version=manifest["sdk"]["version"],
                      **{name: copy.deepcopy(manifest[name]) for name in ("source", "config", "generation")})
        record["cli"] = {"version": manifest["generator"]["cli_version"], "sha256": manifest["generator"]["cli_sha256"]}
        record["generator"]["sha256"] = manifest["generator"]["image_digest"].removeprefix("sha256:")
    return record


def manifest_fixture(record=None):
    record = record or record_fixture()
    return {"schema_version": 2, "sdk": {"repository": attestation.SDK_REPO, "version": record["sdk_version"],
            "module": "github.com/plaid/plaid-go/v" + record["sdk_version"].split(".")[0]},
        **{name: copy.deepcopy(record[name]) for name in ("source", "config", "generation")},
        "generator": {"cli_version": record["cli"]["version"], "cli_sha256": record["cli"]["sha256"],
                      "image_digest": "sha256:" + record["generator"]["sha256"]},
        "legacy": {"source_commit": "a" * 40, "spec_sha256": record["source"]["sha256"],
                   "tree_sha256": "b" * 64, "generator_digest": "sha256:" + "c" * 64},
        "content_sha256": "d" * 64, "fern": record}


def verification_fixture(record):
    identity = f"https://github.com/{attestation.CONFIG_REPO}/{attestation.GEN_WORKFLOW}@refs/heads/master"
    certificate = {"subjectAlternativeName": identity, "issuer": "https://token.actions.githubusercontent.com",
        "buildSignerURI": identity, "buildSignerDigest": record["config"]["commit"],
        "sourceRepositoryURI": "https://github.com/" + attestation.CONFIG_REPO,
        "sourceRepositoryDigest": record["config"]["commit"], "sourceRepositoryRef": "refs/heads/master",
        "runnerEnvironment": "github-hosted", "sourceRepositoryVisibilityAtSigning": "public",
        "runInvocationURI": f"https://github.com/{attestation.CONFIG_REPO}/actions/runs/{record['generation']['run_id']}"}
    return [{"verificationResult": {"signature": {"certificate": certificate}, "verifiedTimestamps": [{"type": "fixture"}],
        "statement": {"_type": "https://in-toto.io/Statement/v1", "predicateType": hosted.FERN_PREDICATE,
                      "predicate": copy.deepcopy(record), "subject": [{"name": "plaid-go-v" + record["sdk_version"] + "-fern-source",
                      "digest": {"sha256": record["content_sha256"]}}]}}}]


class HostedContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.index = common.canonical([[".fern/metadata.json", "100644", "1" * 64], ["client/client.go", "100644", "2" * 64]])
        self.record = record_fixture(index=self.index)
        self.manifest = manifest_fixture(self.record)
        self.index_path, self.bundle = self.root / "index.json", self.root / "bundle.json"
        self.index_path.write_bytes(self.index)
        self.bundle.write_text('{"fixture": "not a signature"}')

    def test_schema2_links_every_input(self):
        self.assertEqual(attestation.validate_manifest(self.manifest), self.manifest)
        changes = [("sdk_version", "50.1.0"), ("source", {**self.record["source"], "sha256": "0" * 64}),
                   ("config", {**self.record["config"], "sha256": "0" * 64}),
                   ("generation", {**self.record["generation"], "run_id": "999"}),
                   ("cli", {**self.record["cli"], "version": "9.0.0"}),
                   ("generator", {**self.record["generator"], "sha256": "0" * 64})]
        for field, value in changes:
            manifest = copy.deepcopy(self.manifest)
            manifest["fern"][field] = value
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                attestation.validate_manifest(manifest)

    def test_schema1_historical_fallback_and_downgrade_guard(self):
        local = copy.deepcopy(self.manifest)
        local["schema_version"] = 1
        del local["fern"]
        attestation.validate_manifest(local)
        hosted.validate_generation_mode(local, {})
        hosted.validate_generation_mode(local, {"generation_mode": "local"})
        with self.assertRaisesRegex(common.PipelineError, "reviewed generation mode"):
            hosted.validate_generation_mode(local, {"generation_mode": "fern-hosted"})
        with self.assertRaises(common.PipelineError):
            hosted.validate_generation_mode(self.manifest, {})

    def test_hosted_mode_checks_reviewed_settings(self):
        generator = self.record["generator"]
        settings = {"generation_mode": "fern-hosted", "generator_image": generator["image"],
                    "generator_version": generator["version"], "generator_digest": "sha256:" + generator["sha256"],
                    "cli_version": self.record["cli"]["version"], "cli_sha256": self.record["cli"]["sha256"]}
        hosted.validate_generation_mode(self.manifest, settings)
        for field in settings:
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                hosted.validate_generation_mode(self.manifest, {**settings, field: "unexpected"})

    def test_missing_or_private_record_fields_and_wrong_key_rejected(self):
        for field in self.record:
            record = copy.deepcopy(self.record)
            del record[field]
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                hosted.validate_fern_record(record)
        for extra in ("repository_url", "branch", "receipt"):
            with self.subTest(extra=extra), self.assertRaises(common.PipelineError):
                hosted.validate_fern_record({**self.record, extra: "not public"})
        record = copy.deepcopy(self.record)
        record["evidence"]["key_sha256"] = "0" * 64
        with self.assertRaisesRegex(common.PipelineError, "signing key"):
            hosted.validate_fern_record(record)

    def test_index_requires_exact_hash_canonical_paths_and_modes(self):
        hosted.validate_fern_index(self.index, self.record)
        with self.assertRaisesRegex(common.PipelineError, "index differs"):
            hosted.validate_fern_index(self.index + b"\n", self.record)
        original = json.loads(self.index)
        cases = [original + [original[0]], list(reversed(original)), [original[0]],
                 [[".fern/metadata.json", "100755", "1" * 64], original[1]]]
        for path in ("go.mod", "go.sum", "scripts/run.go", "legacy/client.go", "internal/caller.go",
                     "wiremock/docker-compose.test.yml", "../secret.go", ".sdk-release/extra.json"):
            cases.append(sorted(original + [[path, "100644", "3" * 64]]))
        for index in cases:
            data = common.canonical(index)
            record = {**self.record, "content_sha256": common.sha256(data)}
            with self.subTest(index=index), self.assertRaises(common.PipelineError):
                hosted.validate_fern_index(data, record)

    def test_evidence_requires_exact_gha_signature_identity_and_subject(self):
        result = verification_fixture(self.record)
        with patch.object(attestation, "run", return_value=common.canonical(result)) as command:
            hosted.verify_fern_evidence(self.index_path, self.bundle, self.record)
        self.assertIn("--source-digest", command.call_args.args)
        self.assertIn(hosted.FERN_PREDICATE, command.call_args.args)
        self.assertNotIn("--no-public-good", command.call_args.args)
        for field, replacement in (("runInvocationURI", "https://github.com/plaid/plaid-openapi/actions/runs/999"),
                                   ("sourceRepositoryDigest", "0" * 40), ("sourceRepositoryVisibilityAtSigning", "private")):
            bad = copy.deepcopy(result)
            bad[0]["verificationResult"]["signature"]["certificate"][field] = replacement
            with self.subTest(field=field), patch.object(attestation, "run", return_value=common.canonical(bad)), self.assertRaises(common.PipelineError):
                hosted.verify_fern_evidence(self.index_path, self.bundle, self.record)
        bad = copy.deepcopy(result)
        bad[0]["verificationResult"]["statement"]["subject"][0]["digest"]["sha256"] = "0" * 64
        with patch.object(attestation, "run", return_value=common.canonical(bad)), self.assertRaises(common.PipelineError):
            hosted.verify_fern_evidence(self.index_path, self.bundle, self.record)
        with patch.object(attestation, "run", side_effect=common.PipelineError("Signature rejected")), self.assertRaises(common.PipelineError):
            hosted.verify_fern_evidence(self.index_path, self.bundle, self.record)
        self.bundle.unlink()
        with self.assertRaisesRegex(common.PipelineError, "signature"):
            hosted.verify_fern_evidence(self.index_path, self.bundle, self.record)


if __name__ == "__main__":
    unittest.main()
