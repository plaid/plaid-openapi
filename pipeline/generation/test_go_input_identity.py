"""Only the shared settings and selected Go inputs should trigger Go generation."""
import json
from pathlib import Path
import tempfile
import unittest

import common
import generate


GENERATORS = """api:
  specs:
    - openapi: ../2020-09-14.yml
      overlays: ./openapi-overlay.yml
auth-schemes:
  clientSecret:
    header: EXAMPLE-SECRET
    type: string
default-group: ts-sdk
readme:
  apiName: Example
groups:
  ts-sdk:
    generators:
      - name: fernapi/fern-typescript-node-sdk
        version: 3.0.0
        config:
          namespaceExport: Example
  go-sdk:
    generators:
      - name: fernapi/fern-go-sdk
        version: 1.70.3
        github:
          repository: example/public-sdk
          mode: pull-request
        config:
          maxRetries: 0
          packageName: example
  ruby-sdk:
    generators:
      - name: fernapi/fern-ruby-sdk
        version: 1.0.0
"""


class GoInputIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="go-input-identity-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        common.git(self.repo, "init", "-q")
        self.write("fern/generators.yml", GENERATORS)
        self.write("fern/fern.config.json", json.dumps({"organization": "example", "version": "6.0.0"}))
        self.write("fern/openapi-overlay.yml", "overlay: 1.0.0\nactions: []\n")
        self.write("2020-09-14.yml", "openapi: 3.0.0\ninfo: {version: 1.0.0}\n")
        self.write(common.WORKFLOW, "name: Go generation\n")
        self.settings = {"cli_version": "5.193.2", "cli_sha256": "a" * 64,
                         "generator_version": "1.70.3", "generator_digest": "sha256:" + "b" * 64}
        self.write("pipeline/generation/settings.json", json.dumps(self.settings))
        self.write("pipeline/generation/generate.py", "# reviewed Go runtime\n")
        self.base = self.commit()
        self.before = generate.config_digest(self.repo)

    def write(self, name, data):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)

    def commit(self):
        common.git(self.repo, "add", "-A")
        common.git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                   "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "Fixture")
        return common.git(self.repo, "rev-parse", "HEAD")

    def changed(self, name, data):
        common.git(self.repo, "checkout", "--detach", self.base)
        self.write(name, data)
        self.commit()
        return generate.config_digest(self.repo)

    def test_other_language_changes_additions_and_shared_default_do_not_change_go_inputs(self):
        cases = [GENERATORS.replace("version: 3.0.0", "version: 4.0.0"),
                 GENERATORS.replace("namespaceExport: Example", "namespaceExport: ChangedNodeClient"),
                 GENERATORS.replace("version: 1.0.0", "version: 2.0.0"),
                 GENERATORS.replace("default-group: ts-sdk", "default-group: ruby-sdk"),
                 GENERATORS.replace("default-group: ts-sdk\n", ""),
                 GENERATORS + "  python-sdk:\n    generators:\n      - name: fernapi/fern-python-sdk\n        version: 5.0.0\n"]
        for index, document in enumerate(cases):
            with self.subTest(case=index):
                self.assertEqual(self.changed("fern/generators.yml", document), self.before)

    def test_shared_cli_version_is_overridden_and_does_not_change_go_inputs(self):
        for value in ("6.1.0", "latest", None):
            shared = {"organization": "example"}
            if value is not None:
                shared["version"] = value
            with self.subTest(version=value):
                self.assertEqual(self.changed("fern/fern.config.json", json.dumps(shared, indent=2)), self.before)

    def test_go_generator_config_and_shared_settings_change_go_inputs(self):
        cases = [GENERATORS.replace("version: 1.70.3", "version: 1.71.0"),
                 GENERATORS.replace("maxRetries: 0", "maxRetries: 1"),
                 GENERATORS.replace("header: EXAMPLE-SECRET", "header: UPDATED-SECRET"),
                 GENERATORS.replace("apiName: Example", "apiName: Updated shared name"),
                 GENERATORS.replace("openapi-overlay.yml", "another-overlay.yml")]
        for index, document in enumerate(cases):
            with self.subTest(case=index):
                self.assertNotEqual(self.changed("fern/generators.yml", document), self.before)
        self.assertNotEqual(self.changed("fern/fern.config.json", json.dumps({"organization": "changed", "version": "6.0.0"})), self.before)

    def test_go_pins_overlay_spec_workflow_and_runtime_remain_conservative(self):
        for key, value in (("cli_version", "5.194.0"), ("cli_sha256", "c" * 64),
                           ("generator_version", "1.71.0"), ("generator_digest", "sha256:" + "d" * 64)):
            with self.subTest(pin=key):
                self.assertNotEqual(self.changed("pipeline/generation/settings.json", json.dumps(dict(self.settings, **{key: value}))), self.before)
        for name in ("fern/openapi-overlay.yml", "2020-09-14.yml", common.WORKFLOW,
                     "pipeline/generation/generate.py", "pipeline/generation/new_runtime.py", "fern/new-input.yml"):
            with self.subTest(path=name):
                self.assertNotEqual(self.changed(name, "changed runtime input\n"), self.before)

    def test_docs_tests_and_fixture_updates_do_not_trigger_generation(self):
        for name in ("pipeline/generation/README.md", "pipeline/generation/test_new.py", "pipeline/generation/new_test.go",
                     "pipeline/generation/fixtures/example.go", "fern/docs.md", "pipeline/tests/fixture.json"):
            with self.subTest(path=name):
                self.assertEqual(self.changed(name, "test or documentation change\n"), self.before)

    def test_uses_committed_head_bytes_not_worktree_or_index(self):
        self.write("fern/generators.yml", GENERATORS.replace("maxRetries: 0", "maxRetries: 2"))
        self.write("fern/fern.config.json", json.dumps({"organization": "uncommitted"}))
        self.write("2020-09-14.yml", "uncommitted spec\n")
        common.git(self.repo, "add", "-A")
        self.assertEqual(generate.config_digest(self.repo), self.before)

    def test_selected_file_mode_changes_remain_inputs(self):
        (self.repo / "fern/generators.yml").chmod(0o755)
        self.commit()
        self.assertNotEqual(generate.config_digest(self.repo), self.before)

    def test_missing_or_duplicate_go_group_is_rejected(self):
        for document in ("groups: {}\n", GENERATORS.replace("go-sdk:", "other-sdk:"),
                         GENERATORS + "  go-sdk:\n    generators: []\n"):
            common.git(self.repo, "checkout", "--detach", self.base)
            self.write("fern/generators.yml", document)
            self.commit()
            with self.subTest(document=document), self.assertRaises(common.PipelineError):
                generate.config_digest(self.repo)


if __name__ == "__main__":
    unittest.main()
