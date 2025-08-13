"""Integration tests for the HTTP API endpoints using FastAPI test client."""

import os

import pytest
from fastapi.testclient import TestClient

from ohdsi_webapi_mcp.http_server import app


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_webapi_env():
    """Set up environment variables for testing."""
    os.environ["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"
    os.environ["WEBAPI_SOURCE_KEY"] = "EUNOMIA"


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ohdsi-webapi-mcp"


class TestConceptSearchEndpoints:
    """Test concept search and discovery endpoints."""

    def test_search_concepts(self, client):
        """Test concept search endpoint."""
        search_data = {"query": "diabetes", "domain": "Condition", "standard_only": True, "limit": 5}

        response = client.post("/vocabulary/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # Check that we got TextContent objects
        first_result = data["data"][0]
        assert "type" in first_result
        assert "text" in first_result
        assert first_result["type"] == "text"
        assert "diabetes" in first_result["text"].lower()

    def test_search_concepts_with_vocabulary_filter(self, client):
        """Test concept search with vocabulary filter."""
        search_data = {"query": "aspirin", "domain": "Drug", "vocabulary": "RxNorm", "limit": 3}

        response = client.post("/vocabulary/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

    def test_search_concepts_no_results(self, client):
        """Test concept search with query that returns no results."""
        search_data = {"query": "zzz_nonexistent_concept_xyz_123", "limit": 5}

        response = client.post("/vocabulary/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        # Should return a message about no results
        assert len(data["data"]) > 0
        assert "no concepts found" in data["data"][0]["text"].lower()

    def test_get_concept_details(self, client):
        """Test get concept details endpoint."""
        # Using Type 2 diabetes concept ID
        concept_data = {"concept_id": 201826}

        response = client.post("/vocabulary/details", json=concept_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

        concept_text = data["data"][0]["text"]
        assert "201826" in concept_text
        assert "diabetes" in concept_text.lower()
        assert "Domain:" in concept_text
        assert "Vocabulary:" in concept_text

    def test_get_concept_details_invalid_id(self, client):
        """Test get concept details with invalid concept ID."""
        concept_data = {"concept_id": 999999999}

        response = client.post("/vocabulary/details", json=concept_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        # Should return an error message (either concept not found or HTTP error)
        result_text = data["data"][0]["text"]
        assert "999999999" in result_text or "not found" in result_text.lower() or "error" in result_text.lower() or "404" in result_text

    def test_list_domains(self, client):
        """Test list domains endpoint."""
        response = client.get("/vocabulary/domains")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

        domains_text = data["data"][0]["text"]
        assert "Available OMOP Domains" in domains_text
        assert "Condition" in domains_text
        assert "Drug" in domains_text
        assert "Total:" in domains_text

    def test_list_vocabularies(self, client):
        """Test list vocabularies endpoint."""
        response = client.get("/vocabulary/vocabularies")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

        vocab_text = data["data"][0]["text"]
        assert "Available OMOP Vocabularies" in vocab_text
        assert "SNOMED" in vocab_text
        assert "RxNorm" in vocab_text
        assert "Total:" in vocab_text


class TestConceptHierarchyEndpoints:
    """Test concept hierarchy browsing endpoints."""

    def test_browse_concept_hierarchy_descendants(self, client):
        """Test browsing concept hierarchy for descendants."""
        hierarchy_data = {
            "concept_id": 201826,  # Type 2 diabetes
            "direction": "descendants",
            "max_levels": 2,
            "limit": 10,
        }

        response = client.post("/vocabulary/hierarchy", json=hierarchy_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

    def test_browse_concept_hierarchy_ancestors(self, client):
        """Test browsing concept hierarchy for ancestors."""
        hierarchy_data = {
            "concept_id": 201826,  # Type 2 diabetes
            "direction": "ancestors",
            "max_levels": 2,
            "limit": 10,
        }

        response = client.post("/vocabulary/hierarchy", json=hierarchy_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0


class TestConceptSetEndpoints:
    """Test concept set creation endpoints."""

    def test_create_concept_set(self, client):
        """Test creating a concept set."""
        concept_set_data = {
            "name": "Test Diabetes Concepts",
            "concept_ids": [201826, 443729],  # Type 2 diabetes, Type 1 diabetes
            "include_descendants": True,
            "include_mapped": False,
        }

        response = client.post("/concept-sets/create", json=concept_set_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

    def test_create_concept_set_from_search(self, client):
        """Test creating a concept set from search terms."""
        concept_set_data = {
            "name": "Diabetes Conditions",
            "search_queries": ["diabetes", "diabetic"],
            "domain": "Condition",
            "include_descendants": True,
            "max_concepts_per_query": 5,
        }

        response = client.post("/concept-sets/create-from-search", json=concept_set_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0


class TestCohortBuildingEndpoints:
    """Test cohort building endpoints."""

    def test_define_primary_criteria(self, client):
        """Test defining primary criteria."""
        criteria_data = {
            "concept_set_id": 1,
            "domain": "ConditionOccurrence",
            "occurrence_type": "First",
            "observation_window_prior": 365,
            "observation_window_post": 0,
        }

        response = client.post("/cohorts/primary-criteria", json=criteria_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

    def test_add_inclusion_rule(self, client):
        """Test adding an inclusion rule."""
        rule_data = {
            "name": "Prior drug exposure",
            "criteria_type": "DrugExposure",
            "concept_set_id": 2,
            "start_window_start": -365,
            "start_window_end": -1,
            "occurrence_count": 1,
        }

        response = client.post("/cohorts/inclusion-rules", json=rule_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

    def test_validate_cohort_definition(self, client):
        """Test cohort definition validation."""
        cohort_def = {
            "name": "Test Cohort",
            "expression": {"primaryCriteria": {"criteriaList": [{"conceptSet": {"id": 1}, "domain": "Condition"}]}},
        }

        validation_data = {"cohort_definition": cohort_def}

        response = client.post("/cohorts/validate", json=validation_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0


class TestPersistenceEndpoints:
    """Test persistence and management endpoints."""

    def test_list_cohorts(self, client):
        """Test listing existing cohorts."""
        list_data = {"limit": 10, "search_term": None}

        response = client.post("/cohorts/list", json=list_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0

    def test_save_cohort_definition(self, client):
        """Test saving a cohort definition."""
        cohort_def = {
            "name": "Test API Cohort",
            "expression": {"primaryCriteria": {"criteriaList": [{"conceptSet": {"id": 1}, "domain": "Condition"}]}},
        }

        save_data = {"name": "Test API Cohort", "cohort_definition": cohort_def, "description": "A test cohort created via API"}

        response = client.post("/cohorts/save", json=save_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) > 0


class TestErrorHandling:
    """Test error handling in HTTP endpoints."""

    def test_search_concepts_missing_query(self, client):
        """Test search endpoint with missing required field."""
        search_data = {
            "domain": "Condition",
            "limit": 5,
            # Missing required "query" field
        }

        response = client.post("/vocabulary/search", json=search_data)
        assert response.status_code == 422  # Validation error

    def test_get_concept_details_missing_id(self, client):
        """Test concept details endpoint with missing concept_id."""
        concept_data = {}  # Missing required "concept_id" field

        response = client.post("/vocabulary/details", json=concept_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_json_payload(self, client):
        """Test endpoint with invalid JSON."""
        response = client.post("/vocabulary/search", data="invalid json", headers={"content-type": "application/json"})
        assert response.status_code == 422  # JSON decode error

    def test_missing_webapi_env_var(self, client, monkeypatch):
        """Test behavior when WEBAPI_BASE_URL is missing."""
        monkeypatch.delenv("WEBAPI_BASE_URL", raising=False)

        search_data = {"query": "test", "limit": 5}
        response = client.post("/vocabulary/search", json=search_data)
        assert response.status_code == 500

        data = response.json()
        assert "WEBAPI_BASE_URL" in data["detail"]


class TestMCPEndpoints:
    """Test MCP-specific endpoints."""

    def test_mcp_endpoint_not_tested(self, client):
        """Note: MCP endpoint (/mcp) is not tested as it's an SSE streaming endpoint.

        The /mcp endpoint provides Server-Sent Events streaming for the MCP protocol
        and maintains an open connection, which would cause tests to hang.
        This endpoint should be tested separately with MCP client tools.
        """
        # Skip testing the streaming MCP endpoint to avoid test hangs
        pass

    def test_openapi_docs_accessible(self, client):
        """Test that OpenAPI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_accessible(self, client):
        """Test that OpenAPI JSON spec is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert spec["info"]["title"] == "OHDSI WebAPI MCP Server"


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    def test_diabetes_research_workflow(self, client):
        """Test a realistic diabetes research workflow."""
        # 1. Search for diabetes concepts
        search_response = client.post(
            "/vocabulary/search", json={"query": "type 2 diabetes", "domain": "Condition", "vocabulary": "SNOMED", "limit": 10}
        )
        assert search_response.status_code == 200

        # 2. Get details for a specific concept
        details_response = client.post("/vocabulary/details", json={"concept_id": 201826})
        assert details_response.status_code == 200

        # 3. Browse concept hierarchy
        hierarchy_response = client.post(
            "/vocabulary/hierarchy", json={"concept_id": 201826, "direction": "descendants", "max_levels": 1, "limit": 5}
        )
        assert hierarchy_response.status_code == 200

        # 4. Create a concept set
        concept_set_response = client.post(
            "/concept-sets/create", json={"name": "Type 2 Diabetes Concepts", "concept_ids": [201826], "include_descendants": True}
        )
        assert concept_set_response.status_code == 200

        # All should succeed
        for response in [search_response, details_response, hierarchy_response, concept_set_response]:
            data = response.json()
            assert data["status"] == "success"

    def test_drug_research_workflow(self, client):
        """Test a realistic drug research workflow."""
        # 1. Search for drug concepts
        search_response = client.post(
            "/vocabulary/search", json={"query": "metformin", "domain": "Drug", "vocabulary": "RxNorm", "limit": 5}
        )
        assert search_response.status_code == 200

        # 2. List available vocabularies to understand drug coding
        vocab_response = client.get("/vocabulary/vocabularies")
        assert vocab_response.status_code == 200

        # 3. Create concept set from search
        concept_set_response = client.post(
            "/concept-sets/create-from-search",
            json={
                "name": "Metformin Medications",
                "search_queries": ["metformin"],
                "domain": "Drug",
                "vocabulary": "RxNorm",
                "max_concepts_per_query": 5,
            },
        )
        assert concept_set_response.status_code == 200

        # All should succeed
        for response in [search_response, vocab_response, concept_set_response]:
            data = response.json()
            assert data["status"] == "success"
