"""Test configuration and fixtures."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_webapi_client():
    """Mock WebAPI client for testing."""
    mock_client = Mock()
    mock_client.get_concepts.return_value = []
    mock_client.get_concept.return_value = {}
    return mock_client


@pytest.fixture
def sample_concept():
    """Sample concept for testing."""
    return {
        "CONCEPT_ID": 201826,
        "CONCEPT_NAME": "Type 2 diabetes mellitus",
        "STANDARD_CONCEPT": "S",
        "CONCEPT_CODE": "44054006",
        "CONCEPT_CLASS_ID": "Clinical Finding",
        "VOCABULARY_ID": "SNOMED",
        "DOMAIN_ID": "Condition",
    }


@pytest.fixture
def sample_cohort_definition():
    """Sample cohort definition for testing."""
    return {
        "cdmVersionRange": ">=5.0.0",
        "PrimaryCriteria": {
            "CriteriaList": [{"ConditionOccurrence": {"CodesetId": 0, "ConditionTypeExclude": False}}],
            "ObservationWindow": {"PriorDays": 0, "PostDays": 0},
            "PrimaryCriteriaLimit": {"Type": "First"},
        },
        "ConceptSets": [
            {
                "id": 0,
                "name": "Test Concept Set",
                "expression": {
                    "items": [
                        {
                            "concept": {
                                "CONCEPT_ID": 201826,
                                "CONCEPT_NAME": "Type 2 diabetes mellitus",
                                "STANDARD_CONCEPT": "S",
                                "CONCEPT_CODE": "44054006",
                                "DOMAIN_ID": "Condition",
                                "VOCABULARY_ID": "SNOMED",
                                "CONCEPT_CLASS_ID": "Clinical Finding",
                            },
                            "isExcluded": False,
                            "includeDescendants": True,
                            "includeMapped": False,
                        }
                    ]
                },
            }
        ],
        "QualifiedLimit": {"Type": "First"},
        "ExpressionLimit": {"Type": "First"},
        "InclusionRules": [],
        "CensoringCriteria": [],
        "CollapseSettings": {"CollapseType": "ERA", "EraPad": 0},
    }
