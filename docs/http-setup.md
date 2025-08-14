# OHDSI WebAPI MCP Server - HTTP Mode Setup

The **HTTP mode** provides a web-based API with Server-Sent Events (SSE) for MCP communication. This mode is ideal for:

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

## MCP Client Configuration

### Claude Desktop (HTTP mode)
Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Note**: Make sure the HTTP server is running before starting Claude Desktop.

### Modern MCP Clients
For MCP clients that support HTTP transport:

```javascript
// Connect to MCP endpoint
const mcpEndpoint = "http://localhost:8000/mcp";

// Or access as REST API
const apiBase = "http://localhost:8000";
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

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  ohdsi-mcp:
    image: ghcr.io/clsweeting/ohdsi-webapi-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI
      # Uncomment if you need cohort size estimation:
      # - WEBAPI_SOURCE_KEY=EUNOMIA
      - MCP_PORT=8000
      - MCP_HOST=0.0.0.0
    command: ["http"]
    restart: unless-stopped
```

```bash
# Start with docker-compose
docker-compose up -d

# Stop
docker-compose down
```

### Building Local Docker Image
```bash
# Clone and build
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
docker build -t ohdsi-webapi-mcp-local .

# Run HTTP mode
docker run -p 8000:8000 --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ohdsi-webapi-mcp-local http
```

## API Access & Testing

### REST API Endpoints

The HTTP mode exposes both MCP and REST endpoints:

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Concept Search
```bash
curl -X POST "http://localhost:8000/concepts/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes",
    "domain": "Condition",
    "limit": 5
  }'
```

#### Get Concept Details
```bash
curl -X POST "http://localhost:8000/concepts/details" \
  -H "Content-Type: application/json" \
  -d '{
    "concept_id": 201826
  }'
```

#### List Domains
```bash
curl http://localhost:8000/concepts/domains
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` in your browser for:
- Complete API documentation
- Interactive endpoint testing
- Request/response examples
- Schema definitions

### MCP Endpoint

The MCP protocol endpoint is available at `/mcp`:
```bash
# Test MCP endpoint (will stream SSE)
curl http://localhost:8000/mcp
```

## Environment Variables

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

### What is WEBAPI_SOURCE_KEY?

The **source key** identifies which CDM database to use for cohort operations. Different OHDSI instances have different available data sources:

- **atlas-demo.ohdsi.org**: Has `EUNOMIA` (synthetic data)
- **Your institution**: Might have `CCAE`, `OPTUM_DOD`, `MDCR`, etc.

**You can start without it!** Most features work fine without a source key:

✅ **Works without source key:**
- Search for medical concepts
- Get concept details and hierarchy
- Browse vocabularies and domains
- Explore the API documentation

❗ **Requires source key:**
- Create and save cohort definitions
- Generate cohorts on data
- Estimate cohort sizes

To find available sources for your WebAPI, visit: `https://your-webapi-url/WebAPI/source/sources`

## Web Integration Examples

### JavaScript/TypeScript
```javascript
// Search for concepts
async function searchConcepts(query) {
  const response = await fetch('http://localhost:8000/concepts/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      domain: 'Condition',
      limit: 10
    })
  });
  
  const result = await response.json();
  return result.data;
}

// Get concept details
async function getConceptDetails(conceptId) {
  const response = await fetch('http://localhost:8000/concepts/details', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept_id: conceptId })
  });
  
  return response.json();
}
```

### Python
```python
import requests

# Search concepts
def search_concepts(query, domain=None, limit=10):
    response = requests.post(
        'http://localhost:8000/concepts/search',
        json={
            'query': query,
            'domain': domain,
            'limit': limit
        }
    )
    return response.json()

# Health check
def check_health():
    response = requests.get('http://localhost:8000/health')
    return response.json()
```

## Testing

### Quick API Test
```bash
# Start the server (no source key needed for basic testing)
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI ohdsi-webapi-mcp-http

# In another terminal, test endpoints
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/concepts/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes", "limit": 5}'

# Browse interactive docs
open http://localhost:8000/docs
```

### Integration Tests
```bash
# Clone the repo for full test suite
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp

# Install dev dependencies
pip install -e ".[dev]"

# Run integration tests
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
poetry run pytest tests/integration/ -v
```

## Production Deployment

### Reverse Proxy (nginx)
```nginx
# /etc/nginx/sites-available/ohdsi-mcp
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # For SSE support
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### Systemd Service
```ini
# /etc/systemd/system/ohdsi-mcp.service
[Unit]
Description=OHDSI WebAPI MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ohdsi-mcp
Environment=WEBAPI_BASE_URL=https://your-webapi.org/WebAPI
Environment=WEBAPI_SOURCE_KEY=YOUR_CDM_SOURCE
Environment=MCP_PORT=8000
Environment=MCP_HOST=127.0.0.1
ExecStart=/usr/local/bin/ohdsi-webapi-mcp-http
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ohdsi-mcp
sudo systemctl start ohdsi-mcp
sudo systemctl status ohdsi-mcp
```

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

### Docker Debugging
```bash
# Check container logs
docker run -p 8000:8000 \
  -e WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
  -e LOG_LEVEL=DEBUG \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest http

# Or with docker-compose
docker-compose logs -f ohdsi-mcp
```

## Next Steps

Once you have HTTP mode working:

1. **Test the API**: Visit `http://localhost:8000/docs` to explore all endpoints
2. **Try concept searches**: Use the interactive docs or curl to test searches
3. **Integrate with your app**: Use the REST API from your web application
4. **Set up MCP client**: Configure Claude Desktop or other MCP clients to use the HTTP endpoint

For stdio mode setup, see [stdio-setup.md](stdio-setup.md).
