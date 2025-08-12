"""MCP Server main entry point.

This module contains the main server implementation and entry point
for the OHDSI WebAPI MCP server.
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .tools.cohorts import add_inclusion_rule, create_concept_set, define_primary_criteria, estimate_cohort_size, validate_cohort_definition
from .tools.concepts import (
    browse_concept_hierarchy,
    create_concept_set_from_search,
    get_concept_details,
    list_domains,
    list_vocabularies,
    search_concepts,
)
from .tools.persistence import clone_cohort, compare_cohorts, list_cohorts, load_existing_cohort, save_cohort_definition

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class McpServerConfig:
    """Configuration for the MCP server."""

    webapi_base_url: str
    webapi_source_key: str | None = None
    log_level: str = "INFO"


def load_config() -> McpServerConfig:
    """Load configuration from environment variables.

    Returns
    -------
    McpServerConfig
        The loaded configuration.

    Raises
    ------
    ValueError
        If required configuration is missing.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    webapi_source_key = os.getenv("WEBAPI_SOURCE_KEY")
    # Note: webapi_source_key is optional - only needed for cohort size estimation
    # Individual tools will validate and prompt for it when needed

    return McpServerConfig(
        webapi_base_url=webapi_base_url,
        webapi_source_key=webapi_source_key,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


# Initialize the MCP server
server = Server("ohdsi-webapi-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools.

    Returns
    -------
    List[types.Tool]
        List of available MCP tools.
    """
    return [
        # Concept Discovery Tools
        types.Tool(
            name="search_concepts",
            description="Search for medical concepts in OMOP vocabularies",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term for concepts"},
                    "domain": {"type": "string", "description": "Domain filter (e.g., 'Condition', 'Drug')"},
                    "vocabulary": {"type": "string", "description": "Vocabulary filter (e.g., 'SNOMED', 'RxNorm')"},
                    "concept_class": {"type": "string", "description": "Concept class filter"},
                    "standard_only": {"type": "boolean", "description": "Return only standard concepts", "default": True},
                    "include_invalid": {"type": "boolean", "description": "Include invalid/deprecated concepts", "default": False},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 20},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_concept_details",
            description="Get detailed information about a specific concept",
            inputSchema={
                "type": "object",
                "properties": {
                    "concept_id": {"type": "integer", "description": "OMOP concept ID"},
                },
                "required": ["concept_id"],
            },
        ),
        types.Tool(
            name="browse_concept_hierarchy",
            description="Browse concept hierarchy (ancestors/descendants)",
            inputSchema={
                "type": "object",
                "properties": {
                    "concept_id": {"type": "integer", "description": "Starting concept ID"},
                    "direction": {
                        "type": "string",
                        "description": "Direction to browse",
                        "enum": ["descendants", "ancestors", "both"],
                        "default": "descendants",
                    },
                    "max_levels": {"type": "integer", "description": "Maximum hierarchy levels", "default": 2},
                    "limit": {"type": "integer", "description": "Maximum concepts per level", "default": 20},
                },
                "required": ["concept_id"],
            },
        ),
        types.Tool(
            name="list_domains",
            description="List all available domains in the OMOP CDM",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="list_vocabularies",
            description="List all available vocabularies in the OMOP CDM",
            inputSchema={"type": "object", "properties": {}},
        ),
        # Concept Set Tools
        types.Tool(
            name="create_concept_set",
            description="Create a concept set from a list of concept IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the concept set"},
                    "concept_ids": {"type": "array", "items": {"type": "integer"}, "description": "List of concept IDs"},
                    "include_descendants": {"type": "boolean", "description": "Include descendant concepts", "default": True},
                    "include_mapped": {"type": "boolean", "description": "Include mapped concepts", "default": False},
                },
                "required": ["name", "concept_ids"],
            },
        ),
        types.Tool(
            name="create_concept_set_from_search",
            description="Create a concept set by searching for concepts",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the concept set"},
                    "search_queries": {"type": "array", "items": {"type": "string"}, "description": "Search terms to find concepts"},
                    "domain": {"type": "string", "description": "Domain filter"},
                    "vocabulary": {"type": "string", "description": "Vocabulary filter"},
                    "include_descendants": {"type": "boolean", "description": "Include descendant concepts", "default": True},
                    "include_mapped": {"type": "boolean", "description": "Include mapped concepts", "default": False},
                    "max_concepts_per_query": {"type": "integer", "description": "Max concepts per search", "default": 10},
                },
                "required": ["name", "search_queries"],
            },
        ),
        # Cohort Building Tools
        types.Tool(
            name="define_primary_criteria",
            description="Define primary criteria for cohort index events",
            inputSchema={
                "type": "object",
                "properties": {
                    "concept_set_id": {"type": "integer", "description": "ID of concept set to use"},
                    "domain": {
                        "type": "string",
                        "description": "Domain type",
                        "enum": [
                            "ConditionOccurrence",
                            "DrugExposure",
                            "ProcedureOccurrence",
                            "Measurement",
                            "Observation",
                            "DeviceExposure",
                        ],
                    },
                    "occurrence_type": {
                        "type": "string",
                        "description": "Occurrence selection",
                        "enum": ["First", "All"],
                        "default": "First",
                    },
                    "observation_window_prior": {"type": "integer", "description": "Prior observation days", "default": 0},
                    "observation_window_post": {"type": "integer", "description": "Post observation days", "default": 0},
                },
                "required": ["concept_set_id", "domain"],
            },
        ),
        types.Tool(
            name="add_inclusion_rule",
            description="Add an inclusion rule to filter cohort subjects",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the inclusion rule"},
                    "criteria_type": {
                        "type": "string",
                        "description": "Type of criteria",
                        "enum": [
                            "ConditionOccurrence",
                            "DrugExposure",
                            "ProcedureOccurrence",
                            "Measurement",
                            "Observation",
                            "DeviceExposure",
                        ],
                    },
                    "concept_set_id": {"type": "integer", "description": "ID of concept set to use"},
                    "start_window_start": {"type": "integer", "description": "Start window start days"},
                    "start_window_end": {"type": "integer", "description": "Start window end days"},
                    "end_window_start": {"type": "integer", "description": "End window start days"},
                    "end_window_end": {"type": "integer", "description": "End window end days"},
                    "occurrence_count": {"type": "integer", "description": "Required occurrences", "default": 1},
                },
                "required": ["name", "criteria_type", "concept_set_id"],
            },
        ),
        types.Tool(
            name="validate_cohort_definition",
            description="Validate a cohort definition for correctness",
            inputSchema={
                "type": "object",
                "properties": {
                    "cohort_definition": {"type": "object", "description": "Cohort definition JSON"},
                },
                "required": ["cohort_definition"],
            },
        ),
        types.Tool(
            name="estimate_cohort_size",
            description="Estimate the size of a cohort without generating it",
            inputSchema={
                "type": "object",
                "properties": {
                    "cohort_definition": {"type": "object", "description": "Cohort definition JSON"},
                    "source_key": {"type": "string", "description": "CDM source key"},
                },
                "required": ["cohort_definition"],
            },
        ),
        # Persistence & Management Tools
        types.Tool(
            name="save_cohort_definition",
            description="Save a cohort definition to the WebAPI",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name for the cohort"},
                    "cohort_definition": {"type": "object", "description": "Cohort definition JSON"},
                    "description": {"type": "string", "description": "Description of the cohort"},
                },
                "required": ["name", "cohort_definition"],
            },
        ),
        types.Tool(
            name="load_existing_cohort",
            description="Load an existing cohort definition from WebAPI",
            inputSchema={
                "type": "object",
                "properties": {
                    "cohort_id": {"type": "integer", "description": "Cohort ID to load"},
                    "cohort_name": {"type": "string", "description": "Cohort name to search for"},
                },
            },
        ),
        types.Tool(
            name="list_cohorts",
            description="List available cohort definitions",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum results", "default": 20},
                    "search_term": {"type": "string", "description": "Filter by name"},
                },
            },
        ),
        types.Tool(
            name="compare_cohorts",
            description="Compare two cohort definitions",
            inputSchema={
                "type": "object",
                "properties": {
                    "cohort_a": {"type": "object", "description": "First cohort definition"},
                    "cohort_b": {"type": "object", "description": "Second cohort definition"},
                    "cohort_a_name": {"type": "string", "description": "Name for first cohort", "default": "Cohort A"},
                    "cohort_b_name": {"type": "string", "description": "Name for second cohort", "default": "Cohort B"},
                },
                "required": ["cohort_a", "cohort_b"],
            },
        ),
        types.Tool(
            name="clone_cohort",
            description="Clone an existing cohort with optional modifications",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_cohort_id": {"type": "integer", "description": "ID of cohort to clone"},
                    "new_name": {"type": "string", "description": "Name for cloned cohort"},
                    "modifications": {"type": "object", "description": "Modifications to apply"},
                    "new_description": {"type": "string", "description": "Description for cloned cohort"},
                },
                "required": ["source_cohort_id", "new_name"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls from MCP clients.

    Parameters
    ----------
    name : str
        Name of the tool to call.
    arguments : Dict[str, Any]
        Arguments for the tool call.

    Returns
    -------
    List[types.TextContent]
        Results from the tool call.

    Raises
    ------
    ValueError
        If the tool name is not recognized.
    """
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        # Concept Discovery Tools
        if name == "search_concepts":
            return await search_concepts(**arguments)
        elif name == "get_concept_details":
            return await get_concept_details(**arguments)
        elif name == "browse_concept_hierarchy":
            return await browse_concept_hierarchy(**arguments)
        elif name == "list_domains":
            return await list_domains(**arguments)
        elif name == "list_vocabularies":
            return await list_vocabularies(**arguments)

        # Concept Set Tools
        elif name == "create_concept_set":
            return await create_concept_set(**arguments)
        elif name == "create_concept_set_from_search":
            return await create_concept_set_from_search(**arguments)

        # Cohort Building Tools
        elif name == "define_primary_criteria":
            return await define_primary_criteria(**arguments)
        elif name == "add_inclusion_rule":
            return await add_inclusion_rule(**arguments)
        elif name == "validate_cohort_definition":
            return await validate_cohort_definition(**arguments)
        elif name == "estimate_cohort_size":
            return await estimate_cohort_size(**arguments)

        # Persistence & Management Tools
        elif name == "save_cohort_definition":
            return await save_cohort_definition(**arguments)
        elif name == "load_existing_cohort":
            return await load_existing_cohort(**arguments)
        elif name == "list_cohorts":
            return await list_cohorts(**arguments)
        elif name == "compare_cohorts":
            return await compare_cohorts(**arguments)
        elif name == "clone_cohort":
            return await clone_cohort(**arguments)

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    try:
        config = load_config()
        logger.setLevel(getattr(logging, config.log_level.upper()))
        logger.info(f"Starting OHDSI WebAPI MCP server with base URL: {config.webapi_base_url}")

        # Run the server using stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ohdsi-webapi-mcp",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise


def cli_main():
    """Synchronous entry point for console script."""
    try:
        asyncio.run(main())
    except Exception as e:
        # Print error to stderr and exit with non-zero code
        import sys

        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
