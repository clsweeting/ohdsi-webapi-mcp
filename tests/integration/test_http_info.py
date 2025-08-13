"""
HTTP API integration tests for info router endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from ohdsi_webapi_mcp.http_server import create_app


@pytest.fixture
def client():
    """Create test client for HTTP API tests."""
    app = create_app()
    return TestClient(app)


class TestInfoRouter:
    """Integration tests for info router endpoints."""

    def test_get_webapi_info_endpoint(self, client):
        """Test WebAPI info endpoint."""
        response = client.get("/info")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Verify response is a list of TextContent objects (MCP format)
        info_data = data["data"]
        assert isinstance(info_data, list)
        if info_data:
            first_item = info_data[0]
            assert isinstance(first_item, dict)
            assert "type" in first_item
            assert "text" in first_item
            assert first_item["type"] == "text"

    def test_get_webapi_version_endpoint(self, client):
        """Test WebAPI version endpoint."""
        response = client.get("/info/version")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Verify response is a list of TextContent objects (MCP format)
        version_data = data["data"]
        assert isinstance(version_data, list)
        if version_data:
            first_item = version_data[0]
            assert isinstance(first_item, dict)
            assert "type" in first_item
            assert "text" in first_item
            assert first_item["type"] == "text"

    def test_check_webapi_health_endpoint(self, client):
        """Test WebAPI health endpoint."""
        response = client.get("/info/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Verify response is a list of TextContent objects (MCP format)
        health_data = data["data"]
        assert isinstance(health_data, list)
        if health_data:
            first_item = health_data[0]
            assert isinstance(first_item, dict)
            assert "type" in first_item
            assert "text" in first_item
            assert first_item["type"] == "text"

    def test_info_endpoints_error_handling(self, client):
        """Test info endpoints error handling."""
        # Test non-existent info endpoint
        response = client.get("/info/nonexistent")
        assert response.status_code == 404

    def test_webapi_connectivity(self, client):
        """Test that info endpoints can connect to WebAPI."""
        # Health endpoint should indicate connectivity status
        response = client.get("/info/health")
        assert response.status_code == 200

        data = response.json()
        health_data = data["data"]

        # Health check should return TextContent with connectivity information
        assert isinstance(health_data, list)
        if health_data:
            health_text = health_data[0]["text"]
            # Should contain some health information
            assert isinstance(health_text, str)
            assert len(health_text) > 0

    def test_info_response_structure(self, client):
        """Test detailed structure of info responses."""
        # Test main info endpoint
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()

        # Should follow standard response format
        assert "status" in data
        assert "data" in data
        assert data["status"] == "success"

        info_data = data["data"]
        assert isinstance(info_data, list)

        # Test version endpoint structure
        response = client.get("/info/version")
        assert response.status_code == 200
        data = response.json()

        version_data = data["data"]
        assert isinstance(version_data, list)

    def test_info_endpoints_performance(self, client):
        """Test that info endpoints respond quickly."""
        import time

        start_time = time.time()
        response = client.get("/info/health")
        end_time = time.time()

        # Health check should be fast (under 10 seconds)
        assert (end_time - start_time) < 10.0
        assert response.status_code == 200
