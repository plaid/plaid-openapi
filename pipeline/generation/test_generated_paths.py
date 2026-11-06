"""Attested generation may change only approved SDK output paths."""
import tempfile
from pathlib import Path
import unittest
import common
import test_pipeline


class GeneratedPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'sdk'
        test_pipeline.init(self.repo)
        for name, data in {
            'go.mod': 'module github.com/plaid/plaid-go/v49\n',
            'README.md': 'github.com/plaid/plaid-go/v49/client\n',
            'legacy/tests/api_test.go': 'package tests\n// github.com/plaid/plaid-go/v49/legacy\n',
            'legacy/tests/fixture.json': '{}\n',
            'internal/caller.go': 'package internal\n// github.com/plaid/plaid-go/v49\n',
            'scripts/release/policy.py': 'policy = True\n',
            'reference.md': 'public reference\n',
        }.items():
            test_pipeline.write(self.repo, name, data)
        self.base = test_pipeline.commit(self.repo)

    def check(self, major=49):
        common.git(self.repo, 'add', '-A')
        common.approved_generated_changes(self.repo, self.repo, major, base_ref=self.base)

    def test_old_protected_hash_gate_accepts_script_but_allowlist_rejects_it(self):
        before = common.protected_state(self.repo)
        test_pipeline.write(self.repo, 'setup.sh', 'echo unexpected\n')
        common.git(self.repo, 'add', '-A')
        self.assertEqual(before, common.protected_state(self.repo))
        with self.assertRaisesRegex(common.PipelineError, 'unapproved path'):
            self.check()

    def test_new_generated_package_and_public_data_allowed(self):
        test_pipeline.write(self.repo, 'new_endpoint/models_2.go', 'package new_endpoint\n')
        test_pipeline.write(self.repo, 'reference.md', 'updated reference\n')
        self.check()

    def test_unknown_config_and_scripts_and_modes_rejected(self):
        for name in ('surprise.yml', 'scripts/helper.go', 'New/client.go', 'client.go'):
            with self.subTest(name=name):
                common.git(self.repo, 'reset', '--hard', self.base)
                common.git(self.repo, 'clean', '-fd')
                test_pipeline.write(self.repo, name, 'unexpected\n')
                if name == 'client.go':
                    (self.repo / name).chmod(0o755)
                with self.assertRaises(common.PipelineError):
                    self.check()

    def test_existing_unknown_non_go_frozen_including_deletion(self):
        for delete in (False, True):
            with self.subTest(delete=delete):
                common.git(self.repo, 'reset', '--hard', self.base)
                path = self.repo / 'legacy/tests/fixture.json'
                if delete:
                    path.unlink()
                else:
                    path.write_text('changed')
                with self.assertRaisesRegex(common.PipelineError, 'maintained content'):
                    self.check()

    def test_legacy_tests_only_exact_major_namespace_change(self):
        path = self.repo / 'legacy/tests/api_test.go'
        original = path.read_bytes()
        path.write_bytes(common.module_rewrite(original, 49, 50))
        self.check(major=50)
        with self.assertRaises(common.PipelineError):
            self.check(major=49)
        path.write_bytes(common.module_rewrite(original, 49, 50) + b'// unrelated\n')
        with self.assertRaises(common.PipelineError):
            self.check(major=50)

    def test_legacy_test_addition_or_deletion_rejected(self):
        test_pipeline.write(self.repo, 'legacy/tests/new_test.go', 'package tests\n')
        with self.assertRaises(common.PipelineError):
            self.check(major=50)
        common.git(self.repo, 'reset', '--hard', self.base)
        (self.repo / 'legacy/tests/api_test.go').unlink()
        with self.assertRaises(common.PipelineError):
            self.check(major=50)

    def test_original_base_used_after_generator_local_commit(self):
        test_pipeline.write(self.repo, 'setup.sh', 'echo unexpected\n')
        test_pipeline.commit(self.repo)
        with self.assertRaisesRegex(common.PipelineError, 'unapproved path'):
            self.check()


if __name__ == '__main__':
    unittest.main()
