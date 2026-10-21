#!/usr/bin/env python3
"""Regenerate the public legacy client, staging validation before any SDK writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import yaml

SOURCE_COMMIT = "7c6ddb9f8e1b2bc59f9761b2aa3878a9452779ff"
GENERATOR_DIGEST = "sha256:74d276d0a094327f3f833d6bc25fa1165cef33ce5204f05496c317314717e892"
IMAGE = "openapitools/openapi-generator-cli@" + GENERATOR_DIGEST
# This identifies the preserved legacy client, independently of the v49 root module.
PACKAGE_VERSION = "48.0.0"
HERE = Path(__file__).resolve().parent


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys rather than silently rewriting an ambiguous spec."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError("spec mappings require unique string keys")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"symlink path is not supported: {part}")
    return path


def check_tree(root):
    for directory, dirs, files in os.walk(root):
        # Git metadata is neither copied nor modified.
        if Path(directory) == root and '.git' in dirs:
            dirs.remove('.git')
        for name in dirs + files:
            path = Path(directory) / name
            if path.is_symlink() or not (path.is_dir() or path.is_file()):
                raise ValueError(f"unsupported SDK entry: {path}")


def prepare_spec(raw):
    spec = yaml.load(raw, Loader=UniqueLoader)
    if not isinstance(spec, dict) or not str(spec.get('openapi', '')).startswith('3.0.'):
        raise ValueError("expected an OpenAPI 3.0 document")
    schemas = spec.get('components', {}).get('schemas')
    if not isinstance(schemas, dict) or not schemas or not spec.get('paths'):
        raise ValueError("spec requires nonempty paths and component schemas")

    if any(not isinstance(schema, dict) for schema in schemas.values()):
        raise ValueError('component schemas must be objects')
    # Only local schema references are supported: the generator must not fetch
    # unreviewed remote inputs or files outside its read-only input directory.
    def check_refs(node):
        if isinstance(node, dict):
            if 'oneOf' in node and not any(node is schema for schema in schemas.values()):
                raise ValueError('oneOf must be a named component schema')
            for key, value in node.items():
                if key == '$ref':
                    if not isinstance(value, str) or not value.startswith('#/'):
                        raise ValueError('external references are not supported')
                    target = spec
                    for segment in value[2:].split('/'):
                        segment = segment.replace('~1', '/').replace('~0', '~')
                        if not isinstance(target, dict) or segment not in target:
                            raise ValueError(f'unresolved reference: {value}')
                        target = target[segment]
                check_refs(value)
        elif isinstance(node, list):
            for value in node:
                check_refs(value)
    check_refs(spec)

    for name, schema in schemas.items():
        if 'oneOf' not in schema:
            continue
        alternatives = schema['oneOf']
        discriminator = schema.get('discriminator', {})
        prop = discriminator.get('propertyName')
        mapping = discriminator.get('mapping')
        if not isinstance(alternatives, list) or len(alternatives) < 2 or not prop or not isinstance(mapping, dict):
            raise ValueError(f'{name}: oneOf requires an explicit discriminator mapping')
        refs = []
        for alternative in alternatives:
            if not isinstance(alternative, dict) or set(alternative) != {'$ref'}:
                raise ValueError(f'{name}: oneOf branches must be schema references')
            ref = alternative['$ref']
            if not ref.startswith('#/components/schemas/'):
                raise ValueError(f'{name}: unsupported oneOf reference')
            refs.append(ref)
        if len(set(refs)) != len(refs) or set(mapping.values()) != set(refs) or len(mapping) != len(refs):
            raise ValueError(f'{name}: discriminator must map each branch exactly once')
        for wire_value, ref in mapping.items():
            branch = schemas[ref.rsplit('/', 1)[1]]
            field = branch.get('properties', {}).get(prop, {})
            if prop not in branch.get('required', []) or field.get('type') != 'string' or field.get('enum') != [wire_value]:
                raise ValueError(f'{name}: branch discriminator must be required and have its single mapped value')
        # Public model_oneof.mustache selects strict dispatch using this marker.
        schema['x-plaid-sdk-one-of-interface'] = True
        branches = []
        for value, ref in sorted(mapping.items()):
            model = ref.rsplit('/', 1)[1]
            if not re.fullmatch(r'[A-Z][A-Za-z0-9]*', model):
                raise ValueError(f'{name}: unsupported Go branch identifier {model}')
            branches.append({'mappingName': value, 'modelName': model})
        schema['x-plaid-sdk-one-of-mapping'] = branches
    return spec


def tree_sha256(root):
    entries = []
    for path in sorted(root.rglob('*')):
        if path.is_file():
            mode = '100755' if path.stat().st_mode & 0o111 else '100644'
            entries.append(['legacy/' + path.relative_to(root).as_posix(), mode, sha(path.read_bytes())])
    return sha(json.dumps(entries, separators=(',', ':')).encode())


def subprocess_env():
    # Go tests need local toolchain/cache settings, not publisher or Plaid
    # credentials from the invoking shell. Ignore persisted Go environment too.
    allowed = (
        'PATH', 'HOME', 'TMPDIR', 'TMP', 'TEMP', 'SYSTEMROOT',
        'DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_CONFIG',
        'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH',
        'GOROOT', 'GOPATH', 'GOCACHE', 'GOMODCACHE', 'GOTOOLCHAIN',
        'GOOS', 'GOARCH', 'CGO_ENABLED',
    )
    env = {name: os.environ[name] for name in allowed if name in os.environ}
    env.update(GOWORK='off', GOENV='off', GOFLAGS='')
    return env


def run(args, cwd=None):
    subprocess.run(args, cwd=cwd, env=subprocess_env(), check=True)


def validate_output(output):
    check_tree(output)
    files = sorted(output.glob('*.go'))
    required = {'api_plaid.go', 'client.go', 'configuration.go', 'response.go', 'utils.go'}
    if not required <= {p.name for p in files} or not any(p.name.startswith('model_') for p in files):
        raise ValueError('generator did not produce the complete Go client')
    for path in files:
        text = path.read_text()
        if not re.search(r'^package plaid$', text, re.M) or 'Code generated by OpenAPI Generator' not in text or path.name.endswith('_test.go'):
            raise ValueError(f'unexpected generated Go file: {path.name}')
    if f'Plaid Go v{PACKAGE_VERSION}' not in (output / 'configuration.go').read_text():
        raise ValueError('legacy client identity was not preserved')
    return files


def generate(spec_path, sdk, module, manifest):
    spec_path, sdk, manifest = map(checked_path, (spec_path, sdk, manifest))
    if not spec_path.is_file() or not sdk.is_dir() or not (sdk / 'go.mod').is_file():
        raise ValueError('spec file and existing SDK module are required')
    if sdk == manifest or sdk in manifest.parents or not manifest.parent.is_dir() or manifest.exists():
        raise ValueError('manifest must be a new file outside SDK, in an existing directory')
    if module != 'github.com/plaid/plaid-go/v49':
        raise ValueError('this migration is scoped to github.com/plaid/plaid-go/v49')
    check_tree(sdk)
    if not (sdk / 'legacy/tests').is_dir():
        raise ValueError('SDK must contain the public v49 legacy/tests layout')
    mod = json.loads(subprocess.check_output(['go', 'mod', 'edit', '-json'], cwd=sdk, env=subprocess_env()))
    if mod['Module']['Path'] != module:
        raise ValueError('existing root module does not match --module')
    check_tree(HERE / 'templates')
    inventory = json.loads((HERE / 'provenance.json').read_text())
    for entry in inventory['files']:
        if sha((HERE / entry['path']).read_bytes()) != entry['vendored_sha256']:
            raise ValueError(f"vendored source checksum mismatch: {entry['path']}")
    raw = spec_path.read_bytes()
    prepared = prepare_spec(raw)
    # Staging on the same filesystem permits directory renames at installation.
    with tempfile.TemporaryDirectory(prefix='.legacy-stage-', dir=sdk.parent) as temporary:
        work = Path(temporary)
        inputs, output, staged = work / 'input', work / 'output', work / 'sdk'
        inputs.mkdir()
        output.mkdir()
        (inputs / 'spec.json').write_text(json.dumps(prepared))
        shutil.copytree(HERE / 'templates', inputs / 'templates')
        run(['docker', 'run', '--rm', '--network=none', '-v', f'{inputs}:/input:ro', '-v', f'{output}:/output', IMAGE,
             'generate', '-i', '/input/spec.json', '-g', 'go', '-t', '/input/templates', '-o', '/output',
             '--additional-properties=packageName=plaid,enumClassPrefix=true,packageVersion=' + PACKAGE_VERSION + ',plaidApiVersion=2020-09-14',
             '--global-property=apiTests=false,modelTests=false,apiDocs=false,modelDocs=false'])
        generated = validate_output(output)
        shutil.copytree(sdk, staged, ignore=shutil.ignore_patterns('.git'))
        legacy = staged / 'legacy'
        for path in legacy.glob('*.go'):
            if not path.name.endswith('_test.go'):
                if 'Code generated by OpenAPI Generator' not in path.read_text():
                    raise ValueError(f'refusing to replace non-generated source: {path.name}')
                path.unlink()
        for path in generated:
            shutil.copy2(path, legacy / path.name)
        # Preserve existing selections; add only missing legacy requirements.
        requirements = {r['Path'] for r in mod.get('Require', [])}
        for dependency in ('golang.org/x/oauth2@v0.0.0-20220822191816-0ebed06d0094', 'github.com/stretchr/testify@v1.8.4'):
            if dependency.split('@')[0] not in requirements:
                run(['go', 'mod', 'edit', '-require=' + dependency], staged)
        run(['go', 'mod', 'tidy'], staged)
        run(['go', 'test', './legacy/...'], staged)
        # The tag enables imports and signatures, but no Sandbox test runs.
        run(['go', 'test', '-tags=plaid_integration', '-run=^$', './legacy/...'], staged)
        result = {'source_commit': SOURCE_COMMIT, 'spec_sha256': sha(raw),
                  'tree_sha256': tree_sha256(legacy), 'generator_digest': GENERATOR_DIGEST}
        backup = work / 'original-legacy'
        originals = {name: (sdk / name).read_bytes() if (sdk / name).exists() else None for name in ('go.mod', 'go.sum')}
        installed = False
        manifest_created = False
        try:
            (sdk / 'legacy').rename(backup)
            legacy.rename(sdk / 'legacy')
            installed = True
            for name in originals:
                if (staged / name).exists():
                    shutil.copy2(staged / name, sdk / name)
            # Exclusive creation prevents accidentally replacing an evidence file.
            with manifest.open('x') as handle:
                manifest_created = True
                handle.write(json.dumps(result, indent=2) + '\n')
        except BaseException:
            if manifest_created:
                manifest.unlink(missing_ok=True)
            if installed:
                shutil.rmtree(sdk / 'legacy')
            if backup.exists():
                backup.rename(sdk / 'legacy')
            for name, data in originals.items():
                if data is None:
                    (sdk / name).unlink(missing_ok=True)
                else:
                    (sdk / name).write_bytes(data)
            raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('spec', 'sdk', 'module', 'manifest'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        generate(Path(args.spec), Path(args.sdk), args.module, Path(args.manifest))
    except (ValueError, OSError, subprocess.CalledProcessError, yaml.YAMLError) as error:
        parser.exit(1, f'legacy generation failed: {error}\n')


if __name__ == '__main__':
    main()
