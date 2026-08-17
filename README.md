# plaid-OpenAPI

Plaid uses the `OpenAPI 3.0.0` specification to schematize our [docs](https://plaid.com/docs) and to generate our supported client libraries. This provides for a consistent typing experience across our external interfaces. Below we have listed some examples and issues we have found when iterating on the specification.

## Naming component schemas

Names under `components.schemas` must match `^[A-Za-z_][A-Za-z0-9_]*$` because the internal Go generators use each component name as a source identifier. Use the existing PascalCase convention (for example, `TransactionsGetRequest`); do not use hyphens, periods, spaces, or a leading digit. Internal generation fails capability validation and reports the offending component path when this requirement is violated.

## Adding a new `x-*` extension tag

If your edit to the OpenAPI spec introduces a new `x-*` extension, add or update its entry on the Slite [Extension Tags](https://plaid.slite.com/app/docs/O4qPiIyok-7HnF) page in the same PR (or link the follow-up doc PR from this PR's description). The Slite [Editing the OpenAPI file](https://plaid.slite.com/app/docs/6fx_S6U4ai4GdT) workflow carries the canonical step-by-step; in short, the Extension Tags entry should record:

- **granularity** — which scope(s) the tag is valid on (schema, object, field, path, operation, `$ref` target);
- **survives strip?** — whether the tag reaches the published `2020-09-14.yml`. All
  `x-plaid-*` and `internalUseFields` entries are stripped; generator-only tags must be
  re-derived in a throwaway input, as `prepare_oneof_openapi.rb` does for exact `oneOf`;
- **primary consumer** — the file(s) that read the tag, with `file.go:NNN` citations;
- **enforced vs intent-only** — `x-hidden-from-docs` at path/operation scope is the canonical intent-only example, and is the source of most author confusion.

Pure codegen internals with no author-visible decision may be skipped if you record the reason at the definition site. Background: per the 2026-04-23 inventory, half of the spec's 20 `x-*` extensions had no Extension Tags row before that revision; missing this step is how that gap accumulated.

## Exact-discriminator `oneOf` support across the five SDKs

A named top-level component `oneOf` must use bare local branch references, an explicit
one-to-one `discriminator.mapping`, and a required singleton discriminator enum on each
direct object branch. Branches may be open or closed; `additionalProperties` controls model
evolution independently of discriminator dispatch. Other named top-level `oneOf` shapes fail
processing. Keep response branches and their nested objects open for additive compatibility;
server-side request strictness is configured separately.

| Language | Construct emitted | What you hold after decode |
|---|---|---|
| Go | `struct` wrapper | the wrapper — inspect its typed branch field or call `GetActualInstance()` |
| Java | `interface` | the branch — `instanceof` |
| Python | `class(ModelComposed)` | the branch — `isinstance` |
| Ruby | `module` | the branch — `is_a?` |
| Node | type alias | the branch — narrow on the discriminator |

Go, Java, Python, and Ruby dispatch at runtime and reject missing or unknown discriminator
values. Node provides compile-time narrowing only; axios returns parsed JSON without runtime
discriminator validation.

Go is the only SDK that returns a wrapper. Its `<Branch>As<Union>(...)` helpers construct
request wrappers; they are not decode accessors. Python also enforces required fields during
deserialization while Go leaves missing fields at their zero values.

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
