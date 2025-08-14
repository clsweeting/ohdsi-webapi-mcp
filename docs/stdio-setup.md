# OHDSI WebAPI MCP Server - stdio Mode Setup

The **stdio mode** uses stdin/stdout communication and is the traditional MCP transport. This mode is ideal for:

- Local MCP clients (Claude Desktop, VS Code MCP extension)
- Command-line usage and scripts
- Process-spawning integrations

## Installation

### Recommended: Using pipx
```bash
# Install pipx if you don't have it (like npx for Python)
pip install pipx

# Install ohdsi-webapi-mcp in an isolated environment
pipx install ohdsi-webapi-mcp

# Command available: ohdsi-webapi-mcp
```

When you run pipx install ohdsi-webapi-mcp, pipx does two things:

1. Creates an isolated environment (like a virtual environment) for the package
2. Creates symlinks to the executable commands in a directory that's in your system PATH.   

pipx puts the commands:
- macOS/Linux: `~/.local/bin/` (which pipx adds to your PATH)
- Windows: `%USERPROFILE%\.local\bin\` or similar\
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

## MCP Client Configuration

### Claude Desktop
Add this to your Claude Desktop MCP configuration file:

```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "ohdsi-webapi-mcp",
      "env": {
        "WEBAPI_BASE_URL": "https://atlas-demo.ohdsi.org/WebAPI"
      }
    }
  }
}
```

**Note**: `WEBAPI_SOURCE_KEY` is optional and only needed for cohort size estimation. Most operations (concept searches, vocabulary browsing, etc.) work without it. For the demo instance, you can add `"WEBAPI_SOURCE_KEY": "EUNOMIA"` if you want to test cohort size estimation.

**Configuration file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### VS Code with MCP Extension
Add this to your VS Code settings:

```json
{
  "mcp.servers": [
    {
      "name": "ohdsi-webapi",
      "command": ["ohdsi-webapi-mcp"],
      "env": {
        "WEBAPI_BASE_URL": "https://atlas-demo.ohdsi.org/WebAPI"
      }
    }
  ]
}
```

**Note**: Add `"WEBAPI_SOURCE_KEY": "EUNOMIA"` only if you need cohort size estimation.

### Generic MCP Client
For any MCP client that supports process spawning:

```bash
# Command to spawn
ohdsi-webapi-mcp

# Required environment variable
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI

# Optional - only add if you need cohort size estimation:
# WEBAPI_SOURCE_KEY=EUNOMIA
```

## Docker Setup

### Using Pre-built Image
```bash
# Test the stdio mode
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest stdio
```

**For cohort testing**, add the source key:
```bash
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest stdio
```

**Note**: Add `-e WEBAPI_SOURCE_KEY="EUNOMIA"` only if you need cohort size estimation.

### Claude Desktop with Docker
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI",
        "ghcr.io/clsweeting/ohdsi-webapi-mcp:latest",
        "stdio"
      ]
    }
  }
}
```

**For cohort features**, add the source key:
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI",
        "ghcr.io/clsweeting/ohdsi-webapi-mcp:latest",
        "stdio"
      ]
    }
  }
}
```

**Note**: Add `"-e", "WEBAPI_SOURCE_KEY=EUNOMIA",` to the args array if you need cohort size estimation.

### Building Local Docker Image
```bash
# Clone and build
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
docker build -t ohdsi-webapi-mcp-local .

# Test stdio mode
docker run --rm -i \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ohdsi-webapi-mcp-local stdio
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
- **`LOG_LEVEL`** (optional): Logging level (default: INFO)
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### What is WEBAPI_SOURCE_KEY?

The **source key** identifies which CDM database to use for cohort operations. Different OHDSI instances have different available data sources:

- **atlas-demo.ohdsi.org**: Has `EUNOMIA` (synthetic data)
- **Your institution**: Might have `CCAE`, `OPTUM_DOD`, `MDCR`, etc.

**You can start without it!** Most concept discovery features work fine without a source key. Add it later when you want to build cohorts.

## Testing

### Quick Test
```bash
# Test the command directly
echo '{"method": "tools/list", "params": {}}' | \
  WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
  ohdsi-webapi-mcp
```

### Expected Output
You should see a JSON response listing available tools like:
```json
{
  "result": {
    "tools": [
      {
        "name": "search_concepts",
        "description": "Search for medical concepts in OMOP vocabularies"
      },
      {
        "name": "get_concept_details", 
        "description": "Get detailed information about a specific concept"
      }
      // ... more tools
    ]
  }
}
```

## Troubleshooting

### Common Issues

#### Command not found
```bash
# If ohdsi-webapi-mcp command not found after pip install
pip install --user ohdsi-webapi-mcp
# Or ensure ~/.local/bin is in your PATH

# With pipx, this shouldn't happen
pipx install ohdsi-webapi-mcp
```

#### Permission errors
```bash
# Use pipx for isolated installation
pipx install ohdsi-webapi-mcp

# Or install with --user flag
pip install --user ohdsi-webapi-mcp
```

#### WebAPI connection issues
- Verify `WEBAPI_BASE_URL` is accessible from your machine
- Test the URL in your browser: `https://your-webapi/WebAPI/info`
- Check firewall/network settings

#### Claude Desktop not recognizing the server
1. Restart Claude Desktop after config changes
2. Check the config file syntax (valid JSON)
3. Verify the command path is correct
4. Check Claude Desktop logs for error messages

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=DEBUG \
WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI \
ohdsi-webapi-mcp
```

## Next Steps

Once you have stdio mode working:

1. **Try some concepts searches** in Claude Desktop:
   - "Search for diabetes concepts in OMOP"
   - "Get details for concept ID 201826"

2. **Build a cohort**:
   - "Create a concept set with type 2 diabetes concepts"
   - "Define primary criteria for a diabetes cohort"

3. **Explore the tools**: Ask Claude "What OHDSI tools are available?" to see all capabilities

For HTTP mode setup, see [http-setup.md](http-setup.md).
