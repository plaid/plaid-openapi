# plaid-openapi-beta

More documentation coming 2/15/21.

## Using the OpenAPI generator

You can use either `docker-cli` or `npm` to install the generator dependency.

**Docker example:**

- Directory that docker runs in and where the OpenAPI file should be located.

`CURRENT_DIR="~/plaid"`

- Directory for generated code output.

`OUTPUT_FOLDER="python"`

```bash
docker run --rm -v $(CURRENT_DIR):/local openapitools/openapi-generator-cli:v5.0.0 generate \
-g python -i local/2020-09-14.yml \
-o local/$(OUTPUT_FOLDER)/generated-python \
-p packageName=plaid
```

**NPM example:**
1. `npm install @openapitools/openapi-generator-cli` the generator dependency.

2. Run the `openapi-generator-cli generate` command.

```bash
openapi-generator-cli generate \
-g python \
-i ./2020-09-14.yml \
-o generated-python \
-p packageName=plaid
```