"""Verify a complete Fern download and return its portable signed receipt.

Verification precedes SDK execution and filtering. The only unsigned envelope
field accepted is keyid; it is removed before the receipt can be published.
"""
from __future__ import annotations

import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

from attestation import parse_json
from common import PipelineError, clean_env, require, sha256

FERN_KEY_SHA256 = "f2751e378c0e9a6bb48bd8f16d90e0b44c456a86374066f7cf2477e8c7626b8b"
BUILDER_ID = "https://buildwithfern.com/fiddle"
BUILD_TYPE = "https://buildwithfern.com/provenance/sdk-generation/v1"
PAYLOAD_TYPE = "application/vnd.in-toto+json"
RECEIPT_PATH = ".fern/provenance.json"
SUBJECT_NAME = "fern:generated-files"
SHA = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
MAX_RECEIPT = 1024 * 1024
MAX_FILE = 100 * 1024 * 1024
MAX_DOWNLOAD = 1024 * 1024 * 1024


def matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()), "Invalid " + label + " fields")


def command(*args):
    try:
        result = subprocess.run([str(arg) for arg in args], env=clean_env(), capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise PipelineError("Fern provenance verification command failed") from None
    require(result.returncode == 0, "Fern provenance verification command failed")
    return result.stdout


def read_download_files(directory: Path):
    """Read bounded regular files through directory FDs; never follow a link."""
    files, count, total = {}, 0, 0
    nofollow = os.O_RDONLY | os.O_NOFOLLOW

    def walk(descriptor, prefix, depth):
        nonlocal count, total
        require(depth <= 32, "Fern download directory depth exceeds limit")
        with os.scandir(descriptor) as entries:
            for entry in entries:
                count += 1
                name = entry.name
                require(count <= 20000 and name not in {"", ".", ".."} and name.lower() != ".git" and
                        "/" not in name and "\\" not in name and not any(ord(char) < 32 or ord(char) == 127 for char in name),
                        "Unsafe path or excessive entries in Fern download")
                name.encode("utf-8")
                relative = prefix + name
                info = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    child = os.open(name, nofollow | os.O_DIRECTORY, dir_fd=descriptor)
                    try:
                        walk(child, relative + "/", depth + 1)
                    finally:
                        os.close(child)
                else:
                    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "Fern download contains a link or special file")
                    limit = MAX_RECEIPT if relative == RECEIPT_PATH else MAX_FILE
                    require(info.st_size <= limit, "Fern download file exceeds size limit")
                    child = os.open(name, nofollow, dir_fd=descriptor)
                    with os.fdopen(child, "rb") as stream:
                        opened = os.fstat(stream.fileno())
                        require(stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1 and opened.st_ino == info.st_ino and opened.st_dev == info.st_dev,
                                "Fern download changed while reading")
                        data = stream.read(limit + 1)
                        after = os.fstat(stream.fileno())
                    require(len(data) == info.st_size and after.st_size == info.st_size and after.st_nlink == 1 and after.st_mtime_ns == info.st_mtime_ns,
                            "Fern download changed or exceeded limits while reading")
                    total += len(data)
                    require(total <= MAX_DOWNLOAD, "Fern download exceeds size limit")
                    files[relative] = data
    root = os.open(directory, nofollow | os.O_DIRECTORY)
    try:
        walk(root, "", 0)
    finally:
        os.close(root)
    require(RECEIPT_PATH in files and ".fern/metadata.json" in files, "Fern download lacks receipt or SDK metadata")
    return files


def download_tree(files):
    """Fern's downloaded tree: regular 100644 blobs, excluding only the receipt."""
    tree = {}
    for path, data in files.items():
        if path == RECEIPT_PATH:
            continue
        cursor = tree
        parts = path.split("/")
        require(all(part not in {"", ".", ".."} and part.lower() != ".git" for part in parts), "Unsafe Fern tree path")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
            require(isinstance(cursor, dict), "Ambiguous Fern tree path")
        require(parts[-1] not in cursor, "Duplicate Fern tree path")
        cursor[parts[-1]] = data

    def git_hash(kind, data):
        return hashlib.sha1(kind + b" " + str(len(data)).encode() + b"\0" + data).digest()

    def digest(node):
        entries = []
        for name, value in node.items():
            directory = isinstance(value, dict)
            key = name.encode() + (b"/" if directory else b"")
            entries.append((key, b"40000" if directory else b"100644", digest(value) if directory else git_hash(b"blob", value)))
        data = b"".join(mode + b" " + key.removesuffix(b"/") + b"\0" + oid for key, mode, oid in sorted(entries))
        return git_hash(b"tree", data)
    return digest(tree).hex()


def decode_base64(value):
    require(isinstance(value, str), "Invalid Fern base64 value")
    data = base64.b64decode(value, validate=True)
    require(base64.b64encode(data).decode() == value, "Noncanonical Fern base64 value")
    return data


def validate_signature_encoding(signature):
    # A canonical P-256 DER signature has two positive, minimally encoded integers.
    require(8 <= len(signature) <= 72 and signature[:2] == bytes((0x30, len(signature) - 2)), "Invalid Fern signature encoding")
    offset = 2
    order = int("ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551", 16)
    for _ in range(2):
        require(offset + 2 <= len(signature) and signature[offset] == 2, "Invalid Fern signature encoding")
        size = signature[offset + 1]
        value = signature[offset + 2:offset + 2 + size]
        require(1 <= size <= 33 and len(value) == size and value[0] < 128 and
                (size == 1 or value[0] != 0 or value[1] >= 128) and 0 < int.from_bytes(value, "big") < order,
                "Invalid Fern signature integer")
        offset += 2 + size
    require(offset == len(signature), "Trailing Fern signature bytes")


def verified_envelope(receipt, public_key, key_sha256):
    require(isinstance(receipt, bytes) and 0 < len(receipt) <= MAX_RECEIPT, "Invalid Fern receipt size")
    envelope = parse_json(receipt)
    fields(envelope, "payloadType payload signatures", "Fern envelope")
    require(envelope["payloadType"] == PAYLOAD_TYPE, "Unexpected Fern payload type")
    payload = decode_base64(envelope["payload"])
    signatures = envelope["signatures"]
    require(isinstance(signatures, list) and len(signatures) == 1, "Expected one Fern signature")
    signature = signatures[0]
    require(isinstance(signature, dict) and set(signature) in ({"sig"}, {"sig", "keyid"}) and
            ("keyid" not in signature or isinstance(signature["keyid"], str)), "Unexpected Fern signature fields")
    signature_bytes = decode_base64(signature["sig"])
    validate_signature_encoding(signature_bytes)
    require(isinstance(public_key, bytes) and 0 < len(public_key) <= 16384 and matches(SHA256, key_sha256), "Invalid Fern public key")
    kind = PAYLOAD_TYPE.encode()
    pae = b"DSSEv1 %d %s %d %s" % (len(kind), kind, len(payload), payload)
    with tempfile.TemporaryDirectory(prefix="fern-verification-") as temporary:
        root = Path(temporary)
        key, sig, message = root / "key.pem", root / "signature", root / "pae"
        key.write_bytes(public_key)
        sig.write_bytes(signature_bytes)
        message.write_bytes(pae)
        der = command("openssl", "pkey", "-pubin", "-in", key, "-outform", "DER")
        require(sha256(der) == key_sha256, "Fern public key does not match pinned key")
        require(len(der) == 91 and der.startswith(bytes.fromhex("3059301306072a8648ce3d020106082a8648ce3d03010703420004")),
                "Expected ECDSA P-256 Fern public key")
        command("openssl", "dgst", "-sha256", "-verify", key, "-signature", sig, message)
    portable = canonical({"payloadType": PAYLOAD_TYPE, "payload": envelope["payload"], "signatures": [{"sig": signature["sig"]}]})
    return parse_json(payload), portable


def validate_expected(expected):
    fields(expected, "job_id sdk_version cli_version generator inputs", "trusted Fern expectations")
    require(matches(UUID, expected["job_id"]) and matches(VERSION, expected["sdk_version"]) and
            matches(VERSION, expected["cli_version"]), "Invalid expected Fern job or version")
    generator = expected["generator"]
    fields(generator, "image version sha256", "trusted Fern generator")
    require(generator["image"] == "fernapi/fern-go-sdk" and matches(VERSION, generator["version"]) and
            matches(SHA256, generator["sha256"]), "Invalid expected Fern generator")
    names = {"fern:../2020-09-14.yml", "fern:openapi-overlay.yml", "fern:generators.yml", "fern:generators.yml#" + generator["image"]}
    inputs = expected["inputs"]
    require(isinstance(inputs, dict) and set(inputs) in (names, names | {"fern:ir.json"}) and
            all(matches(SHA256, value) for value in inputs.values()), "Missing or unexpected trusted Fern input hashes")


def validate_statement(statement, expected, tree):
    fields(statement, "_type subject predicateType predicate", "Fern statement")
    require(statement["_type"] == "https://in-toto.io/Statement/v1" and statement["predicateType"] == "https://slsa.dev/provenance/v1",
            "Unexpected Fern statement type")
    require(statement["subject"] == [{"name": SUBJECT_NAME, "digest": {"gitTree": tree}}], "Signed Fern download tree differs")
    predicate = statement["predicate"]
    fields(predicate, "buildDefinition runDetails", "Fern predicate")
    definition, details = predicate["buildDefinition"], predicate["runDetails"]
    fields(definition, "buildType externalParameters internalParameters resolvedDependencies", "Fern build definition")
    fields(details, "builder metadata", "Fern run details")
    require(definition["buildType"] == BUILD_TYPE and details["builder"] == {"id": BUILDER_ID}, "Untrusted Fern builder or build type")
    external, internal = definition["externalParameters"], definition["internalParameters"]
    fields(external, "organization api generator output", "Fern external parameters")
    fields(internal, "jobId taskId", "Fern internal parameters")
    generator = expected["generator"]
    require(external == {"organization": "plaid", "api": "api", "generator": {name: generator[name] for name in ("image", "version")},
                         "output": {"mode": "downloadFiles"}}, "Unexpected signed Fern request identity")
    require(internal["jobId"] == expected["job_id"] and matches(UUID, internal["taskId"]), "Signed Fern job differs from request")
    metadata = details["metadata"]
    fields(metadata, "invocationId finishedOn", "Fern invocation metadata")
    require(metadata["invocationId"] == expected["job_id"] + "/" + internal["taskId"], "Signed Fern invocation differs from request")
    finished = metadata["finishedOn"]
    require(isinstance(finished, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z", finished), "Invalid Fern completion timestamp")
    datetime.datetime.fromisoformat(finished.removesuffix("Z") + "+00:00")
    dependencies = definition["resolvedDependencies"]
    require(isinstance(dependencies, list), "Invalid signed Fern dependencies")
    inputs, images = {}, []
    for item in dependencies:
        require(isinstance(item, dict) and set(item) in ({"uri", "digest"}, {"name", "digest"}), "Unexpected signed Fern dependency")
        fields(item["digest"], "sha256", "Fern dependency digest")
        require(matches(SHA256, item["digest"]["sha256"]), "Invalid Fern dependency digest")
        if "uri" in item:
            images.append(item)
        else:
            name = item["name"]
            require(isinstance(name, str) and name not in inputs, "Duplicate signed Fern input")
            inputs[name] = item["digest"]["sha256"]
    require(images == [{"uri": "docker://docker.io/" + generator["image"] + ":" + generator["version"],
                        "digest": {"sha256": generator["sha256"]}}], "Signed Fern generator image differs")
    require(set(inputs) == set(expected["inputs"]) | {"fern:ir.json"} and
            all(inputs[name] == digest for name, digest in expected["inputs"].items()), "Signed Fern inputs differ from request")


def verify_download(directory: Path, public_key: bytes, expected: dict) -> dict:
    """Return {summary, receipt}; inputs/job identity must come from the launch."""
    return _verify_download(directory, public_key, expected, key_sha256=FERN_KEY_SHA256)


def _verify_download(directory, public_key, expected, *, key_sha256):
    """Only tests may substitute an ephemeral signer through this private helper."""
    try:
        validate_expected(expected)
        files = read_download_files(directory)
        statement, receipt = verified_envelope(files[RECEIPT_PATH], public_key, key_sha256)
        tree = download_tree(files)
        validate_statement(statement, expected, tree)
        metadata = parse_json(files[".fern/metadata.json"])
        generator = expected["generator"]
        module = "github.com/plaid/plaid-go/v" + expected["sdk_version"].split(".")[0]
        require(metadata["sdkVersion"] == "v" + expected["sdk_version"] and metadata["cliVersion"] == expected["cli_version"] and
                metadata["generatorName"] == generator["image"] and metadata["generatorVersion"] == generator["version"] and
                metadata["generatorConfig"]["module"]["path"] == module and metadata["generatorConfig"]["importPath"] == module,
                "Signed SDK metadata differs from the requested version, CLI, generator or module")
        summary = {"schema_version": 1, "output_mode": "downloadFiles", "receipt_sha256": sha256(receipt), "key_sha256": key_sha256,
                   "git_tree": tree, "sdk_version": expected["sdk_version"], "generator": dict(generator),
                   "inputs_sha256": sha256(canonical(expected["inputs"])), "job_id_sha256": sha256(expected["job_id"].encode())}
        return {"summary": summary, "receipt": receipt}
    except PipelineError:
        raise
    except (KeyError, TypeError, ValueError, UnicodeError, IndexError, AttributeError, OSError, RecursionError):
        raise PipelineError("Malformed Fern download, receipt or expectations") from None
