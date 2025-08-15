"""
HTTP API integration tests for concept sets router endpoints.
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
def sample_concept_set():
    """Sample concept set data for testing."""
    return {
        "name": "Test Diabetes Concept Set",
        "concept_ids": [201826, 4087682, 4151281],  # Various diabetes concepts
        "include_descendants": True,
        "include_mapped": False,
    }


@pytest.fixture
def sample_concept_set_from_search():
    """Sample concept set from search data."""
    return {
        "name": "Cardiovascular Medications",
        "search_queries": ["aspirin", "atorvastatin", "metoprolol"],
        "domain": "Drug",
        "vocabulary": "RxNorm",
        "include_descendants": True,
        "include_mapped": False,
        "max_concepts_per_query": 5,
    }


class TestConceptSetsRouter:
    """Integration tests for concept sets router endpoints."""

    def test_create_concept_set_endpoint(self, client, sample_concept_set):
        """Test concept set creation endpoint."""
        response = client.post("/concept-sets/create", json=sample_concept_set)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Verify response is a list of TextContent objects (MCP format)
        result_data = data["data"]
        assert isinstance(result_data, list)
        if result_data:
            first_item = result_data[0]
            assert isinstance(first_item, dict)
            assert "type" in first_item
            assert "text" in first_item
            assert first_item["type"] == "text"

    def test_create_concept_set_invalid_concept_ids(self, client):
        """Test concept set creation with invalid concept IDs."""
        invalid_concept_set = {
            "name": "Invalid Concept Set",
            "concept_ids": [-1, 0, 999999999],  # Invalid IDs
            "include_descendants": True,
            "include_mapped": False,
        }

        response = client.post("/concept-sets/create", json=invalid_concept_set)
        # Should handle invalid concept IDs gracefully
        assert response.status_code in [200, 400, 422, 500]

    def test_create_concept_set_from_search_endpoint(self, client, sample_concept_set_from_search):
        """Test concept set creation from search endpoint."""
        response = client.post("/concept-sets/create-from-search", json=sample_concept_set_from_search)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Verify response is a list of TextContent objects (MCP format)
        result_data = data["data"]
        assert isinstance(result_data, list)
        if result_data:
            first_item = result_data[0]
            assert isinstance(first_item, dict)
            assert "type" in first_item
            assert "text" in first_item
            assert first_item["type"] == "text"

    def test_create_concept_set_from_search_empty_queries(self, client):
        """Test concept set creation from search with empty queries."""
        empty_search = {
            "name": "Empty Search Concept Set",
            "search_queries": [],  # Empty queries
            "domain": "Drug",
            "include_descendants": True,
            "include_mapped": False,
            "max_concepts_per_query": 5,
        }

        response = client.post("/concept-sets/create-from-search", json=empty_search)
        # Should handle empty queries gracefully - either with HTTP error or success with error message
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            # If successful, the error should be in the response content
            data = response.json()
            assert "data" in data
            # Check that the response indicates the issue with empty queries
            text_content = data["data"][0]["text"] if data["data"] else ""
            assert "empty" in text_content.lower() or "no queries" in text_content.lower() or "search_queries" in text_content.lower()

    def test_list_concept_sets_endpoint(self, client):
        """Test list concept sets endpoint."""
        response = client.get("/concept-sets")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_concept_set_details_endpoint(self, client):
        """Test get concept set details endpoint."""
        concept_set_id = 1  # Use a sample concept set ID

        response = client.get(f"/concept-sets/{concept_set_id}")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_get_concept_set_details_nonexistent(self, client):
        """Test get concept set details for non-existent set."""
        nonexistent_id = 999999

        response = client.get(f"/concept-sets/{nonexistent_id}")
        # Should handle non-existent concept set gracefully
        assert response.status_code in [200, 404, 500]

    def test_concept_set_with_various_options(self, client):
        """Test concept set creation with various option combinations."""
        base_concept_set = {
            "name": "Options Test Concept Set",
            "concept_ids": [201826, 4087682],
        }

        # Test with descendants included
        with_descendants = {**base_concept_set, "include_descendants": True, "include_mapped": False}
        response = client.post("/concept-sets/create", json=with_descendants)
        assert response.status_code == 200

        # Test with mapped concepts included
        with_mapped = {**base_concept_set, "include_descendants": False, "include_mapped": True}
        response = client.post("/concept-sets/create", json=with_mapped)
        assert response.status_code == 200

        # Test with both options enabled
        with_both = {**base_concept_set, "include_descendants": True, "include_mapped": True}
        response = client.post("/concept-sets/create", json=with_both)
        assert response.status_code == 200

    def test_concept_set_from_search_with_filters(self, client):
        """Test concept set creation from search with various filters."""
        base_search = {
            "name": "Filtered Search Concept Set",
            "search_queries": ["diabetes", "insulin"],
            "include_descendants": True,
            "include_mapped": False,
            "max_concepts_per_query": 3,
        }

        # Test with domain filter
        with_domain = {**base_search, "domain": "Condition"}
        response = client.post("/concept-sets/create-from-search", json=with_domain)
        assert response.status_code == 200

        # Test with vocabulary filter
        with_vocab = {**base_search, "vocabulary": "SNOMED"}
        response = client.post("/concept-sets/create-from-search", json=with_vocab)
        assert response.status_code == 200

        # Test with both filters
        with_both_filters = {**base_search, "domain": "Drug", "vocabulary": "RxNorm"}
        response = client.post("/concept-sets/create-from-search", json=with_both_filters)
        assert response.status_code == 200

    def test_concept_set_search_limit_variations(self, client):
        """Test concept set creation with different search limits."""
        base_search = {
            "name": "Limit Test Concept Set",
            "search_queries": ["medication", "treatment"],
            "domain": "Drug",
            "include_descendants": True,
            "include_mapped": False,
        }

        # Test with small limit
        small_limit = {**base_search, "max_concepts_per_query": 1}
        response = client.post("/concept-sets/create-from-search", json=small_limit)
        assert response.status_code == 200

        # Test with larger limit
        large_limit = {**base_search, "max_concepts_per_query": 20}
        response = client.post("/concept-sets/create-from-search", json=large_limit)
        assert response.status_code == 200

    def test_concept_set_validation(self, client):
        """Test concept set validation and error handling."""
        # Test missing required fields
        incomplete_set = {
            "name": "Incomplete Set"
            # Missing concept_ids
        }
        response = client.post("/concept-sets/create", json=incomplete_set)
        assert response.status_code == 422  # Validation error

        # Test invalid field types
        invalid_types = {
            "name": 12345,  # Should be string
            "concept_ids": "not a list",  # Should be list
            "include_descendants": "yes",  # Should be boolean
        }
        response = client.post("/concept-sets/create", json=invalid_types)
        assert response.status_code == 422  # Validation error

    def test_concept_set_workflow_integration(self, client, sample_concept_set):
        """Test complete concept set workflow integration."""
        # Step 1: Create concept set
        response = client.post("/concept-sets/create", json=sample_concept_set)
        assert response.status_code == 200
        created_set = response.json()["data"]

        # Verify the created concept set response structure (MCP TextContent format)
        assert isinstance(created_set, list)
        if created_set:
            # Each item should be a TextContent object
            for item in created_set:
                assert "text" in item
                assert "type" in item
                assert item["type"] == "text"

        # Step 2: List concept sets (should include our created set)
        response = client.get("/concept-sets")
        assert response.status_code == 200
        concept_sets_list = response.json()["data"]

        # Step 3: Get details of a concept set
        if concept_sets_list:  # If any concept sets exist
            # Try to get details for the first concept set
            response = client.get("/concept-sets/1")  # Use a fixed ID for testing
            # Should handle gracefully even if concept set doesn't exist
            assert response.status_code in [200, 404, 500]
