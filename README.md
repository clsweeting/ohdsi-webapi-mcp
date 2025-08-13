# OHDSI WebAPI MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Model Context Protocol (MCP) server that provides LLM agents with tools to interact with OHDSI WebAPI for cohort building and analysis.

## Transport Modes

This server supports **two transport modes** to fit different use cases:

### 📟 **stdio Mode** (Traditional)
- **Best for**: Local MCP clients, command-line usage
- **Transport**: stdin/stdout communication
- **Command**: `ohdsi-webapi-mcp`
- **Use case**: Claude Desktop, VS Code MCP extension

### 🌐 **HTTP Mode** (Modern)
- **Best for**: Web integration, remote access, testing
- **Transport**: HTTP with Server-Sent Events (SSE)
- **Command**: `ohdsi-webapi-mcp-http`
- **Use case**: Web applications, remote MCP clients, API testing
- **Bonus**: Includes Swagger UI at `/docs` for API exploration

## Supported Functionality

### Concept Discovery
- `search_concepts` - Search for medical concepts by name or code
- `get_concept_details` - Get detailed information about a specific concept
- `browse_concept_hierarchy` - Navigate concept relationships and hierarchies

### Cohort Building
- `create_concept_set` - Build reusable concept sets
- `define_primary_criteria` - Set index event criteria
- `add_inclusion_rule` - Add filtering criteria with time windows
- `validate_cohort_definition` - Validate cohort logic and structure

### Persistence & Analysis
- `save_cohort_definition` - Save cohort to WebAPI
- `load_existing_cohort` - Retrieve saved cohort definitions
- `estimate_cohort_size` - Preview patient counts
- `compare_cohorts` - Analyze differences between cohort definitions


## Quick Start

Choose your preferred transport mode:

### 📟 **stdio Mode** (Traditional MCP)
Perfect for Claude Desktop, VS Code, and local MCP clients.

```bash
# Install
pipx install ohdsi-webapi-mcp

# Configure Claude Desktop (see docs/stdio-setup.md for details)
# Start with just the WebAPI URL - no source key needed initially!
# Then ask Claude: "Search for diabetes concepts in OMOP"
```

**→ [Complete stdio Setup Guide](docs/stdio-setup.md)**

### 🌐 **HTTP Mode** (Modern Web API)
Great for web apps, testing, and remote access with Swagger UI.

```bash
# Install & run
pipx install ohdsi-webapi-mcp
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI ohdsi-webapi-mcp-http

# Test the API (no source key needed for concept searches!)
curl http://localhost:8000/health
open http://localhost:8000/docs  # Interactive API docs
```

**→ [Complete HTTP Setup Guide](docs/http-setup.md)**

## Installation

Both modes use the same installation - choose your method:

### Recommended: pipx
```bash
pip install pipx
pipx install ohdsi-webapi-mcp
```

### Alternative: pip
```bash
pip install ohdsi-webapi-mcp
```

### Alternative: Docker
```bash
# stdio mode (start with concept searches - no source key needed!)
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest stdio

# HTTP mode (same - source key optional)
docker run -p 8000:8000 --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest http
```




## Environment Variables

Both modes support the same environment variables:

- **`WEBAPI_BASE_URL`** (required): Base URL of your OHDSI WebAPI instance
- **`WEBAPI_SOURCE_KEY`** (optional): CDM source key - only needed for cohort operations, not concept searches
- **`MCP_PORT`** (HTTP mode only): Port for HTTP server (default: 8000)
- **`MCP_HOST`** (HTTP mode only): Host for HTTP server (default: 0.0.0.0)
- **`LOG_LEVEL`** (optional): Logging level (default: INFO)

💡 **New to OHDSI?** Start with just `WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI` - most features work without a source key!

## Documentation

- **[stdio Mode Setup](docs/stdio-setup.md)** - Complete guide for Claude Desktop, VS Code, and traditional MCP clients
- **[HTTP Mode Setup](docs/http-setup.md)** - Complete guide for web integration, API access, and modern MCP clients

## Development

For development setup, testing, and contributing:

```bash
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
pip install -e ".[dev]"

# Run tests
make test

# Available commands:
# ohdsi-webapi-mcp          (stdio mode)
# ohdsi-webapi-mcp-http     (HTTP mode)
``` 

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Related Projects

- [ohdsi-webapi-client](https://github.com/clsweeting/ohdsi-webapi-client) - Python client for OHDSI WebAPI
- [ohdsi-cohort-schemas](https://github.com/clsweeting/ohdsi-cohort-schemas) - Pydantic models for OHDSI cohort definitions
