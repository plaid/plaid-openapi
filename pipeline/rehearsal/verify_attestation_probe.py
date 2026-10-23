"""Exercise the production verifier against a real, non-release attestation."""
import argparse
import hashlib
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "generation"))
from attestation import verified_attestation
from common import PipelineError, require, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    directory = parser.parse_args().directory
    artifact, bundle = directory / "subject.txt", directory / "bundle.json"
    require(artifact.read_bytes() == b"Non-release SDK automation attestation rehearsal.\n", "Unexpected subject content")
    require(os.environ["GITHUB_REPOSITORY"] == "plaid/plaid-openapi" and
            os.environ["GITHUB_REF"] == "refs/heads/anguyen-sdk-attestation-rehearsal", "Unexpected rehearsal context")
    predicate = {"rehearsal": True, "sdk_release": False}
    arguments = dict(repository="plaid/plaid-openapi", workflow=".github/workflows/sdk-pipeline-checks.yml",
                     ref=os.environ["GITHUB_REF"], commit=os.environ["GITHUB_SHA"],
                     predicate_type="https://plaid.com/attestations/sdk-rehearsal/v1", predicate=predicate,
                     subjects=[{"name": "plaid-sdk-attestation-rehearsal", "digest": {
                         "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}}],
                     run_id=os.environ["GITHUB_RUN_ID"])
    result = {"sdk_release": False, "status": "running", "rejected": [],
              "source_commit": os.environ["GITHUB_SHA"], "run_id": os.environ["GITHUB_RUN_ID"]}
    try:
        verified = verified_attestation(artifact, bundle, **arguments)
        save_json(directory / "verified.json", verified)
        result["real_signature_verified"] = True
        tampered = directory / "tampered.txt"
        tampered.write_bytes(artifact.read_bytes() + b"changed\n")
        checks = [
            ("changed artifact", tampered, {}),
            ("production generation workflow", artifact, {"workflow": ".github/workflows/generate-go-sdk.yml"}),
            ("wrong source commit", artifact, {"commit": "0" * 40}),
            ("production predicate", artifact, {"predicate_type": "https://plaid.com/attestations/sdk-generation/v1"}),
            ("altered predicate", artifact, {"predicate": {"rehearsal": False, "sdk_release": True}}),
            ("wrong run", artifact, {"run_id": "1"}),
        ]
        for label, subject, changes in checks:
            try:
                verified_attestation(subject, bundle, **dict(arguments, **changes))
            except PipelineError:
                result["rejected"].append(label)
            else:
                raise PipelineError("Verifier accepted " + label)
        result["status"] = "passed"
    finally:
        if result["status"] != "passed":
            result["status"] = "failed"
        save_json(directory / "result.json", result)


if __name__ == "__main__":
    main()
