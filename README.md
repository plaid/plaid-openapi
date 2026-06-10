# plaid-OpenAPI

Plaid uses the `OpenAPI 3.0.0` specification to schematize our [docs](https://plaid.com/docs) and to generate our supported client libraries. This provides for a consistent typing experience across our external interfaces. Below we have listed some examples and issues we have found when iterating on the specification.

## Adding a new `x-*` extension tag

If your edit to the OpenAPI spec introduces a new `x-*` extension, add or update its entry on the Slite [Extension Tags](https://plaid.slite.com/app/docs/O4qPiIyok-7HnF) page in the same PR (or link the follow-up doc PR from this PR's description). The Slite [Editing the OpenAPI file](https://plaid.slite.com/app/docs/6fx_S6U4ai4GdT) workflow carries the canonical step-by-step; in short, the Extension Tags entry should record:

- **granularity** — which scope(s) the tag is valid on (schema, object, field, path, operation, `$ref` target);
- **survives strip?** — whether the tag passes through `cmd/process.go` into the published `2020-09-14.yml`, or is stripped before consumers see it (all `x-plaid-*` are stripped by the prefix rule at `process.go:348-349`; explicitly-internal non-`x-plaid-*` tags belong in `internalUseFields` at `process.go:20-23`);
- **primary consumer** — the file(s) that read the tag, with `file.go:NNN` citations;
- **enforced vs intent-only** — `x-hidden-from-docs` at path/operation scope is the canonical intent-only example, and is the source of most author confusion.

Pure codegen internals with no author-visible decision may be skipped if you record the reason at the definition site. Background: per the 2026-04-23 inventory, half of the spec's 20 `x-*` extensions had no Extension Tags row before that revision; missing this step is how that gap accumulated.

## Using the OpenAPI generator

You can find examples on the official [OpenApiGenerator docs](https://github.com/OpenAPITools/openapi-generator#3---usage).

### Generating Plaid supported client libraries

The following are approximate commands that we use to generate our 5 client libraries:

#### plaid-node
OpenAPI Generator version: 5.1.1

```bash
openapi-generator-cli generate -g typescript-axios  \
-i 2020-09-14.yml \
-o build/generated-node \
-p npmName=plaid,supportsES6=true,modelPropertyNaming=original \
-t local/templates/typescript-axios
```

#### plaid-python
OpenAPI Generator version: 6.1

```bash
openapi-generator-cli generate -g python \
-i 2020-09-14.yml \
-o build/generated-python \
-p packageName=plaid \
--global-property apiTests=false,modelTests=false \
-t templates/python
```

#### plaid-ruby
OpenAPI Generator version: 6.3

```bash
openapi-generator-cli generate -g ruby  \
-i 2020-09-14.yml \
-o build/generated-ruby \
--global-property=apiTests=false,modelTests=false,useAutoload=true  \
--library=faraday \
-p gemName=plaid,gemRequiredRubyVersion=">= 3.0.0" \
-t local/templates/ruby

```

#### plaid-java
OpenAPI Generator version: 5.1.1

```bash
openapi-generator-cli generate -g java \
-i 2020-09-14.yml \
-o build/generated-java \
--library=retrofit2 \
--global-property apiDocs=false,modelDocs=false,apiTests=false,modelTests=false \
-p artifactId=plaid,apiPackage=com.plaid.client.request,modelPackage=com.plaid.client.model,dateLibrary=java8 \
-t templates/java \
--type-mappings=BigDecimal=Double
```

#### plaid-go
OpenAPI Generator version: 5.2

```bash
openapi-generator-cli -g go \
-i 2020-09-14.yml \
-o build/plaid-go \
--global-property=apiTests=false,modelTests=false,apiDocs=false,modelDocs=false \
-t templates/go \
-p packageName=plaid,enumClassPrefix=true,
```

All template edits can be found on their corresponding in the `/templates` folder for the associated library.

### Known issues with openapi-generator

The [openapi-generator](https://github.com/OpenAPITools/openapi-generator) often uses different styles based on the language you are generating.

- We found that we had to modify our mustache templates to get `servers` and `securitySchemes` working for some generators. If possible, try not to modify these templates as they cause breaking changes upon upgrading, but modifications might be necessary for cases like these.

- Enums as used by Plaid are extensible; that is, the API may add new enum values at will. However, OpenAPI generator for some languages will enable enum validation by default. You must disable strict enum validation for responses in your generated libraries, or your users may experience crashes when encountering a newly-added enum value in a response.
