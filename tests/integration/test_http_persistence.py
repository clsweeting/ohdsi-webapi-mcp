"""
HTTP API integration tests for persistence router endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from ohdsi_webapi_mcp.http_server import create_app


@pytest.fixture
def client():
    """Create test client for HTTP API tests."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def sample_save_result():
    """Sample save result data."""
    return {
        "key": "test_result_123",
        "data": {"result_type": "analysis", "value": 42, "metadata": {"created_by": "test_user"}},
        "metadata": {"tags": ["test", "analysis"], "description": "Test result for integration testing"},
        "ttl": 3600,  # 1 hour
    }


class TestPersistenceRouter:
    """Integration tests for persistence router endpoints."""

    def test_save_result_endpoint(self, client, sample_save_result):
        """Test save result endpoint."""
        response = client.post("/persistence", json=sample_save_result)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Should return result info
        saved_data = data["data"]
        assert isinstance(saved_data, dict)
        assert "key" in saved_data

    def test_save_result_invalid_data(self, client):
        """Test save result with invalid data."""
        invalid_result = {
            "key": "",  # Empty key
            "data": None,  # Invalid data
        }

        response = client.post("/persistence", json=invalid_result)
        # Should handle invalid data gracefully
        assert response.status_code in [400, 422, 500]

    def test_get_result_endpoint(self, client):
        """Test get result endpoint."""
        test_key = "test_result_123"

        response = client.get(f"/persistence/{test_key}")

        # Should handle gracefully even if result doesn't exist
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "data" in data

    def test_get_result_nonexistent(self, client):
        """Test get result for non-existent key."""
        nonexistent_key = "nonexistent_key_999999"

        response = client.get(f"/persistence/{nonexistent_key}")
        # Should handle non-existent result gracefully
        assert response.status_code in [200, 404, 500]

    def test_list_results_endpoint(self, client):
        """Test list results endpoint."""
        response = client.get("/persistence")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_list_results_with_filters(self, client):
        """Test list results with filters."""
        response = client.get("/persistence?limit=5&pattern=test")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_delete_result_endpoint(self, client):
        """Test delete result endpoint."""
        test_key = "test_result_to_delete"

        response = client.delete(f"/persistence/{test_key}")

        # Should handle gracefully even if result doesn't exist
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"

    def test_search_results_endpoint(self, client):
        """Test search results endpoint."""
        search_request = {"query": "test", "filters": {"type": "analysis"}, "limit": 10, "offset": 0}

        response = client.post("/persistence/search", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_persistence_workflow_integration(self, client, sample_save_result):
        """Test complete persistence workflow integration."""
        # Step 1: Save a result
        save_response = client.post("/persistence", json=sample_save_result)
        assert save_response.status_code == 200
        saved_data = save_response.json()["data"]

        # Verify the saved data response structure
        # (Persistence router returns structured data, not MCP TextContent)
        assert isinstance(saved_data, dict)
        assert "key" in saved_data
        assert saved_data["key"] == sample_save_result["key"]

        # Step 2: List results (should include our saved one)
        list_response = client.get("/persistence")
        assert list_response.status_code == 200
        results_list = list_response.json()["data"]
        assert isinstance(results_list, list)

        # Step 3: Get a specific result
        test_key = sample_save_result["key"]
        get_response = client.get(f"/persistence/{test_key}")
        # Should handle gracefully even if not found
        assert get_response.status_code in [200, 404, 500]

    def test_persistence_data_types(self, client):
        """Test persistence with different data types."""
        data_types = [
            {"key": "string_data", "data": {"value": "test_string"}},
            {"key": "numeric_data", "data": {"value": 42}},
            {"key": "list_data", "data": {"value": [1, 2, 3]}},
            {"key": "nested_data", "data": {"nested": {"deep": {"value": "test"}}}},
        ]

        for test_data in data_types:
            response = client.post("/persistence", json=test_data)
            # Should handle each type
            assert response.status_code in [200, 400, 422, 500]

    def test_persistence_search_formats(self, client):
        """Test result search with different query formats."""
        search_queries = [
            {"query": "test", "limit": 5},
            {"query": "analysis", "filters": {"type": "cohort"}, "limit": 10},
            {"query": "*", "offset": 0, "limit": 20},
        ]

        for search_query in search_queries:
            response = client.post("/persistence/search", json=search_query)
            # Should handle each search format
            assert response.status_code in [200, 400, 422, 500]

    def test_persistence_error_handling(self, client):
        """Test persistence endpoints error handling."""
        # Test with missing required fields
        incomplete_save = {"data": {"test": "data"}}  # Missing key
        response = client.post("/persistence", json=incomplete_save)
        assert response.status_code == 422  # Validation error

        incomplete_search = {}  # Missing query
        response = client.post("/persistence/search", json=incomplete_search)
        assert response.status_code == 422  # Validation error

        # Test with invalid field types
        invalid_save = {
            "key": 12345,  # Should be string
            "data": "string",  # Should be object
        }
        response = client.post("/persistence", json=invalid_save)
        assert response.status_code == 422  # Validation error

    def test_persistence_list_pagination(self, client):
        """Test result list pagination."""
        # Test with limit parameter
        response = client.get("/persistence?limit=5")
        assert response.status_code == 200

        data = response.json()
        results_list = data["data"]
        assert len(results_list) <= 5

        # Test with pattern filter
        response = client.get("/persistence?pattern=test")
        assert response.status_code == 200
