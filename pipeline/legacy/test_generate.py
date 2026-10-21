import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('legacy_generate', Path(__file__).with_name('generate.py'))
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def document():
    return {'openapi': '3.0.0', 'paths': {'/test': {}}, 'components': {'schemas': {
        'Choice': {'oneOf': [{'$ref': '#/components/schemas/First'}, {'$ref': '#/components/schemas/Second'}],
                   'discriminator': {'propertyName': 'kind', 'mapping': {'first': '#/components/schemas/First', 'second': '#/components/schemas/Second'}}},
        'First': {'type': 'object', 'required': ['kind'], 'properties': {'kind': {'type': 'string', 'enum': ['first']}}},
        'Second': {'type': 'object', 'required': ['kind'], 'properties': {'kind': {'type': 'string', 'enum': ['second']}}},
    }}}


class PreparationTests(unittest.TestCase):

    def test_subprocess_environment_excludes_credentials_and_go_overrides(self):
        environment = {
            'PATH': '/tools', 'HOME': '/home/test', 'GOCACHE': '/cache/go',
            'DOCKER_HOST': 'unix:///docker.sock', 'GITHUB_TOKEN': 'not-forwarded',
            'PLAID_SECRET': 'not-forwarded', 'AWS_SESSION_TOKEN': 'not-forwarded',
            'GOENV': '/private/config', 'GOWORK': '/private/go.work',
            'GOFLAGS': '-modfile=/private/go.mod', 'GOPROXY': 'https://secret@proxy',
        }
        with mock.patch.dict(generator.os.environ, environment, clear=True):
            expected = {'PATH': '/tools', 'HOME': '/home/test', 'GOCACHE': '/cache/go',
                        'DOCKER_HOST': 'unix:///docker.sock', 'GOWORK': 'off',
                        'GOENV': 'off', 'GOFLAGS': ''}
            self.assertEqual(generator.subprocess_env(), expected)
            with mock.patch.object(generator.subprocess, 'run') as command:
                generator.run(['go', 'test', './legacy/...'])
                self.assertEqual(command.call_args.kwargs['env'], expected)

    def test_explicit_wire_mapping_only(self):
        prepared = generator.prepare_spec(json.dumps(document()))['components']['schemas']['Choice']
        self.assertTrue(prepared['x-plaid-sdk-one-of-interface'])
        self.assertEqual(prepared['x-plaid-sdk-one-of-mapping'], [
            {'mappingName': 'first', 'modelName': 'First'}, {'mappingName': 'second', 'modelName': 'Second'}])

    def test_incomplete_or_ambiguous_union_rejected(self):
        for change in ('missing_mapping', 'optional_discriminator', 'wrong_enum', 'inline_branch'):
            with self.subTest(change=change):
                doc = document()
                schemas = doc['components']['schemas']
                if change == 'missing_mapping':
                    del schemas['Choice']['discriminator']['mapping']['first']
                elif change == 'optional_discriminator':
                    schemas['First']['required'] = []
                elif change == 'wrong_enum':
                    schemas['First']['properties']['kind']['enum'] = ['wrong']
                else:
                    schemas['Choice']['oneOf'][0] = {'type': 'string'}
                with self.assertRaises(ValueError):
                    generator.prepare_spec(json.dumps(doc))

    def test_remote_ref_and_duplicate_key_rejected(self):
        doc = document()
        doc['components']['schemas']['First']['properties']['remote'] = {'$ref': 'https://example.com/schema'}
        with self.assertRaisesRegex(ValueError, 'external references'):
            generator.prepare_spec(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, 'unique string keys'):
            generator.prepare_spec('openapi: 3.0.0\nopenapi: 3.0.1\n')

    def test_manifest_hash_includes_modes_and_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'a.go').write_bytes(b'a')
            expected = hashlib.sha256(json.dumps([['legacy/a.go', '100644', hashlib.sha256(b'a').hexdigest()]], separators=(',', ':')).encode()).hexdigest()
            self.assertEqual(generator.tree_sha256(root), expected)
            (root / 'a.go').chmod(0o755)
            self.assertNotEqual(generator.tree_sha256(root), expected)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'link').symlink_to(root / 'target')
            with self.assertRaises(ValueError):
                generator.check_tree(root)
            with self.assertRaises(ValueError):
                generator.checked_path(root / 'link')

    def test_missing_generator_output_preserves_sdk(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sdk = root / 'sdk'
            (sdk / 'legacy/tests').mkdir(parents=True)
            (sdk / 'go.mod').write_text('module github.com/plaid/plaid-go/v49\n')
            (sdk / 'client.go').write_text('root fern content')
            (sdk / 'legacy/old.go').write_text('old legacy content')
            spec = root / 'spec.json'
            spec.write_text(json.dumps(document()))
            before = {p.relative_to(sdk): p.read_bytes() for p in sdk.rglob('*') if p.is_file()}
            with mock.patch.object(generator, 'run'), mock.patch.object(generator.subprocess, 'check_output', return_value=b'{"Module":{"Path":"github.com/plaid/plaid-go/v49"}}') as read_module:
                with mock.patch.dict(generator.os.environ, {'GITHUB_TOKEN': 'not-forwarded', 'PLAID_SECRET': 'not-forwarded'}):
                    with self.assertRaisesRegex(ValueError, 'complete Go client'):
                        generator.generate(spec, sdk, 'github.com/plaid/plaid-go/v49', root / 'manifest.json')
                self.assertNotIn('GITHUB_TOKEN', read_module.call_args.kwargs['env'])
                self.assertNotIn('PLAID_SECRET', read_module.call_args.kwargs['env'])
                self.assertEqual(read_module.call_args.kwargs['env']['GOENV'], 'off')
                self.assertEqual(read_module.call_args.kwargs['env']['GOWORK'], 'off')
            after = {p.relative_to(sdk): p.read_bytes() for p in sdk.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            self.assertFalse((root / 'manifest.json').exists())


    def test_success_preserves_root_and_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sdk = root / 'sdk'
            (sdk / 'legacy/tests').mkdir(parents=True)
            (sdk / 'go.mod').write_text('module github.com/plaid/plaid-go/v49\n')
            (sdk / 'client.go').write_text('root fern content')
            (sdk / 'legacy/tests/preserved_test.go').write_text('public test content')
            (sdk / 'legacy/old.go').write_text('// Code generated by OpenAPI Generator\npackage plaid\n')
            spec_path = root / 'spec.json'
            spec_path.write_text(json.dumps(document()))

            def fake_run(args, cwd=None):
                if args[0] != 'docker':
                    return
                mount = next(arg for arg in args if arg.endswith(':/output'))
                output = Path(mount[:-len(':/output')])
                for name in ('api_plaid.go', 'client.go', 'configuration.go', 'response.go', 'utils.go', 'model_choice.go'):
                    (output / name).write_text('// Code generated by OpenAPI Generator\npackage plaid\n// Plaid Go v48.0.0\n')

            with mock.patch.object(generator, 'run', side_effect=fake_run), mock.patch.object(generator.subprocess, 'check_output', return_value=b'{"Module":{"Path":"github.com/plaid/plaid-go/v49"}}'):
                result = generator.generate(spec_path, sdk, 'github.com/plaid/plaid-go/v49', root / 'manifest.json')
            self.assertEqual((sdk / 'client.go').read_text(), 'root fern content')
            self.assertEqual((sdk / 'legacy/tests/preserved_test.go').read_text(), 'public test content')
            self.assertFalse((sdk / 'legacy/old.go').exists())
            self.assertEqual(result['tree_sha256'], generator.tree_sha256(sdk / 'legacy'))
            self.assertEqual(json.loads((root / 'manifest.json').read_text()), result)


if __name__ == '__main__':
    unittest.main()
