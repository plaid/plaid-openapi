import unittest
from common import PipelineError
from workflow_outputs import outputs


class WorkflowOutputsTests(unittest.TestCase):
    def test_generated_output_and_noop(self):
        value = {"status": "generated", "rehearsal": False, "content_sha256": "a" * 64,
                 "subject_name": "plaid-go-v50.1.0-source"}
        self.assertEqual(outputs(value)["rehearsal"], "false")
        self.assertEqual(outputs({"status": "unchanged", "rehearsal": True})["digest"], "")

    def test_missing_rehearsal_or_string_boolean_rejected(self):
        for value in ({"status": "ready"}, {"status": "ready", "rehearsal": "false"}):
            with self.assertRaises(PipelineError):
                outputs(value)

    def test_output_injection_rejected(self):
        for field in ("status", "version", "content_sha256", "subject_name", "mode"):
            with self.subTest(field=field), self.assertRaises(PipelineError):
                outputs({"status": "ready", "rehearsal": True, field: "ready\nrehearsal=false"})

    def test_unpaired_subject_rejected(self):
        with self.assertRaises(PipelineError):
            outputs({"status": "ready", "rehearsal": False, "subject_name": "plaid-go-v50.1.0-source"})


if __name__ == "__main__":
    unittest.main()
