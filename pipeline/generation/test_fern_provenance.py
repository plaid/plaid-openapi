"""Cryptographic boundary tests use ephemeral local signers, never Fern credentials."""
import base64
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zlib

import common
import fern_provenance as provenance


class SignedFixture:
    """Reusable local receipt/SDK fixture for retrieval and verifier tests."""
    def __init__(self, root):
        self.root, self.sdk = Path(root), Path(root) / "sdk"
        self.key_path, self.public_path = self.root / "key.pem", self.root / "public.pem"
        provenance.command("openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", self.key_path)
        provenance.command("openssl", "pkey", "-in", self.key_path, "-pubout", "-out", self.public_path)
        self.public_key = self.public_path.read_bytes()
        self.key_pin = common.sha256(provenance.command("openssl", "pkey", "-pubin", "-in", self.public_path, "-outform", "DER"))
        self.sdk.mkdir()
        common.git(self.sdk, "init", "-q")
        self.metadata = {"sdkVersion": "v50.0.0", "generatorName": "fernapi/fern-go-sdk", "generatorVersion": "1.70.3"}
        (self.sdk / ".fern").mkdir()
        (self.sdk / ".fern/metadata.json").write_text(json.dumps(self.metadata))
        (self.sdk / "client.go").write_text("package sdk\n")
        self.commit = self.commit_files()
        self.tree = common.git(self.sdk, "rev-parse", "HEAD^{tree}")
        generator = {"image": "fernapi/fern-go-sdk", "version": "1.70.3", "sha256": "a" * 64}
        names = ("fern:../spec.yml", "fern:openapi-overlay.yml", "fern:generators.yml", "fern:generators.yml#" + generator["image"])
        self.expected = {"repository": "https://github.com/example/sdk-staging", "job_id": "11111111-1111-1111-1111-111111111111",
                         "sdk_version": "50.0.0", "generator": generator,
                         "inputs": {name: common.sha256(name.encode()) for name in names}}
        task = "22222222-2222-2222-2222-222222222222"
        self.statement = {"_type": "https://in-toto.io/Statement/v1", "predicateType": "https://slsa.dev/provenance/v1",
            "subject": [{"name": self.expected["repository"], "digest": {"gitTree": self.tree, "gitCommit": self.commit}}],
            "predicate": {"buildDefinition": {
                "buildType": provenance.BUILD_TYPE,
                "externalParameters": {"generator": {key: generator[key] for key in ("image", "version")},
                                       "output": {"repository": self.expected["repository"], "branch": "fixture-branch"}},
                "internalParameters": {"jobId": self.expected["job_id"], "taskId": task},
                "resolvedDependencies": [
                    {"uri": "docker://docker.io/fernapi/fern-go-sdk:1.70.3", "digest": {"sha256": generator["sha256"]}},
                    {"name": "fern:ir.json", "digest": {"sha256": "b" * 64}},
                    *[{"name": name, "digest": {"sha256": digest}} for name, digest in self.expected["inputs"].items()]]},
                "runDetails": {"builder": {"id": provenance.BUILDER_ID},
                               "metadata": {"invocationId": self.expected["job_id"] + "/" + task}}}}

    def commit_files(self):
        common.git(self.sdk, "add", "-A")
        common.git(self.sdk, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                   "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "Fixture")
        return common.git(self.sdk, "rev-parse", "HEAD")

    def receipt(self, statement=None):
        return self.sign_payload(common.canonical(self.statement if statement is None else statement))

    def sign_payload(self, payload):
        kind = provenance.PAYLOAD_TYPE.encode()
        path = self.root / "pae"
        path.write_bytes(b"DSSEv1 %d %s %d %s" % (len(kind), kind, len(payload), payload))
        signature = provenance.command("openssl", "dgst", "-sha256", "-sign", self.key_path, path)
        return common.canonical({"payloadType": provenance.PAYLOAD_TYPE, "payload": base64.b64encode(payload).decode(),
                                 "signatures": [{"keyid": "local-fixture", "sig": base64.b64encode(signature).decode()}]})

    def verify(self, receipt=None):
        return provenance._verify(self.receipt() if receipt is None else receipt, self.public_key, self.sdk,
                                  self.commit, self.expected, key_sha256=self.key_pin)


class FernProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="fern-local-signer-test-")
        self.addCleanup(self.temporary.cleanup)
        self.fixture = SignedFixture(self.temporary.name)

    def mutate(self, path, value):
        statement = copy.deepcopy(self.fixture.statement)
        cursor = statement
        for component in path[:-1]:
            cursor = cursor[component]
        cursor[path[-1]] = value
        return self.fixture.receipt(statement)

    def test_summary_verifies_signature_and_omits_private_identities(self):
        fixture = self.fixture
        receipt = fixture.receipt()
        summary = fixture.verify(receipt)
        self.assertEqual(summary["receipt_sha256"], common.sha256(receipt))
        self.assertEqual(summary["git_tree"], fixture.tree)
        self.assertEqual(summary["git_commit"], fixture.commit)
        self.assertEqual(summary["job_id_sha256"], common.sha256(fixture.expected["job_id"].encode()))
        self.assertEqual(summary["inputs_sha256"], common.sha256(common.canonical(dict(sorted(fixture.expected["inputs"].items())))))
        encoded = json.dumps(summary)
        for identity in [fixture.expected["repository"], fixture.expected["job_id"], "fixture-branch", "fern:../spec.yml"]:
            self.assertNotIn(identity, encoded)
        self.assertEqual(set(summary), {"schema_version", "receipt_sha256", "key_sha256", "git_commit", "git_tree",
                                       "sdk_version", "generator", "inputs_sha256", "job_id_sha256"})

    def test_public_api_rejects_local_test_key(self):
        fixture = self.fixture
        with self.assertRaisesRegex(common.PipelineError, "pinned key"):
            provenance.verify(fixture.receipt(), fixture.public_key, fixture.sdk, fixture.commit, fixture.expected)

    def test_each_missing_changed_or_duplicate_input_rejected(self):
        original = self.fixture.statement["predicate"]["buildDefinition"]["resolvedDependencies"]
        for name in [*self.fixture.expected["inputs"], "fern:ir.json"]:
            for mutation in ("missing", "duplicate", "changed"):
                if name == "fern:ir.json" and mutation == "changed":
                    continue  # We record IR; equality requires a caller-supplied expected IR hash.
                dependencies = copy.deepcopy(original)
                entry = next(item for item in dependencies if item.get("name") == name)
                if mutation == "missing":
                    dependencies.remove(entry)
                elif mutation == "duplicate":
                    dependencies.append(copy.deepcopy(entry))
                else:
                    entry["digest"]["sha256"] = "c" * 64
                with self.subTest(input=name, mutation=mutation), self.assertRaises(common.PipelineError):
                    self.fixture.verify(self.mutate(["predicate", "buildDefinition", "resolvedDependencies"], dependencies))

    def test_optional_expected_ir_is_checked(self):
        self.fixture.expected["inputs"]["fern:ir.json"] = "b" * 64
        self.fixture.verify()
        self.fixture.expected["inputs"]["fern:ir.json"] = "c" * 64
        with self.assertRaisesRegex(common.PipelineError, "inputs"):
            self.fixture.verify()

    def test_unexpected_dependency_and_duplicate_image_rejected(self):
        original = self.fixture.statement["predicate"]["buildDefinition"]["resolvedDependencies"]
        for extra in ({"name": "fern:unknown.yml", "digest": {"sha256": "c" * 64}}, original[0]):
            with self.subTest(extra=extra), self.assertRaises(common.PipelineError):
                self.fixture.verify(self.mutate(["predicate", "buildDefinition", "resolvedDependencies"], original + [extra]))

    def test_generator_and_image_digest_must_match(self):
        paths = [(["predicate", "buildDefinition", "externalParameters", "generator", "image"], "fernapi/fern-other-sdk"),
                 (["predicate", "buildDefinition", "externalParameters", "generator", "version"], "9.0.0"),
                 (["predicate", "buildDefinition", "resolvedDependencies", 0, "uri"], "docker://other:1.0.0"),
                 (["predicate", "buildDefinition", "resolvedDependencies", 0, "digest", "sha256"], "c" * 64)]
        for path, value in paths:
            with self.subTest(path=path), self.assertRaises(common.PipelineError):
                self.fixture.verify(self.mutate(path, value))

    def test_builder_and_build_type_must_match(self):
        for path in (["predicate", "buildDefinition", "buildType"], ["predicate", "runDetails", "builder", "id"]):
            with self.subTest(path=path), self.assertRaisesRegex(common.PipelineError, "builder"):
                self.fixture.verify(self.mutate(path, "https://example.invalid/untrusted"))

    def test_job_and_invocation_must_match_launch(self):
        paths = [["predicate", "buildDefinition", "internalParameters", "jobId"],
                 ["predicate", "buildDefinition", "internalParameters", "taskId"],
                 ["predicate", "runDetails", "metadata", "invocationId"]]
        for path in paths:
            with self.subTest(path=path), self.assertRaisesRegex(common.PipelineError, "job"):
                self.fixture.verify(self.mutate(path, "33333333-3333-3333-3333-333333333333"))

    def test_subject_and_output_repository_must_match(self):
        for path in (["subject", 0, "name"], ["predicate", "buildDefinition", "externalParameters", "output", "repository"]):
            with self.subTest(path=path), self.assertRaisesRegex(common.PipelineError, "repository"):
                self.fixture.verify(self.mutate(path, "https://github.com/example/other"))

    def test_signed_commit_and_tree_must_match_local_objects(self):
        for field in ("gitCommit", "gitTree"):
            with self.subTest(field=field), self.assertRaisesRegex(common.PipelineError, "commit"):
                self.fixture.verify(self.mutate(["subject", 0, "digest", field], "0" * 40))

    def test_raw_tree_bytes_must_match_signed_object_hash(self):
        fixture = self.fixture
        path = fixture.sdk / ".git/objects" / fixture.tree[:2] / fixture.tree[2:]
        data = provenance.git_object(fixture.sdk, "tree", fixture.tree) + b"100644 extra\0" + bytes.fromhex("0" * 40)
        path.chmod(0o600)
        path.write_bytes(zlib.compress(b"tree " + str(len(data)).encode() + b"\0" + data))
        with self.assertRaisesRegex(common.PipelineError, "object does not match"):
            fixture.verify()

    def test_git_replace_does_not_change_verified_bytes(self):
        fixture = self.fixture
        (fixture.sdk / "client.go").write_text("package changed\n")
        second = fixture.commit_files()
        common.git(fixture.sdk, "replace", fixture.commit, second)
        self.assertEqual(fixture.verify()["git_tree"], fixture.tree)

    def test_metadata_version_and_generator_must_match(self):
        fixture = self.fixture
        for field, value in (("sdkVersion", "v99.0.0"), ("generatorName", "fernapi/fern-other-sdk"), ("generatorVersion", "99.0.0")):
            metadata = {**fixture.metadata, field: value}
            (fixture.sdk / ".fern/metadata.json").write_text(json.dumps(metadata))
            fixture.commit = fixture.commit_files()
            fixture.tree = common.git(fixture.sdk, "rev-parse", "HEAD^{tree}")
            fixture.statement["subject"][0]["digest"] = {"gitCommit": fixture.commit, "gitTree": fixture.tree}
            with self.subTest(field=field), self.assertRaisesRegex(common.PipelineError, "metadata"):
                fixture.verify()

    def test_tampered_payload_and_signature_rejected(self):
        for field in ("payload", "sig"):
            envelope = json.loads(self.fixture.receipt())
            target = envelope if field == "payload" else envelope["signatures"][0]
            data = bytearray(base64.b64decode(target[field]))
            data[-1] ^= 1
            target[field] = base64.b64encode(data).decode()
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                self.fixture.verify(common.canonical(envelope))

    def test_duplicate_json_keys_and_non_json_values_rejected(self):
        for raw in (b'{"payload": "a", "payload": "b"}', b'{"payload": NaN}'):
            with self.subTest(raw=raw), self.assertRaises(common.PipelineError):
                self.fixture.verify(raw)
        with self.assertRaises(common.PipelineError):
            self.fixture.verify(self.fixture.sign_payload(b'{"_type": "one", "_type": "two"}'))

    def test_wrong_statement_and_payload_types_rejected(self):
        for field in ("_type", "predicateType"):
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                self.fixture.verify(self.mutate([field], "unexpected"))
        envelope = json.loads(self.fixture.receipt())
        envelope["payloadType"] = "application/json"
        with self.assertRaises(common.PipelineError):
            self.fixture.verify(common.canonical(envelope))

    def test_omitted_expected_inputs_never_weakens_policy(self):
        for name in list(self.fixture.expected["inputs"]):
            value = self.fixture.expected["inputs"].pop(name)
            with self.subTest(name=name), self.assertRaisesRegex(common.PipelineError, "Trusted Fern inputs"):
                self.fixture.verify()
            self.fixture.expected["inputs"][name] = value

    def test_malformed_records_fail_without_echoing_input(self):
        secret_marker = "EXAMPLE_PRIVATE_VALUE"
        for value in (None, [secret_marker], secret_marker, {secret_marker: secret_marker}):
            with self.subTest(value=value), self.assertRaises(common.PipelineError) as failure:
                self.fixture.verify(self.fixture.sign_payload(common.canonical(value)))
            self.assertNotIn(secret_marker, str(failure.exception))


if __name__ == "__main__":
    unittest.main()
