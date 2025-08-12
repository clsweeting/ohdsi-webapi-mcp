"""Tests for concept search tools."""

from unittest.mock import Mock, patch

import pytest

from ohdsi_webapi_mcp.tools.concepts import search_concepts


class TestConceptSearch:
    """Test concept search functionality."""

    @pytest.mark.asyncio
    async def test_search_concepts_with_mock(self, monkeypatch):
        """Test search_concepts with mocked WebAPI client."""
        # Set required environment variable
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        # Create mock concept objects
        mock_concept1 = Mock()
        mock_concept1.concept_id = 201826
        mock_concept1.concept_name = "Type 2 diabetes mellitus"
        mock_concept1.domain_id = "Condition"
        mock_concept1.vocabulary_id = "SNOMED"
        mock_concept1.concept_code = "44054006"
        mock_concept1.standard_concept = "S"

        mock_concept2 = Mock()
        mock_concept2.concept_id = 443767
        mock_concept2.concept_name = "Diabetes mellitus due to genetic defect"
        mock_concept2.domain_id = "Condition"
        mock_concept2.vocabulary_id = "SNOMED"
        mock_concept2.concept_code = "123456789"
        mock_concept2.standard_concept = "S"

        mock_concepts = [mock_concept1, mock_concept2]

        # Mock the WebAPI client
        with patch("ohdsi_webapi_mcp.tools.concepts.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.vocab.search.return_value = mock_concepts

            # Call the function
            results = await search_concepts("diabetes", domain="Condition", limit=10)

            # Verify WebAPI client was called correctly
            mock_client_class.assert_called_once_with("https://test.example.com/WebAPI")
            mock_client.vocab.search.assert_called_once_with(
                query="diabetes", page_size=10, domain_id="Condition", standard_concept="S", invalid_reason=""
            )
            mock_client.close.assert_called_once()

            # Verify results
            assert len(results) == 3  # Header + 2 concepts
            assert "Found 2 concepts for 'diabetes'" in results[0].text
            assert "Type 2 diabetes mellitus" in results[1].text
            assert "201826" in results[1].text
            assert "Diabetes mellitus due to genetic defect" in results[2].text

    @pytest.mark.asyncio
    async def test_search_concepts_no_results(self, monkeypatch):
        """Test search_concepts when no concepts are found."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        with patch("ohdsi_webapi_mcp.tools.concepts.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.vocab.search.return_value = []

            results = await search_concepts("nonexistent", limit=10)

            assert len(results) == 1
            assert "No concepts found for query: 'nonexistent'" in results[0].text

    @pytest.mark.asyncio
    async def test_search_concepts_missing_env(self, monkeypatch):
        """Test search_concepts raises error when WEBAPI_BASE_URL is missing."""
        monkeypatch.delenv("WEBAPI_BASE_URL", raising=False)

        with pytest.raises(ValueError, match="WEBAPI_BASE_URL environment variable is required"):
            await search_concepts("diabetes")

    @pytest.mark.asyncio
    async def test_search_concepts_with_all_params(self, monkeypatch):
        """Test search_concepts with all parameters."""
        monkeypatch.setenv("WEBAPI_BASE_URL", "https://test.example.com/WebAPI")

        mock_concept = Mock()
        mock_concept.concept_id = 1234
        mock_concept.concept_name = "Metformin"
        mock_concept.domain_id = "Drug"
        mock_concept.vocabulary_id = "RxNorm"
        mock_concept.concept_code = "6809"
        mock_concept.standard_concept = "S"

        with patch("ohdsi_webapi_mcp.tools.concepts.WebApiClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.vocab.search.return_value = [mock_concept]

            results = await search_concepts(query="metformin", domain="Drug", vocabulary="RxNorm", limit=5)

            mock_client.vocab.search.assert_called_once_with(
                query="metformin", page_size=5, domain_id="Drug", vocabulary_id="RxNorm", standard_concept="S", invalid_reason=""
            )

            assert len(results) == 2  # Header + 1 concept
            assert "Found 1 concepts for 'metformin'" in results[0].text
            assert "Metformin" in results[1].text
            assert "Drug" in results[1].text
            assert "RxNorm" in results[1].text
