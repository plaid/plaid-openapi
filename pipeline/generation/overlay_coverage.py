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
FIX_COMMAND = "python3 pipeline/generation/overlay_coverage.py --fix"
NAME_TARGET = re.compile(r"\$\.paths\['([^']+)'\]\.([a-z]+)")
SCHEMA_CREDENTIAL_TARGET = re.compile(r"\$\.components\.schemas\.([A-Za-z0-9_]+)\.properties\.(client_id|secret)")


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


def coverage_errors(spec: dict, overlay: dict) -> tuple[int, list[str]]:
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
    return count, sorted(set(errors))


def check(spec: dict, overlay: dict) -> int:
    count, errors = coverage_errors(spec, overlay)
    require(not errors, "Incomplete Fern overlay coverage:\n" + "\n".join(errors) +
            f"\n\nRun `{FIX_COMMAND}` to add the missing entries, then review the suggested names.")
    return count


def validate(spec: bytes, overlay: bytes) -> int:
    return check(load(spec), load(overlay))


def credential_locations(effective: dict, path: str, method: str, operation: dict):
    """Yield (overlay target, credential) pairs a mechanical removal can fix."""
    body = operation.get("requestBody", {})
    for media, definition in body.get("content", {}).items():
        schema = definition.get("schema", {})
        ref = schema.get("$ref", "")
        if ref.startswith("#/components/schemas/") and "/" not in ref[len("#/components/schemas/"):]:
            location = f"$.components.schemas.{ref.rsplit('/', 1)[1]}"
            schema = reference(effective, ref)
        elif "$ref" not in schema:
            location = f"$.paths['{path}'].{method}.requestBody.content['{media}'].schema"
        else:
            continue
        for field in sorted(AUTH_FIELDS & set(schema.get("properties", {}))):
            yield f"{location}.properties.{field}", field


def words(segment: str) -> str:
    return "".join(word[:1].upper() + word[1:] for word in segment.split("_"))


def suggest_name(path: str, named: dict[str, tuple[list[str], str]]) -> tuple[list[str], str] | None:
    """Suggest a group from the closest named sibling path and a verb-first method name."""
    *body, verb = [segment for segment in path.split("/") if segment]
    shared, siblings = 0, []
    for other, name in named.items():
        prefix = [segment for segment in other.split("/") if segment][:-1]
        length = next((i for i, (a, b) in enumerate(zip(prefix, body)) if a != b), min(len(prefix), len(body)))
        if length > shared:
            shared, siblings = length, []
        if length == shared and length:
            siblings.append((prefix, name))
    if not siblings:
        return None
    groups = [name[0] for _, name in siblings]
    group = max(groups, key=groups.count)
    # A sibling whose method is only its verb shows how much of the path the group covers.
    covered = [len(prefix) for other, (g, method) in named.items()
               for prefix in [[s for s in other.split("/") if s][:-1]]
               if g == group and method == other.rsplit("/", 1)[1] and prefix == body[:len(prefix)]]
    first, *rest = verb.split("_")
    return group, first + "".join(map(words, rest)) + "".join(map(words, body[max(covered, default=shared):]))


def action_blocks(text: str) -> list[tuple[str, str]]:
    blocks = re.split(r"(?m)^(?=  - target: )", text)
    return [(re.match(r"  - target: (\S+)", block)[1] if block.startswith("  - target: ") else "", block)
            for block in blocks]


def insert(blocks: list[tuple[str, str]], target: str, block: str, section: re.Pattern, key) -> None:
    members = [i for i, (existing, text) in enumerate(blocks) if section.fullmatch(existing) and
               (section is not NAME_TARGET or "x-fern-sdk-method-name" in text)]
    require(members, f"No existing overlay section for {target}; add it by hand")
    later = [i for i in members if key(blocks[i][0]) > key(target)]
    blocks.insert(later[0] if later else members[-1] + 1, (target, block))


def fix(spec_data: bytes, overlay_text: str) -> tuple[str, list[str]]:
    """Return the overlay with missing names and credential removals added, plus the names to review."""
    spec, overlay = load(spec_data), load(overlay_text.encode())
    effective = apply_overlay(spec, overlay)
    named = {path: (operation["x-fern-sdk-group-name"], operation["x-fern-sdk-method-name"])
             for path, item in effective.get("paths", {}).items()
             for method, operation in item.items()
             if method in METHODS and isinstance(operation, dict) and operation.get("x-fern-sdk-method-name")}
    blocks, suggested = action_blocks(overlay_text), []
    for path, item in sorted(effective.get("paths", {}).items()):
        for method, operation in item.items():
            if method not in METHODS or not isinstance(operation, dict):
                continue
            if not (operation.get("x-fern-sdk-group-name") or operation.get("x-fern-sdk-method-name")):
                name = suggest_name(path, named)
                if name:
                    group, method_name = name
                    target = f"$.paths['{path}'].{method}"
                    entries = "".join(f"        - {g}\n" for g in group)
                    insert(blocks, target, f"  - target: {target}\n    update:\n      x-fern-sdk-group-name:\n"
                           f"{entries}      x-fern-sdk-method-name: {method_name}\n", NAME_TARGET, lambda t: t)
                    suggested.append(f"{method.upper()} {path}: {'.'.join(group)}.{method_name}")
            for target, _ in credential_locations(effective, path, method, operation):
                if target not in (existing for existing, _ in blocks):
                    section = SCHEMA_CREDENTIAL_TARGET if SCHEMA_CREDENTIAL_TARGET.fullmatch(target) else re.compile(r".*\.properties\.(client_id|secret)")
                    insert(blocks, target, f"  - target: {target}\n    remove: true\n", section, lambda t: t)
    result = "".join(block for _, block in blocks)
    _, errors = coverage_errors(spec, load(result.encode()))
    require(not errors, "These overlay entries need to be added by hand:\n" + "\n".join(errors))
    return result, suggested


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path("2020-09-14.yml"))
    parser.add_argument("--overlay", type=Path, default=Path("fern/openapi-overlay.yml"))
    parser.add_argument("--fix", action="store_true", help="add missing names and credential removals to the overlay")
    args = parser.parse_args()
    try:
        if args.fix:
            text, suggested = fix(args.spec.read_bytes(), args.overlay.read_text())
            args.overlay.write_text(text)
            print("Review these suggested SDK names; they become public method names:" if suggested
                  else "No SDK names needed review.")
            print("\n".join(f"  {name}" for name in suggested))
        print(f"Validated overlay coverage for {validate(args.spec.read_bytes(), args.overlay.read_bytes())} operations")
    except (PipelineError, OSError) as exc:
        parser.exit(1, str(exc) + "\n")
