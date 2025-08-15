## Configuration

Configuration is via environment variables

See [environment variables](./enviroment-variables.md)
- **`WEBAPI_BASE_URL`** (required): Base URL of your OHDSI WebAPI instance
  - Example: `https://atlas-demo.ohdsi.org/WebAPI`
- **`WEBAPI_SOURCE_KEY`** (optional): CDM source key for cohort operations
  - **Only needed for**: Creating cohorts, saving cohort definitions, generating cohorts
  - **Not needed for**: Concept searches, vocabulary browsing, concept details
  - **Demo value**: `EUNOMIA` (works with atlas-demo.ohdsi.org)
  - **Other examples**: `OPTUM_DOD`, `CCAE`, `MDCR` (depends on your WebAPI instance)
  - **How to find yours**: Visit your WebAPI at `/source/sources` or ask your OHDSI admin
- **`MCP_PORT`** (optional): Port for HTTP server (default: 8000)
- **`MCP_HOST`** (optional): Host for HTTP server (default: 0.0.0.0)
- **`LOG_LEVEL`** (optional): Logging level (default: INFO)
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

At it's simplest, you only really need `WEBAPI_BASE_URL` - pointing to your OHDSI WebAPI. 

For more information about WEBAPI_SOURCE_KEY, see [this document](./source_key.md). 





## Environment Variables

Both modes support the same environment variables:

- **`WEBAPI_BASE_URL`** (required): Base URL of your OHDSI WebAPI instance
- **`WEBAPI_SOURCE_KEY`** (optional): CDM source key - only needed for cohort operations, not concept searches
- **`MCP_PORT`** (HTTP mode only): Port for HTTP server (default: 8000)
- **`MCP_HOST`** (HTTP mode only): Host for HTTP server (default: 0.0.0.0)
- **`LOG_LEVEL`** (optional): Logging level (default: INFO)

💡 **New to OHDSI?** Start with just `WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI` - most features work without a source key!
