# plaid-OpenAPI

Plaid uses the `OpenAPI 3.0.0` specification to schematize our [docs](https://plaid.com/docs) and to generate our supported client libraries. This provides for a consistent typing experience across our external interfaces. Below we have listed some examples and issues we have found when iterating on the specification.

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
