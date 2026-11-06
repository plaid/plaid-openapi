# Generate and publish the Go SDK

An approved merge to `plaid/plaid-openapi` drives the Go release: generate both clients, validate them, attest the exact output, open a ready SDK PR, integrate it after automated checks, then attest and publish its signed version tag. Updates need no separate human SDK approval or merge: compatible API changes stay within the current module major, while detected breaking API changes generate the next major.

The spec and Fern configuration live together in this public repository. Each production run uses `GITHUB_SHA` for both inputs. Push, scheduled catch-up and manual production generation run only from the original public repository's `master`; pull-request, fork and repository-dispatch contexts cannot enter that pipeline. Manual runs can choose a reviewed version override, but cannot choose another spec commit or URL.

## Fern-hosted generation

The reviewed `generation_mode` setting selects `fern-hosted`. The production
switches still control activation; merging the implementation does not enable it.
The input fingerprint covers the Go group, shared API inputs and Go pipeline
controls. Edits confined to other SDK groups or the shared CLI default do not
trigger a Go release. The workflow runs these stages:

1. Pin the public spec/config commit, SDK base and proposed version.
2. Request Fern-hosted generation into a fresh local output directory. Verify its
   signature, requested job, input hashes, generator image and complete file tree. Export only
   allowed generated files and sign a public-safe record of that verification.
3. Add legacy from the same spec and apply the reviewed customizations. Seal the
   assembled candidate before any SDK tests execute.
4. Test that sealed candidate in a separate job. A breaking API change repeats
   generation and assembly for the next major and checks equivalence in both
   module namespaces. Test jobs return decisions, never replacement SDK files.
5. Reverify the original sealed files, issue the final generation attestation,
   and pass them to the existing SDK PR, integration and release workflows.

The assembly seal uses a separate predicate, so an untested provisional candidate
cannot qualify as completed generation. The final SDK's schema-2 manifest links
Fern verification to Plaid's final assembly; the SDK consumer verifies both
records and the generation mode at the exact public config commit. Removing the
Fern proof or substituting a local-generation manifest stops publication.

The request job needs only `FERN_TOKEN`; it does not open a staging PR or read a
private GitHub repository. Assembly and test jobs receive no Fern or publishing
credentials. Only reviewed generated paths are exported, with metadata reduced
to version identity. The fresh generated caller is compared against the maintained
public caller with its reviewed security hook removed.

The original signed provenance is carried in `.sdk-release/fern-provenance.json`.
Its signed payload and signature are unchanged. Only the unsigned signing-key
identifier is omitted, since it can contain provider infrastructure details.
Unexpected payload fields stop generation before publication. The signed tree
covers all downloaded files except that provenance file; modes are normalized to
`100644` according to Fern's directory-proof format.

Go pins CLI 5.193.2 in `settings.json` and overrides only its disposable Go
config; the shared CLI default used by other SDK languages is unchanged. Optional
registry writes are rejected locally through the FDR-origin override. Remote
`local-file-system` output means Fern runs the generator and downloads its files;
this is distinct from running the generator with `--local`.

`local` remains an explicit reviewed fallback using the previous generator path;
changing provider requires a config review. Secret-free PR rehearsals exercise
that local path, while a hosted rehearsal needs the protected request credentials.
Manual `rehearsal: true` runs skip all signatures and publishing, including the
assembly seal. Their artifacts cannot pass the production signature checks.

## Pre-merge hosted rehearsal

`sdk-rehearsal.yml` runs on same-repository PRs changing that workflow or
`pipeline/rehearsal/`. It checks out the exact PR head and captures the current public SDK `master`
commit, detaches at that SHA, and records it in the report. This follows the
reviewed SDK baseline across major releases without accepting arbitrary refs.
An SDK candidate still awaiting publication blocks rehearsal. Prior production
release evidence is removed locally before generation.
It calls the production generation, legacy, build, mock-test and compatibility
functions on a standard GitHub runner. Its candidate version is only a local
test value; no tag is created or reserved.

This separate workflow has only Contents read permission, no secrets, no signing
job and no publishing steps. Checkout credentials are not persisted. Its public
artifacts are an unsigned SDK archive, API comparison and rehearsal report with
phase timings and sampled whole-runner memory availability. It does not emit the
manifest or signed bundle required by the publishing workflow. Raw logs and
temporary work directories are not uploaded. Memory sampling can miss short peaks.

This checks generation correctness and runner capacity, not real signing,
App permissions, protected-branch integration, tag publication or notifications.
Those remain activation checks after review and access setup.

## Generation and publication boundaries

- The source is the tracked `2020-09-14.yml` at the exact workflow commit. Fern config refers to `../2020-09-14.yml`. Rendering makes a disposable copy of those exact bytes beside the temporary Fern config; it never adds a second repository spec. Previous SDK source commits must remain ancestors and spec versions cannot move backward.
- The request job checks the CLI archive checksum and verifies Fern's signed generator image digest. Assembly runs the public-only legacy generator on exactly the same spec bytes. The local fallback still executes Fern by immutable image digest.
- Maintained customizations, license, release history and release/integration automation survive generation. Both hosted downloads and the local fallback compare the fresh generated caller with the maintained security hook removed. An incompatible runtime change stops generation until the caller is reconciled.
- Fern Go 1.70.3 regenerates the transfer diligence upload's `purpose` field as JSON, adding quotes. A narrow post-generation correction restores the [published v49 text-field behavior](https://github.com/plaid/plaid-go/blob/0d83b050ea325adda35c6d88bdf24b46fe2f7044/transfer/diligence/raw_client.go#L103). It checks the exact generator version, method, endpoint and serialization shape, recognizes already-correct output, and stops on unknown shapes. The public upload regression test is preserved; the generated file is otherwise refreshed normally.
- `harden_wire_tests.py` sets explicit dummy credentials and custom mock endpoints in the reviewed generated test shapes. WireMock mappings require those headers; compose binds only to loopback without verbose request logging. The helper rejects unfamiliar generator versions or test shapes. Runtime destination checks stay enabled.
- Before generation, every operation must have an explicit Fern group and method
  name after applying the overlay, and request bodies must not retain top-level
  `client_id` or `secret` fields. Shared request schemas are checked too.
- Before attestation and again before opening the SDK PR, changed paths are limited to non-executable lowercase Go package files (outside scripts and maintained controls), `go.mod`, `go.sum`, `.fern/metadata.json`, `reference.md`, and `wiremock/wiremock-mappings.json`. Other existing files remain unchanged except the deterministic changelog entry and exact major-version namespace rewrites in maintained Go files/README. Existing `legacy/tests/` files may only receive those namespace rewrites; additions and deletions require a separately reviewed SDK change. The comparison uses the original SDK base, including when generation creates local commits.
- The Go floor build and complete local mock suite must pass before the final generation attestation or SDK PR can be produced. Compatibility is checked against the latest published stable tag in the current root module major, including `legacy/`. The `major` setting is a minimum supported major, not a release pin. The first candidate uses the next minor version; detected API breaks trigger fresh generation of both clients at the next major’s `N.0.0`, with the root module, self imports, maintained Go files and README updated to that namespace. A temporary source copy normalizes the final candidate back to the probe namespace for API comparisons in both directions; unexpected final API drift stops generation. Explicit version overrides remain within the current major and stop on breaking changes. Comparison/tool failures never trigger a major release. Legacy continues to use the same spec and preserves its v48 client identity.
- If a generation has merged but its tag is absent, the job returns `awaiting-release` before choosing another version. The tag must be annotated and peel to the exact first-parent commit that introduced the manifest. A tag on the generated PR head or another commit is rejected. Later unrelated commits carrying the same published manifest are allowed.
- A separate job validates the package and uses public Sigstore attestation to bind its content digest to the manifest. The signed source and config repository/commit must match `plaid/plaid-openapi` and the same workflow SHA. Verification requires the exact workflow, `master`, public visibility, run identity, predicate and subject. No generated SDK code executes in this job.
- The PR job verifies the signature before obtaining its narrowly scoped App token. `SDK_PR_APP_BOT_ID` pins the numeric bot user ID; the public SDK integration and release workflows use the same identity. Same-input retries recheck the existing ready PR, base, one-parent generation commit, content and signature. They never rebase or overwrite existing branches, change drafts, or recreate closed PRs.

Public artifact uploads use explicit file allowlists: prepared plans, filtered `fern-output.tar.gz`, `fern-content.json`, `fern-record.json`, `fern-provenance.json`, `fern.bundle.json`, assembled `sdk.tar.gz`, `content.json`, `manifest.json`, `plan.json`, `result.json`, the separate `assembly.bundle.json`, final `generation.bundle.json`, and public API comparisons. The final SDK carries the final manifest, generation signature, Fern verification index/signature and original portable Fern provenance. Environment dumps, raw CLI debug output, test logs and temporary work directories are not uploaded. The CLI debug file used to check the raw generated caller stays in disposable local storage; failed logged subprocess output is withheld from public job logs. SDK `.fern/metadata.json` contains only version identity.

## Activation

1. Verify CODEOWNERS resolves to maintainers with write access and enable required code-owner review for public spec, `fern/`, `pipeline/` and workflow changes. Land the public SDK's maintained customizations, integration/release automation and ownership rules. For the first automatic release after a manual release, install its reviewed predecessor pins.
2. Set `SDK_FAILURE_ASSIGNEE` to a repository maintainer and verify assigned failure issues reach them. Leave `SDK_PIPELINE_ENABLED`, `SDK_AUTOMERGE_ENABLED` and `SDK_RELEASE_ENABLED` off while preparing. `rehearsal: true` only generates and tests; trusted workflow input guards prevent signing or PR publication even if artifact outputs change.
3. Land the SDK schema-2 consumer before enabling hosted generation. In this repo, configure `SDK_PR_APP_ID`, `SDK_PR_APP_PRIVATE_KEY` and `SDK_PR_APP_BOT_ID` for the protected `sdk-pr-publishing` environment. Restrict it to `master` without a per-run reviewer gate. The PR App needs Contents and Pull requests write only on `plaid-go`, with no workflow permission or review bypass. Configure the separate integration and release identities in the SDK repo.
4. Create a `fern-generation` environment restricted to `master` and configure `FERN_TOKEN`. Generation needs no private staging repository or reader App. The separate creator, integration and release Apps retain their public SDK roles.
5. After approving deployment, enable generation and run a real signed candidate while automatic integration and release remain disabled. Validate the public integration workflow's no-write mode, then enable automatic integration with tag publication still disabled. Run the public release's no-tag attestation rehearsal and verify the exact control/signing identities and repository protections.
6. Enable publication only after the hosted rehearsal passes. Dispatch the first already-merged candidate explicitly; enabling a flag does not replay an old push event. Thereafter approved input changes should generate, integrate and publish automatically.

Scheduled catch-up runs every 15 minutes, subject to GitHub scheduling delays. A different pending generation PR waits for integration or failure resolution; an advanced base, edited/draft/closed PR or conflicting tag stops rather than guessing how to repair it. A failed release leaves generation waiting until the release retry succeeds.

## Recovering a stale generated PR

The current pipeline stops if SDK master advances while a generated PR is open.
It does not automatically rebase or change signed candidate content. After checking
that the candidate is obsolete, close its PR and dispatch generation again with an
appropriate unused version above the latest published tag. The new run uses the
current reviewed source and SDK base, creates fresh evidence and opens another PR.
For example, an abandoned unpublished 49.1.0 proposal may be replaced by 49.2.0.
Never move or reuse a published tag. Closing a PR alone does not permit recreating
the same inputs/version; changing a retry's version changes its branch identity.

The failure-reporting workflow creates or updates an assigned issue for a failed
trusted generation run. It does not guarantee email or Slack delivery; validate
notification settings during activation. Check the linked run and API report,
then close the issue after recovery. Pending CI is a wait state, not a failure.

## Local checks

```sh
python3 -m pip install --require-hashes -r pipeline/legacy/requirements.txt
python3 -B -m unittest discover -s pipeline/generation -p 'test_*.py' -v
python3 -B -m unittest discover -s pipeline/legacy -p 'test_*.py' -v
go test pipeline/generation/harden_internal_tests.go pipeline/generation/harden_internal_tests_test.go
actionlint .github/workflows/generate-go-sdk.yml .github/workflows/sdk-pipeline-checks.yml
```

`generate.py --output DIR` requires the trusted GitHub context and a clean exact checkout. `publish_pr.py --artifact DIR --unsigned` validates local packages and cannot publish them. Signature-policy unit tests mock the cryptographic subprocess boundary; they do not establish real hosted signing or App permissions.
