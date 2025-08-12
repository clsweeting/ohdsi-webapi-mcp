#!/usr/bin/env python3
"""Test MCP server using the official MCP client library."""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_with_mcp_client():
    """Test using the official MCP client."""

    # Configure environment
    env = os.environ.copy()
    env["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"

    server_params = StdioServerParameters(command="poetry", args=["run", "ohdsi-webapi-mcp"], env=env)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")

            # Call a tool
            result = await session.call_tool("search_concepts", arguments={"query": "diabetes", "domain": "Condition", "limit": 3})

            print("Tool result:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(test_with_mcp_client())
