"""Tests for the MCP server."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from ohdsi_webapi_mcp.server import load_config


def test_load_config_basic(monkeypatch):
    """Test basic config loading."""
    monkeypatch.setenv("WEBAPI_BASE_URL", "http://localhost:8080/WebAPI")

    config = load_config()
    assert config.webapi_base_url == "http://localhost:8080/WebAPI"
    assert config.log_level == "INFO"


def test_load_config_missing_required_env(monkeypatch):
    """Test loading config with missing required environment variables."""
    monkeypatch.delenv("WEBAPI_BASE_URL", raising=False)

    with pytest.raises(ValueError, match="WEBAPI_BASE_URL environment variable is required"):
        load_config()


def test_load_config_with_all_env(monkeypatch):
    """Test config loading with all environment variables."""
    monkeypatch.setenv("WEBAPI_BASE_URL", "https://atlas.example.com/WebAPI")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = load_config()
    assert config.webapi_base_url == "https://atlas.example.com/WebAPI"
    assert config.log_level == "DEBUG"


class TestMCPTools:
    """Test MCP tool implementations."""

    @pytest.mark.asyncio
    async def test_search_concepts(self, monkeypatch):
        """Test concept search tool."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        from ohdsi_webapi_mcp.tools.vocabulary import search_concepts

        with patch("ohdsi_webapi_mcp.tools.vocabulary.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.vocabulary.search.return_value = []

            result = await search_concepts("diabetes", domain="Condition", limit=10)

            assert isinstance(result, list)
            assert len(result) >= 1
            assert all(hasattr(item, "text") for item in result)

    @pytest.mark.asyncio
    async def test_get_concept_details(self, monkeypatch):
        """Test concept details tool."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        from ohdsi_webapi_mcp.tools.vocabulary import get_concept_details

        with patch("ohdsi_webapi_mcp.tools.vocabulary.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_concept = Mock()
            mock_concept.concept_id = 201826
            mock_concept.concept_name = "Test Concept"
            mock_concept.domain_id = "Condition"
            mock_concept.vocabulary_id = "SNOMED"
            mock_concept.concept_class_id = "Clinical Finding"
            mock_concept.concept_code = "44054006"
            mock_concept.standard_concept = "S"
            mock_concept.invalid_reason = None
            mock_client.vocabulary.get_concept.return_value = mock_concept
            mock_client.vocabulary.get_concept_relationships.return_value = []
            mock_client.close = AsyncMock()  # Mock async close method

            result = await get_concept_details(201826)

            assert isinstance(result, list)
            assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_create_concept_set(self, monkeypatch):
        """Test concept set creation tool."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        from ohdsi_webapi_mcp.tools.concept_sets import create_concept_set

        with patch("ohdsi_webapi_mcp.tools.concept_sets.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock concept objects
            mock_concept1 = Mock()
            mock_concept1.concept_id = 201826
            mock_concept1.concept_name = "Type 2 Diabetes"
            mock_concept1.domain_id = "Condition"
            mock_concept1.vocabulary_id = "SNOMED"
            mock_concept1.concept_class_id = "Clinical Finding"
            mock_concept1.concept_code = "44054006"
            mock_concept1.standard_concept = "S"
            mock_concept1.invalid_reason = None

            mock_concept2 = Mock()
            mock_concept2.concept_id = 12345
            mock_concept2.concept_name = "Test Concept"
            mock_concept2.domain_id = "Condition"
            mock_concept2.vocabulary_id = "SNOMED"
            mock_concept2.concept_class_id = "Clinical Finding"
            mock_concept2.concept_code = "12345"
            mock_concept2.standard_concept = "S"
            mock_concept2.invalid_reason = None

            # Set up async mock for get_concept to return different concepts based on ID
            async def mock_get_concept(concept_id):
                if concept_id == 201826:
                    return mock_concept1
                elif concept_id == 12345:
                    return mock_concept2
                return None

            mock_client.vocabulary.get_concept.side_effect = mock_get_concept
            mock_client.close = AsyncMock()  # Mock async close method

            result = await create_concept_set("Test Set", [201826, 12345])

            assert isinstance(result, list)
            assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_validate_cohort_definition(self, sample_cohort_definition, monkeypatch):
        """Test cohort definition validation."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        from ohdsi_webapi_mcp.tools.cohorts import validate_cohort_definition

        result = await validate_cohort_definition(sample_cohort_definition)

        assert isinstance(result, list)
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_save_cohort_definition(self, sample_cohort_definition, monkeypatch):
        """Test cohort definition saving."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        from ohdsi_webapi_mcp.tools.persistence import save_cohort_definition

        with patch("ohdsi_webapi_mcp.tools.persistence.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock saved cohort response
            mock_saved_cohort = Mock()
            mock_saved_cohort.id = 123
            mock_saved_cohort.name = "Test Cohort"
            mock_saved_cohort.description = "Test description"
            mock_saved_cohort.created_date = "2024-01-01"

            mock_client.cohort_definitions.create.return_value = mock_saved_cohort
            mock_client.close = AsyncMock()  # Mock async close method

            result = await save_cohort_definition("Test Cohort", sample_cohort_definition)

            assert isinstance(result, list)
            assert len(result) >= 1
