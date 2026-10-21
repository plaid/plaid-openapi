"""Only successful API comparisons may emit a public breaking-change report."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import common
import generate


class CompatibilityReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.output.mkdir()
        self.values = generate.settings()

    def compare(self, work):
        generate.compatibility_gate(self.root / "old", self.root / "new",
                                    "github.com/plaid/plaid-go/v49", True,
                                    self.values, work, output=self.output)

    def test_breaking_report_survives_temporary_checkout_cleanup(self):
        report = b"Incompatible changes:\n- (*Client).ExistingMethod: removed\n"
        with tempfile.TemporaryDirectory(dir=self.root) as temporary:
            work = Path(temporary)
            with patch.object(generate, "run", side_effect=[b"", b"", b"", report]) as run:
                with self.assertRaisesRegex(common.PipelineError, "Breaking SDK or legacy API change"):
                    self.compare(work)
                self.assertIn("-incompatible", run.call_args.args[0])
        self.assertFalse(work.exists())
        self.assertEqual((self.output / "api-diff.txt").read_bytes(), report)
        self.assertEqual(json.loads((self.output / "result.json").read_text()),
                         {"status": "breaking-change", "report": "api-diff.txt"})
        self.assertEqual(sorted(path.name for path in self.output.iterdir()),
                         ["api-diff.txt", "result.json"])

    def test_compatible_api_does_not_emit_a_blocked_result(self):
        work = self.root / "work"
        work.mkdir()
        with patch.object(generate, "run", side_effect=[b"", b"", b"", b""]):
            self.compare(work)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_failed_comparison_does_not_publish_tool_logs_as_api_report(self):
        work = self.root / "work"
        work.mkdir()
        with patch.object(generate, "run", side_effect=[b"", b"", b"", common.PipelineError("comparison failed")]):
            with self.assertRaisesRegex(common.PipelineError, "comparison failed"):
                self.compare(work)
        self.assertEqual(list(self.output.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
