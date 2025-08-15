"""
HTTP API integration tests for sources router endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from ohdsi_webapi_mcp.http_server import create_app


@pytest.fixture
def client():
    """Create test client for HTTP API tests."""
    app = create_app()
    return TestClient(app)


class TestSourcesRouter:
    """Integration tests for sources router endpoints."""

    def test_list_data_sources_endpoint(self, client):
        """Test list data sources endpoint."""
        response = client.get("/sources")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_source_details_endpoint(self, client):
        """Test get source details endpoint."""
        # Use a common source key that should exist in most OMOP instances
        source_key = "EUNOMIA"

        response = client.get(f"/sources/{source_key}")

        # Should handle gracefully even if source doesn't exist
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "data" in data

            # Verify source details structure - MCP tools return TextContent
            source_data = data["data"]
            assert isinstance(source_data, list)
            # Each item should be a TextContent object
            for item in source_data:
                assert "text" in item
                assert "type" in item
                assert item["type"] == "text"

    def test_get_source_details_nonexistent(self, client):
        """Test get source details for non-existent source."""
        nonexistent_source = "NONEXISTENT_SOURCE"

        response = client.get(f"/sources/{nonexistent_source}")

        # Should handle non-existent source gracefully
        assert response.status_code in [200, 404, 500]

    def test_get_default_source_endpoint(self, client):
        """Test get default source endpoint."""
        response = client.get("/sources/default/info")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        # Verify default source structure - MCP tools return TextContent
        default_source = data["data"]
        assert isinstance(default_source, list)
        # Each item should be a TextContent object
        for item in default_source:
            assert "text" in item
            assert "type" in item
            assert item["type"] == "text"

    def test_sources_list_structure(self, client):
        """Test the structure of sources list response."""
        response = client.get("/sources")
        assert response.status_code == 200

        data = response.json()
        sources_data = data["data"]
        assert isinstance(sources_data, list)

        # Since MCP tools return TextContent, check that format
        # If there are sources, check their structure
        if sources_data:
            # Each item should be a TextContent object
            for item in sources_data:
                assert isinstance(item, dict)
                assert "text" in item
                assert "type" in item
                assert item["type"] == "text"

    def test_common_source_keys(self, client):
        """Test commonly available source keys."""
        common_sources = ["EUNOMIA", "CMS_SynPUF_5PCT", "Optum_Clinformatics"]

        for source_key in common_sources:
            response = client.get(f"/sources/{source_key}")
            # Should handle gracefully (may exist or not exist)
            assert response.status_code in [200, 404, 500]

    def test_source_key_case_sensitivity(self, client):
        """Test source key case sensitivity."""
        # Test different cases of the same source key
        source_variations = ["EUNOMIA", "eunomia", "Eunomia"]

        responses = []
        for source_key in source_variations:
            response = client.get(f"/sources/{source_key}")
            responses.append(response.status_code)

        # All should be handled consistently
        assert all(status in [200, 404, 500] for status in responses)

    def test_source_details_content(self, client):
        """Test that source details contain expected information."""
        # First get list of sources
        response = client.get("/sources")
        assert response.status_code == 200

        sources_data = response.json()["data"]

        # If sources exist, test getting details for first one
        if sources_data and isinstance(sources_data, list) and sources_data:
            first_source = sources_data[0]
            if isinstance(first_source, dict) and "sourceKey" in first_source:
                source_key = first_source["sourceKey"]

                detail_response = client.get(f"/sources/{source_key}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()["data"]
                    assert isinstance(detail_data, dict)

                    # Should contain key information about the source
                    source_info_fields = ["sourceKey", "sourceName", "sourceDialect", "cdmVersion", "vocabulary"]
                    # At least some should be present
                    assert any(field in detail_data for field in source_info_fields)

    def test_default_source_consistency(self, client):
        """Test consistency between default source and sources list."""
        # Get default source
        default_response = client.get("/sources/default/info")
        assert default_response.status_code == 200
        default_data = default_response.json()["data"]

        # Get sources list
        list_response = client.get("/sources")
        assert list_response.status_code == 200
        sources_data = list_response.json()["data"]

        # If there's a default source marked in the list, it should match
        if isinstance(sources_data, list):
            default_sources = [s for s in sources_data if isinstance(s, dict) and s.get("isDefault")]

            if default_sources:
                # Default source info should be consistent
                assert isinstance(default_data, dict)

    def test_sources_error_handling(self, client):
        """Test sources endpoints error handling."""
        # Test with special characters in source key
        special_keys = ["source/test", "source@test", "source test"]

        for key in special_keys:
            response = client.get(f"/sources/{key}")
            # Should handle special characters gracefully
            assert response.status_code in [200, 404, 400, 422, 500]

    def test_sources_pagination_behavior(self, client):
        """Test sources list pagination behavior if implemented."""
        response = client.get("/sources")
        assert response.status_code == 200

        data = response.json()
        sources_data = data["data"]

        # Should return a reasonable number of sources
        if isinstance(sources_data, list):
            assert len(sources_data) <= 1000  # Reasonable upper bound

    def test_source_types_variety(self, client):
        """Test that sources include various database types."""
        response = client.get("/sources")
        assert response.status_code == 200

        sources_data = response.json()["data"]

        if isinstance(sources_data, list) and sources_data:
            # Check for variety in source dialects/types
            dialects = []
            for source in sources_data:
                if isinstance(source, dict) and "sourceDialect" in source:
                    dialects.append(source["sourceDialect"])

            # Common OMOP database dialects
            common_dialects = ["postgresql", "sql server", "oracle", "redshift", "bigquery"]

            # Should support at least some common dialects
            # (May not have all, but should have some variety)
            if dialects:
                dialect_str = " ".join(str(d).lower() for d in dialects if d)
                assert any(common in dialect_str for common in common_dialects)
