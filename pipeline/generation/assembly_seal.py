"""Verify a sealed pre-test SDK artifact without accepting a test job's SDK bytes."""
import argparse
import os
from pathlib import Path
import tempfile

import attestation
import generate
import hosted_contract
import publish_pr
from common import PipelineError, require

ASSEMBLY_PREDICATE = "https://plaid.com/attestations/sdk-assembly/v1"
ASSEMBLY_BUNDLE = "assembly.bundle.json"


def require_context(manifest, plan):
    """A mutable artifact flag cannot turn a production run into an unsigned run."""
    event = attestation.parse_json(Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes())
    values = generate.settings()
    _, rehearsal = generate.event_request(os.environ.get("GITHUB_EVENT_NAME"), event, values)
    metadata = event.get("repository") or {}
    require(os.environ.get("GITHUB_REPOSITORY") == attestation.CONFIG_REPO and
            metadata.get("full_name") == attestation.CONFIG_REPO and metadata.get("private") is False and
            metadata.get("fork") is False and metadata.get("default_branch") == "master" and
            os.environ.get("GITHUB_REF") == "refs/heads/master", "Untrusted SDK assembly verification context")
    require(os.environ.get("GITHUB_SHA") == manifest["config"]["commit"] and
            os.environ.get("GITHUB_RUN_ID") == manifest["generation"]["run_id"],
            "Assembly artifact is from another workflow source or run")
    require(rehearsal == plan["rehearsal"], "Artifact rehearsal flag differs from the actual workflow request")
    hosted_contract.validate_generation_mode(manifest, values)
    return rehearsal


def verify_assembly_artifact(directory: Path, sdk: Path):
    manifest, plan = publish_pr.verify_artifact(directory, sdk, signed=False)
    rehearsal = require_context(manifest, plan)
    bundle = directory / ASSEMBLY_BUNDLE
    if rehearsal:
        require(not bundle.exists(), "Unsigned rehearsal must not carry an assembly signature")
    else:
        require(bundle.is_file() and not bundle.is_symlink(), "Production assembly signature is missing")
        attestation.verified_attestation(directory / "content.json", bundle,
            repository=attestation.CONFIG_REPO, workflow=attestation.GEN_WORKFLOW,
            ref="refs/heads/master", commit=manifest["config"]["commit"],
            predicate_type=ASSEMBLY_PREDICATE, predicate=manifest,
            subjects=[{"name": "plaid-go-v" + manifest["sdk"]["version"] + "-assembly",
                       "digest": {"sha256": manifest["content_sha256"]}}],
            run_id=manifest["generation"]["run_id"])
    return manifest, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="sdk-assembly-verification-") as temporary:
        verify_assembly_artifact(args.artifact, Path(temporary) / "sdk")
    print("SDK assembly artifact verified")


if __name__ == "__main__":
    try:
        main()
    except (PipelineError, OSError, ValueError, KeyError) as error:
        raise SystemExit(str(error)) from None
