"""Verify Fern's signed generation against trusted launch inputs before assembly.

Only a sanitized summary leaves this module. Receipts may contain private repository
and source identities; callers must retain their original bytes in private storage.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile

from attestation import parse_json
from common import PipelineError, canonical, clean_env, require, sha256

FERN_KEY_SHA256 = "f2751e378c0e9a6bb48bd8f16d90e0b44c456a86374066f7cf2477e8c7626b8b"
BUILDER_ID = "https://buildwithfern.com/fiddle"
BUILD_TYPE = "https://buildwithfern.com/provenance/sdk-generation/v1"
PAYLOAD_TYPE = "application/vnd.in-toto+json"
SHA = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
MAX_RECEIPT = 1024 * 1024


def matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def command(*args, cwd=None):
    """Never echo key paths, Git identities or subprocess output to public logs."""
    try:
        result = subprocess.run([str(arg) for arg in args], cwd=cwd,
                                env=clean_env(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1"),
                                capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise PipelineError("Fern provenance verification command failed") from None
    require(result.returncode == 0, "Fern provenance verification command failed")
    return result.stdout


def git_object(repo, kind, oid):
    require(matches(SHA, oid), "Invalid signed Git object identifier")
    data = command("git", "cat-file", kind, oid, cwd=repo)
    # Hash the actual bytes, with replacement objects and lazy network fetch disabled.
    actual = hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()
    require(actual == oid, "Signed Git object does not match its bytes")
    return data


def tree_entry(tree, wanted):
    entries, position = {}, 0
    while position < len(tree):
        space, nul = tree.find(b" ", position), tree.find(b"\0", position)
        require(position < space < nul and nul + 21 <= len(tree), "Malformed signed Git tree")
        mode, name = tree[position:space], tree[space + 1:nul]
        require(name and name not in entries and b"/" not in name, "Ambiguous signed Git tree")
        entries[name] = (mode, tree[nul + 1:nul + 21].hex())
        position = nul + 21
    require(wanted in entries, "Signed SDK metadata is missing")
    return entries[wanted]


def sdk_metadata(repo, tree):
    mode, oid = tree_entry(tree, b".fern")
    require(mode == b"40000", "Signed SDK metadata directory has unexpected mode")
    mode, oid = tree_entry(git_object(repo, "tree", oid), b"metadata.json")
    require(mode == b"100644", "Signed SDK metadata has unexpected mode")
    return parse_json(git_object(repo, "blob", oid))


def validate_expected(expected):
    require(isinstance(expected, dict) and set(expected) ==
            {"repository", "job_id", "sdk_version", "generator", "inputs"}, "Invalid trusted Fern expectations")
    require(isinstance(expected["repository"], str) and
            re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", expected["repository"]),
            "Invalid trusted Fern output repository")
    require(matches(UUID, expected["job_id"]), "Invalid trusted Fern job identifier")
    require(matches(VERSION, expected["sdk_version"]), "Invalid trusted SDK version")
    generator, inputs = expected["generator"], expected["inputs"]
    require(isinstance(generator, dict) and set(generator) == {"image", "version", "sha256"},
            "Invalid trusted Fern generator")
    require(isinstance(generator["image"], str) and
            re.fullmatch(r"fernapi/fern-[a-z0-9-]+-sdk", generator["image"]) and
            matches(VERSION, generator["version"]) and matches(SHA256, generator["sha256"]),
            "Invalid trusted Fern generator identity")
    require(isinstance(inputs, dict) and all(isinstance(name, str) and name.startswith("fern:") and
            matches(SHA256, digest) for name, digest in inputs.items()), "Invalid trusted Fern input hashes")
    required = {"fern:generators.yml", "fern:openapi-overlay.yml", "fern:generators.yml#" + generator["image"]}
    specs = set(inputs) - required - {"fern:ir.json"}
    require(required <= inputs.keys() and specs and all("#" not in name for name in specs),
            "Trusted Fern inputs must include spec, overlay, configuration and resolved generator entry")


def verify(receipt: bytes, public_key: bytes, sdk_repo: Path, commit: str, expected: dict) -> dict:
    """Verify original receipt bytes, pinned Fern key, raw Git output and launch policy.

    expected is constructed from trusted launch inputs: repository URL, job_id,
    sdk_version, generator {image, version, sha256}, inputs {Fern name: sha256}.
    It must never be copied from the unverified receipt.
    """
    return _verify(receipt, public_key, sdk_repo, commit, expected, key_sha256=FERN_KEY_SHA256)


def _verify(receipt, public_key, sdk_repo, commit, expected, *, key_sha256):
    """The private key-pin parameter supports ephemeral test signers only."""
    try:
        return _verify_checked(receipt, public_key, sdk_repo, commit, expected, key_sha256)
    except PipelineError:
        raise
    except (KeyError, TypeError, ValueError, UnicodeError, binascii.Error, IndexError, AttributeError):
        raise PipelineError("Malformed Fern provenance or trusted expectations") from None


def _verify_checked(receipt, public_key, sdk_repo, commit, expected, key_sha256):
    validate_expected(expected)
    require(isinstance(receipt, bytes) and 0 < len(receipt) <= MAX_RECEIPT, "Invalid Fern receipt size")
    require(isinstance(public_key, bytes) and 0 < len(public_key) <= 16384, "Invalid Fern public key size")
    require(matches(SHA, commit), "Expected exact raw SDK commit")
    require(matches(SHA256, key_sha256), "Invalid Fern public key pin")
    envelope = parse_json(receipt)
    require(isinstance(envelope, dict) and set(envelope) == {"payloadType", "payload", "signatures"},
            "Invalid Fern DSSE envelope")
    require(envelope["payloadType"] == PAYLOAD_TYPE, "Unexpected Fern DSSE payload type")
    require(isinstance(envelope["payload"], str), "Invalid Fern DSSE payload")
    payload = base64.b64decode(envelope["payload"], validate=True)
    kind = PAYLOAD_TYPE.encode()
    pae = b"DSSEv1 %d %s %d %s" % (len(kind), kind, len(payload), payload)
    signatures = envelope["signatures"]
    require(isinstance(signatures, list) and len(signatures) == 1, "Expected one Fern signature")
    signature = signatures[0]
    require(isinstance(signature, dict) and set(signature) <= {"keyid", "sig"} and
            isinstance(signature.get("sig"), str), "Invalid Fern signature")
    signature_bytes = base64.b64decode(signature["sig"], validate=True)
    with tempfile.TemporaryDirectory(prefix="fern-provenance-") as temporary:
        root = Path(temporary)
        key_path, signature_path, pae_path = root / "key.pem", root / "signature", root / "pae"
        key_path.write_bytes(public_key)
        signature_path.write_bytes(signature_bytes)
        pae_path.write_bytes(pae)
        der = command("openssl", "pkey", "-pubin", "-in", key_path, "-outform", "DER")
        require(sha256(der) == key_sha256, "Fern public key does not match pinned key")
        prefix = bytes.fromhex("3059301306072a8648ce3d020106082a8648ce3d03010703420004")
        require(len(der) == 91 and der.startswith(prefix), "Expected ECDSA P-256 Fern public key")
        command("openssl", "dgst", "-sha256", "-verify", key_path, "-signature", signature_path, pae_path)
    statement = parse_json(payload)
    require(statement["_type"] == "https://in-toto.io/Statement/v1" and
            statement["predicateType"] == "https://slsa.dev/provenance/v1", "Unexpected Fern statement type")
    subjects = statement["subject"]
    require(isinstance(subjects, list) and len(subjects) == 1, "Expected one signed SDK subject")
    subject = subjects[0]
    require(subject["name"] == expected["repository"], "Signed SDK repository differs from expected repository")
    require(subject["digest"]["gitCommit"] == commit, "Signed SDK commit differs from expected commit")
    tree_oid = subject["digest"]["gitTree"]
    require(matches(SHA, tree_oid), "Invalid signed SDK tree identifier")
    commit_bytes = git_object(sdk_repo, "commit", commit)
    require(commit_bytes.split(b"\n", 1)[0] == b"tree " + tree_oid.encode(), "Signed SDK tree differs from commit")
    tree_bytes = git_object(sdk_repo, "tree", tree_oid)
    predicate = statement["predicate"]
    definition, details = predicate["buildDefinition"], predicate["runDetails"]
    require(definition["buildType"] == BUILD_TYPE and details["builder"]["id"] == BUILDER_ID,
            "Untrusted Fern builder or build type")
    internal = definition["internalParameters"]
    require(internal["jobId"] == expected["job_id"] and matches(UUID, internal["taskId"]),
            "Signed Fern job differs from expected job")
    require(details["metadata"]["invocationId"] == expected["job_id"] + "/" + internal["taskId"],
            "Signed Fern invocation differs from expected job and task")
    external = definition["externalParameters"]
    require(external["output"]["repository"] == expected["repository"], "Signed Fern output repository differs")
    generator = expected["generator"]
    require(external["generator"] == {key: generator[key] for key in ("image", "version")},
            "Signed Fern generator differs from expected generator")
    dependencies = definition["resolvedDependencies"]
    require(isinstance(dependencies, list), "Invalid signed Fern dependencies")
    inputs, images = {}, []
    for item in dependencies:
        require(isinstance(item, dict) and set(item) in ({"uri", "digest"}, {"name", "digest"}),
                "Ambiguous signed Fern dependency")
        require(isinstance(item["digest"], dict) and set(item["digest"]) == {"sha256"} and
                matches(SHA256, item["digest"]["sha256"]), "Invalid signed Fern dependency digest")
        if "uri" in item:
            images.append(item)
        else:
            name = item["name"]
            require(isinstance(name, str) and name not in inputs, "Duplicate signed Fern input")
            inputs[name] = item["digest"]["sha256"]
    expected_image = {"uri": "docker://docker.io/" + generator["image"] + ":" + generator["version"],
                      "digest": {"sha256": generator["sha256"]}}
    require(images == [expected_image], "Signed Fern generator image digest differs or is ambiguous")
    require(set(inputs) == set(expected["inputs"]) | {"fern:ir.json"} and
            all(inputs[name] == digest for name, digest in expected["inputs"].items()),
            "Signed Fern inputs are missing, unexpected or different")
    metadata = sdk_metadata(sdk_repo, tree_bytes)
    require(metadata["sdkVersion"] in {expected["sdk_version"], "v" + expected["sdk_version"]} and
            metadata["generatorName"] == generator["image"] and metadata["generatorVersion"] == generator["version"],
            "Signed SDK metadata differs from expected version or generator")
    return {"schema_version": 1, "receipt_sha256": sha256(receipt), "key_sha256": key_sha256,
            "git_commit": commit, "git_tree": tree_oid, "sdk_version": expected["sdk_version"],
            "generator": dict(generator), "inputs_sha256": sha256(canonical(dict(sorted(expected["inputs"].items())))),
            "job_id_sha256": sha256(expected["job_id"].encode())}
