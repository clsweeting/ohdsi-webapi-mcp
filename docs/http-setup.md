# OHDSI WebAPI MCP Server - HTTP Mode Setup

The standard remote transport for MCP servers is "Streamable HTTP," which uses HTTP POST for client-to-server messages and can optionally use Server-Sent Events (SSE) for server-to-client streaming.

This mode is ideal for:

- Web applications and remote access
- API testing and development
- Modern MCP clients that support HTTP transport
- Integration with web frameworks


## Installation

### Recommended: Using pipx
```bash
# Install pipx if you don't have it (like npx for Python)
pip install pipx

# Install ohdsi-webapi-mcp in an isolated environment
pipx install ohdsi-webapi-mcp

# Command available: ohdsi-webapi-mcp-http
```

### Alternative: Global installation
```bash
pip install ohdsi-webapi-mcp
```

### Development Installation
```bash
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
pip install -e .
```




## Starting the HTTP Server

### Basic Usage
```bash
# Start on default port 8000 (most features work without source key)
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI ohdsi-webapi-mcp-http

# Server will be available at:
# - Health check: http://localhost:8000/health
# - MCP endpoint: http://localhost:8000/mcp
# - API docs: http://localhost:8000/docs
```

### With Cohort Features
```bash
# Basic usage (works for most operations)
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
ohdsi-webapi-mcp-http

# Add source key only if you need cohort size estimation
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
WEBAPI_SOURCE_KEY=EUNOMIA \
ohdsi-webapi-mcp-http
```

### Custom Configuration
```bash
# Custom port and host (minimal config)
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
MCP_PORT=8080 \
MCP_HOST=0.0.0.0 \
ohdsi-webapi-mcp-http

# Full configuration with cohort size estimation support
WEBAPI_BASE_URL=https://your-webapi.org/WebAPI \
MCP_PORT=8080 \
MCP_HOST=0.0.0.0 \
WEBAPI_SOURCE_KEY=YOUR_CDM_SOURCE \
ohdsi-webapi-mcp-http
```

### Background Process
```bash
# Run in background
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
nohup ohdsi-webapi-mcp-http > server.log 2>&1 &

# Check if running
curl http://localhost:8000/health
```



## Alternative: Docker Setup

### Using Pre-built Image
```bash
# Basic setup (concept searches, vocabulary browsing)
docker run -p 8000:8000 --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest http

# With cohort size estimation features
docker run -p 8000:8000 --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  -e WEBAPI_SOURCE_KEY="EUNOMIA" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest http

# Server available at http://localhost:8000
```

-------------


## API Access & Testing

### REST API Endpoints

The HTTP mode exposes both MCP and REST endpoints. You can explore the REST API endpoints at `http://localhost:8000/docs` 

### Testing with curl 

Health check endpoint: 

```bash
curl http://localhost:8000/health
```

Concept search: 

```bash
curl -X POST "http://localhost:8000/concepts/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes",
    "domain": "Condition",
    "limit": 5
  }'
```

Get concept details: 

```bash
curl -X POST "http://localhost:8000/concepts/details" \
  -H "Content-Type: application/json" \
  -d '{
    "concept_id": 201826
  }'
```

List domains: 

```bash
curl http://localhost:8000/concepts/domains
```

### MCP Endpoint

The MCP protocol endpoint is available at `/mcp`:
```bash
# Test MCP endpoint (will stream SSE)
curl http://localhost:8000/mcp
```

The best way to interact with the MCP server is via the MCP Inspector as described in the ['testing' section here](./development.md). 

-------------

## Troubleshooting

### Common Issues

#### Port already in use
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
MCP_PORT=8080 ohdsi-webapi-mcp-http
```

#### Server not accessible
```bash
# Check if server is running
curl http://localhost:8000/health

# Check logs
LOG_LEVEL=DEBUG ohdsi-webapi-mcp-http

# Bind to all interfaces
MCP_HOST=0.0.0.0 ohdsi-webapi-mcp-http
```

#### CORS issues (browser)
The server includes CORS headers for development. For production, configure your reverse proxy for CORS.

#### WebAPI connection issues
- Verify `WEBAPI_BASE_URL` is accessible: `curl https://your-webapi/WebAPI/info`
- Check firewall settings
- Verify SSL certificates if using HTTPS

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=DEBUG \
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
ohdsi-webapi-mcp-http
```

