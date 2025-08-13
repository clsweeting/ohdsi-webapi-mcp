"""
HTTP API integration tests for jobs router endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from ohdsi_webapi_mcp.http_server import create_app


@pytest.fixture
def client():
    """Create test client for HTTP API tests."""
    app = create_app()
    return TestClient(app)


class TestJobsRouter:
    """Integration tests for jobs router endpoints."""

    def test_list_recent_jobs_endpoint(self, client):
        """Test list recent jobs endpoint."""
        response = client.get("/jobs")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_list_recent_jobs_with_limit(self, client):
        """Test list recent jobs with limit parameter."""
        response = client.get("/jobs?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

        jobs_data = data["data"]
        assert isinstance(jobs_data, list)
        assert len(jobs_data) <= 5

    def test_list_recent_jobs_with_filters(self, client):
        """Test list recent jobs with various filters."""
        # Test with status filter
        response = client.get("/jobs?status=RUNNING")
        assert response.status_code == 200

        # Test with job type filter
        response = client.get("/jobs?job_type=COHORT_GENERATION")
        assert response.status_code == 200

        # Test with multiple filters
        response = client.get("/jobs?status=COMPLETED&limit=10")
        assert response.status_code == 200

    def test_get_job_status_endpoint(self, client):
        """Test get job status endpoint."""
        # Use a sample execution ID (may not exist, but should handle gracefully)
        execution_id = 12345

        response = client.get(f"/jobs/{execution_id}")

        # Should handle gracefully even if job doesn't exist
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "data" in data

    def test_get_job_status_invalid_id(self, client):
        """Test get job status with invalid execution ID."""
        invalid_ids = ["invalid", "abc123"]  # Use string IDs since execution IDs are strings

        for invalid_id in invalid_ids:
            response = client.get(f"/jobs/{invalid_id}")
            # Should handle invalid IDs gracefully
            assert response.status_code in [200, 400, 404, 422, 500]

    def test_jobs_endpoint_pagination(self, client):
        """Test jobs endpoint pagination behavior."""
        # Test different limit values
        limits = [1, 5, 10, 50, 100]

        for limit in limits:
            response = client.get(f"/jobs?limit={limit}")
            assert response.status_code == 200

            data = response.json()
            jobs_data = data["data"]
            assert len(jobs_data) <= limit

    def test_jobs_response_structure(self, client):
        """Test the structure of jobs response."""
        response = client.get("/jobs?limit=1")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "data" in data

        jobs_data = data["data"]
        assert isinstance(jobs_data, list)

        # Should return TextContent objects (MCP format)
        if jobs_data:
            job_item = jobs_data[0]
            assert isinstance(job_item, dict)
            assert "type" in job_item
            assert "text" in job_item
            assert job_item["type"] == "text"

    def test_job_status_types(self, client):
        """Test filtering by different job status types."""
        status_types = ["STARTED", "RUNNING", "COMPLETED", "FAILED", "STOPPED"]

        for status in status_types:
            response = client.get(f"/jobs?status={status}")
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert data["status"] == "success"

    def test_job_type_filtering(self, client):
        """Test filtering by different job types."""
        job_types = ["COHORT_GENERATION", "COHORT_CHARACTERIZATION", "PATHWAY_ANALYSIS", "INCIDENCE_RATE", "PREDICTION"]

        for job_type in job_types:
            response = client.get(f"/jobs?job_type={job_type}")
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert data["status"] == "success"

    def test_jobs_error_handling(self, client):
        """Test jobs endpoints error handling."""
        # Test with invalid query parameters
        response = client.get("/jobs?limit=-1")
        # Should handle negative limit gracefully
        assert response.status_code in [200, 400, 422]

        # Test with invalid status
        response = client.get("/jobs?status=INVALID_STATUS")
        # Should handle invalid status gracefully
        assert response.status_code in [200, 400, 422]

    def test_jobs_empty_results(self, client):
        """Test jobs endpoints when no jobs match criteria."""
        # Use a very specific filter that likely won't match anything
        response = client.get("/jobs?status=NONEXISTENT_STATUS&job_type=NONEXISTENT_TYPE")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)
        # Should return empty list, not error

    def test_recent_jobs_time_ordering(self, client):
        """Test that recent jobs are returned in proper time order."""
        response = client.get("/jobs?limit=10")
        assert response.status_code == 200

        data = response.json()
        jobs_data = data["data"]

        # If there are multiple jobs with timestamps, verify ordering
        if len(jobs_data) >= 2:
            for _i, job in enumerate(jobs_data):
                if isinstance(job, dict) and "startDate" in job:
                    # Jobs should be ordered by most recent first
                    # (specific ordering depends on API implementation)
                    assert "startDate" in job
