# Automatic Go SDK releases

After an approved change to the public spec or Go generation configuration merges
to `master`, this repository generates both Go clients from that exact commit,
checks compatibility, and signs a record of the inputs and output. A scoped App
opens a generated PR in `plaid/plaid-go`. That repository verifies the signature,
protected files and required CI before automatically merging and publishing a
signed version tag. Normal releases need no second human approval or button press.

This implementation is disabled by default. Spec/config/workflow changes still
require human review. The SDK integration and publication controls must be reviewed
and installed before enabling the producer here.

## Inputs and maintained behavior

`fern/` contains only the released Go configuration. The workflow reads the spec
and config at the same commit; there is no second spec copy to synchronize and no
cross-repository notification App. Each future language should have an independent
workflow, generator pin, version policy, checks and publisher.

The legacy generator uses pinned, already-public Go SDK templates and a small
standalone adapter. Its provenance and verification instructions are under
`pipeline/legacy/`. It keeps the legacy client's existing identity and the shared
root module; it does not copy the internal monorepo or its Git history.

Generation preserves handwritten SDK files, release controls and previous release
history. It compares public API compatibility with the latest published version.
Breaking changes stop for an explicitly reviewed major transition. The normal
version proposal is the next minor within the configured major. Generation waits
for a merged candidate to be tagged before proposing another version. Edited,
draft or closed generated PRs are not overwritten or reopened automatically.

## Permissions and activation

1. Protect `master` with human and code-owner review for the spec, Fern settings,
   pipeline code and workflows. PR checks must not receive publishing credentials
   or run untrusted code through `pull_request_target`.
2. Install the SDK PR App only on `plaid/plaid-go` with Contents write and Pull
   requests write. It needs no workflow permission, Administration write, branch
   review bypass or release-tag creation permission.
3. Create `sdk-pr-publishing`, restricted to protected `master`, with
   `SDK_PR_APP_PRIVATE_KEY`. Configure repository variables `SDK_PR_APP_ID` and
   `SDK_PR_APP_BOT_ID` (the App's numeric GitHub bot user ID). Normal runs must not
   require an environment approval. The SDK repo configures the separate merge
   and tag-publishing identities and their controls.
4. Keep `SDK_PIPELINE_ENABLED` absent/false. Use the explicit `rehearsal` input to
   generate and validate without signing, opening PRs or creating tags. Generation
   and testing get no publishing credentials. Publish only the allowlisted SDK
   artifacts; do not upload work directories, arbitrary logs or environment dumps.
5. Rehearse real public attestations and PR creation, then automatic merging and
   signed publication against an approved disposable destination. Verify retries,
   edited/stale candidates, conflicting tags, status-check enforcement and clean
   module installation. Local tests do not prove hosted permissions.
6. Confirm workflow failure notifications reach the owning team, then enable the
   reviewed stages. Disable generation, integration and release flags to pause the
   pipeline; keep the reviewed manual release procedure available. Never move or
   reuse a published version.

The public SDK's release setup must record the existing manual v49.0.0 tag and its
exact spec/SDK commits before the first automated successor. Existing published
versions are never regenerated in place.

Credentials live in protected Actions secrets, never in this repository. Public
configuration and public logs must not contain internal-only material. This repo
uses public GitHub attestations, so it does not require a private config repository
or a private-attestation read credential.
