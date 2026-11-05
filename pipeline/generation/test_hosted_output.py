import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import common
import hosted_output


class HostedOutputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hosted-output-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo, self.out = self.root / "repo", self.root / "out"
        self.repo.mkdir()
        self.out.mkdir()
        common.git(self.repo, "init", "-q")
        self.ignore = b"go.mod\ngo.sum\ninternal/caller.go\nlegacy/\n.github/\nREADME.md\n"
        self.settings = {"cli_version": "5.193.2", "generator_image": "fernapi/fern-go-sdk", "generator_version": "1.70.3"}
        self.write(".fernignore", self.ignore)
        self.write("go.mod", b"module github.com/example/private-sdk/v49\n")
        self.write("go.sum", b"private baseline module data\n")
        self.write("client.go", b"package plaid\n// previous client\n")
        self.write("internal/caller.go", b"package internal\n// maintained\n")
        self.write("legacy/client.go", b"package legacy\n")
        self.write("README.md", b"Private SDK staging instructions\n")
        self.write(".github/workflows/ci.yml", b"name: private-workflow\n")
        self.write(".fern/metadata.json", b'{"sdkVersion":"v49.0.0"}')
        self.base = self.commit()
        self.public_paths = {"go.mod", "go.sum", "client.go", "internal/caller.go", ".fern/metadata.json"}
        self.metadata = {"cliVersion": "5.193.2", "generatorName": "fernapi/fern-go-sdk", "generatorVersion": "1.70.3",
                         "sdkVersion": "v50.0.0", "originGitCommit": self.base,
                         "privateDetail": "https://github.com/example/private-sdk",
                         "generatorConfig": {"module": {"path": "github.com/plaid/plaid-go/v50"},
                                             "importPath": "github.com/plaid/plaid-go/v50", "maxRetries": 0}}
        self.candidate()

    def write(self, name, data):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def commit(self):
        common.git(self.repo, "add", "-A")
        common.git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                   "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "Fixture")
        return common.git(self.repo, "rev-parse", "HEAD")

    def candidate(self):
        self.write(".fern/metadata.json", json.dumps(self.metadata).encode())
        self.write("client.go", b"package plaid\n// fresh generated client\n")
        self.write("new/client.go", b"package new\n")
        self.head = self.commit()

    def export(self, **kwargs):
        return hosted_output.export_verified_output(repo=self.repo, base=self.base, commit=self.head,
            public_ignore=self.ignore, public_paths=self.public_paths, version="50.0.0", settings=self.settings,
            output=self.out, private_repository="example/private-sdk", **kwargs)

    def test_export_is_generated_only_and_metadata_is_public(self):
        result = self.export()
        index = (self.out / "fern-content.json").read_bytes()
        self.assertEqual(result, common.sha256(index))
        self.assertEqual([row[0] for row in json.loads(index)], [".fern/metadata.json", "client.go", "new/client.go"])
        with tarfile.open(self.out / "fern-output.tar.gz") as archive:
            metadata = json.load(archive.extractfile(".fern/metadata.json"))
            self.assertEqual(set(metadata), {"cliVersion", "generatorName", "generatorVersion", "sdkVersion"})
            self.assertTrue(all(entry.isfile() and entry.mode == 0o644 for entry in archive))
        self.assertNotIn(b"example/private-sdk", index)

    def test_verified_parent_relationship_survives_shallow_cache_marker(self):
        (self.repo / ".git/shallow").write_text(self.head + "\n")
        self.export()
        self.assertTrue((self.out / "fern-content.json").is_file())

    def test_unchanged_private_go_leftover_cannot_be_exported(self):
        common.git(self.repo, "checkout", "--detach", self.base)
        self.write("private_extra.go", b"package private\n// internal notes\n")
        self.base = self.commit()
        self.candidate()
        with self.assertRaises(common.PipelineError):
            self.export()
        self.assertFalse(any(self.out.iterdir()))

    def test_changed_controls_legacy_unknown_or_executable_paths_rejected(self):
        for name, data in (("legacy/client.go", b"package changed\n"), ("internal/caller.go", b"package changed\n"),
                           (".github/workflows/ci.yml", b"changed"), ("setup.sh", b"#!/bin/sh\n")):
            with self.subTest(name=name):
                common.git(self.repo, "checkout", "--detach", self.head)
                self.write(name, data)
                changed = self.commit()
                old = self.head
                self.head = changed
                with self.assertRaises(common.PipelineError):
                    self.export()
                self.head = old
        common.git(self.repo, "checkout", "--detach", self.head)
        (self.repo / "client.go").chmod(0o755)
        self.head = self.commit()
        with self.assertRaises(common.PipelineError):
            self.export()

    def test_private_preservation_cannot_silently_hide_generated_paths(self):
        common.git(self.repo, "checkout", "--detach", self.base)
        self.write(".fernignore", self.ignore + b"client.go\n")
        self.base = self.commit()
        self.candidate()
        with self.assertRaises(common.PipelineError):
            self.export()

    def test_raw_private_references_never_enter_public_artifact(self):
        self.write("client.go", b"package plaid\n// https://github.com/example/private-sdk\n")
        self.head = self.commit()
        with self.assertRaises(common.PipelineError) as failure:
            self.export()
        self.assertNotIn("example/private-sdk", str(failure.exception))
        self.assertFalse(any(self.out.iterdir()))

    def test_enterprise_github_reference_cannot_enter_public_artifact(self):
        self.write("client.go", b"package plaid\n// https://github.corp.example/team/private\n")
        self.head = self.commit()
        with self.assertRaises(common.PipelineError):
            self.export()
        self.assertFalse(any(self.out.iterdir()))

    def test_credential_echo_in_generated_bytes_cannot_enter_public_artifact(self):
        self.write("client.go", b"package plaid\n// fixture-reader-credential\n")
        self.head = self.commit()
        with self.assertRaises(common.PipelineError) as failure:
            self.export(forbidden_values=(b"fixture-reader-credential",))
        self.assertNotIn("fixture-reader-credential", str(failure.exception))
        self.assertFalse(any(self.out.iterdir()))

    def test_unknown_mock_server_delta_rejected(self):
        self.write("wiremock/docker-compose.test.yml", b"services: {private: {image: unsafe}}\n")
        self.head = self.commit()
        with self.assertRaises(common.PipelineError):
            self.export()

    def test_known_mock_server_change_is_filtered_out(self):
        common.git(self.repo, "checkout", "--detach", self.base)
        self.write("wiremock/docker-compose.test.yml", hosted_output.COMPOSE_HARDENED.encode())
        self.base = self.commit()
        self.candidate()
        self.write("wiremock/docker-compose.test.yml", hosted_output.COMPOSE_RAW.encode())
        self.head = self.commit()
        self.export()
        self.assertNotIn(b"docker-compose", (self.out / "fern-content.json").read_bytes())

    def test_metadata_module_or_retry_changes_rejected(self):
        for change in ({"maxRetries": 1}, {"importPath": "github.com/example/private-sdk/v50"}):
            self.metadata["generatorConfig"].update(change)
            self.write(".fern/metadata.json", json.dumps(self.metadata).encode())
            self.head = self.commit()
            with self.subTest(change=change), self.assertRaises(common.PipelineError):
                self.export()

    def test_actual_blob_bytes_checked_not_just_recorded_object_id(self):
        import zlib
        oid = common.git(self.repo, "rev-parse", self.head + ":client.go")
        path = self.repo / ".git/objects" / oid[:2] / oid[2:]
        changed = b"package replaced\n"
        path.chmod(0o600)
        path.write_bytes(zlib.compress(b"blob " + str(len(changed)).encode() + b"\0" + changed))
        with self.assertRaises(common.PipelineError):
            self.export()


if __name__ == "__main__":
    unittest.main()
