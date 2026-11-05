"""Read a private Fern PR with an explicit machine credential, then verify it.

The receipt and repository details stay in the private snapshot. Only the
verifier's sanitized summary may be copied into a public artifact. This module
never invokes gh, fetches Git objects, executes SDK code, or writes to GitHub.
"""

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

import fern_provenance

MAX_RESPONSE_BYTES = 1024 * 1024
MAX_BODY_BYTES = 256 * 1024
MAX_RECEIPT_BYTES = 128 * 1024
TIMEOUT_SECONDS = 30
START = "<!-- fern-provenance-start -->"
END = "<!-- fern-provenance-end -->"


class DeliveryError(RuntimeError):
    """Safe to log: messages never include response bodies, URLs or credentials."""


def require(condition, message):
    if not condition:
        raise DeliveryError(message)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("invalid number")


def _json(data):
    try:
        return json.loads(data, object_pairs_hook=_unique_pairs,
                          parse_constant=_reject_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise DeliveryError("Private SDK response contains invalid JSON") from None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        raise DeliveryError("Private SDK API redirects are forbidden")


def _get(path, machine_token):
    require(isinstance(machine_token, str) and machine_token and
            all(32 < ord(char) < 127 for char in machine_token), "An explicit machine credential is required")
    url = "https://api.github.com/" + path
    request = urllib.request.Request(url, method="GET", headers={
        "Authorization": "Bearer " + machine_token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "plaid-sdk-generation",
    })
    # Do not forward the credential through an ambient proxy or a redirected URL.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            require(response.geturl() == url, "Private SDK API returned a different URL")
            require(response.getcode() == 200, "Private SDK API did not return success")
            size = response.headers.get("Content-Length")
            require(size is None or (size.isdecimal() and int(size) <= MAX_RESPONSE_BYTES),
                    "Private SDK response exceeds the size limit")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        # Do not read or include GitHub's error body or URL in an exception.
        code = error.code if type(error.code) is int else 0
        error.close()
        raise DeliveryError(f"Private SDK API read failed (HTTP {code})") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise DeliveryError("Private SDK API read failed") from None
    require(len(body) <= MAX_RESPONSE_BYTES, "Private SDK response exceeds the size limit")
    result = _json(body)
    require(isinstance(result, dict), "Private SDK API returned an unexpected object")
    return result


def extract_receipt(body):
    require(isinstance(body, str), "Private SDK PR body is missing or too large")
    try:
        body_bytes = body.encode()
    except UnicodeError:
        raise DeliveryError("Private SDK PR body contains invalid text") from None
    require(len(body_bytes) <= MAX_BODY_BYTES, "Private SDK PR body is missing or too large")
    require(body.count(START) == body.count(END) == 1, "Expected exactly one Fern provenance block")
    match = re.search(re.escape(START) + r"\s*```json\s*(.*?)\s*```\s*" + re.escape(END), body, re.S)
    require(match is not None, "Fern provenance block is malformed")
    receipt = match.group(1).encode()
    require(0 < len(receipt) <= MAX_RECEIPT_BYTES, "Fern provenance receipt exceeds the size limit")
    require(isinstance(_json(receipt), dict), "Fern provenance envelope must be an object")
    return receipt


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _repository(value, repository, repository_id):
    require(isinstance(value, dict) and type(value.get("id")) is int and value["id"] == repository_id
            and value.get("full_name") == repository and value.get("private") is True
            and value.get("fork") is False, "Private SDK repository identity or visibility changed")


@dataclass(frozen=True)
class PullSnapshot:
    # All fields are private operational data; even repr() must not expose them.
    repository: str = field(repr=False)
    repository_id: int = field(repr=False)
    number: int = field(repr=False)
    base: str = field(repr=False)
    head: str = field(repr=False)
    base_ref: str = field(repr=False)
    head_ref: str = field(repr=False)
    body_sha256: str = field(repr=False)
    receipt: bytes = field(repr=False)


@dataclass(frozen=True)
class VerifiedDelivery:
    snapshot: PullSnapshot = field(repr=False)
    public_summary: dict


def fetch_snapshot(*, repository, repository_id, number, expected_base, machine_token, expected_head=None):
    """Read only; callers must supply an installation/service token explicitly."""
    require(isinstance(repository, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            and all(part not in (".", "..") for part in repository.split("/")), "Invalid configured SDK repository")
    require(type(repository_id) is int and repository_id > 0 and type(number) is int and number > 0,
            "Invalid configured SDK repository or PR ID")
    require(_sha(expected_base) and (expected_head is None or _sha(expected_head)), "Expected fixed SDK commit identities")
    prefix = "repos/" + repository
    _repository(_get(prefix, machine_token), repository, repository_id)
    pull = _get(prefix + "/pulls/" + str(number), machine_token)
    require(type(pull.get("number")) is int and pull["number"] == number
            and pull.get("state") == "open" and pull.get("merged") is False, "Private SDK PR is not the expected open candidate")
    base, head = pull.get("base"), pull.get("head")
    require(isinstance(base, dict) and isinstance(head, dict), "Private SDK PR has no base or head")
    for side in (base, head):
        _repository(side.get("repo"), repository, repository_id)
        require(_sha(side.get("sha")) and isinstance(side.get("ref"), str) and side["ref"], "Private SDK PR has invalid commit metadata")
    require(base["sha"] == expected_base and (expected_head is None or head["sha"] == expected_head),
            "Private SDK PR base or head differs from the requested candidate")
    body = pull.get("body")
    receipt = extract_receipt(body)
    return PullSnapshot(repository, repository_id, number, base["sha"], head["sha"], base["ref"], head["ref"],
                        hashlib.sha256(body.encode()).hexdigest(), receipt)


def fetch_and_verify(*, repository, repository_id, number, expected_base, machine_token,
                     sdk_repo: Path, public_key: bytes, expected: dict, expected_head=None):
    """Verify the original private receipt and reject PR changes during verification.

    sdk_repo is an already-fetched Git object cache. expected is built from the
    current generation request, including its independent Fern job ID. Fetching
    objects or executing generated code is intentionally outside this boundary.
    """
    require(isinstance(expected, dict) and expected.get("repository") == "https://github.com/" + repository,
            "Expected provenance repository differs from the retrieval target")
    arguments = dict(repository=repository, repository_id=repository_id, number=number,
                     expected_base=expected_base, expected_head=expected_head, machine_token=machine_token)
    snapshot = fetch_snapshot(**arguments)
    try:
        summary = fern_provenance.verify(snapshot.receipt, public_key, sdk_repo, snapshot.head, expected)
    except Exception:
        raise DeliveryError("Private Fern provenance verification failed") from None
    require(fetch_snapshot(**arguments) == snapshot, "Private SDK PR changed during provenance verification")
    return VerifiedDelivery(snapshot, summary)
