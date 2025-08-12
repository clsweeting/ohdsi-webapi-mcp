# OHDSI WebAPI MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Model Context Protocol (MCP) server that provides LLM agents with tools to interact with OHDSI WebAPI for cohort building and analysis.

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

### Recommended: Using pipx (isolated installation)
```bash
# Install pipx if you don't have it (like npx for Python)
pip install pipx

# Install ohdsi-webapi-mcp in an isolated environment
pipx install ohdsi-webapi-mcp

# The command is available globally but dependencies are isolated
```
**Why pipx?** Like `npx` for Node.js, `pipx` installs CLI tools in isolated environments so they don't conflict with your other Python packages, but the commands are still available globally.

### Alternative: Global installation
```bash
pip install ohdsi-webapi-mcp
```

### Docker (no Python installation required)
```bash
# Quick start - pull and run the pre-built image
docker run -i --rm \
  -e WEBAPI_BASE_URL="https://atlas-demo.ohdsi.org/WebAPI" \
  ghcr.io/clsweeting/ohdsi-webapi-mcp:latest
```

> 📖 **For detailed Docker usage, development workflows, and troubleshooting**, see [docs/docker.md](docs/docker.md)

### Development installation
```bash
git clone https://github.com/clsweeting/ohdsi-webapi-mcp.git
cd ohdsi-webapi-mcp
pip install -e .
```




## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

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

**Optional:** Add a default source key for cohort operations:
```json
{
  "mcpServers": {
    "ohdsi-webapi": {
      "command": "ohdsi-webapi-mcp",
      "env": {
        "WEBAPI_BASE_URL": "https://your-webapi-instance.org/WebAPI",
      }
    }
  }
}
```

### VS Code with MCP Extension

Configure in your VS Code settings:

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


## Developing & Contributing

Please see [docs/development.md](docs/development.md) for more information. 

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Related Projects

- [ohdsi-webapi-client](https://github.com/clsweeting/ohdsi-webapi-client) - Python client for OHDSI WebAPI
- [ohdsi-cohort-schemas](https://github.com/clsweeting/ohdsi-cohort-schemas) - Pydantic models for OHDSI cohort definitions
