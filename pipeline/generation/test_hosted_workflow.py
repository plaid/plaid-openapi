"""Check the real hosted workflow's artifact and credential boundaries."""
import ast
from pathlib import Path
import re
import unittest

import yaml

import assembly_seal
import common

ROOT = Path(__file__).resolve().parents[2]


def steps_using(job, action):
    return [step for step in job["steps"] if step.get("uses", "").startswith(action + "@")]


def run_text(job):
    return "\n".join(step.get("run", "") for step in job["steps"])


def needs_of(job):
    value = job.get("needs", [])
    return {value} if isinstance(value, str) else set(value)


def evaluate(expression, state):
    """Evaluate the workflow's small routing expression, not a copied routing table."""
    expression = expression.removeprefix("${{").removesuffix("}}").strip()
    expression = re.sub(r"needs\.([a-z0-9-]+)\.(result|outputs)(?:\.([a-z_]+))?",
        lambda match: repr(state[match[1]][match[2]] if match[2] == "result" else state[match[1]]["outputs"].get(match[3], "")), expression)
    expression = expression.replace("github.run_id", "'123'")
    expression = expression.replace("always()", "True").replace("cancelled()", "False")
    expression = re.sub(r"!(?!=)", " not ", expression).replace("&&", " and ").replace("||", " or ")
    return eval(expression, {"__builtins__": {}, "format": lambda pattern, value: pattern.format(value)})


class HostedWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.safe_load((ROOT / ".github/workflows/generate-go-sdk.yml").read_text())
        cls.jobs = cls.workflow["jobs"]

    def test_direct_generation_uses_no_private_repository_reader(self):
        for name in ("request-minor", "request-major"):
            job = self.jobs[name]
            self.assertFalse(steps_using(job, "actions/create-github-app-token"))
            self.assertNotIn("FERN_OUTPUT_", str(job))
            self.assertNotIn("SDK_FERN_READ_TOKEN", str(job))
            secrets = re.findall(r"secrets\.([A-Z_]+)", str(job))
            self.assertEqual(set(secrets), {"FERN_TOKEN"})
            self.assertIn("fern-provenance.json", steps_using(job, "actions/upload-artifact")[0]["with"]["path"])

    def test_hosted_sdk_execution_occurs_only_after_sealing_on_read_only_jobs(self):
        for lane in ("minor", "major"):
            assemble, seal, validate = (self.jobs[prefix + lane] for prefix in ("assemble-", "seal-", "validate-"))
            self.assertIn("assemble-" + lane, needs_of(seal))
            self.assertIn("seal-" + lane, needs_of(validate))
            self.assertIn("hosted_pipeline.py assemble", run_text(assemble))
            self.assertIn("hosted_pipeline.py validate", run_text(validate))
            for job in (assemble, validate):
                self.assertNotIn("environment", job)
                self.assertTrue(all(access == "read" for access in job["permissions"].values()))
                self.assertNotIn("secrets.", str(job))
                self.assertFalse(steps_using(job, "actions/create-github-app-token"))
            self.assertNotIn("hosted_pipeline.py validate", run_text(seal))
        parsed = ast.parse((ROOT / "pipeline/generation/hosted_pipeline.py").read_text())
        functions = {node.name: node for node in parsed.body if isinstance(node, ast.FunctionDef)}
        calls = lambda node: {call.func.attr for call in ast.walk(node)
                             if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)}
        self.assertNotIn("verify_sdk", calls(functions["assemble"]))
        self.assertNotIn("compatibility_gate", calls(functions["assemble"]))
        self.assertIn("verify_sdk", calls(functions["validate"]))

    def test_validation_returns_no_sdk_bytes_to_publication(self):
        for lane in ("minor", "major"):
            job = self.jobs["validate-" + lane]
            uploaded = steps_using(job, "actions/upload-artifact")
            self.assertEqual(len(uploaded), 1)
            paths = uploaded[0]["with"]["path"].strip().splitlines()
            self.assertEqual({path.rsplit("/", 1)[1] for path in paths}, {"result.json", "api-diff.txt"})
            self.assertFalse(any("*" in path for path in paths))
            downloads = [step["with"]["name"] for step in steps_using(job, "actions/download-artifact")]
            self.assertIn("go-sealed-" + lane + "-${{ github.run_id }}", downloads)
            self.assertNotIn("go-candidate-" + lane + "-${{ github.run_id }}", downloads)
        major_downloads = [step["with"]["name"] for step in steps_using(self.jobs["validate-major"], "actions/download-artifact")]
        self.assertIn("go-sealed-minor-${{ github.run_id }}", major_downloads)
        selected = steps_using(self.jobs["generate"], "actions/download-artifact")[0]["with"]["name"]
        self.assertIn("go-sealed-minor-", selected)
        self.assertIn("go-sealed-major-", selected)
        self.assertNotIn("go-validation-", selected)
        self.assertNotIn("go-candidate-", selected)

    def test_assembly_seal_never_qualifies_as_publishable_generation(self):
        for lane in ("minor", "major"):
            job = self.jobs["seal-" + lane]
            attest = steps_using(job, "actions/attest")
            self.assertEqual(len(attest), 1)
            self.assertEqual(attest[0]["with"]["predicate-type"], assembly_seal.ASSEMBLY_PREDICATE)
            self.assertNotEqual(attest[0]["with"]["predicate-type"], common.PREDICATE)
            self.assertTrue(attest[0]["with"]["subject-name"].endswith("-assembly"))
            self.assertIn("needs.prepare.outputs.rehearsal == 'false'", attest[0]["if"])
            self.assertIn("assembly_seal.py", run_text(job))
            upload = steps_using(job, "actions/upload-artifact")[0]
            self.assertIn("assembly.bundle.json", upload["with"]["path"])
        final = self.jobs["attest-generation"]
        self.assertIn("generate", needs_of(final))
        self.assertIn("assembly_seal.py", run_text(final))
        self.assertEqual(steps_using(final, "actions/attest")[0]["with"]["predicate-type"], common.PREDICATE)
        self.assertIn("attest-generation", needs_of(self.jobs["open-sdk-pr"]))
        self.assertIn("needs.generate.outputs.status == 'generated'", final["if"])
        self.assertIn("inputs.rehearsal == false", final["if"])
        self.assertIn("vars.SDK_PIPELINE_ENABLED == 'true'", final["if"])

    def test_major_request_requires_validated_breaking_minor(self):
        request = self.jobs["request-major"]
        self.assertIn("validate-minor", needs_of(request))
        self.assertIn("needs.validate-minor.outputs.status == 'needs-major'", request["if"])
        self.assertNotIn("assemble-minor.outputs", request["if"])

    def test_selection_waits_for_validation_and_handles_skipped_major_or_noop(self):
        job = self.jobs["generate"]
        selector = steps_using(job, "actions/download-artifact")[0]["with"]["name"]
        state = {name: {"result": "skipped", "outputs": {"status": ""}}
                 for name in needs_of(job)}
        state["prepare"] = {"result": "success", "outputs": {"status": "ready", "mode": "fern-hosted"}}
        self.assertFalse(evaluate(job["if"], state))
        state["validate-minor"] = {"result": "failure", "outputs": {"status": "generated"}}
        self.assertFalse(evaluate(job["if"], state))
        state["validate-minor"] = {"result": "success", "outputs": {"status": "generated"}}
        self.assertTrue(evaluate(job["if"], state))
        self.assertEqual(evaluate(selector, state), "go-sealed-minor-123")
        state["validate-minor"]["outputs"]["status"] = "needs-major"
        self.assertFalse(evaluate(job["if"], state))
        state["validate-major"] = {"result": "failure", "outputs": {"status": "generated"}}
        self.assertFalse(evaluate(job["if"], state))
        state["validate-major"]["result"] = "success"
        self.assertTrue(evaluate(job["if"], state))
        self.assertEqual(evaluate(selector, state), "go-sealed-major-123")
        state["prepare"]["outputs"]["status"] = "unchanged"
        self.assertTrue(evaluate(job["if"], state))
        self.assertEqual(evaluate(selector, state), "go-prepared-123")
        state["prepare"]["outputs"] = {"status": "ready", "mode": "local"}
        state["generate-local"] = {"result": "success", "outputs": {"status": "unchanged"}}
        self.assertTrue(evaluate(job["if"], state))
        self.assertEqual(evaluate(selector, state), "go-local-123")
        validation = next(step for step in job["steps"] if "assembly_seal.py" in step.get("run", ""))
        self.assertEqual(validation["if"], "steps.result.outputs.status == 'generated'")
        result_position = next(index for index, step in enumerate(job["steps"]) if step.get("id") == "result")
        self.assertLess(result_position, job["steps"].index(validation))


if __name__ == "__main__":
    unittest.main()
