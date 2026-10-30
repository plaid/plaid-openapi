# Generate and publish the Go SDK

An approved merge to `plaid/plaid-openapi` drives the Go release: generate both clients, validate them, attest the exact output, open a ready SDK PR, integrate it after automated checks, then attest and publish its signed version tag. Compatible updates within v49 need no separate human SDK approval or merge.

The spec and Fern configuration live together in this public repository. Each production run uses `GITHUB_SHA` for both inputs. Push, scheduled catch-up and manual production generation run only from the original public repository's `master`; pull-request, fork and repository-dispatch contexts cannot enter that pipeline. Manual runs can choose a reviewed version override, but cannot choose another spec commit or URL.

## Pre-merge hosted rehearsal

`sdk-rehearsal.yml` runs on same-repository PRs changing that workflow or
`pipeline/rehearsal/`. It checks out the exact PR head and the SDK commit pinned
in `pipeline/rehearsal/run.py`, so neither automation PR needs to merge first.
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
- The generation job has read-only GitHub permissions and no publishing credential. It checks the CLI archive checksum and executes the generator by immutable image digest. The public-only legacy generator receives exactly the same spec bytes.
- Maintained customizations, license, release history and release/integration automation survive generation. An unexpected generated caller change stops the run until its runtime is reconciled with the destination and redirect checks.
- Fern Go 1.70.3 regenerates the transfer diligence upload's `purpose` field as JSON, adding quotes. A narrow post-generation correction restores the [published v49 text-field behavior](https://github.com/plaid/plaid-go/blob/0d83b050ea325adda35c6d88bdf24b46fe2f7044/transfer/diligence/raw_client.go#L103). It checks the exact generator version, method, endpoint and serialization shape, recognizes already-correct output, and stops on unknown shapes. The public upload regression test is preserved; the generated file is otherwise refreshed normally.
- `harden_wire_tests.py` sets explicit dummy credentials and custom mock endpoints in the reviewed generated test shapes. WireMock mappings require those headers; compose binds only to loopback without verbose request logging. The helper rejects unfamiliar generator versions or test shapes. Runtime destination checks stay enabled.
- Before generation, every operation must have an explicit Fern group and method
  name after applying the overlay, and request bodies must not retain top-level
  `client_id` or `secret` fields. Shared request schemas are checked too. `overlay_coverage.py --fix` writes the missing
  entries into the checked-in overlay for review; generation never infers names
  or removals on its own.
- The Go floor build and complete local mock suite run before producing the candidate. Compatibility is checked against the latest published stable tag in the configured major, including `legacy/`. A breaking change stops generation and preserves `api-diff.txt` plus a `breaking-change` result in the run artifacts. The current implementation is v49-only; a new major needs reviewed module/import migration work in both clients. Legacy continues to regenerate from the same spec.
- If a generation has merged but its tag is absent, the job returns `awaiting-release` before choosing another version. The tag must be annotated and peel to the exact first-parent commit that introduced the manifest. A tag on the generated PR head or another commit is rejected. Later unrelated commits carrying the same published manifest are allowed.
- A separate job validates the package and uses public Sigstore attestation to bind its content digest to the manifest. The signed source and config repository/commit must match `plaid/plaid-openapi` and the same workflow SHA. Verification requires the exact workflow, `master`, public visibility, run identity, predicate and subject. No generated SDK code executes in this job.
- The PR job verifies the signature before obtaining its narrowly scoped App token. `SDK_PR_APP_BOT_ID` pins the numeric bot user ID; the public SDK integration and release workflows use the same identity. Same-input retries recheck the existing ready PR, base, one-parent generation commit, content and signature. They never rebase or overwrite existing branches, change drafts, or recreate closed PRs.

Public artifact uploads are explicitly limited to `sdk.tar.gz`, `content.json`, `manifest.json`, `plan.json`, `result.json`, the public `api-diff.txt` comparison when generation stops on a breaking change, and the signed `generation.bundle.json`. Environment dumps, raw CLI debug output, test logs and temporary work directories are not uploaded. The CLI debug file used to check the raw generated caller stays in disposable local storage; failed logged subprocess output is withheld from public job logs. SDK `.fern/metadata.json` contains only version identity.

## Activation

1. Verify CODEOWNERS resolves to maintainers with write access and enable required code-owner review for public spec, `fern/`, `pipeline/` and workflow changes. Land the public SDK's maintained customizations, integration/release automation and ownership rules. For the first automatic release after a manual release, install its reviewed predecessor pins.
2. Set `SDK_FAILURE_ASSIGNEE` to a repository maintainer and verify assigned failure issues reach them. Leave `SDK_PIPELINE_ENABLED`, `SDK_AUTOMERGE_ENABLED` and `SDK_RELEASE_ENABLED` off while preparing. `rehearsal: true` only generates and tests; trusted workflow input guards prevent signing or PR publication even if artifact outputs change.
3. In this repo, configure `SDK_PR_APP_ID`, `SDK_PR_APP_PRIVATE_KEY` and `SDK_PR_APP_BOT_ID` for the protected `sdk-pr-publishing` environment. Restrict it to `master` without a per-run reviewer gate. The PR App needs Contents and Pull requests write only on `plaid-go`, with no workflow permission or review bypass. Configure the separate integration and release identities in the SDK repo.
4. After approving deployment, enable generation and run a real signed candidate while automatic integration and release remain disabled. Validate the public integration workflow's no-write mode, then enable automatic integration with tag publication still disabled. Run the public release's no-tag attestation rehearsal and verify the exact control/signing identities and repository protections.
5. Enable publication only after the hosted rehearsal passes. Dispatch the first already-merged candidate explicitly; enabling a flag does not replay an old push event. Thereafter approved input changes should generate, integrate and publish automatically.

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
