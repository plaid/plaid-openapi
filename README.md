# plaid-OpenAPI-beta

Plaid uses the `OpenAPI 3.0.0` specification to schematize our [docs](https://plaid.com/docs) and to generate our supported client libraries (in beta). This provides for a consistent typing experience across our external interfaces. Below we have listed some examples and issues we have found when iterating on the specification.

## Using the OpenAPI generator

You can use either `docker-cli` or `npm` to install the generator dependency.

### Docker

| Env var       | Example value | Description                                                                 |
|---------------|---------------|-----------------------------------------------------------------------------|
| CURRENT_DIR   | ~/plaid       | Directory that docker runs in and where the OpenAPI file should be located. |
| OUTPUT_FOLDER | python        | Directory for generated code output.                                        |



```bash
docker run --rm -v $(CURRENT_DIR):/local openapitools/openapi-generator-cli:v5.0.0 generate \
-g python -i local/2020-09-14.yml \
-o local/$(OUTPUT_FOLDER)/generated-python \
-p packageName=plaid
```

### NPM

1. Install the generator dependency `npm install @openapitools/openapi-generator-cli -g`

2. Run the `openapi-generator-cli generate` command.

```bash
openapi-generator-cli generate \
-g python \
-i ./2020-09-14.yml \
-o generated-python \
-p packageName=plaid
```

### Generating Plaid supported client libraries

#### plaid-node

```bash
openapi-generator-cli generate -g typescript-axios  \
-i 2020-09-14.yml \
-o build/generated-node \
-p npmName=plaid,supportsES6=true,npmVersion='9.0.0-beta.10',modelPropertyNaming=original \
-t local/templates/typescript-axios
```

#### plaid-python

```bash
openapi-generator-cli generate -g python \
-i 2020-09-14.yml \
-o build/generated-python \
-p packageName=plaid,packageVersion=8.0.0b6 \
--global-property apiTests=false,modelTests=false \
-t templates/python
```

#### plaid-ruby

```bash
openapi-generator-cli generate -g ruby  \
-i 2020-09-14.yml \
-o build/generated-ruby \
--global-property=apiTests=false,modelTests=false  \
--library=faraday \
-p gemName=plaid,gemRequiredRubyVersion=">= 2.7.1",gemVersion=14.0.0.beta1 \
-t local/templates/ruby

```

#### plaid-java

```bash
openapi-generator-cli generate -g java \
-i 2020-09-14.yml \
-o build/generated-java \
--library=retrofit2 \
--global-property apiDocs=false,modelDocs=false,apiTests=false,modelTests=false \
-p artifactId=plaid,apiPackage=com.plaid.client.request,modelPackage=com.plaid.client.model,artifactVersion=9.0.0-beta-1 \
-t templates/java \
--type-mappings=BigDecimal=Double
```

All template edits can be found on their corresponding `plaid-language` beta release branches in the `/templates` folder.

### Known issues with openapi-generator

The [openapi-generator](https://github.com/OpenAPITools/openapi-generator) often uses different styles based on the language you are generating.

- Not all generators fully support the `servers` or `securitySchemes` components of the `OpenAPI 3.0.0` spec. You may find yourself needing to markup the underlying `.mustache` templates ingested by the generator.
- Sometimes there are issues when upgrading the generator versions to minor and patch releases. For ease of upgrade, its best to limit your modification of the underlying `.mustache` templates to as little as possible.
