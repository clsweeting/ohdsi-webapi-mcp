# MCP Client Configuration Examples

## Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "ohdsi-webapi-mcp",
      "args": [],
      "env": {
        "WEBAPI_BASE_URL": "https://atlas-demo.ohdsi.org/WebAPI",
        "WEBAPI_SOURCE_KEY": "EUNOMIA"
      }
    }
  }
}
```

## Cline (VS Code)

Add to your VS Code settings:

```json
{
  "cline.mcp.servers": [
    {
      "name": "ohdsi-webapi",
      "command": "ohdsi-webapi-mcp",
      "env": {
        "WEBAPI_BASE_URL": "https://your-atlas-instance.org/WebAPI",
        "WEBAPI_SOURCE_KEY": "YOUR_DATA_SOURCE"
      }
    }
  ]
}
```

## Continue (VS Code)

Add to your Continue config:

```json
{
  "mcp": [
    {
      "name": "ohdsi-webapi",
      "serverName": "ohdsi-webapi-mcp",
      "params": {
        "WEBAPI_BASE_URL": "https://your-atlas.org/WebAPI",
        "WEBAPI_SOURCE_KEY": "YOUR_SOURCE"
      }
    }
  ]
}
```

## Environment Variables

Users need to configure these environment variables:

- `WEBAPI_BASE_URL`: The base URL of your OHDSI WebAPI instance
  - Example: `https://atlas-demo.ohdsi.org/WebAPI`
- `WEBAPI_SOURCE_KEY`: Your CDM data source key
  - Example: `EUNOMIA`, `SYNPUF1K`, etc.

## Installation

### Option 1: Global Installation (Recommended for most users)
```bash
# Install globally from PyPI (once published)
pip install ohdsi-webapi-mcp

# Or install globally from GitHub
pip install git+https://github.com/clsweeting/ohdsi-webapi-mcp.git
```

### Option 2: Virtual Environment (Recommended for developers)
```bash
# Create a virtual environment
python -m venv ohdsi-mcp-env
source ohdsi-mcp-env/bin/activate  # On Windows: ohdsi-mcp-env\Scripts\activate

# Install in the virtual environment
pip install ohdsi-webapi-mcp

# The command will be available as long as the venv is activated
```

### Option 3: Using pipx (Isolated installation)
```bash
# Install pipx if you don't have it
pip install pipx

# Install ohdsi-webapi-mcp in an isolated environment
pipx install ohdsi-webapi-mcp

# The command is available globally but dependencies are isolated
```

### Option 4: Development Installation
```bash
# Clone and install in development mode
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
pip install -e .
```

### Option 5: Docker (No Python required!)
```bash
# Pull the pre-built image (once published)
docker pull ohdsi/webapi-mcp:latest

# Or build from source
docker build -t ohdsi-webapi-mcp .
```

**Docker Configuration for MCP Clients:**
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI",
        "-e", "WEBAPI_SOURCE_KEY=EUNOMIA",
        "ohdsi/webapi-mcp:latest"
      ]
    }
  }
}
```

**Note**: For MCP clients to find the `ohdsi-webapi-mcp` command, it needs to be on your PATH. Global installation (Option 1), pipx (Option 3), or Docker (Option 5) make this easiest.

## Available Tools

Once configured, the following tools become available to the MCP client:

### Concept Discovery
- `search_concepts` - Search for medical concepts
- `get_concept_details` - Get detailed concept information
- `browse_concept_hierarchy` - Browse concept relationships
- `list_domains` - List available domains
- `list_vocabularies` - List available vocabularies

### Concept Sets
- `create_concept_set` - Create concept sets from concept IDs
- `create_concept_set_from_search` - Create concept sets from search terms

### Cohort Building
- `define_primary_criteria` - Define cohort primary criteria
- `add_inclusion_rule` - Add inclusion rules
- `validate_cohort_definition` - Validate cohort definitions
- `estimate_cohort_size` - Estimate cohort size

### Persistence & Management
- `save_cohort_definition` - Save cohorts to WebAPI
- `load_existing_cohort` - Load existing cohorts
- `list_cohorts` - List available cohorts
- `compare_cohorts` - Compare cohort definitions
- `clone_cohort` - Clone existing cohorts
