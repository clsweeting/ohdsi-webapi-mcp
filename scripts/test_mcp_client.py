#!/usr/bin/env python3
"""Test the MCP server manually using the MCP client SDK.

This script starts an MCP client and tests the server functionality.
Run with: poetry run python scripts/test_mcp_client.py
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def test_mcp_server():
    """Test the MCP server using stdio transport."""
    print("🧪 Testing MCP Server...")

    # Set environment
    env = os.environ.copy()
    env["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"

    try:
        # Start the MCP server as a subprocess
        server_cmd = [sys.executable, "-m", "ohdsi_webapi_mcp.server"]
        process = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=Path(__file__).parent.parent,
        )

        print("📡 MCP Server started, testing tool calls...")

        # Test 1: List tools
        list_tools_request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        print(f"🔧 Tools available: {response.strip()}")

        # Test 2: Call search_concepts tool
        search_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "search_concepts", "arguments": {"query": "diabetes", "domain": "Condition", "limit": 3}},
        }

        process.stdin.write(json.dumps(search_request) + "\n")
        process.stdin.flush()

        response = process.stdout.readline()
        print(f"🔍 Search result: {response.strip()}")

        # Clean up
        process.terminate()
        process.wait(timeout=5)

        print("✅ MCP Server test completed!")

    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        if "process" in locals():
            process.terminate()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
