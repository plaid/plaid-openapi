"""Reject incomplete overlays before generating a new public SDK."""

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch

import generate
from common import PipelineError
import overlay_coverage as coverage


NAMES = {"x-fern-sdk-group-name": ["accounts"], "x-fern-sdk-method-name": "get"}


def fixture(method="post"):
    spec = {"paths": {"/accounts/get": {method: {
        "requestBody": {"$ref": "#/components/requestBodies/Input"}}}},
        "components": {
            "requestBodies": {"Input": {"content": {"application/json": {
                "schema": {"$ref": "#/components/schemas/Input"}}}}},
            "schemas": {"Input": {"properties": {"client_id": {"type": "string"},
                                                     "secret": {"type": "string"},
                                                     "business": {"properties": {"secret": {"type": "string"}}}}}}}}
    overlay = {"overlay": "1.0.0", "actions": [
        {"target": f"$.paths['/accounts/get'].{method}", "update": deepcopy(NAMES)},
        {"target": "$.components.schemas.Input.properties.client_id", "remove": True},
        {"target": "$.components.schemas.Input.properties.secret", "remove": True}]}
    return spec, overlay


def yaml_text(overlay):
    lines = ["overlay: 1.0.0", "actions:"]
    for action in overlay["actions"]:
        lines.append(f"  - target: {action['target']}")
        if action.get("remove"):
            lines.append("    remove: true")
        else:
            lines.append("    update:")
            lines.append("      x-fern-sdk-group-name:")
            lines.extend(f"        - {group}" for group in action["update"]["x-fern-sdk-group-name"])
            lines.append(f"      x-fern-sdk-method-name: {action['update']['x-fern-sdk-method-name']}")
    return "\n".join(lines) + "\n"


class CoverageTests(unittest.TestCase):
    def test_current_public_spec_and_overlay(self):
        root = Path(__file__).resolve().parents[2]
        count = coverage.validate((root / "2020-09-14.yml").read_bytes(),
                                  (root / "fern/openapi-overlay.yml").read_bytes())
        self.assertGreater(count, 0)

    def test_all_http_methods_require_names(self):
        for method in sorted(coverage.METHODS):
            with self.subTest(method=method):
                spec, overlay = fixture(method)
                self.assertEqual(coverage.check(spec, overlay), 1)
                overlay["actions"].pop(0)
                with self.assertRaisesRegex(PipelineError, "missing explicit SDK group name"):
                    coverage.check(spec, overlay)

    def test_new_endpoint_without_overlay_fails(self):
        spec, overlay = fixture()
        spec["paths"]["/accounts/new"] = deepcopy(spec["paths"]["/accounts/get"])
        with self.assertRaisesRegex(PipelineError, "POST /accounts/new: missing explicit SDK method name"):
            coverage.check(spec, overlay)

    def test_auth_removal_must_affect_referenced_request(self):
        spec, overlay = fixture()
        overlay["actions"][-1]["target"] = "$.components.schemas.Unused.properties.secret"
        with self.assertRaisesRegex(PipelineError, "body credentials remain: secret"):
            coverage.check(spec, overlay)

    def test_effective_schema_composition_and_inline_multipart(self):
        spec, overlay = fixture()
        operation = spec["paths"]["/accounts/get"]["post"]
        operation["requestBody"] = {"content": {"multipart/form-data": {"schema": {
            "allOf": [{"$ref": "#/components/schemas/Input"},
                      {"oneOf": [{"properties": {"secret": {"type": "string"}}}]}]}}}}
        with self.assertRaisesRegex(PipelineError, "multipart/form-data.*body credentials remain: secret"):
            coverage.check(spec, overlay)

    def test_nested_business_fields_are_allowed_and_source_unmodified(self):
        spec, overlay = fixture()
        original = deepcopy(spec)
        self.assertEqual(coverage.check(spec, overlay), 1)
        self.assertEqual(spec, original)

    def test_later_overlay_action_can_reintroduce_credential(self):
        spec, overlay = fixture()
        overlay["actions"].append({"target": "$.components.schemas.Input.properties",
                                   "update": {"secret": {"type": "string"}}})
        with self.assertRaisesRegex(PipelineError, "body credentials remain: secret"):
            coverage.check(spec, overlay)

    def test_shared_schema_and_wildcard_removal(self):
        spec, overlay = fixture()
        spec["paths"]["/accounts/new"] = deepcopy(spec["paths"]["/accounts/get"])
        overlay["actions"][0]["target"] = "$.paths[*].post"
        self.assertEqual(coverage.check(spec, overlay), 2)

    def test_unknown_selector_and_external_reference_stop_for_review(self):
        spec, overlay = fixture()
        overlay["actions"][0]["target"] = "$..post"
        with self.assertRaisesRegex(PipelineError, "Unsupported overlay target"):
            coverage.check(spec, overlay)
        spec, overlay = fixture()
        spec["paths"]["/accounts/get"]["post"]["requestBody"]["$ref"] = "other.yml#/Input"
        with self.assertRaisesRegex(PipelineError, "within the public spec"):
            coverage.check(spec, overlay)

    def test_fix_adds_suggested_names_and_credential_removals(self):
        spec, overlay = fixture()
        spec["paths"]["/accounts/balance/get"] = {"post": {"requestBody": {"content": {"application/json": {
            "schema": {"$ref": "#/components/schemas/Balance"}}}}}}
        spec["paths"]["/accounts/inline/get"] = {"post": {"requestBody": {"content": {"application/json": {
            "schema": {"properties": {"secret": {"type": "string"}, "account_id": {"type": "string"}}}}}}}}
        spec["components"]["schemas"]["Balance"] = {"properties": {"client_id": {"type": "string"},
                                                                   "secret": {"type": "string"}}}
        text, suggested = coverage.fix(json.dumps(spec).encode(), yaml_text(overlay))
        self.assertEqual(suggested, ["POST /accounts/balance/get: accounts.getBalance",
                                     "POST /accounts/inline/get: accounts.getInline"])
        fixed = coverage.load(text.encode())
        self.assertEqual(coverage.check(spec, fixed), 3)
        self.assertTrue(text.startswith(yaml_text(overlay).split("  - target:")[0]))
        self.assertIn("$.paths['/accounts/inline/get'].post.requestBody.content['application/json']"
                      ".schema.properties.secret", text)
        self.assertEqual(coverage.fix(json.dumps(spec).encode(), text), (text, []))

    def test_fix_leaves_unfixable_shapes_for_review(self):
        spec, overlay = fixture()
        spec["paths"]["/accounts/get"]["post"]["requestBody"] = {"content": {"multipart/form-data": {"schema": {
            "allOf": [{"properties": {"secret": {"type": "string"}}}]}}}}
        with self.assertRaisesRegex(PipelineError, "added by hand:\nPOST /accounts/get .*secret"):
            coverage.fix(json.dumps(spec).encode(), yaml_text(overlay))

    def test_failure_names_the_fix_command(self):
        spec, overlay = fixture()
        spec["paths"]["/accounts/new"] = deepcopy(spec["paths"]["/accounts/get"])
        with self.assertRaisesRegex(PipelineError, "overlay_coverage.py --fix"):
            coverage.check(spec, overlay)

    def test_duplicate_yaml_key_rejected(self):
        with self.assertRaisesRegex(PipelineError, "Duplicate YAML key"):
            coverage.load(b'paths: {}\npaths: {}\n')

    def test_publisher_import_does_not_need_generation_dependencies(self):
        result = subprocess.run([sys.executable, "-S", "-c", "import publish_pr"],
                                cwd=Path(__file__).parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_generation_stops_before_running_generator(self):
        spec, overlay = fixture()
        spec["paths"]["/accounts/new"] = deepcopy(spec["paths"]["/accounts/get"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "fern").mkdir()
            (root / "fern/openapi-overlay.yml").write_text(json.dumps(overlay))
            (root / "event.json").write_text('{}')
            with patch.object(generate, "ROOT", root), \
                    patch.object(generate, "settings", return_value={"sdk_repository": "plaid/plaid-go", "sdk_branch": "master", "major": 49}), \
                    patch.object(generate, "event_request", return_value=("", True)), \
                    patch.object(generate, "check_context", return_value=("plaid/plaid-openapi", "a" * 40, "1")), \
                    patch.object(generate, "fetch_repository", return_value="b" * 40), \
                    patch.object(generate, "git", return_value=""), \
                    patch.object(generate, "pending_release", return_value=None), \
                    patch.object(generate, "verified_spec", return_value=("a" * 40, json.dumps(spec).encode())), \
                    patch.object(generate, "propose_version", side_effect=AssertionError("Generation continued without validating the overlay")), \
                    patch.object(generate, "generate_new_client") as generator, \
                    patch.dict(os.environ, {"GITHUB_EVENT_PATH": str(root / "event.json"), "GITHUB_EVENT_NAME": "workflow_dispatch"}), \
                    patch("sys.argv", ["generate.py", "--output", str(root / "output")]):
                with self.assertRaisesRegex(PipelineError, "POST /accounts/new: missing explicit"):
                    generate.main()
                generator.assert_not_called()


if __name__ == "__main__":
    unittest.main()
