#!/bin/bash
set -e

# Check the first argument to determine which mode to run
case "$1" in
    "stdio")
        echo "Starting OHDSI WebAPI MCP server in stdio mode..."
        exec python -m ohdsi_webapi_mcp.server
        ;;
    "http")
        echo "Starting OHDSI WebAPI MCP server in HTTP mode..."
        exec python -m ohdsi_webapi_mcp.http_server
        ;;
    "ohdsi-webapi-mcp")
        echo "Starting OHDSI WebAPI MCP server in stdio mode (legacy)..."
        exec python -m ohdsi_webapi_mcp.server
        ;;
    "ohdsi-webapi-mcp-http")
        echo "Starting OHDSI WebAPI MCP server in HTTP mode (legacy)..."
        exec python -m ohdsi_webapi_mcp.http_server
        ;;
    *)
        # If it's not a recognized mode, pass through to the original command
        # This allows running other commands like bash, sh, etc.
        exec "$@"
        ;;
esac
