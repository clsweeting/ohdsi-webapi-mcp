"""Integration tests using subprocess to test MCP server."""

import asyncio
import json
import os
import subprocess
from pathlib import Path

import pytest


class TestMCPServerIntegration:
    """Integration tests that spawn the actual MCP server process."""

    # @pytest.mark.asyncio
    # async def test_server_startup_and_shutdown(self):
    #     """Test that the MCP server can start and stop cleanly."""
    #     env = os.environ.copy()
    #     env["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"
    #     env["WEBAPI_SOURCE_KEY"] = "EUNOMIA"

    #     # Start server process
    #     process = await asyncio.create_subprocess_exec(
    #         "poetry",
    #         "run",
    #         "ohdsi-webapi-mcp",
    #         stdin=asyncio.subprocess.PIPE,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #         env=env,
    #         cwd=Path(__file__).parent.parent,
    #     )

    #     try:
    #         # Send initialize request
    #         init_request = {
    #             "jsonrpc": "2.0",
    #             "id": 1,
    #             "method": "initialize",
    #             "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
    #         }

    #         # Send request
    #         request_json = json.dumps(init_request) + "\n"
    #         process.stdin.write(request_json.encode())
    #         await process.stdin.drain()

    #         # Read response with timeout
    #         try:
    #             response_line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
    #             response = json.loads(response_line.decode())

    #             # Should get a successful response
    #             assert "result" in response or "error" not in response
    #             assert response.get("id") == 1

    #         except TimeoutError:
    #             pytest.fail("Server did not respond within timeout")

    #     finally:
    #         # Clean shutdown
    #         process.terminate()
    #         try:
    #             await asyncio.wait_for(process.wait(), timeout=5.0)
    #         except TimeoutError:
    #             process.kill()
    #             await process.wait()

    def test_server_command_line_interface(self):
        """Test that the CLI entry point works."""
        env = os.environ.copy()
        env["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"
        env["WEBAPI_SOURCE_KEY"] = "EUNOMIA"

        # Try to start and immediately terminate
        process = subprocess.Popen(
            ["poetry", "run", "ohdsi-webapi-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=Path(__file__).parent.parent,
        )

        try:
            # Give it a moment to start
            stdout, stderr = process.communicate(timeout=2)

            # Should not exit with error immediately
            # (it should wait for input)
            assert process.returncode != 1

        except subprocess.TimeoutExpired:
            # Expected - server should wait for input
            process.terminate()
            process.wait(timeout=5)
            # This is the expected behavior

        except Exception as e:
            process.terminate()
            process.wait(timeout=5)
            pytest.fail(f"Server failed to start: {e}")

    # def test_server_missing_env_vars(self):
    #     """Test server fails gracefully with missing environment variables."""
    #     env = os.environ.copy()
    #     # Remove required env vars
    #     env.pop("WEBAPI_BASE_URL", None)
    #     env.pop("WEBAPI_SOURCE_KEY", None)

    #     process = subprocess.Popen(
    #         ["poetry", "run", "ohdsi-webapi-mcp"],
    #         stdin=subprocess.PIPE,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         env=env,
    #         cwd=Path(__file__).parent.parent,
    #     )

    #     try:
    #         stdout, stderr = process.communicate(timeout=5)

    #         # Should exit with error
    #         assert process.returncode != 0

    #         # Should have helpful error message
    #         error_output = stderr.decode()
    #         assert "WEBAPI_BASE_URL" in error_output or "required" in error_output.lower()

    #     except subprocess.TimeoutExpired:
    #         process.terminate()
    #         process.wait()
    #         pytest.fail("Server should have failed quickly with missing env vars")


class TestMCPServerOutputFormat:
    """Test that MCP server outputs are correctly formatted for LLMs."""

    def test_all_tools_return_text_content(self):
        """Test that all tool implementations return TextContent for LLMs."""
        # Import tool functions
        # This is more of a static analysis test
        # Each tool should return List[types.TextContent]
        # We can test this by checking the return type annotations
        import inspect

        from ohdsi_webapi_mcp.tools.concepts import get_concept_details, search_concepts

        for tool_func in [search_concepts, get_concept_details]:
            sig = inspect.signature(tool_func)
            return_annotation = sig.return_annotation

            # Should return List[types.TextContent] or similar
            assert "TextContent" in str(return_annotation) or "List" in str(return_annotation)


class TestMCPServerPerformance:
    """Basic performance tests for MCP server."""

    @pytest.mark.asyncio
    async def test_server_startup_time(self):
        """Test that server starts within reasonable time."""
        import time

        env = os.environ.copy()
        env["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"
        env["WEBAPI_SOURCE_KEY"] = "EUNOMIA"

        start_time = time.time()

        process = await asyncio.create_subprocess_exec(
            "poetry",
            "run",
            "ohdsi-webapi-mcp",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=Path(__file__).parent.parent,
        )

        try:
            # Send a simple request to test responsiveness
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
            }

            process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()

            try:
                await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
                startup_time = time.time() - start_time

                # Should start within 10 seconds
                assert startup_time < 10.0, f"Server took {startup_time:.2f}s to respond"

            except TimeoutError:
                pytest.fail("Server took too long to respond")

        finally:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
