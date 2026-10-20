# Public legacy Go generation

This adapter regenerates `legacy/` in an existing public v49 SDK checkout. The root Fern client and the existing `legacy/tests` are preserved. It uses only the public sources listed in `provenance.json`; no private generator helper or test adapter is required.

Install Python dependencies with `python3 -m pip install --require-hashes -r pipeline/legacy/requirements.txt`. Python 3.10+, Docker, and Go are required. The Docker image must be available locally or pullable; generation runs with container networking disabled. Go may download the checkout's module dependencies during staging. Subprocesses receive only selected local path, Docker, Go toolchain, and cache settings; unrelated credentials are excluded, and `GOENV`/`GOWORK` are disabled.

```sh
python3 pipeline/legacy/generate.py \
  --spec /absolute/path/2020-09-14.yml \
  --sdk /absolute/path/plaid-go \
  --module github.com/plaid/plaid-go/v49 \
  --manifest /absolute/path/outside-sdk/legacy-manifest.json
python3 -m unittest discover -s pipeline/legacy -p 'test_*.py'
```

Use physical absolute paths, without symlink components. The manifest must not exist, and its parent directory must already exist. The adapter rejects duplicate YAML keys, external or unresolved references, unsupported union shapes, symlinks, incomplete generator output, and replacement of handwritten legacy Go files. It stages generation and module tidy, runs offline legacy tests, and compiles the `plaid_integration` tests with `-run=^$` before replacing any SDK files. It never runs Sandbox tests. Ordinary installation errors restore the previous legacy directory and module files; process termination during installation is not a transactional filesystem operation.

The only dependency additions are missing `oauth2` and `testify` requirements from the public SDK; existing selected versions are retained before `go mod tidy`. Only `legacy/`, `go.mod`, and `go.sum` may change. Root source files are copied for staged compilation and never installed back.

## Union preparation

The public spec has four discriminated `oneOf` schemas. The public v48 `model_oneof.mustache` expects `x-plaid-sdk-one-of-interface`, which the public spec does not contain. The adapter validates that every branch has exactly one explicit mapping and a required, single-value string discriminator, then adds the marker to a temporary generation input.

OpenAPI Generator 5.2.0 also includes Go class names in its `mappedModels`, in addition to explicit wire values. The sole vendored template patch changes the two strict discriminator loops to use `x-plaid-sdk-one-of-mapping`, derived exclusively from the public spec's explicit mapping. This preserves published wire behavior and avoids accepting class names or rejecting valid branches during marshal. The other five templates and the upstream license are unchanged. `provenance.json` records both original and vendored hashes. All Python code and the offline regression fixture are newly authored here.

The legacy client keeps `packageVersion=48.0.0` and `Plaid Go v48.0.0`, matching the public v49 legacy package. Its module path remains `github.com/plaid/plaid-go/v49`. Client identity and module major version are separate.

## Reproduction evidence

Using public spec commit `496cde4222c0e6e9911796886b2b6fee45502ac9` (API 1.778.0), public template commit `7c6ddb9f8e1b2bc59f9761b2aa3878a9452779ff`, and the pinned image:

- The generated SDK matched public v49 commit `0d83b050ea325adda35c6d88bdf24b46fe2f7044` byte-for-byte: 2,735 files total, including all 2,246 generated legacy Go files. No files were added, removed, or changed; root `go.mod`/`go.sum` and legacy tests also matched.
- `go test ./legacy/...` passed. `go test -tags=plaid_integration -run=^$ ./legacy/...` compiled and passed without executing integration tests.
- Copying `testdata/union_test.go` temporarily into a generated package and running `go test -run=TestPublicDiscriminatorContract .` fails on raw-spec generation with `Data matches more than one schema in oneOf(CraReportGetRequestProduct)`. It passes against the prepared output, including rejection of a Go class name as a wire discriminator.
- The image's generator JAR hash was independently checked against `2199ced3e63a8015ed2fdb907fd2dfb056754b928c3d4c1c0b7194fb328733c9`.

The reproduction manifest's `tree_sha256` is `55086702e87547569337cc057e348305917157d1f7509eb4d79c8fd59ecd59b9`. Its input is JSON with no trailing newline and compact separators: a lexically sorted list of `["legacy/relative/path", "100644" or "100755", "file SHA-256"]` for every legacy file, including preserved tests. `spec_sha256` hashes the original spec bytes, and `source_commit` identifies the public template snapshot. This is evidence for the pinned spec and SDK baseline; future public spec changes still require review of their generated diff.
