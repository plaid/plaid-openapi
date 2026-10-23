"""Check the SDK names and authentication shape of the effective Fern input."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import re

import yaml

from common import PipelineError, require

METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
AUTH_FIELDS = {"client_id", "secret"}
# The checked-in overlay uses member selectors and object wildcards. Stop for
# review if it adopts other JSONPath features instead of silently ignoring them.
TOKEN = re.compile(r"\.([A-Za-z_][A-Za-z0-9_-]*)|\['([^'\\]*)'\]|\[\*\]")


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        require(key not in result, f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def load(data: bytes) -> dict:
    try:
        result = yaml.load(data, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise PipelineError("Invalid YAML in spec or overlay") from exc
    require(isinstance(result, dict), "Spec and overlay must be YAML objects")
    return result


def targets(document: dict, expression: str) -> list[tuple[dict, str]]:
    require(isinstance(expression, str) and expression.startswith("$"), "Invalid overlay target")
    nodes = [(None, None, document)]
    position = 1
    while position < len(expression):
        match = TOKEN.match(expression, position)
        require(match is not None, f"Unsupported overlay target; review coverage check: {expression}")
        key = match[1] or match[2]
        selected = []
        for _, _, value in nodes:
            require(isinstance(value, dict), f"Overlay target traverses a non-object: {expression}")
            if key is None:
                selected.extend((value, k, v) for k, v in value.items())
            elif key in value:
                selected.append((value, key, value[key]))
        nodes = selected
        position = match.end()
    require(expression != "$", "Root overlay actions require coverage review")
    return [(parent, key) for parent, key, _ in nodes]


def merge(target: dict, update: dict) -> None:
    for key, value in update.items():
        if isinstance(target.get(key), dict) and isinstance(value, dict):
            merge(target[key], value)
        elif isinstance(target.get(key), list) and isinstance(value, list):
            target[key].extend(deepcopy(value))
        else:
            target[key] = deepcopy(value)


def apply_overlay(spec: dict, overlay: dict) -> dict:
    require(overlay.get("overlay") == "1.0.0" and isinstance(overlay.get("actions"), list), "Unsupported overlay format")
    result = deepcopy(spec)
    for action in overlay["actions"]:
        require(isinstance(action, dict), "Invalid overlay action")
        removing = action.get("remove") is True
        require(removing != ("update" in action), "Overlay action must update or remove")
        for parent, key in targets(result, action.get("target")):
            if removing:
                del parent[key]
            else:
                require(isinstance(parent[key], dict) and isinstance(action["update"], dict), "Overlay update must merge objects")
                merge(parent[key], action["update"])
    return result


def reference(document: dict, ref: str) -> dict:
    require(isinstance(ref, str) and ref.startswith("#/"), "Request references must resolve within the public spec")
    value = document
    for part in ref[2:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        require(isinstance(value, dict) and key in value, f"Unresolved request reference: {ref}")
        value = value[key]
    require(isinstance(value, dict), f"Request reference is not an object: {ref}")
    return value


def resolve(document: dict, value: dict, seen: frozenset[str] = frozenset()):
    """Yield a schema/reference and its same-level composition branches only."""
    require(isinstance(value, dict), "Request definition must be an object")
    yield value
    if "$ref" in value:
        ref = value["$ref"]
        if ref not in seen:
            yield from resolve(document, reference(document, ref), seen | {ref})
    for composition in ("allOf", "anyOf", "oneOf"):
        for branch in value.get(composition, []):
            yield from resolve(document, branch, seen)


def check(spec: dict, overlay: dict) -> int:
    effective = apply_overlay(spec, overlay)
    errors = []
    count = 0
    for path, path_item in effective.get("paths", {}).items():
        require(isinstance(path_item, dict) and "$ref" not in path_item, "Referenced path items require coverage review")
        for method, operation in path_item.items():
            if method not in METHODS:
                continue
            count += 1
            label = f"{method.upper()} {path}"
            require(isinstance(operation, dict), f"Invalid operation: {label}")
            group = operation.get("x-fern-sdk-group-name")
            names = [group] if isinstance(group, str) else group
            if not (isinstance(names, list) and names and all(isinstance(n, str) and n.strip() for n in names)):
                errors.append(f"{label}: missing explicit SDK group name")
            name = operation.get("x-fern-sdk-method-name")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{label}: missing explicit SDK method name")
            for body in resolve(effective, operation.get("requestBody", {})):
                for media, definition in body.get("content", {}).items():
                    for schema in resolve(effective, definition.get("schema", {})):
                        # Nested business objects may legitimately have these names;
                        # only top-level request credentials belong in auth headers.
                        remaining = AUTH_FIELDS & set(schema.get("properties", {}))
                        if remaining:
                            errors.append(f"{label} ({media}): body credentials remain: {', '.join(sorted(remaining))}")
    require(count > 0, "No operations found in effective SDK spec")
    require(not errors, "Incomplete Fern overlay coverage:\n" + "\n".join(sorted(set(errors))))
    return count


def validate(spec: bytes, overlay: bytes) -> int:
    return check(load(spec), load(overlay))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path("2020-09-14.yml"))
    parser.add_argument("--overlay", type=Path, default=Path("fern/openapi-overlay.yml"))
    args = parser.parse_args()
    try:
        print(f"Validated overlay coverage for {validate(args.spec.read_bytes(), args.overlay.read_bytes())} operations")
    except (PipelineError, OSError) as exc:
        parser.exit(1, str(exc) + "\n")
