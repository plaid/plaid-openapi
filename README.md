# plaid-OpenAPI-beta

Plaid uses the `OpenAPI 3.0.0` specification to schematize our [docs](https://plaid.com/docs) and to generate our supported client libraries (in beta). This provides for a consistent typing experience across our external interfaces. Below we have listed some examples and issues we have found when iterating on the specification.

## Using the OpenAPI generator

You can find examples on the official [OpenApiGenerator docs](https://github.com/OpenAPITools/openapi-generator#3---usage).

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
-p artifactId=plaid,apiPackage=com.plaid.client.request,modelPackage=com.plaid.client.model,artifactVersion=9.0.0-beta-1,dateLibrary=java8 \
-t templates/java \
--type-mappings=BigDecimal=Double
```

All template edits can be found on their corresponding `plaid-language` beta release branches in the `/templates` folder.

### Known issues with openapi-generator

The [openapi-generator](https://github.com/OpenAPITools/openapi-generator) often uses different styles based on the language you are generating.

- We found that we had to modify our mustache templates to get `servers` and `securitySchemes` working for some generators. If possible, try not to modify these templates as they cause breaking changes upon upgrading, but modifications might be necessary for cases like these.
