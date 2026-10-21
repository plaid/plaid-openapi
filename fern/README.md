# Released SDK configuration

This directory contains the production Go SDK configuration for the public spec
at `../2020-09-14.yml`. Spec and configuration changes are reviewed together; the
workflow generates from their exact shared commit. Only Go is enabled here.
Configurations for other languages can be added when ready, with independent
version pins, checks and release workflows. Draft configurations stay in staging.

- `fern.config.json` pins the Fern CLI.
- `generators.yml` pins the Go generator and client options.
- `openapi-overlay.yml` supplies sub-client names, pagination, typed errors,
  client-level authentication and the multipart upload correction.

The workflow checks that the CLI and generator versions match the checksum/image
pins in `pipeline/generation/settings.json`. The public module is
`github.com/plaid/plaid-go/v49`; SDK versions passed to Fern include the leading
`v`. Preserve the `Plaid-Version` header and disabled automatic retries when
updating configuration, unless a behavior change is explicitly reviewed.

When adding an operation to the spec, update its sub-client/method naming and
pagination where needed. The overlay strips legacy request-body credentials
because the new client supplies them through client options. Never put real
credentials, private endpoints, or unpublished API definitions in these files.

Configuration changes alone do not authorize a release. Publication stays off
until the repository controls and hosted rehearsal in `../SDK_AUTOMATION.md`
are complete.
