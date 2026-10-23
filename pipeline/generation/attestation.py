"""Generation attestation policy, matched to public scripts/release/policy.py.

No CLI path accepts preverified JSON. gh performs cryptographic verification;
identity and exact predicate/subject checks follow on its verified result.
"""
import os
import re
import json
import subprocess
from common import PipelineError, clean_env, require

SDK_REPO = "plaid/plaid-go"
CONFIG_REPO = "plaid/plaid-openapi"
SPEC_REPO = "plaid/plaid-openapi"
GEN_WORKFLOW = ".github/workflows/generate-go-sdk.yml"
ReleaseError = PipelineError

def run(*args):
    env = clean_env()
    if os.environ.get("GH_TOKEN"):
        env["GH_TOKEN"] = os.environ["GH_TOKEN"]
    result = subprocess.run([str(arg) for arg in args], env=env, capture_output=True, timeout=180)
    require(result.returncode == 0, "Cryptographic attestation verification failed; publication stopped")
    return result.stdout

def parse_json(data):
    def pairs(values):
        result = {}
        for key, value in values:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result

    def constant(_):
        raise ReleaseError("Non-JSON numeric constant")

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError) as error:
        raise ReleaseError("Invalid JSON") from error

def hex_value(value, length, label):
    require(isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value), f"Invalid {label}")

def decimal(value, label):
    require(isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*", value), f"Invalid {label}")

def version(value):
    numeric = r"(?:0|[1-9][0-9]*)"
    require(isinstance(value, str) and re.fullmatch(rf"{numeric}\.{numeric}\.{numeric}(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", value), "Invalid SDK version")
    require(int(value.split(".")[0]) >= 49, "Automated releases start at v49")
    for identifier in value.partition("-")[2].split("."):
        require(not (identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0")), "Invalid prerelease version")

def keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected.split()), f"Invalid {label} fields")

def validate_manifest(value):
    keys(value, "schema_version sdk source config generator legacy content_sha256 generation", "manifest")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "Unsupported manifest schema")
    keys(value["sdk"], "repository version module", "sdk")
    sdk = value["sdk"]
    require(sdk["repository"] == SDK_REPO, "Untrusted SDK repository")
    version(sdk["version"])
    require(sdk["module"] == f"github.com/{SDK_REPO}/v{sdk['version'].split('.')[0]}", "Incorrect module path")
    keys(value["source"], "repository commit path sha256", "source")
    require(value["source"]["repository"] == SPEC_REPO and value["source"]["path"] == "2020-09-14.yml", "Untrusted public spec location")
    keys(value["config"], "repository commit sha256", "config")
    require(value["config"]["repository"] == CONFIG_REPO, "Untrusted public config repository")
    for name in ("source", "config"):
        hex_value(value[name]["commit"], 40, f"{name} commit")
        hex_value(value[name]["sha256"], 64, f"{name} digest")
    require(value["source"]["commit"] == value["config"]["commit"], "Spec and config must share the same public commit")
    keys(value["generator"], "cli_version cli_sha256 image_digest", "generator")
    require(isinstance(value["generator"]["cli_version"], str) and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["generator"]["cli_version"]), "Invalid Fern CLI version")
    hex_value(value["generator"]["cli_sha256"], 64, "Fern CLI digest")
    keys(value["legacy"], "source_commit spec_sha256 tree_sha256 generator_digest", "legacy")
    hex_value(value["legacy"]["source_commit"], 40, "legacy generator source commit")
    for name in ("spec_sha256", "tree_sha256"):
        hex_value(value["legacy"][name], 64, f"legacy {name}")
    require(value["legacy"]["spec_sha256"] == value["source"]["sha256"], "Both SDKs must use the same public spec")
    for digest in (value["generator"]["image_digest"], value["legacy"]["generator_digest"]):
        require(isinstance(digest, str) and digest.startswith("sha256:"), "Generator must be digest-pinned")
        hex_value(digest[7:], 64, "generator image digest")
    hex_value(value["content_sha256"], 64, "content digest")
    keys(value["generation"], "repository workflow run_id", "generation")
    require(value["generation"]["repository"] == CONFIG_REPO and value["generation"]["workflow"] == GEN_WORKFLOW, "Untrusted generation workflow")
    decimal(value["generation"]["run_id"], "generation run ID")
    return value

def verified_attestation(artifact, bundle, *, repository, workflow, ref, commit, predicate_type, predicate, subjects, run_id):
    identity = f"https://github.com/{repository}/{workflow}@{ref}"
    arguments = ["gh", "attestation", "verify", str(artifact), "--bundle", str(bundle),
                 "--hostname", "github.com", "--repo", repository, "--cert-identity", identity,
                 "--cert-oidc-issuer", "https://token.actions.githubusercontent.com", "--source-ref", ref,
                 "--source-digest", commit, "--signer-digest", commit, "--deny-self-hosted-runners",
                 "--predicate-type", predicate_type, "--format", "json"]
    results = parse_json(run(*arguments))
    require(isinstance(results, list) and results, "No verified attestation returned")
    for result in results:
        verification = result.get("verificationResult", {})
        certificate = verification.get("signature", {}).get("certificate", {})
        statement = verification.get("statement", {})
        expected_certificate = {
            "subjectAlternativeName": identity,
            "issuer": "https://token.actions.githubusercontent.com",
            "buildSignerURI": identity,
            "buildSignerDigest": commit,
            "sourceRepositoryURI": f"https://github.com/{repository}",
            "sourceRepositoryDigest": commit,
            "sourceRepositoryRef": ref,
            "runnerEnvironment": "github-hosted",
            "sourceRepositoryVisibilityAtSigning": "public",
        }
        require(all(certificate.get(key) == value for key, value in expected_certificate.items()), "Verified certificate identity does not match release policy")
        invocation = rf"https://github\.com/{re.escape(repository)}/actions/runs/{re.escape(run_id)}(?:/attempts/[1-9][0-9]*)?"
        require(re.fullmatch(invocation, certificate.get("runInvocationURI", "")), "Attestation run ID mismatch")
        require(verification.get("verifiedTimestamps"), "Attestation has no verified timestamp")
        require(statement.get("_type") == "https://in-toto.io/Statement/v1" and statement.get("predicateType") == predicate_type, "Wrong attestation statement type")
        require(statement.get("predicate") == predicate, "Attestation predicate differs from manifest")
        actual_subjects = statement.get("subject")
        require(isinstance(actual_subjects, list) and len(actual_subjects) == len(subjects), "Unexpected attestation subjects")
        require(sorted(actual_subjects, key=lambda item: item.get("name", "")) == sorted(subjects, key=lambda item: item["name"]), "Attested subjects do not match artifacts")
    return results
