#!/usr/bin/env python3
"""Manual MCP server testing via JSON-RPC over stdio."""

import asyncio
import json
from typing import Any


async def test_mcp_server():
    """Test MCP server by sending JSON-RPC messages."""

    # Start the MCP server process
    process = await asyncio.create_subprocess_exec(
        "poetry",
        "run",
        "ohdsi-webapi-mcp",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd="/Users/chassweeting/Code/msft/ohdsi/ohdsi-webapi-mcp",
    )

    async def send_request(method: str, params: dict[str, Any] = None) -> dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
        }
        if params:
            request["params"] = params

        request_json = json.dumps(request) + "\n"
        print(f"→ Sending: {request_json.strip()}")

        process.stdin.write(request_json.encode())
        await process.stdin.drain()

        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode())
        print(f"← Received: {json.dumps(response, indent=2)}")
        return response

    try:
        # Initialize the server
        print("\n=== Initializing MCP Server ===")
        await send_request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}})

        # List available tools
        print("\n=== Listing Tools ===")
        await send_request("tools/list")

        # Test a tool call
        print("\n=== Testing search_concepts Tool ===")
        await send_request("tools/call", {"name": "search_concepts", "arguments": {"query": "diabetes", "limit": 3}})

    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        await process.wait()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
