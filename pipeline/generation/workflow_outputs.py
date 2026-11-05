"""Emit only bounded, validated workflow outputs from generation results."""
import argparse
import os
from pathlib import Path
import re

from attestation import parse_json
from common import require


def outputs(value):
    require(isinstance(value, dict), "Expected a generation result")
    status = value.get("status")
    require(status in {"ready", "assembled", "generated", "needs-major", "unchanged", "awaiting-release"}, "Unexpected generation status")
    rehearsal = value.get("rehearsal")
    require(type(rehearsal) is bool, "Generation result is missing its rehearsal state")
    mode, version = value.get("mode", ""), value.get("version", "")
    require(mode in {"", "local", "fern-hosted"}, "Unexpected generation mode")
    require(isinstance(version, str) and (version == "" or re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version)), "Unexpected result version")
    digest, subject = value.get("content_sha256", ""), value.get("subject_name", "")
    require(isinstance(digest, str) and (digest == "" or re.fullmatch(r"[0-9a-f]{64}", digest)), "Unexpected result digest")
    require(isinstance(subject, str) and (subject == "" or re.fullmatch(r"plaid-go-v[0-9]+\.[0-9]+\.[0-9]+-(?:fern-)?source", subject)), "Unexpected result subject")
    require(bool(digest) == bool(subject), "Digest and subject must be present together")
    return {"status": status, "mode": mode, "version": version, "rehearsal": str(rehearsal).lower(), "digest": digest, "subject": subject}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    value = parse_json(args.result.read_bytes())
    with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
        stream.write("".join(key + "=" + item + "\n" for key, item in outputs(value).items()))


if __name__ == "__main__":
    main()
