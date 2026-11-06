"""Automatic major selection and source-only namespace normalization."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import common
import generate
import test_pipeline


class MajorVersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sdk = self.root / 'sdk'
        test_pipeline.init(self.sdk)
        test_pipeline.write(self.sdk, 'go.mod', 'module github.com/plaid/plaid-go/v49\n')
        test_pipeline.write(self.sdk, 'internal/caller.go', 'package internal\n// github.com/plaid/plaid-go/v49/core\n')
        test_pipeline.write(self.sdk, 'README.md', 'github.com/plaid/plaid-go/v49\r\n')
        test_pipeline.write(self.sdk, 'scripts/release/helper.go', '// github.com/plaid/plaid-go/v49\n')
        test_pipeline.write(self.sdk, '.circleci/helper.go', '// github.com/plaid/plaid-go/v49\n')
        test_pipeline.commit(self.sdk)
        self.output = self.root / 'output'
        self.output.mkdir()
        self.values = generate.settings()

    def exercise(self, major, tags, breaks=False, override='', final_break=False):
        work = self.root / ('work-' + str(len(list(self.root.glob('work-*')))))
        work.mkdir()
        versions = []
        def candidate(sdk, data, version, values, stage):
            stage.mkdir()
            versions.append(version)
            self.assertEqual((sdk / 'go.mod').read_text().splitlines()[0],
                             'module github.com/plaid/plaid-go/v' + version.split('.')[0])
            test_pipeline.write(sdk, 'generated.go', 'package plaid\n')
            common.git(sdk, 'add', '-A')
            return {'version': version}
        def compare(old, sdk, module, published, values, stage, **kwargs):
            report = b'legacy: ExistingMethod removed\n' if len(versions) == 1 and breaks else b''
            if report and not kwargs.get('allow_breaking'):
                raise common.PipelineError('Breaking SDK or legacy API change')
            if len(versions) == 2:
                self.assertEqual((old / 'go.mod').read_bytes(), (sdk / 'go.mod').read_bytes())
                if final_break:
                    raise common.PipelineError('Unexpected final API drift')
            return report
        with patch.object(generate, 'generate_candidate', side_effect=candidate), patch.object(generate, 'compatibility_gate', side_effect=compare):
            result = generate.generate_versioned_candidate(self.sdk, self.root / 'old', b'spec', tags, major,
                                                          override, True, self.values, work, self.output)
        return result, versions

    def test_minor_then_major_then_minor_then_further_major(self):
        result, versions = self.exercise(49, ['v49.0.0'])
        self.assertEqual((result[0], versions), ('49.1.0', ['49.1.0']))
        result, versions = self.exercise(49, ['v49.1.0'], breaks=True)
        self.assertEqual((result[0], versions), ('50.0.0', ['49.2.0', '50.0.0']))
        self.assertEqual(generate.current_major(self.sdk, self.values), 50)
        result, versions = self.exercise(50, ['v49.1.0', 'v50.0.0'])
        self.assertEqual((result[0], versions), ('50.1.0', ['50.1.0']))
        result, versions = self.exercise(50, ['v50.1.0'], breaks=True)
        self.assertEqual((result[0], versions), ('51.0.0', ['50.2.0', '51.0.0']))

    def test_explicit_override_never_silently_changes_major(self):
        with self.assertRaisesRegex(common.PipelineError, 'Breaking'):
            self.exercise(49, ['v49.0.0'], breaks=True, override='49.0.1')
        self.assertEqual(generate.current_major(self.sdk, self.values), 49)

    def test_comparison_failure_does_not_retry_as_major(self):
        work = self.root / 'failure-work'
        work.mkdir()
        with patch.object(generate, 'generate_candidate', return_value={}) as candidate, patch.object(generate, 'compatibility_gate', side_effect=common.PipelineError('comparison failed')):
            with self.assertRaisesRegex(common.PipelineError, 'comparison failed'):
                generate.generate_versioned_candidate(self.sdk, self.root / 'old', b'spec', ['v49.0.0'],
                                                      49, '', True, self.values, work, self.output)
            candidate.assert_called_once()
        self.assertEqual(generate.current_major(self.sdk, self.values), 49)

    def test_final_generation_api_drift_stops_release(self):
        with self.assertRaisesRegex(common.PipelineError, 'final API drift'):
            self.exercise(49, ['v49.0.0'], breaks=True, final_break=True)

    def test_stale_module_and_major_override_stop_before_generation(self):
        for tags, override in ((['v50.0.0'], ''), (['v49.0.0'], '50.0.0')):
            with self.subTest(tags=tags, override=override), self.assertRaises(common.PipelineError):
                self.exercise(49, tags, override=override)

    def test_unpublished_higher_root_major_stops_before_generation(self):
        generate.rewrite_module(self.sdk, 49, 50)
        for tags in (['v49.0.0'], []):
            with self.subTest(tags=tags), self.assertRaisesRegex(common.PipelineError, 'latest published'):
                self.exercise(50, tags)

    def test_exact_module_rewrite_preserves_controls_and_line_endings(self):
        readme = self.sdk / 'README.md'
        readme.write_bytes(b'github.com/plaid/plaid-go/v49\r\ngithub.com/plaid/plaid-go/v490 github.com/plaid/plaid-go/v49-extra\r\n')
        common.git(self.sdk, 'add', '-A')
        expected = common.expected_protected_state(self.sdk, 50)
        generate.rewrite_module(self.sdk, 49, 50)
        self.assertEqual(readme.read_bytes(), b'github.com/plaid/plaid-go/v50\r\ngithub.com/plaid/plaid-go/v490 github.com/plaid/plaid-go/v49-extra\r\n')
        self.assertEqual((self.sdk / 'scripts/release/helper.go').read_text(), '// github.com/plaid/plaid-go/v49\n')
        self.assertEqual((self.sdk / '.circleci/helper.go').read_text(), '// github.com/plaid/plaid-go/v49\n')
        self.assertEqual(common.protected_state(self.sdk), expected)
        (self.sdk / 'internal/caller.go').write_text('unrelated edit')
        common.git(self.sdk, 'add', '-A')
        self.assertNotEqual(common.protected_state(self.sdk), expected)

    def test_floor_cannot_override_current_module_major(self):
        generate.rewrite_module(self.sdk, 49, 50)
        self.assertEqual(generate.current_major(self.sdk, self.values), 50)
        with self.assertRaises(common.PipelineError):
            generate.current_major(self.sdk, {**self.values, 'major': 51})


if __name__ == '__main__':
    unittest.main()
