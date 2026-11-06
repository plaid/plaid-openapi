"""Real local signatures and filesystem tests; no Fern credentials or SDK runs."""
import base64
import copy
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import common
import fern_provenance as provenance


class DownloadFixture:
    def __init__(self, root):
        self.root, self.directory = Path(root), Path(root) / "download"
        self.directory.mkdir()
        self.key, self.public = self.root / "key.pem", self.root / "public.pem"
        provenance.command("openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", self.key)
        provenance.command("openssl", "pkey", "-in", self.key, "-pubout", "-out", self.public)
        self.public_key = self.public.read_bytes()
        self.pin = common.sha256(provenance.command("openssl", "pkey", "-pubin", "-in", self.public, "-outform", "DER"))
        generator = {"image": "fernapi/fern-go-sdk", "version": "1.70.3", "sha256": "a" * 64}
        names = ("fern:../2020-09-14.yml", "fern:openapi-overlay.yml", "fern:generators.yml", "fern:generators.yml#" + generator["image"])
        self.expected = {"job_id": "11111111-1111-1111-1111-111111111111", "sdk_version": "50.0.0", "cli_version": "5.193.2",
                         "generator": generator, "inputs": {name: common.sha256(name.encode()) for name in names}}
        self.metadata = {"sdkVersion": "v50.0.0", "cliVersion": "5.193.2", "generatorName": generator["image"], "generatorVersion": generator["version"],
                         "generatorConfig": {"module": {"path": "github.com/plaid/plaid-go/v50"}, "importPath": "github.com/plaid/plaid-go/v50"}}
        self.write(".fern/metadata.json", provenance.canonical(self.metadata))
        self.write("client/client.go", b"package client\n")
        self.write(provenance.RECEIPT_PATH, b"{}")
        tree = provenance.download_tree(provenance.read_download_files(self.directory))
        task = "22222222-2222-2222-2222-222222222222"
        self.statement = {"_type": "https://in-toto.io/Statement/v1", "predicateType": "https://slsa.dev/provenance/v1",
            "subject": [{"name": provenance.SUBJECT_NAME, "digest": {"gitTree": tree}}],
            "predicate": {"buildDefinition": {"buildType": provenance.BUILD_TYPE,
                "externalParameters": {"organization": "plaid", "api": "api", "generator": {key: generator[key] for key in ("image", "version")},
                                       "output": {"mode": "downloadFiles"}},
                "internalParameters": {"jobId": self.expected["job_id"], "taskId": task},
                "resolvedDependencies": [
                    {"uri": "docker://docker.io/fernapi/fern-go-sdk:1.70.3", "digest": {"sha256": generator["sha256"]}},
                    {"name": "fern:ir.json", "digest": {"sha256": "b" * 64}},
                    *[{"name": name, "digest": {"sha256": value}} for name, value in self.expected["inputs"].items()]]},
                "runDetails": {"builder": {"id": provenance.BUILDER_ID},
                    "metadata": {"invocationId": self.expected["job_id"] + "/" + task, "finishedOn": "2026-01-02T03:04:05.123456789Z"}}}}
        self.sign()

    def write(self, name, data):
        target = self.directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def sign(self, statement=None, payload=None):
        payload = payload if payload is not None else provenance.canonical(self.statement if statement is None else statement)
        kind, path = provenance.PAYLOAD_TYPE.encode(), self.root / "pae"
        path.write_bytes(b"DSSEv1 %d %s %d %s" % (len(kind), kind, len(payload), payload))
        signature = provenance.command("openssl", "dgst", "-sha256", "-sign", self.key, path)
        self.envelope = {"payloadType": provenance.PAYLOAD_TYPE, "payload": base64.b64encode(payload).decode(),
                         "signatures": [{"keyid": "opaque-signer-reference", "sig": base64.b64encode(signature).decode()}]}
        self.write(provenance.RECEIPT_PATH, provenance.canonical(self.envelope))

    def verify(self):
        return provenance._verify_download(self.directory, self.public_key, self.expected, key_sha256=self.pin)


class FernDownloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="fern-download-local-test-")
        self.addCleanup(self.temporary.cleanup)
        self.fixture = DownloadFixture(self.temporary.name)

    def test_portable_receipt_preserves_signed_bytes_and_reverifies(self):
        result = self.fixture.verify()
        portable = provenance.parse_json(result["receipt"])
        self.assertEqual(set(portable), {"payloadType", "payload", "signatures"})
        self.assertEqual(portable["payload"], self.fixture.envelope["payload"])
        self.assertEqual(portable["signatures"], [{"sig": self.fixture.envelope["signatures"][0]["sig"]}])
        self.assertEqual(provenance.canonical(portable), result["receipt"])
        self.assertNotIn(b"opaque-signer-reference", result["receipt"])
        self.assertEqual(result["summary"]["receipt_sha256"], common.sha256(result["receipt"]))
        self.assertNotIn("git_commit", result["summary"])
        self.assertEqual(result["summary"]["output_mode"], "downloadFiles")
        self.fixture.write(provenance.RECEIPT_PATH, result["receipt"])
        self.assertEqual(self.fixture.verify(), result)

    def test_public_api_never_accepts_local_signer(self):
        with self.assertRaisesRegex(common.PipelineError, "pinned key"):
            provenance.verify_download(self.fixture.directory, self.fixture.public_key, self.fixture.expected)

    def test_edits_additions_and_deletions_change_the_full_tree(self):
        target = self.fixture.directory / "client/client.go"
        original = target.read_bytes()
        target.write_bytes(original + b"// changed\n")
        with self.assertRaisesRegex(common.PipelineError, "tree differs"):
            self.fixture.verify()
        target.unlink()
        with self.assertRaisesRegex(common.PipelineError, "tree differs"):
            self.fixture.verify()
        target.write_bytes(original)
        self.fixture.write(".github/extra.yml", b"name: extra\n")
        with self.assertRaisesRegex(common.PipelineError, "tree differs"):
            self.fixture.verify()

    def test_tree_matches_git_normalized_modes_and_ignores_empty_directories(self):
        self.fixture.write("alpha.beta", b"fixture\n")
        self.fixture.write("alpha/file.go", b"package alpha\n")
        (self.fixture.directory / "empty").mkdir()
        (self.fixture.directory / "client/client.go").chmod(0o755)
        files = provenance.read_download_files(self.fixture.directory)
        actual = provenance.download_tree(files)
        git_dir = self.fixture.root / "git-comparison"
        shutil.copytree(self.fixture.directory, git_dir)
        (git_dir / provenance.RECEIPT_PATH).unlink()
        common.git(git_dir, "init", "-q")
        common.git(git_dir, "-c", "core.fileMode=false", "add", "-A", "-f")
        self.assertEqual(common.git(git_dir, "write-tree"), actual)

    def test_links_and_git_metadata_are_rejected(self):
        self.fixture.write("outside-target", b"fixture")
        link = self.fixture.directory / "link.go"
        for directory in (False, True):
            link.symlink_to(self.fixture.directory / ("client" if directory else "outside-target"), target_is_directory=directory)
            with self.subTest(directory=directory), self.assertRaises(common.PipelineError):
                self.fixture.verify()
            link.unlink()
        os.link(self.fixture.directory / "outside-target", link)
        with self.assertRaises(common.PipelineError):
            self.fixture.verify()
        link.unlink()
        (self.fixture.directory / "outside-target").unlink()
        for name in (".git/config", "nested/.git/config", "nested/.GIT/config"):
            self.fixture.write(name, b"fixture")
            with self.subTest(name=name), self.assertRaises(common.PipelineError):
                self.fixture.verify()
            (self.fixture.directory / name).unlink()
            (self.fixture.directory / name).parent.rmdir()

    def test_scanner_bounds_and_unsafe_paths(self):
        with patch.object(provenance, "MAX_FILE", 1), self.assertRaises(common.PipelineError):
            self.fixture.verify()
        with patch.object(provenance, "MAX_DOWNLOAD", 1), self.assertRaises(common.PipelineError):
            self.fixture.verify()
        for name in ("../escape.go", "/absolute.go", "nested/../escape.go"):
            with self.subTest(name=name), self.assertRaises(common.PipelineError):
                provenance.download_tree({name: b"fixture"})
        self.fixture.write("bad\\name.go", b"fixture")
        with self.assertRaises(common.PipelineError):
            self.fixture.verify()

    def test_missing_changed_or_duplicate_signed_inputs(self):
        original = self.fixture.statement["predicate"]["buildDefinition"]["resolvedDependencies"]
        for name in [*self.fixture.expected["inputs"], "fern:ir.json"]:
            for action in ("missing", "duplicate", "changed"):
                if name == "fern:ir.json" and action == "changed":
                    continue
                statement = copy.deepcopy(self.fixture.statement)
                dependencies = statement["predicate"]["buildDefinition"]["resolvedDependencies"]
                item = next(item for item in dependencies if item.get("name") == name)
                if action == "missing":
                    dependencies.remove(item)
                elif action == "duplicate":
                    dependencies.append(copy.deepcopy(item))
                else:
                    item["digest"]["sha256"] = "c" * 64
                self.fixture.sign(statement)
                with self.subTest(name=name, action=action), self.assertRaises(common.PipelineError):
                    self.fixture.verify()
        self.assertEqual(self.fixture.statement["predicate"]["buildDefinition"]["resolvedDependencies"], original)

    def test_expected_ir_is_checked_when_present(self):
        self.fixture.expected["inputs"]["fern:ir.json"] = "b" * 64
        self.fixture.verify()
        self.fixture.expected["inputs"]["fern:ir.json"] = "c" * 64
        with self.assertRaises(common.PipelineError):
            self.fixture.verify()

    def test_generator_digest_builder_job_and_subject_are_bound(self):
        mutations = [
            lambda s: s["subject"][0].update(name="unexpected"),
            lambda s: s["subject"][0]["digest"].update(gitCommit="0" * 40),
            lambda s: s["predicate"]["buildDefinition"].update(buildType="unexpected"),
            lambda s: s["predicate"]["runDetails"]["builder"].update(id="unexpected"),
            lambda s: s["predicate"]["buildDefinition"]["internalParameters"].update(jobId="33333333-3333-3333-3333-333333333333"),
            lambda s: s["predicate"]["buildDefinition"]["externalParameters"]["generator"].update(version="9.0.0"),
            lambda s: s["predicate"]["buildDefinition"]["externalParameters"]["output"].update(mode="github"),
            lambda s: s["predicate"]["buildDefinition"]["resolvedDependencies"][0]["digest"].update(sha256="0" * 64),
            lambda s: s["predicate"]["buildDefinition"]["resolvedDependencies"].append(copy.deepcopy(s["predicate"]["buildDefinition"]["resolvedDependencies"][0])),
        ]
        for index, mutate in enumerate(mutations):
            statement = copy.deepcopy(self.fixture.statement)
            mutate(statement)
            self.fixture.sign(statement)
            with self.subTest(index=index), self.assertRaises(common.PipelineError):
                self.fixture.verify()

    def test_unexpected_signed_fields_cannot_be_published(self):
        paths = [[], ["predicate"], ["subject", 0], ["subject", 0, "digest"], ["predicate", "buildDefinition"],
                 ["predicate", "buildDefinition", "externalParameters"], ["predicate", "buildDefinition", "internalParameters"],
                 ["predicate", "runDetails"], ["predicate", "runDetails", "builder"], ["predicate", "runDetails", "metadata"],
                 ["predicate", "buildDefinition", "resolvedDependencies", 0]]
        for path in paths:
            statement = copy.deepcopy(self.fixture.statement)
            current = statement
            for key in path:
                current = current[key]
            current["unexpected"] = "opaque-private-reference"
            self.fixture.sign(statement)
            with self.subTest(path=path), self.assertRaises(common.PipelineError) as failure:
                self.fixture.verify()
            self.assertNotIn("opaque-private-reference", str(failure.exception))

    def test_bad_timestamps_or_unknown_dependency_names_rejected(self):
        for timestamp in ("opaque-private-reference", "2026-02-31T03:04:05Z", "2026-01-02T03:04:05Z extra"):
            statement = copy.deepcopy(self.fixture.statement)
            statement["predicate"]["runDetails"]["metadata"]["finishedOn"] = timestamp
            self.fixture.sign(statement)
            with self.subTest(timestamp=timestamp), self.assertRaises(common.PipelineError):
                self.fixture.verify()
        self.fixture.expected["inputs"]["fern:private-spec.yml"] = "c" * 64
        with self.assertRaises(common.PipelineError):
            self.fixture.verify()

    def test_signature_and_payload_tampering_or_noncanonical_encoding_rejected(self):
        for field in ("payload", "sig"):
            envelope = copy.deepcopy(self.fixture.envelope)
            target = envelope if field == "payload" else envelope["signatures"][0]
            value = bytearray(base64.b64decode(target[field]))
            value[-1] ^= 1
            target[field] = base64.b64encode(value).decode()
            self.fixture.write(provenance.RECEIPT_PATH, provenance.canonical(envelope))
            with self.subTest(field=field), self.assertRaises(common.PipelineError):
                self.fixture.verify()
        signature = base64.b64decode(self.fixture.envelope["signatures"][0]["sig"])
        with self.assertRaises(common.PipelineError):
            provenance.validate_signature_encoding(signature + b"opaque-extra-data")
        with self.assertRaises(common.PipelineError):
            provenance.decode_base64("Zh==")  # Decodes like Zg== but has nonzero unused bits.

    def test_duplicate_json_keys_and_unknown_envelope_fields_rejected(self):
        for raw in (b'{"payload":"a","payload":"b"}', b'{"payload":NaN}'):
            self.fixture.write(provenance.RECEIPT_PATH, raw)
            with self.assertRaises(common.PipelineError):
                self.fixture.verify()
        self.fixture.sign(payload=b'{"_type":"one","_type":"two"}')
        with self.assertRaises(common.PipelineError):
            self.fixture.verify()
        self.fixture.sign()
        envelope = {**self.fixture.envelope, "unexpected": "opaque-private-reference"}
        self.fixture.write(provenance.RECEIPT_PATH, provenance.canonical(envelope))
        with self.assertRaises(common.PipelineError):
            self.fixture.verify()

    def test_signed_metadata_requires_expected_cli_sdk_and_module(self):
        for field, value in (("sdkVersion", "v99.0.0"), ("cliVersion", "9.0.0"), ("generatorVersion", "9.0.0")):
            metadata = {**self.fixture.metadata, field: value}
            self.fixture.write(".fern/metadata.json", provenance.canonical(metadata))
            statement = copy.deepcopy(self.fixture.statement)
            statement["subject"][0]["digest"]["gitTree"] = provenance.download_tree(provenance.read_download_files(self.fixture.directory))
            self.fixture.sign(statement)
            with self.subTest(field=field), self.assertRaisesRegex(common.PipelineError, "metadata"):
                self.fixture.verify()
        metadata = copy.deepcopy(self.fixture.metadata)
        metadata["generatorConfig"]["module"]["path"] = "github.com/example/wrong"
        self.fixture.write(".fern/metadata.json", provenance.canonical(metadata))
        statement = copy.deepcopy(self.fixture.statement)
        statement["subject"][0]["digest"]["gitTree"] = provenance.download_tree(provenance.read_download_files(self.fixture.directory))
        self.fixture.sign(statement)
        with self.assertRaisesRegex(common.PipelineError, "metadata"):
            self.fixture.verify()


if __name__ == "__main__":
    unittest.main()
