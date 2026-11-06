import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

import common
import generate
import hosted_output


class HostedOutputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hosted-output-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.raw, self.out = self.root / "raw", self.root / "out"
        self.raw.mkdir()
        self.out.mkdir()
        self.version = "50.0.0"
        self.settings = {"cli_version": "5.193.2", "generator_image": "fernapi/fern-go-sdk", "generator_version": "1.70.3"}
        self.caller = ("package internal\n// github.com/plaid/plaid-go/v50/core\nfunc request() {\n" +
                       generate.CALLER_HOOK + "\tresp, err := c.retrier.Run()\n}\n").encode()
        self.public_files = {
            ".fernignore": ("100644", b"go.mod\ngo.sum\ninternal/caller.go\nlegacy/\n.github/\nREADME.md\nCONTRIBUTING.md\n"),
            "go.mod": ("100644", b"module github.com/plaid/plaid-go/v50\n"),
            "internal/caller.go": ("100644", self.caller),
        }
        self.metadata = {"cliVersion": "5.193.2", "generatorName": "fernapi/fern-go-sdk", "generatorVersion": "1.70.3",
                         "sdkVersion": "v50.0.0", "originGitCommit": "a" * 40,
                         "generatorConfig": {"module": {"path": "github.com/plaid/plaid-go/v50"},
                                             "importPath": "github.com/plaid/plaid-go/v50", "maxRetries": 0}}
        self.write(".fern/metadata.json", json.dumps(self.metadata).encode())
        self.write(".fern/provenance.json", b'{"fixture":"original receipt with private key label"}')
        self.write("client.go", b"package plaid\n// fresh generated client\n")
        self.write("new/client.go", b"package new\n")
        self.write("internal/caller.go", self.caller.replace(generate.CALLER_HOOK.encode(), b""))
        self.write("go.mod", b"module github.com/plaid/plaid-go/v50\n")
        self.write("go.sum", b"generated module dependencies\n")
        self.write("README.md", b"Generated README\n")
        self.write("CONTRIBUTING.md", b"Generated instructions\n")
        self.write("wiremock/docker-compose.test.yml", hosted_output.COMPOSE_RAW.encode())
        self.refresh()

    def write(self, name, data):
        path = self.raw / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def refresh(self):
        self.tree = hosted_output.fern_provenance.download_tree(hosted_output.fern_provenance.read_download_files(self.raw))

    def export(self, **kwargs):
        return hosted_output.export_verified_output(directory=self.raw, expected_tree=self.tree,
            public_files=self.public_files, version=self.version, settings=self.settings, output=self.out, **kwargs)

    def test_export_is_generated_only_and_metadata_is_public(self):
        result = self.export()
        index = (self.out / "fern-content.json").read_bytes()
        self.assertEqual(result, common.sha256(index))
        self.assertEqual([row[0] for row in json.loads(index)], [".fern/metadata.json", "client.go", "new/client.go"])
        with tarfile.open(self.out / "fern-output.tar.gz") as archive:
            metadata = json.load(archive.extractfile(".fern/metadata.json"))
            self.assertEqual(set(metadata), {"cliVersion", "generatorName", "generatorVersion", "sdkVersion"})
            self.assertTrue(all(entry.isfile() and entry.mode == 0o644 for entry in archive))
            self.assertNotIn(".fern/provenance.json", archive.getnames())
            self.assertNotIn("internal/caller.go", archive.getnames())

    def test_downloaded_tree_matches_git_and_excludes_receipt_empty_directories(self):
        self.write("a.c", b"first sort key\n")
        self.write("a/nested.go", b"package a\n")
        (self.raw / "empty").mkdir()
        self.refresh()
        repo = self.root / "git-proof"
        shutil.copytree(self.raw, repo)
        (repo / ".fern/provenance.json").unlink()
        common.git(repo, "init", "-q")
        common.git(repo, "add", "-A", "-f")
        self.assertEqual(common.git(repo, "write-tree"), self.tree)
        self.write(".fern/provenance.json", b"different receipt bytes")
        self.assertEqual(hosted_output.fern_provenance.download_tree(hosted_output.fern_provenance.read_download_files(self.raw)), self.tree)

    def test_changed_after_verification_bytes_are_rejected(self):
        self.write("client.go", b"package replaced\n")
        with self.assertRaises(common.PipelineError):
            self.export()
        self.assertFalse(any(self.out.iterdir()))

    def test_fresh_caller_must_equal_reviewed_public_runtime_without_guard(self):
        self.write("internal/caller.go", b"package changed\n")
        self.refresh()
        with self.assertRaises(common.PipelineError):
            self.export()

    def test_caller_comparison_supports_exact_major_module_rewrite(self):
        self.version = "51.0.0"
        self.metadata["sdkVersion"] = "v51.0.0"
        self.metadata["generatorConfig"]["module"]["path"] = "github.com/plaid/plaid-go/v51"
        self.metadata["generatorConfig"]["importPath"] = "github.com/plaid/plaid-go/v51"
        self.write(".fern/metadata.json", json.dumps(self.metadata).encode())
        self.write("internal/caller.go", common.module_rewrite(self.caller, 50, 51).replace(generate.CALLER_HOOK.encode(), b""))
        self.refresh()
        self.export()

    def test_unexpected_fresh_controls_scripts_and_legacy_are_rejected(self):
        for name in ("legacy/client.go", ".github/workflows/ci.yml", ".fernignore", "setup.sh", "scripts/setup.go"):
            with self.subTest(name=name):
                self.write(name, b"unexpected generated control\n")
                self.refresh()
                with self.assertRaises(common.PipelineError):
                    self.export()
                (self.raw / name).unlink()

    def test_symlinks_and_git_metadata_are_rejected(self):
        (self.raw / "link.go").symlink_to(self.raw / "client.go")
        with self.assertRaises(common.PipelineError):
            self.export()
        (self.raw / "link.go").unlink()
        (self.raw / ".git").mkdir()
        with self.assertRaises(common.PipelineError):
            self.export()

    def test_exported_file_modes_are_regular_even_if_download_modes_differ(self):
        (self.raw / "client.go").chmod(0o755)
        self.export()
        with tarfile.open(self.out / "fern-output.tar.gz") as archive:
            self.assertTrue(all(entry.isfile() and entry.mode == 0o644 for entry in archive))

    def test_enterprise_reference_or_credential_echo_cannot_enter_public_artifact(self):
        for data, forbidden in ((b"package plaid\n// https://github.corp.example/team/private\n", ()),
                                (b"package plaid\n// fixture-fern-credential\n", (b"fixture-fern-credential",))):
            self.write("client.go", data)
            self.refresh()
            with self.subTest(data=data), self.assertRaises(common.PipelineError) as failure:
                self.export(forbidden_values=forbidden)
            self.assertNotIn("fixture-fern-credential", str(failure.exception))
            self.assertFalse(any(self.out.iterdir()))

    def test_unknown_mock_server_configuration_rejected(self):
        self.write("wiremock/docker-compose.test.yml", b"services: {unreviewed: {image: unsafe}}\n")
        self.refresh()
        with self.assertRaises(common.PipelineError):
            self.export()

    def test_metadata_module_or_retry_changes_rejected(self):
        for change in ({"maxRetries": 1}, {"importPath": "github.com/example/other-sdk/v50"}):
            self.metadata["generatorConfig"].update(change)
            self.write(".fern/metadata.json", json.dumps(self.metadata).encode())
            self.refresh()
            with self.subTest(change=change), self.assertRaises(common.PipelineError):
                self.export()


if __name__ == "__main__":
    unittest.main()
