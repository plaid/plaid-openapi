# SDK generation configuration

This directory is the source of truth for Fern SDK configuration and the public
spec at `../2020-09-14.yml`. Update generator pins, client options, and the shared
overlay here.

The `go-sdk` group targets `plaid/plaid-go` through the existing production
pipeline. TypeScript, Python, Java, and Ruby default to local output under
`generated/`. Release automation supplies its destination and package metadata
separately while using the generator versions and client options defined here.

- `fern.config.json` pins the Fern CLI.
- `generators.yml` pins each language generator and its client options.
- `openapi-overlay.yml` supplies sub-client names, pagination, typed errors,
  client-level authentication and the multipart upload correction.

Overlay coverage is checked before Go generation runs. Shared spec-sync PRs
test the validation logic without requiring the Go overlay to be ready. To
check readiness manually, run `python3 pipeline/generation/overlay_coverage.py`
from the repository root.

The workflow checks that the CLI and generator versions match the checksum/image
pins in `pipeline/generation/settings.json`. The public module is
`github.com/plaid/plaid-go/v49`; SDK versions passed to Fern include the leading
`v`. Preserve the `Plaid-Version` header and disabled automatic retries when
updating configuration, unless a behavior change is explicitly reviewed.

When adding an operation to the spec, run
`python3 pipeline/generation/overlay_coverage.py --fix` from the repository root
(with `pipeline/legacy/requirements.txt` installed). It adds the credential
removals and a suggested sub-client/method name; review the suggested name,
because it becomes a public method, and add pagination where needed. The overlay
strips legacy request-body credentials because the new client supplies them
through client options. Never put real
credentials, private endpoints, or unpublished API definitions in these files.

Configuration changes alone do not authorize a release. Publication stays off
until the repository controls and hosted rehearsal in `../SDK_AUTOMATION.md`
are complete.
