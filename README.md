# OHDSI WebAPI MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Model Context Protocol (MCP) server that provides LLM agents with tools to interact with OHDSI WebAPI for cohort building and analysis.

## Transport Modes

This server supports **two transport modes** to fit different use cases:

* **stdio Mode** 
* **HTTP using streaming HTTP** 

## Supported Functionality

Concept Discovery
- `search_concepts` - Search for medical concepts by name or code
- `get_concept_details` - Get detailed information about a specific concept
- `browse_concept_hierarchy` - Navigate concept relationships and hierarchies

Cohort Building
- `create_concept_set` - Build reusable concept sets
- `define_primary_criteria` - Set index event criteria
- `add_inclusion_rule` - Add filtering criteria with time windows
- `validate_cohort_definition` - Validate cohort logic and structure

Persistence & Analysis
- `save_cohort_definition` - Save cohort to WebAPI
- `load_existing_cohort` - Retrieve saved cohort definitions
- `estimate_cohort_size` - Preview patient counts
- `compare_cohorts` - Analyze differences between cohort definitions


## Documentation 

Installation & running the MCP server: 
- [stdio Mode Setup](docs/stdio-setup.md) - Complete guide for Claude Desktop, VS Code, and traditional MCP clients in stdio mode 
- [HTTP Mode Setup](docs/http-setup.md) - Complete guide for web integration, API access, running MCP clients in http mode. 
- [Configuration via environment variables](docs/configuration-env-vars.md). 


Using with an MCP client: 
- Using [Claude Code](docs/test-with-claude-code.md) 
- Using [Claude Desktop](docs/test-with-claude-desktop.md)
- Testing with [MCP Inspector](docs/mcp-inspector.md)

Developers:
- **[Development]** - Developing & contributing. 


## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Related Projects

- [ohdsi-webapi-client](https://github.com/clsweeting/ohdsi-webapi-client) - Python client for OHDSI WebAPI
- [ohdsi-cohort-schemas](https://github.com/clsweeting/ohdsi-cohort-schemas) - Pydantic models for OHDSI cohort definitions
