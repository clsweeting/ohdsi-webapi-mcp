"""Tests for MCP protocol compliance."""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from ohdsi_webapi_mcp.server import server


class TestMCPProtocol:
    """Test MCP protocol compliance."""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, monkeypatch):
        """Test that server initializes correctly."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        assert isinstance(server, Server)
    
    @pytest.mark.asyncio
    async def test_tools_list(self, monkeypatch):
        """Test that tools/list returns expected tools."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        # Get tools list - note: the server's list_tools handler is decorated
        # We need to call it directly since we can't easily mock the MCP protocol layer
        tools = await server._call_request_handler(
            server._tools_request_handlers.get("tools/list"),
            {}
        )
        
        # Check expected tools are present
        tool_names = [tool.name for tool in tools.tools]
        expected_tools = [
            "search_concepts",
            "get_concept_details", 
            "create_concept_set",
            "validate_cohort_definition",
            "save_cohort_definition"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_tool_call_search_concepts(self, monkeypatch):
        """Test calling search_concepts tool via MCP."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        server = create_server()
        
        # Mock the WebAPI client
        with patch('ohdsi_webapi_mcp.tools.concepts.WebApiClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock concept response
            mock_concept = AsyncMock()
            mock_concept.concept_id = 201826
            mock_concept.concept_name = "Type 2 diabetes mellitus"
            mock_concept.domain_id = "Condition"
            mock_concept.vocabulary_id = "SNOMED"
            mock_concept.concept_code = "44054006"
            mock_concept.standard_concept = "S"
            
            mock_client.vocab.search.return_value = [mock_concept]
            
            # Call tool via MCP
            request = types.CallToolRequest(
                name="search_concepts",
                arguments={"query": "diabetes", "limit": 10}
            )
            
            result = await server.call_tool(request)
            
            # Verify response
            assert isinstance(result, types.CallToolResult)
            assert len(result.content) >= 1
            assert isinstance(result.content[0], types.TextContent)
            assert "diabetes" in result.content[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_call_invalid_tool(self, monkeypatch):
        """Test calling non-existent tool returns error."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        server = create_server()
        
        request = types.CallToolRequest(
            name="nonexistent_tool",
            arguments={}
        )
        
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.call_tool(request)
    
    @pytest.mark.asyncio
    async def test_tool_call_invalid_arguments(self, monkeypatch):
        """Test calling tool with invalid arguments."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        server = create_server()
        
        # Missing required 'query' argument
        request = types.CallToolRequest(
            name="search_concepts",
            arguments={"limit": 10}  # missing 'query'
        )
        
        with pytest.raises((ValueError, TypeError)):
            await server.call_tool(request)


class TestMCPIntegration:
    """Integration tests for full MCP workflow."""
    
    @pytest.mark.asyncio
    async def test_full_mcp_workflow(self, monkeypatch):
        """Test complete MCP workflow: list tools -> call tool."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        server = create_server()
        
        # 1. List tools
        tools_response = await server.list_tools()
        assert len(tools_response.tools) > 0
        
        # 2. Find search_concepts tool
        search_tool = None
        for tool in tools_response.tools:
            if tool.name == "search_concepts":
                search_tool = tool
                break
        
        assert search_tool is not None
        assert search_tool.description is not None
        assert "inputSchema" in search_tool.inputSchema or "properties" in search_tool.inputSchema
        
        # 3. Call the tool (with mock)
        with patch('ohdsi_webapi_mcp.tools.concepts.WebApiClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.vocab.search.return_value = []
            
            request = types.CallToolRequest(
                name="search_concepts",
                arguments={"query": "test", "limit": 5}
            )
            
            result = await server.call_tool(request)
            assert isinstance(result, types.CallToolResult)
            assert len(result.content) >= 1


class TestMCPErrorHandling:
    """Test MCP error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, monkeypatch):
        """Test handling of network errors from WebAPI."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")
        monkeypatch.setenv("WEBAPI_SOURCE_KEY", "TEST")
        
        server = create_server()
        
        # Mock network error
        with patch('ohdsi_webapi_mcp.tools.concepts.WebApiClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.vocab.search.side_effect = Exception("Network error")
            
            request = types.CallToolRequest(
                name="search_concepts",
                arguments={"query": "diabetes"}
            )
            
            # Should handle error gracefully, not crash
            result = await server.call_tool(request)
            assert isinstance(result, types.CallToolResult)
            # Error should be reported in content
            assert "error" in result.content[0].text.lower()
