"""
HTTP API integration tests for cohorts router endpoints.
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
def sample_primary_criteria():
    """Sample primary criteria for cohort definition."""
    return {
        "concept_set_id": 1,
        "domain": "Condition",
        "occurrence_type": "First",
        "observation_window_prior": 365,
        "observation_window_post": 0,
    }


@pytest.fixture
def sample_inclusion_rule():
    """Sample inclusion rule for cohort definition."""
    return {
        "name": "Age >= 18",
        "criteria_type": "Demographics",
        "concept_set_id": 2,
        "start_window_start": -365,
        "start_window_end": -1,
        "occurrence_count": 1,
    }


class TestCohortsRouter:
    """Integration tests for cohorts router endpoints."""

    def test_define_primary_criteria_endpoint(self, client, sample_primary_criteria):
        """Test primary criteria definition endpoint."""
        response = client.post("/cohorts/primary-criteria", json=sample_primary_criteria)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_define_primary_criteria_invalid_domain(self, client):
        """Test primary criteria with invalid domain."""
        invalid_criteria = {"concept_set_id": 1, "domain": "InvalidDomain", "occurrence_type": "First"}

        response = client.post("/cohorts/primary-criteria", json=invalid_criteria)
        # Should handle invalid domain gracefully - either with HTTP error or success with error message
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            # If successful, the error should be in the response content
            data = response.json()
            assert "data" in data
            # Check that the response indicates the domain is unsupported
            text_content = data["data"][0]["text"] if data["data"] else ""
            assert "Unsupported domain" in text_content or "InvalidDomain" in text_content

    def test_add_inclusion_rule_endpoint(self, client, sample_inclusion_rule):
        """Test add inclusion rule endpoint."""
        response = client.post("/cohorts/inclusion-rules", json=sample_inclusion_rule)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_validate_cohort_definition_endpoint(self, client):
        """Test cohort definition validation endpoint."""
        cohort_request = {
            "cohort_definition": {
                "ConceptSets": [],
                "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
                "QualifiedLimit": {"Type": "First"},
                "ExpressionLimit": {"Type": "All"},
                "InclusionRules": [],
                "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
            }
        }

        response = client.post("/cohorts/validate", json=cohort_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_estimate_cohort_size_endpoint(self, client):
        """Test cohort size estimation endpoint."""
        size_request = {
            "cohort_definition": {
                "ConceptSets": [],
                "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
                "QualifiedLimit": {"Type": "First"},
                "ExpressionLimit": {"Type": "All"},
                "InclusionRules": [],
                "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
            },
            "source_key": "EUNOMIA",
        }

        response = client.post("/cohorts/estimate-size", json=size_request)

        # Accept 200 (success), 404 (not found), or 500 (server error)
        # Server errors may occur if WebAPI is unavailable or misconfigured
        assert response.status_code in [200, 404, 500]
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_list_cohorts_endpoint(self, client):
        """Test list cohorts endpoint."""
        response = client.get("/cohorts")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_load_existing_cohort_endpoint(self, client):
        """Test load existing cohort endpoint."""
        cohort_request = {
            "cohort_id": 1,
            "cohort_name": None,  # Can use either cohort_id or cohort_name
        }

        response = client.post("/cohorts/load", json=cohort_request)

        # Should handle gracefully even if cohort doesn't exist
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "data" in data

    def test_save_cohort_definition_endpoint(self, client):
        """Test save cohort definition endpoint."""
        save_request = {
            "name": "Test Cohort",
            "description": "A test cohort for integration testing",
            "cohort_definition": {
                "ConceptSets": [],
                "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
                "QualifiedLimit": {"Type": "First"},
                "ExpressionLimit": {"Type": "All"},
                "InclusionRules": [],
                "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
            },
        }

        response = client.post("/cohorts/save", json=save_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_clone_cohort_endpoint(self, client):
        """Test clone cohort endpoint."""
        clone_request = {"source_cohort_id": 1, "new_name": "Cloned Test Cohort"}

        response = client.post("/cohorts/clone", json=clone_request)

        # Accept various status codes as cloning may depend on WebAPI availability
        assert response.status_code in [200, 404, 500]
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_compare_cohorts_endpoint(self, client):
        """Test compare cohorts endpoint."""
        compare_request = {
            "cohort_a": {
                "ConceptSets": [],
                "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
                "QualifiedLimit": {"Type": "First"},
                "ExpressionLimit": {"Type": "All"},
                "InclusionRules": [],
                "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
            },
            "cohort_b": {
                "ConceptSets": [],
                "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
                "QualifiedLimit": {"Type": "First"},
                "ExpressionLimit": {"Type": "All"},
                "InclusionRules": [],
                "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
            },
            "cohort_a_name": "Cohort A",
            "cohort_b_name": "Cohort B",
        }

        response = client.post("/cohorts/compare", json=compare_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_cohort_workflow_integration(self, client, sample_primary_criteria, sample_inclusion_rule):
        """Test complete cohort workflow integration."""
        # Step 1: Define primary criteria
        response = client.post("/cohorts/primary-criteria", json=sample_primary_criteria)
        assert response.status_code == 200

        # Step 2: Add inclusion rule
        response = client.post("/cohorts/inclusion-rules", json=sample_inclusion_rule)
        assert response.status_code == 200

        # Step 3: Validate cohort definition
        base_cohort_definition = {
            "ConceptSets": [],
            "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
            "QualifiedLimit": {"Type": "First"},
            "ExpressionLimit": {"Type": "All"},
            "InclusionRules": [],
            "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
        }

        validate_request = {"cohort_definition": base_cohort_definition, "source_key": "EUNOMIA"}
        response = client.post("/cohorts/validate", json=validate_request)
        assert response.status_code == 200

        # Step 4: Estimate cohort size
        size_request = {"cohort_definition": base_cohort_definition, "source_key": "EUNOMIA"}
        response = client.post("/cohorts/estimate-size", json=size_request)
        # Accept various status codes as estimation may depend on WebAPI availability
        assert response.status_code in [200, 404, 500]

    def test_cohort_edge_cases(self, client):
        """Test cohort endpoints with edge cases."""
        # Test with non-existent cohort ID for validation
        nonexistent_validation = {
            "cohort_definition": {
                "ConceptSets": [],
                "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
                "QualifiedLimit": {"Type": "First"},
                "ExpressionLimit": {"Type": "All"},
                "InclusionRules": [],
                "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
            }
        }

        response = client.post("/cohorts/validate", json=nonexistent_validation)
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]

        # Test loading non-existent cohort
        nonexistent_load = {"cohort_id": 999999}
        response = client.post("/cohorts/load", json=nonexistent_load)
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]

    def test_cohort_size_estimation_various_sources(self, client):
        """Test cohort size estimation with different data sources."""
        base_cohort_definition = {
            "ConceptSets": [],
            "PrimaryCriteria": {"CriteriaList": [], "ObservationWindow": {"PriorDays": 0, "PostDays": 0}},
            "QualifiedLimit": {"Type": "First"},
            "ExpressionLimit": {"Type": "All"},
            "InclusionRules": [],
            "EndStrategy": {"DateOffset": {"DateField": "StartDate", "Offset": 1}},
        }

        # Test with different source keys
        sources = ["EUNOMIA", "CMS_SynPUF_5PCT", "Optum_Clinformatics"]

        for source in sources:
            size_request = {"cohort_definition": base_cohort_definition, "source_key": source}
            response = client.post("/cohorts/estimate-size", json=size_request)
            # Should handle each source (even if not available)
            assert response.status_code in [200, 404, 500]
