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

- **Concept Search**: Find medical concepts across OMOP vocabularies
- **Cohort Building**: Create and validate cohort definitions programmatically  

Available Tools: 

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


## Installation

The installation depends on which transport mode you plan to use:

### stdio Mode Installation

#### Recommended: Using pipx (isolated installation)
```bash
# Install pipx if you don't have it (like npx for Python)
pip install pipx

# Install ohdsi-webapi-mcp in an isolated environment
pipx install ohdsi-webapi-mcp

# Commands available: ohdsi-webapi-mcp, ohdsi-webapi-mcp-http
```

#### Alternative: Global installation
```bash
pip install ohdsi-webapi-mcp
```

#### Docker (stdio mode)
```bash
# For MCP clients that spawn processes (like Claude Desktop)
# Uses default entrypoint: ohdsi-webapi-mcp
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest
```

### HTTP Mode Installation

#### Using pipx/pip (same as above)
```bash
pipx install ohdsi-webapi-mcp
# Then run: ohdsi-webapi-mcp-http
```

#### Docker (HTTP mode)
```bash
# For web access and remote MCP clients
# Overrides entrypoint to: ohdsi-webapi-mcp-http
docker run -p 8000:8000 --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest \
  ohdsi-webapi-mcp-http

# Server available at: http://localhost:8000
# MCP endpoint at: http://localhost:8000/mcp
# API docs at: http://localhost:8000/docs
```

### Development Installation
```bash
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
pip install -e .

# Available commands:
# ohdsi-webapi-mcp          (stdio mode)
# ohdsi-webapi-mcp-http     (HTTP mode)
```

**Why pipx?** Like `npx` for Node.js, `pipx` installs CLI tools in isolated environments so they don't conflict with your other Python packages, but the commands are still available globally.




## MCP Client Configuration

### stdio Mode (Traditional)

#### Claude Desktop
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "ohdsi-webapi-mcp",
      "env": {
        "WEBAPI_BASE_URL": "https://your-webapi-instance.org/WebAPI"
      }
    }
  }
}
```

#### VS Code with MCP Extension
```json
{
  "mcp.servers": [
    {
      "name": "ohdsi-webapi",
      "command": ["ohdsi-webapi-mcp"],
      "env": {
        "WEBAPI_BASE_URL": "https://your-webapi-instance.org/WebAPI"
      }
    }
  ]
}
```

#### Docker (stdio mode)
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI",
        "ghcr.io/clsweeting/ohdsi-webapi-mcp:latest"
      ]
    }
  }
}
```

### HTTP Mode (Modern)

#### Start the HTTP Server
```bash
# Start HTTP server on default port 8000
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI ohdsi-webapi-mcp-http

# Or with custom port
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI MCP_PORT=8080 ohdsi-webapi-mcp-http
```

#### Claude Desktop (HTTP mode)
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### Web Integration
```javascript
// Access as regular REST API
const response = await fetch('http://localhost:8000/concepts/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'diabetes',
    limit: 10
  })
});

// Or browse the interactive docs at http://localhost:8000/docs
```

#### Docker (HTTP mode)
```bash
# Run HTTP server in Docker (overrides default stdio entrypoint)
docker run -p 8000:8000 \
  -e WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest \
  ohdsi-webapi-mcp-http

# Then configure Claude Desktop with: http://localhost:8000/mcp
```

### Environment Variables

Both modes support the same environment variables:

- **`WEBAPI_BASE_URL`** (required): Base URL of your OHDSI WebAPI instance
- **`WEBAPI_SOURCE_KEY`** (optional): Default CDM source key for cohort operations
- **`MCP_PORT`** (HTTP mode only): Port for HTTP server (default: 8000)
- **`MCP_HOST`** (HTTP mode only): Host for HTTP server (default: 0.0.0.0)
- **`LOG_LEVEL`** (optional): Logging level (default: INFO)

## Testing & Development

### Quick HTTP API Test
```bash
# Start the HTTP server
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI ohdsi-webapi-mcp-http

# Test with curl (in another terminal)
curl -X POST "http://localhost:8000/concepts/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes", "limit": 5}'

# Check health
curl http://localhost:8000/health

# Browse interactive docs
open http://localhost:8000/docs
```

### MCP Client Testing
```bash
# Test stdio mode
echo '{"method": "tools/list", "params": {}}' | WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI ohdsi-webapi-mcp

# Test HTTP mode MCP endpoint
curl http://localhost:8000/mcp
```


## Developing & Contributing

Please see [docs/development.md](docs/development.md) for more information. 

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Related Projects

- [ohdsi-webapi-client](https://github.com/clsweeting/ohdsi-webapi-client) - Python client for OHDSI WebAPI
- [ohdsi-cohort-schemas](https://github.com/clsweeting/ohdsi-cohort-schemas) - Pydantic models for OHDSI cohort definitions
