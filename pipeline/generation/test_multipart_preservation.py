"""Preserve the published v49 transfer upload fix across the known generator bug.

Fixture is the public file at:
https://github.com/plaid/plaid-go/blob/0d83b050ea325adda35c6d88bdf24b46fe2f7044/transfer/diligence/raw_client.go
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import common
import generate


class MultipartPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.sdk = Path(self.temporary.name)
        self.path = self.sdk / "transfer/diligence/raw_client.go"
        self.path.parent.mkdir(parents=True)
        self.expected = (Path(__file__).parent / "fixtures/transfer_diligence_raw_client.go.txt").read_bytes()
        self.path.write_bytes(self.expected)
        self.values = generate.settings()
        (self.sdk / ".fern").mkdir()
        self.metadata = self.sdk / ".fern/metadata.json"
        self.metadata.write_text(json.dumps({"generatorVersion": "1.70.3"}))

    def test_known_generator_output_is_restored_to_the_exact_published_file(self):
        generated = self.expected.replace(b'writer.WriteField("purpose", string(request.Purpose))',
                                          b'writer.WriteJSON("purpose", string(request.Purpose))')
        self.assertNotEqual(generated, self.expected)
        self.path.write_bytes(generated)
        self.assertTrue(generate.restore_published_multipart_field(self.sdk, self.values))
        self.assertEqual(self.path.read_bytes(), self.expected)

    def test_already_correct_output_is_unchanged(self):
        self.assertFalse(generate.restore_published_multipart_field(self.sdk, self.values))
        self.assertEqual(self.path.read_bytes(), self.expected)

    def test_unknown_shape_fails_without_editing_the_file(self):
        shapes = [self.expected.replace(b'writer.WriteField("purpose", string(request.Purpose))',
                                        b'writer.WriteJSON("purpose", request.Purpose)'),
                  self.expected.replace(b'"/transfer/diligence/document/upload"', b'"/other/upload"'),
                  self.expected.replace(b'UploadDocument(', b'NewUploadDocument('),
                  self.expected.replace(b'writer.WriteFile("file", request.File)', b'writer.WriteField("purpose", "extra")')]
        for value in shapes:
            with self.subTest(value=value[:30]):
                self.path.write_bytes(value)
                with self.assertRaises(common.PipelineError):
                    generate.restore_published_multipart_field(self.sdk, self.values)
                self.assertEqual(self.path.read_bytes(), value)

    def test_new_generator_version_requires_review(self):
        values = copy.deepcopy(self.values)
        values["generator_version"] = "1.71.0"
        with self.assertRaisesRegex(common.PipelineError, "new generator version"):
            generate.restore_published_multipart_field(self.sdk, values)
        self.assertEqual(self.path.read_bytes(), self.expected)

    def test_mismatched_generated_metadata_fails(self):
        self.metadata.write_text(json.dumps({"generatorVersion": "1.71.0"}))
        with self.assertRaisesRegex(common.PipelineError, "pinned generated version"):
            generate.restore_published_multipart_field(self.sdk, self.values)
        self.assertEqual(self.path.read_bytes(), self.expected)


if __name__ == "__main__":
    unittest.main()
