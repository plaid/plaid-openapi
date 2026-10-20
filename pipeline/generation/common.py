"""Shared, dependency-free boundaries for the public generation pipeline."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import urllib.error
import urllib.request

MANIFEST = ".sdk-release/manifest.json"
BUNDLE = ".sdk-release/generation.bundle.json"
PREDICATE = "https://plaid.com/attestations/sdk-generation/v1"
WORKFLOW = ".github/workflows/generate-go-sdk.yml"
SHA = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")
PRESERVED_PREFIXES = (".github/", "scripts/release/")
PRESERVED_FILES = {
    ".fernignore", "README.md", "CHANGELOG.md", "LICENSE", ".circleci/config.yml",
    "internal/caller.go", "internal/destination.go", "internal/destination_test.go",
    "credential_destination_test.go", "core/custom_endpoint.go", "option/custom_endpoint.go",
    "retry_default_test.go",
    "wire_test_security_test.go",
    "transfer_diligence_upload_test.go",
}


class PipelineError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PipelineError(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_env(**extra: str) -> dict[str, str]:
    """Allow normal tool/cache paths, never forward publishing or Plaid credentials."""
    names = ("PATH", "HOME", "TMPDIR", "DOCKER_HOST", "DOCKER_CONFIG", "GOCACHE", "GOMODCACHE")
    env = {name: os.environ[name] for name in names if name in os.environ}
    env.update({"GOWORK": "off", "GOFLAGS": "", "GOENV": "off", "GOSUMDB": "sum.golang.org", "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
                "GOPROXY": "https://proxy.golang.org,direct", "GOTOOLCHAIN": "local",
                "FERN_DISABLE_TELEMETRY": "true", "FERN_TELEMETRY_DISABLED": "1"})
    env.update(extra)
    return env


def run(argv: list[str], cwd: Path | None = None, *, env: dict[str, str] | None = None,
        timeout: int = 900, log: Path | None = None) -> bytes:
    result = subprocess.run(argv, cwd=cwd, env=env or clean_env(), capture_output=True, timeout=timeout)
    if log:
        log.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        # Commands are deliberately credential-free; publishing passes tokens only in env.
        detail = "output withheld from public logs" if log else (result.stderr or result.stdout).decode(errors="replace")[-2500:]
        raise PipelineError(f"{argv[0]} failed ({result.returncode}): {detail}")
    return result.stdout


def git(repo: Path, *args: str) -> str:
    return run(["git", *args], repo).decode().strip()


def check_sha(value: str) -> str:
    require(bool(SHA.fullmatch(value)), "Expected an exact lowercase 40-character commit SHA")
    return value


def version_tuple(value: str) -> tuple[int, int, int]:
    match = VERSION.fullmatch(value)
    require(match is not None, "Expected stable SDK version MAJOR.MINOR.PATCH without a v prefix")
    return tuple(map(int, match.groups()))  # type: ignore[union-attr,return-value]


def propose_version(tags: list[str], major: int, override: str = "") -> str:
    versions = []
    for tag in tags:
        match = VERSION.fullmatch(tag.removeprefix("v"))
        if match and int(match[1]) == major:
            versions.append(tuple(map(int, match.groups())))
    if override:
        proposed = version_tuple(override)
        require(proposed[0] == major, "Major overrides require a reviewed change to the configured major")
        require(not versions or proposed > max(versions), "SDK version must exceed the latest published version")
        return override
    return f"{major}.{max(versions)[1] + 1}.0" if versions else f"{major}.0.0"


def spec_version(data: bytes) -> tuple[int, ...]:
    text = data.decode("utf-8")
    info = re.search(r"^info:\s*\n((?:[ \t].*\n|\s*\n)*)", text, re.MULTILINE)
    require(info is not None, "Public spec has no YAML info object")
    versions = re.findall(r'^  version:\s*[\'"]?(\d{4}-\d{2}-\d{2})_(\d+)\.(\d+)\.(\d+)[\'"]?\s*$', info[1], re.MULTILINE)
    require(len(versions) == 1, "Expected one dated Plaid info.version in the spec")
    date, major, minor, patch = versions[0]
    return tuple(map(int, date.split("-"))) + (int(major), int(minor), int(patch))


def safe_path(name: str) -> str:
    path = PurePosixPath(name)
    require(bool(name) and not path.is_absolute() and ".." not in path.parts and
            "." not in path.parts and str(path) == name and "\\" not in name,
            f"Unsafe artifact path: {name!r}")
    require(all(part.lower() != ".git" for part in path.parts), "Artifact must not contain Git metadata")
    require(not any(ord(char) < 32 or ord(char) == 127 for char in name), "Control character in artifact path")
    return name


def blobs(repo: Path, identifiers: list[str]) -> dict[str, bytes]:
    identifiers = list(dict.fromkeys(identifiers))
    process = subprocess.run(["git", "cat-file", "--batch"], cwd=repo, env=clean_env(),
                             input=("\n".join(identifiers) + "\n").encode(), capture_output=True, timeout=180)
    require(process.returncode == 0, "Could not read SDK Git objects")
    data, offset, result = process.stdout, 0, {}
    for oid in identifiers:
        end = data.index(b"\n", offset)
        actual, kind, raw_size = data[offset:end].split()
        size = int(raw_size)
        require(actual.decode() == oid and kind == b"blob" and size <= 100 * 1024 * 1024, "Unexpected Git blob")
        start = end + 1
        result[oid] = data[start:start + size]
        require(len(result[oid]) == size and data[start + size:start + size + 1] == b"\n", "Truncated Git blob")
        offset = start + size + 1
    return result


def entries(repo: Path, *, ref: str | None = None) -> list[list[str]]:
    """Use Git modes and blob bytes, never filesystem traversal or symlink following."""
    records = run(["git", "ls-tree", "-rz", ref], repo) if ref else run(["git", "ls-files", "--stage", "-z"], repo)
    selected = []
    for record in records.split(b"\0"):
        if not record:
            continue
        meta, path = record.split(b"\t", 1)
        fields = meta.decode().split()
        mode, oid = (fields[0], fields[2]) if ref else (fields[0], fields[1])
        require(mode in {"100644", "100755"}, "SDK contains a symlink, submodule or unsupported Git mode")
        if not ref:
            require(fields[2] == "0", "SDK index has unresolved merge entries")
        name = safe_path(path.decode("utf-8"))
        if name.startswith(".sdk-release/"):
            require(name in {MANIFEST, BUNDLE}, "Unexpected .sdk-release file")
            continue
        selected.append((name, mode, oid))
    values = blobs(repo, [oid for _, _, oid in selected])
    return sorted([[name, mode, sha256(values[oid])] for name, mode, oid in selected])


def content(repo: Path, *, ref: str | None = None) -> tuple[bytes, str]:
    data = canonical(entries(repo, ref=ref))
    return data, sha256(data)


def protected(name: str) -> bool:
    return name in PRESERVED_FILES or name.startswith(PRESERVED_PREFIXES)


def protected_state(repo: Path) -> dict[str, tuple[str, str]]:
    return {path: (mode, digest) for path, mode, digest in entries(repo) if protected(path)}


def public_get(url: str, *, token: str | None = None, payload: object | None = None,
               method: str | None = None) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "plaid-sdk-generation"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = None if payload is None else canonical(payload)
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise PipelineError(f"GitHub request failed with HTTP {exc.code}: {url}") from None


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def archive_sdk(repo: Path, output: Path) -> None:
    """Package staged bytes with deterministic modes; no .git or untracked files."""
    with tarfile.open(output, "w:gz") as archive:
        records = run(["git", "ls-files", "--stage", "-z"], repo)
        parsed = []
        for record in records.split(b"\0"):
            if record:
                meta, path = record.split(b"\t", 1)
                mode, oid, stage = meta.decode().split()
                parsed.append((mode, oid, stage, path))
        values = blobs(repo, [oid for _, oid, _, _ in parsed])
        import io
        for mode, oid, stage, path in parsed:
            require(mode in {"100644", "100755"} and stage == "0", "Unsafe SDK index entry")
            name = safe_path(path.decode())
            data = values[oid]
            member = tarfile.TarInfo(name)
            member.mode = int(mode[-3:], 8)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))


def extract_sdk(archive: Path, target: Path) -> None:
    require(not target.exists(), "Refusing to overwrite an existing SDK directory")
    target.mkdir(parents=True)
    with tarfile.open(archive, "r:gz") as source:
        seen = set()
        total = 0
        for member in source:
            name = safe_path(member.name)
            require(name not in seen and member.isfile() and member.mode in {0o644, 0o755}, "Unsafe or duplicate archive entry")
            seen.add(name)
            total += member.size
            require(member.size <= 100 * 1024 * 1024 and total <= 1024 * 1024 * 1024 and len(seen) <= 20000,
                    "SDK archive exceeds bounded file/count/size limits")
            output = target / name
            output.parent.mkdir(parents=True, exist_ok=True)
            stream = source.extractfile(member)
            require(stream is not None, "Missing archive bytes")
            output.write_bytes(stream.read())
            output.chmod(member.mode)
