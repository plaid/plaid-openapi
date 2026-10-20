"""Policy/orchestration tests. Attestation tests mock only the gh subprocess boundary."""

import copy
import io
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import attestation
import common
import generate
import publish_pr


def commit(repo, message="fixture"):
    common.git(repo, "add", "-A")
    common.git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
               "-c", "commit.gpgsign=false", "commit", "-qm", message)
    return common.git(repo, "rev-parse", "HEAD")


def init(repo):
    repo.mkdir()
    common.git(repo, "init", "-q", "-b", "master")


def write(repo, name, data):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


def spec(version="1.767.1"):
    return f'openapi: 3.0.3\ninfo:\n  title: Plaid\n  version: "2020-09-14_{version}"\npaths: {{}}\n'.encode()


def certificate_result(manifest):
    repository = "plaid/plaid-openapi"
    identity = f"https://github.com/{repository}/{common.WORKFLOW}@refs/heads/master"
    sha = manifest["config"]["commit"]
    return [{"verificationResult": {
        "signature": {"certificate": {
            "subjectAlternativeName": identity, "issuer": "https://token.actions.githubusercontent.com",
            "buildSignerURI": identity, "buildSignerDigest": sha,
            "sourceRepositoryURI": "https://github.com/" + repository, "sourceRepositoryDigest": sha,
            "sourceRepositoryRef": "refs/heads/master", "runnerEnvironment": "github-hosted",
            "sourceRepositoryVisibilityAtSigning": "public",
            "runInvocationURI": "https://github.com/" + repository + "/actions/runs/123/attempts/1"}},
        "verifiedTimestamps": [{"type": "tlog"}],
        "statement": {"_type": "https://in-toto.io/Statement/v1", "predicateType": common.PREDICATE,
                      "predicate": manifest,
                      "subject": [{"name": "plaid-go-v49.0.0-source", "digest": {"sha256": manifest["content_sha256"]}}]}}}]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.values = generate.settings()

    def fixture(self):
        repo, artifact = self.root / "sdk", self.root / "artifact"
        init(repo)
        artifact.mkdir()
        write(repo, "go.mod", "module github.com/plaid/plaid-go/v49\n\ngo 1.21\n")
        write(repo, "go.sum", "")
        write(repo, "legacy/client.go", "package plaid\n")
        write(repo, "client.go", "package plaid\n")
        common.save_json(repo / ".fern/metadata.json", {"sdkVersion": "v49.0.0", "cliVersion": "5.134.0",
                                                       "generatorName": "fernapi/fern-go-sdk", "generatorVersion": "1.70.3"})
        base = commit(repo)
        data, digest = common.content(repo)
        legacy_hash = common.sha256(common.canonical([item for item in common.entries(repo) if item[0].startswith("legacy/")]))
        legacy = {"source_commit": "b" * 40, "spec_sha256": common.sha256(spec()),
                  "tree_sha256": legacy_hash, "generator_digest": "sha256:" + "c" * 64}
        manifest = generate.manifest_for(self.values, version="49.0.0", source_commit="d" * 40,
                                         source_bytes=spec(), config_repo="plaid/plaid-openapi",
                                         config_commit="d" * 40, config_hash="e" * 64,
                                         run_id="123", legacy=legacy, content_hash=digest)
        common.save_json(repo / common.MANIFEST, manifest)
        common.git(repo, "add", "-A")
        common.archive_sdk(repo, artifact / "sdk.tar.gz")
        (artifact / "content.json").write_bytes(data)
        common.save_json(artifact / "manifest.json", manifest)
        (artifact / "generation.bundle.json").write_text('{"fixture_only": true}')
        identity = generate.input_identity("49.0.0", manifest["source"]["sha256"], manifest["config"]["sha256"])
        plan = {"sdk_base": base, "branch": "sdk-generation/go-v49-" + identity,
                "identity": identity, "rehearsal": False}
        common.save_json(artifact / "plan.json", plan)
        return repo, artifact, manifest, plan

    def test_documentation_and_tests_do_not_change_release_inputs(self):
        repo = self.root / "config"
        init(repo)
        write(repo, "fern/generators.yml", "groups: {}\n")
        write(repo, "pipeline/generation/generate.py", "# runtime\n")
        commit(repo)
        expected = generate.config_digest(repo)
        for name in ("fern/README.md", "pipeline/generation/README.md",
                     "pipeline/generation/test_pipeline.py", "pipeline/generation/harden_internal_tests_test.go",
                     "pipeline/generation/fixtures/sample.go.txt", "pipeline/legacy/testdata/union_test.go",
                     ".github/workflows/sdk-pipeline-checks.yml"):
            with self.subTest(path=name):
                write(repo, name, "test or documentation only\n")
                commit(repo)
                self.assertEqual(generate.config_digest(repo), expected)

    def test_generation_inputs_still_change_release_fingerprint(self):
        repo = self.root / "config"
        init(repo)
        write(repo, "fern/generators.yml", "groups: {}\n")
        commit(repo)
        before = generate.config_digest(repo)
        for name in ("2020-09-14.yml", "fern/fern.config.json", "fern/openapi-overlay.yml",
                     "pipeline/generation/generate.py", "pipeline/generation/settings.json",
                     "pipeline/generation/harden_internal_tests.go", "pipeline/generation/new_runtime.py",
                     "pipeline/legacy/generate.py", "pipeline/legacy/provenance.json",
                     "pipeline/legacy/requirements.txt", "pipeline/legacy/templates/client.mustache",
                     common.WORKFLOW):
            with self.subTest(path=name):
                write(repo, name, "generation input\n")
                commit(repo)
                after = generate.config_digest(repo)
                self.assertNotEqual(after, before)
                before = after

    def test_version_selection(self):
        self.assertEqual(common.propose_version([], 49), "49.0.0")
        tags = ["v48.99.0", "v49.0.0-beta.1", "v49.1.5", "v49.2.0"]
        self.assertEqual(common.propose_version(tags, 49), "49.3.0")
        self.assertEqual(common.propose_version(tags, 49, "49.2.1"), "49.2.1")
        for value in ["v49.3.0", "49.01.0", "49.2.0", "50.0.0", "49.3.0;whoami"]:
            with self.subTest(value=value), self.assertRaises(common.PipelineError):
                common.propose_version(tags, 49, value)

    def test_sdk_subprocesses_do_not_receive_publishing_credentials(self):
        sensitive = {"GH_TOKEN": "secret", "GITHUB_TOKEN": "secret", "SDK_PR_TOKEN": "secret",
                     "FERN_TOKEN": "secret", "PLAID_SECRET": "secret", "GIT_CONFIG_COUNT": "9",
                     "GIT_CONFIG_VALUE_0": "secret", "GIT_SSH_COMMAND": "unexpected-ssh"}
        with patch.dict(os.environ, sensitive):
            env = common.clean_env()
        self.assertFalse(set(sensitive).intersection(env))
        self.assertEqual(env["HOME"], os.environ["HOME"])

    def test_logged_subprocess_failure_does_not_disclose_debug_output(self):
        log = self.root / "generation-debug.log"
        with self.assertRaises(common.PipelineError) as error:
            common.run(["python3", "-c", "import sys; print('sensitive-debug-marker'); sys.exit(1)"], log=log)
        self.assertNotIn("sensitive-debug-marker", str(error.exception))
        self.assertIn("sensitive-debug-marker", log.read_text())

    def test_public_uploads_are_exact_candidate_file_allowlists(self):
        workflow = (generate.ROOT / ".github/workflows/generate-go-sdk.yml").read_text()
        blocks = workflow.split("uses: actions/upload-artifact@")[1:]
        self.assertEqual(len(blocks), 2)
        for index, block in enumerate(blocks):
            paths = block.split("          path: |\n", 1)[1].split("          retention-days:", 1)[0]
            entries = [line.strip() for line in paths.splitlines()]
            allowed = {"sdk.tar.gz", "content.json", "manifest.json", "plan.json", "result.json"}
            if index:
                allowed.add("generation.bundle.json")
            self.assertEqual({entry.rsplit("/", 1)[-1] for entry in entries}, allowed)
            self.assertTrue(all(entry.startswith("${{ runner.temp }}/") and not entry.endswith("/") and "*" not in entry for entry in entries))
        self.assertEqual(workflow.count("(github.event_name != 'workflow_dispatch' || inputs.rehearsal == false)"), 2)

    def test_only_push_schedule_and_manual_inputs_are_accepted(self):
        for name in ("push", "schedule"):
            self.assertEqual(generate.event_request(name, {}, self.values), ("", False))
        self.assertEqual(generate.event_request("workflow_dispatch", {"inputs": {"rehearsal": True}}, self.values), ("", True))
        for name in ("pull_request", "pull_request_target", "repository_dispatch"):
            with self.subTest(name=name), self.assertRaises(common.PipelineError):
                generate.event_request(name, {}, self.values)
        for inputs in ({"spec_commit": "a" * 40}, {"url": "https://example.invalid/spec"}, {"rehearsal": "unexpected"}):
            with self.subTest(inputs=inputs), self.assertRaises(common.PipelineError):
                generate.event_request("workflow_dispatch", {"inputs": inputs}, self.values)

    def test_generation_context_rejects_forks_prs_private_and_disabled(self):
        event = {"repository": {"full_name": "plaid/plaid-openapi", "private": False, "fork": False, "default_branch": "master"}}
        baseline = {"GITHUB_REPOSITORY": "plaid/plaid-openapi", "GITHUB_REF": "refs/heads/master",
                    "GITHUB_SHA": "a" * 40, "GITHUB_RUN_ID": "123", "SDK_PIPELINE_ENABLED": "true", "GITHUB_EVENT_NAME": "push"}
        for changes in ({"GITHUB_REPOSITORY": "someone/plaid-openapi"}, {"GITHUB_REF": "refs/heads/test"},
                        {"SDK_PIPELINE_ENABLED": "false"}, {"GITHUB_EVENT_NAME": "pull_request"},
                        {"GITHUB_EVENT_NAME": "pull_request_target"}):
            with self.subTest(changes=changes), patch.dict(os.environ, {**baseline, **changes}, clear=True), self.assertRaises(common.PipelineError):
                generate.check_context(event, self.values, False)
        for changes in ({"private": True}, {"fork": True}, {"full_name": "someone/plaid-openapi"}):
            value = copy.deepcopy(event)
            value["repository"].update(changes)
            with self.subTest(changes=changes), patch.dict(os.environ, baseline, clear=True), self.assertRaises(common.PipelineError):
                generate.check_context(value, self.values, False)
        with patch.dict(os.environ, baseline, clear=True), patch.object(generate, "git", side_effect=["a" * 40, ""]):
            self.assertEqual(generate.check_context(event, self.values, False), ("plaid/plaid-openapi", "a" * 40, "123"))

    def test_spec_uses_exact_config_commit_even_if_newer_spec_is_available(self):
        source = self.root / "source"
        init(source)
        write(source, "2020-09-14.yml", spec().decode())
        earlier = commit(source)
        write(source, "2020-09-14.yml", spec("1.768.0").decode())
        later = commit(source)
        with self.assertRaisesRegex(common.PipelineError, "same checked-out"):
            generate.verified_spec(source, earlier, self.values)
        common.git(source, "checkout", "--detach", earlier)
        actual_commit, actual_bytes = generate.verified_spec(source, earlier, self.values)
        self.assertEqual((actual_commit, actual_bytes), (earlier, spec()))
        self.assertNotEqual(actual_commit, later)

    def test_same_version_source_commit_rollback_is_rejected(self):
        source = self.root / "source"
        init(source)
        write(source, "2020-09-14.yml", spec().decode())
        earlier = commit(source)
        write(source, "2020-09-14.yml", spec().decode() + "# reviewed correction, same version\n")
        later = commit(source)
        sdk, _, manifest, _ = self.fixture()
        manifest["source"].update(commit=later, sha256=common.sha256((source / "2020-09-14.yml").read_bytes()))
        manifest["config"]["commit"] = later
        manifest["legacy"]["spec_sha256"] = manifest["source"]["sha256"]
        common.save_json(sdk / common.MANIFEST, manifest)
        self.assertEqual(generate.verified_spec(source, later, self.values, sdk)[0], later)
        common.git(source, "checkout", "--detach", earlier)
        with self.assertRaises(common.PipelineError):
            generate.verified_spec(source, earlier, self.values, sdk)

    def test_lower_spec_version_than_published_manifest_is_rejected(self):
        source = self.root / "source"
        init(source)
        write(source, "2020-09-14.yml", spec().decode())
        original = commit(source)
        sdk, _, manifest, _ = self.fixture()
        manifest["source"]["commit"] = original
        manifest["config"]["commit"] = original
        common.save_json(sdk / common.MANIFEST, manifest)
        write(source, "2020-09-14.yml", spec("1.762.0").decode())
        downgraded = commit(source)
        with self.assertRaisesRegex(common.PipelineError, "older"):
            generate.verified_spec(source, downgraded, self.values, sdk)

    def test_manifest_rejects_different_source_and_config_commits(self):
        _, _, manifest, _ = self.fixture()
        manifest["source"]["commit"] = "a" * 40
        with self.assertRaisesRegex(common.PipelineError, "same public commit"):
            attestation.validate_manifest(manifest)

    def test_compatibility_baseline_is_published_tag_not_changed_master(self):
        upstream, sdk, before = self.root / "upstream", self.root / "sdk", self.root / "before"
        init(upstream)
        write(upstream, "go.mod", "module example.invalid/sdk\n\ngo 1.21\n")
        write(upstream, "api.go", "package sdk\nfunc Published() string { return \"\" }\n")
        published = commit(upstream)
        common.git(upstream, "tag", "v49.0.0")
        write(upstream, "api.go", "package sdk\nfunc Published() int { return 0 }\n")
        changed_master = commit(upstream)
        common.run(["git", "clone", str(upstream), str(sdk)])
        selected = generate.published_baseline(sdk, ["v49.0.0", "v49.1.0-preview.1"], 49, before)
        self.assertEqual(selected, "v49.0.0")
        self.assertEqual(common.git(before, "rev-parse", "HEAD"), published)
        self.assertNotEqual(common.git(before, "rev-parse", "HEAD"), changed_master)
        self.assertIn("Published() string", (before / "api.go").read_text())

    def release_fixture(self, *, tag_target="release", later_commit=False, annotated=True):
        upstream, _, _, plan = self.fixture()
        common.git(upstream, "checkout", "-b", "sdk-generation-fixture")
        generated = commit(upstream, "Generated SDK fixture")
        common.git(upstream, "checkout", "master")
        common.git(upstream, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                   "-c", "commit.gpgsign=false", "merge", "--no-ff", "sdk-generation-fixture", "-m", "Integrate generated SDK")
        released = common.git(upstream, "rev-parse", "HEAD")
        if tag_target:
            target = {"release": released, "generated": generated, "old": plan["sdk_base"]}[tag_target]
            args = ["-a", "v49.0.0", "-m", "Unsigned annotated test fixture", target] if annotated else ["v49.0.0", target]
            common.git(upstream, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                       "-c", "tag.gpgsign=false", "tag", *args)
        if later_commit:
            write(upstream, "README.md", "Later documentation change\n")
            commit(upstream, "Update documentation")
        sdk = self.root / "checked-sdk"
        common.run(["git", "clone", "--shared", str(upstream), str(sdk)])
        tags = common.git(sdk, "ls-remote", "--tags", "origin", "refs/tags/v*")
        return sdk, tags, released

    def test_pending_release_waits_for_tag(self):
        sdk, tags, _ = self.release_fixture(tag_target=None)
        self.assertEqual(generate.pending_release(sdk, tags), "49.0.0")

    def test_published_release_tag_is_peeled_to_exact_integration_commit(self):
        sdk, tags, released = self.release_fixture()
        self.assertNotEqual(common.git(sdk, "rev-parse", "v49.0.0"), released)
        self.assertEqual(common.git(sdk, "rev-parse", "v49.0.0^{commit}"), released)
        self.assertIsNone(generate.pending_release(sdk, tags))

    def test_later_documentation_commit_does_not_make_published_release_pending(self):
        sdk, tags, released = self.release_fixture(later_commit=True)
        self.assertNotEqual(common.git(sdk, "rev-parse", "HEAD"), released)
        self.assertIsNone(generate.pending_release(sdk, tags))

    def test_tag_on_generated_pr_head_conflicts_with_integration_commit(self):
        sdk, tags, _ = self.release_fixture(tag_target="generated")
        with self.assertRaisesRegex(common.PipelineError, "conflicts"):
            generate.pending_release(sdk, tags)

    def test_lightweight_tag_cannot_complete_automated_publication(self):
        sdk, tags, _ = self.release_fixture(annotated=False)
        with self.assertRaisesRegex(common.PipelineError, "annotated"):
            generate.pending_release(sdk, tags)

    def test_manual_baseline_without_manifest_does_not_enter_pending_gate(self):
        sdk = self.root / "manual-sdk"
        sdk.mkdir()
        self.assertIsNone(generate.pending_release(sdk, ""))

    def test_pending_publication_stops_before_version_selection_or_generation(self):
        upstream, _, _ = self.release_fixture(tag_target=None)
        event = self.root / "event.json"
        event.write_text('{"repository":{"full_name":"plaid/plaid-openapi","private":false,"fork":false}}')
        output = self.root / "output"
        def fetch(repository, branch, destination):
            self.assertEqual(repository, "plaid/plaid-go")
            common.run(["git", "clone", "--shared", str(upstream), str(destination)])
            return common.git(destination, "rev-parse", "HEAD")
        env = {"GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": "workflow_dispatch"}
        with patch.dict(os.environ, env), patch("sys.argv", ["generate.py", "--output", str(output)]), \
             patch.object(generate, "check_context", return_value=("plaid/plaid-openapi", "a" * 40, "123")), \
             patch.object(generate, "fetch_repository", side_effect=fetch) as fetching, \
             patch.object(generate, "propose_version") as proposing, \
             patch.object(generate, "generate_new_client") as generating:
            generate.main()
        self.assertEqual(json.loads((output / "result.json").read_text())["status"], "awaiting-release")
        self.assertEqual(fetching.call_count, 1)
        proposing.assert_not_called()
        generating.assert_not_called()

    def test_canonical_digest_modes_paths_and_exclusions(self):
        repo = self.root / "repo"
        init(repo)
        write(repo, "z.go", "package z\n")
        write(repo, "a/é.txt", "data")
        (repo / "z.go").chmod(0o755)
        write(repo, common.MANIFEST, "{}")
        write(repo, common.BUNDLE, "{}")
        commit(repo)
        expected = [["a/é.txt", "100644", common.sha256(b"data")], ["z.go", "100755", common.sha256(b"package z\n")]]
        self.assertEqual(common.content(repo)[0], json.dumps(expected, separators=(",", ":"), ensure_ascii=True).encode())
        write(repo, ".sdk-release/extra.json", "{}")
        common.git(repo, "add", "-A")
        with self.assertRaises(common.PipelineError):
            common.content(repo)

    def test_symlinks_and_unsafe_paths_rejected(self):
        for name in ["../escape", "/absolute", "a/.Git/config", "a\\b", "a\nname"]:
            with self.subTest(name=name), self.assertRaises(common.PipelineError):
                common.safe_path(name)
        repo = self.root / "repo"
        init(repo)
        (repo / "link").symlink_to("/etc/passwd")
        common.git(repo, "add", "link")
        with self.assertRaises(common.PipelineError):
            common.content(repo)

    def test_archive_rejects_traversal_and_links(self):
        for i, kind in enumerate(["../outside", "symlink"]):
            archive = self.root / f"bad{i}.tar.gz"
            with tarfile.open(archive, "w:gz") as output:
                entry = tarfile.TarInfo(kind)
                if kind == "symlink":
                    entry.type = tarfile.SYMTYPE
                    entry.linkname = "/etc/passwd"
                output.addfile(entry, io.BytesIO(b""))
            with self.assertRaises(common.PipelineError):
                common.extract_sdk(archive, self.root / f"out{i}")

    def test_local_config_pins_actual_image_and_has_no_publishing_settings(self):
        config = self.root / "config"
        generate.render_config(config, self.root / "sdk", spec(), "49.0.0", self.values)
        text = (config / "fern/generators.yml").read_text()
        self.assertIn("name: fernapi/fern-go-sdk@" + self.values["generator_digest"], text)
        self.assertIn("location: local-file-system", text)
        self.assertIn("path: github.com/plaid/plaid-go/v49", text)
        self.assertNotIn("repository:", text)
        self.assertNotIn("  java-sdk:", text)

    def test_sdk_metadata_contains_only_version_identity(self):
        sdk = self.root / "sdk"
        sdk.mkdir()
        metadata = {"cliVersion": "5.134.0", "generatorName": "fernapi/fern-go-sdk", "generatorVersion": "1.70.3",
                    "sdkVersion": "v49.0.0", "generatorConfig": {"importPath": "github.com/plaid/plaid-go/v49",
                    "module": {"path": "github.com/plaid/plaid-go/v49"}, "maxRetries": 0, "extra_setting": "must-not-leak"}}
        common.save_json(sdk / ".fern/metadata.json", metadata)
        generate.sanitize_metadata(sdk, "49.0.0", "github.com/plaid/plaid-go/v49", self.values)
        text = (sdk / ".fern/metadata.json").read_text()
        self.assertNotIn("extra_setting", text)
        self.assertNotIn("generatorConfig", text)
        self.assertEqual(len(json.loads(text)), 4)

    def test_valid_signed_fixture_requires_real_gh_boundary(self):
        _, artifact, manifest, _ = self.fixture()
        result = certificate_result(manifest)
        with patch.object(attestation, "run", return_value=json.dumps(result).encode()) as verify:
            actual, _ = publish_pr.verify_artifact(artifact, self.root / "verified")
        self.assertEqual(actual, manifest)
        self.assertNotIn("--no-public-good", verify.call_args.args)
        self.assertIn("refs/heads/master", verify.call_args.args)
        self.assertIn("--deny-self-hosted-runners", verify.call_args.args)
        self.assertIn("--source-digest", verify.call_args.args)
        identity_flags = {"--cert-identity", "--cert-identity-regex", "--signer-repo", "--signer-workflow"}
        self.assertEqual(identity_flags.intersection(verify.call_args.args), {"--cert-identity"})

    def test_tampered_content_fails_before_cryptographic_verification(self):
        repo, artifact, manifest, _ = self.fixture()
        write(repo, "client.go", "package corrupted\n")
        common.git(repo, "add", "-A")
        common.archive_sdk(repo, artifact / "sdk.tar.gz")
        with patch.object(attestation, "run") as verify, self.assertRaisesRegex(common.PipelineError, "content"):
            publish_pr.verify_artifact(artifact, self.root / "verified")
        verify.assert_not_called()

    def test_wrong_signer_predicate_run_and_subject_rejected(self):
        _, artifact, manifest, _ = self.fixture()
        changes = [lambda v: v[0]["verificationResult"]["signature"]["certificate"].update(buildSignerDigest="0" * 40),
                   lambda v: v[0]["verificationResult"]["signature"]["certificate"].update(sourceRepositoryVisibilityAtSigning="private"),
                   lambda v: v[0]["verificationResult"]["signature"]["certificate"].update(runInvocationURI="https://github.com/plaid/plaid-openapi/actions/runs/999"),
                   lambda v: v[0]["verificationResult"]["statement"]["predicate"]["sdk"].update(version="49.9.0"),
                   lambda v: v[0]["verificationResult"]["statement"]["subject"][0].update(name="different-source")]
        for i, change in enumerate(changes):
            value = copy.deepcopy(certificate_result(manifest))
            change(value)
            with self.subTest(index=i), patch.object(attestation, "run", return_value=json.dumps(value).encode()), self.assertRaises(common.PipelineError):
                publish_pr.verify_artifact(artifact, self.root / f"bad{i}")

    def test_missing_bundle_and_duplicate_json_are_rejected(self):
        _, artifact, _, _ = self.fixture()
        (artifact / "generation.bundle.json").unlink()
        with self.assertRaisesRegex(common.PipelineError, "bundle"):
            publish_pr.verify_artifact(artifact, self.root / "verified")
        with self.assertRaises(common.PipelineError):
            attestation.parse_json('{"schema_version":1,"schema_version":2}')

    def test_pending_pr_is_never_updated(self):
        repo, artifact, manifest, plan = self.fixture()
        event = self.root / "event.json"
        event.write_text('{"repository":{"full_name":"plaid/plaid-openapi","private":false,"fork":false}}')
        env = {"GITHUB_REPOSITORY": "plaid/plaid-openapi", "GITHUB_REF": "refs/heads/master",
               "SDK_PIPELINE_ENABLED": "true", "GITHUB_SHA": manifest["config"]["commit"],
               "GITHUB_RUN_ID": "123", "GITHUB_EVENT_PATH": str(event), "GITHUB_EVENT_NAME": "workflow_dispatch", "SDK_PR_TOKEN": "fixture-token",
               "SDK_PR_APP_BOT_ID": "12345"}
        existing = {"html_url": "https://github.com/plaid/plaid-go/pull/1", "state": "open", "draft": False,
                    "user": {"type": "Bot", "id": 12345},
                    "head": {"repo": {"full_name": "plaid/plaid-go"}, "ref": plan["branch"], "sha": "f" * 40},
                    "base": {"repo": {"full_name": "plaid/plaid-go"}, "ref": "master", "sha": plan["sdk_base"]}}
        ref = {"ref": "refs/heads/master", "object": {"type": "commit", "sha": plan["sdk_base"]}}
        with patch.dict(os.environ, env, clear=True), patch.object(publish_pr, "pending_pr", return_value=existing), patch.object(publish_pr, "public_get", return_value=ref) as api, patch.object(publish_pr, "recover_pushed_branch") as recover, patch.object(publish_pr, "run") as execute:
            self.assertEqual(publish_pr.publish(artifact, repo, manifest, plan, self.root), "https://github.com/plaid/plaid-go/pull/1")
        self.assertEqual(api.call_count, 1)
        self.assertNotIn("method", api.call_args.kwargs)
        recover.assert_called_once_with("plaid/plaid-go", plan["branch"], manifest, plan, self.root, "f" * 40)
        execute.assert_not_called()

    def test_other_pending_pr_blocks_new_generation(self):
        response = [{"head": {"repo": {"full_name": "plaid/plaid-go"}, "ref": "sdk-generation/go-v49-other"}}]
        with patch.object(publish_pr, "public_get", return_value=response), self.assertRaisesRegex(common.PipelineError, "pending"):
            publish_pr.pending_pr("plaid/plaid-go", "sdk-generation/go-v49-current", token="fixture")

    def test_rehearsal_never_enters_signed_publishing(self):
        _, artifact, _, plan = self.fixture()
        plan["rehearsal"] = True
        common.save_json(artifact / "plan.json", plan)
        with patch.object(attestation, "run") as verify, self.assertRaisesRegex(common.PipelineError, "rehearsal"):
            publish_pr.verify_artifact(artifact, self.root / "verified")
        verify.assert_not_called()


if __name__ == "__main__":
    unittest.main()
