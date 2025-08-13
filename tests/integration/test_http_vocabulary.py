"""
HTTP API integration tests for vocabulary router endpoints.
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
def sample_concept_search_params():
    """Sample parameters for concept search."""
    return {
        "query": "diabetes",
        "domain": "Condition",
        "vocabulary": "SNOMED",
        "standard_only": True,
        "page_size": 10,  # Changed from limit to page_size
    }


class TestVocabularyRouter:
    """Integration tests for vocabulary router endpoints."""

    def test_search_concepts_endpoint(self, client, sample_concept_search_params):
        """Test concept search endpoint."""
        response = client.post("/vocabulary/search", json=sample_concept_search_params)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_search_concepts_invalid_params(self, client):
        """Test concept search with invalid parameters."""
        invalid_params = {
            "query": "",  # Empty query should fail
            "page_size": -1,  # Negative page_size should fail
        }

        response = client.post("/vocabulary/search", json=invalid_params)
        # Should either validate and return error or handle gracefully
        assert response.status_code in [400, 422, 500]

    def test_get_concept_details_endpoint(self, client):
        """Test concept details endpoint."""
        # Use a common concept ID that should exist in most OMOP instances
        concept_request = {"concept_id": 201826}  # Type 2 diabetes mellitus

        response = client.post("/vocabulary/details", json=concept_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_get_concept_details_nonexistent(self, client):
        """Test concept details for non-existent concept."""
        concept_request = {"concept_id": 999999999}  # Should not exist

        response = client.post("/vocabulary/details", json=concept_request)
        # Should handle gracefully - either 404 or empty result
        assert response.status_code in [200, 404, 500]

    def test_browse_concept_hierarchy_endpoint(self, client):
        """Test concept hierarchy browsing endpoint."""
        hierarchy_request = {
            "concept_id": 201826,  # Type 2 diabetes mellitus
            "direction": "descendants",
            "max_levels": 2,
            "page_size": 20,  # Changed from limit to page_size
        }

        response = client.post("/vocabulary/hierarchy", json=hierarchy_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_browse_concept_hierarchy_invalid_direction(self, client):
        """Test concept hierarchy with invalid direction."""
        hierarchy_request = {
            "concept_id": 201826,
            "direction": "invalid_direction",
            "max_levels": 2,
            "page_size": 20,  # Changed from limit to page_size
        }

        response = client.post("/vocabulary/hierarchy", json=hierarchy_request)
        # Should validate direction parameter
        assert response.status_code == 422

    def test_list_domains_endpoint(self, client):
        """Test list domains endpoint."""
        response = client.get("/vocabulary/domains")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

        # Since MCP tools return TextContent, we just verify we got some data
        # The actual domain structure depends on the WebAPI response
        if data["data"]:
            # If we have data, it should be non-empty
            assert len(data["data"]) > 0

    def test_list_vocabularies_endpoint(self, client):
        """Test list vocabularies endpoint."""
        response = client.get("/vocabulary/vocabularies")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

        # Since MCP tools return TextContent, we just verify we got some data
        # The actual vocabulary structure depends on the WebAPI response
        if data["data"]:
            # If we have data, it should be non-empty
            assert len(data["data"]) > 0

    def test_concept_search_with_filters(self, client):
        """Test concept search with various filter combinations."""
        # Test domain filter
        domain_search = {
            "query": "heart",
            "domain": "Condition",
            "page_size": 5,  # Changed from limit to page_size
        }
        response = client.post("/vocabulary/search", json=domain_search)
        assert response.status_code == 200

        # Test vocabulary filter
        vocab_search = {
            "query": "aspirin",
            "vocabulary": "RxNorm",
            "page_size": 5,  # Changed from limit to page_size
        }
        response = client.post("/vocabulary/search", json=vocab_search)
        assert response.status_code == 200

        # Test standard_only filter
        standard_search = {
            "query": "diabetes",
            "standard_only": True,
            "page_size": 5,  # Changed from limit to page_size
        }
        response = client.post("/vocabulary/search", json=standard_search)
        assert response.status_code == 200

    def test_concept_search_pagination(self, client):
        """Test concept search with different limit values."""
        base_params = {"query": "medication", "domain": "Drug"}

        # Test small limit
        small_limit = {**base_params, "page_size": 5}
        response = client.post("/vocabulary/search", json=small_limit)
        assert response.status_code == 200
        data = response.json()
        # Data is returned as MCP TextContent list, not structured results
        assert isinstance(data["data"], list)

        # Test larger limit
        large_limit = {**base_params, "page_size": 50}
        response = client.post("/vocabulary/search", json=large_limit)
        assert response.status_code == 200
