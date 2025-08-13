"""Tools for cohort building and management."""

import json
import os
from typing import Any

import mcp.types as types
from ohdsi_cohort_schemas import CohortExpression
from ohdsi_webapi import WebApiClient


async def define_primary_criteria(
    concept_set_id: int, domain: str, occurrence_type: str = "First", observation_window_prior: int = 0, observation_window_post: int = 0
) -> list[types.TextContent]:
    """Define primary criteria for cohort index events.

    Parameters
    ----------
    concept_set_id : int
        ID of the concept set to use.
    domain : str
        Domain type (e.g., 'ConditionOccurrence', 'DrugExposure', 'ProcedureOccurrence').
    occurrence_type : str, optional
        Occurrence selection type ('First', 'All'), by default "First".
    observation_window_prior : int, optional
        Prior observation days required, by default 0.
    observation_window_post : int, optional
        Post observation days required, by default 0.

    Returns
    -------
    List[types.TextContent]
        Primary criteria definition formatted for MCP client.
    """
    try:
        # Map domain to criteria type
        domain_mapping = {
            "ConditionOccurrence": "ConditionOccurrence",
            "Condition": "ConditionOccurrence",
            "DrugExposure": "DrugExposure",
            "Drug": "DrugExposure",
            "ProcedureOccurrence": "ProcedureOccurrence",
            "Procedure": "ProcedureOccurrence",
            "Measurement": "Measurement",
            "Observation": "Observation",
            "DeviceExposure": "DeviceExposure",
            "Device": "DeviceExposure",
        }

        criteria_type = domain_mapping.get(domain)
        if not criteria_type:
            return [
                types.TextContent(type="text", text=f"Unsupported domain: {domain}. Supported domains: {', '.join(domain_mapping.keys())}")
            ]

        # Build primary criteria
        criteria_item = {criteria_type: {"CodesetId": concept_set_id, f"{criteria_type}TypeExclude": False}}

        primary_criteria = {
            "CriteriaList": [criteria_item],
            "ObservationWindow": {"PriorDays": observation_window_prior, "PostDays": observation_window_post},
            "PrimaryCriteriaLimit": {"Type": occurrence_type},
        }

        result = f"""Primary Criteria Definition:

Domain: {domain} ({criteria_type})
Concept Set ID: {concept_set_id}
Occurrence Type: {occurrence_type}
Observation Window: {observation_window_prior} days prior, {observation_window_post} days post

Primary Criteria JSON:
{json.dumps(primary_criteria, indent=2)}

This defines the index event for your cohort. Subjects will enter the cohort when they have a {criteria_type.lower()} record matching the concepts in concept set {concept_set_id}.
"""

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error defining primary criteria: {str(e)}")]


async def add_inclusion_rule(
    name: str,
    criteria_type: str,
    concept_set_id: int,
    start_window_start: int | None = None,
    start_window_end: int | None = None,
    end_window_start: int | None = None,
    end_window_end: int | None = None,
    occurrence_count: int = 1,
) -> list[types.TextContent]:
    """Add an inclusion rule to filter cohort subjects.

    Parameters
    ----------
    name : str
        Name of the inclusion rule.
    criteria_type : str
        Type of criteria (e.g., 'ConditionOccurrence', 'DrugExposure').
    concept_set_id : int
        ID of the concept set to use.
    start_window_start : Optional[int], optional
        Start window start days relative to index, by default None.
    start_window_end : Optional[int], optional
        Start window end days relative to index, by default None.
    end_window_start : Optional[int], optional
        End window start days relative to index, by default None.
    end_window_end : Optional[int], optional
        End window end days relative to index, by default None.
    occurrence_count : int, optional
        Required number of occurrences, by default 1.

    Returns
    -------
    List[types.TextContent]
        Inclusion rule definition formatted for MCP client.
    """
    try:
        # Build criteria expression
        criteria_item = {criteria_type: {"CodesetId": concept_set_id, f"{criteria_type}TypeExclude": False}}

        # Add occurrence count if specified
        if occurrence_count > 1:
            criteria_item[criteria_type]["OccurrenceCount"] = occurrence_count

        # Build time windows
        start_window = None
        end_window = None

        if start_window_start is not None or start_window_end is not None:
            start_window = {
                "Start": {
                    "Days": start_window_start if start_window_start is not None else 0,
                    "Coeff": -1 if (start_window_start or 0) < 0 else 1,
                },
                "End": {"Days": start_window_end if start_window_end is not None else 0, "Coeff": -1 if (start_window_end or 0) < 0 else 1},
                "UseIndexEnd": False,
                "UseEventEnd": False,
            }

        if end_window_start is not None or end_window_end is not None:
            end_window = {
                "Start": {
                    "Days": end_window_start if end_window_start is not None else 0,
                    "Coeff": -1 if (end_window_start or 0) < 0 else 1,
                },
                "End": {"Days": end_window_end if end_window_end is not None else 0, "Coeff": -1 if (end_window_end or 0) < 0 else 1},
                "UseIndexEnd": False,
                "UseEventEnd": False,
            }

        inclusion_rule = {
            "name": name,
            "expression": {"Type": "ALL", "CriteriaList": [criteria_item], "DemographicCriteriaList": [], "Groups": []},
        }

        if start_window:
            inclusion_rule["expression"]["StartWindow"] = start_window
        if end_window:
            inclusion_rule["expression"]["EndWindow"] = end_window

        result = f"""Inclusion Rule '{name}':

Criteria: {criteria_type} matching concept set {concept_set_id}
Occurrence count: {occurrence_count}
"""

        if start_window:
            result += f"Start window: {start_window_start} to {start_window_end} days relative to index\n"
        if end_window:
            result += f"End window: {end_window_start} to {end_window_end} days relative to index\n"

        result += f"\nInclusion Rule JSON:\n{json.dumps(inclusion_rule, indent=2)}"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating inclusion rule: {str(e)}")]


async def validate_cohort_definition(cohort_definition: dict[str, Any]) -> list[types.TextContent]:
    """Validate a cohort definition for correctness and best practices.

    Parameters
    ----------
    cohort_definition : Dict[str, Any]
        Cohort definition JSON.

    Returns
    -------
    List[types.TextContent]
        Validation results formatted for MCP client.
    """
    try:
        # Use ohdsi_cohort_schemas for validation
        cohort = CohortExpression(**cohort_definition)

        warnings = []
        errors = []

        # Basic structure validation
        if not cohort.PrimaryCriteria:
            errors.append("Missing PrimaryCriteria - cohort must have index events defined")

        if not cohort.ConceptSets:
            warnings.append("No ConceptSets defined - cohort may not work as expected")

        # Validate concept sets
        if cohort.ConceptSets:
            for cs in cohort.ConceptSets:
                if not cs.expression or not cs.expression.items:
                    errors.append(f"Concept set '{cs.name}' has no concepts defined")

                # Check for overly broad concept sets
                if cs.expression and len(cs.expression.items) > 100:
                    warnings.append(f"Concept set '{cs.name}' has {len(cs.expression.items)} concepts - consider if this is intended")

        # Validate primary criteria
        if cohort.PrimaryCriteria:
            if not cohort.PrimaryCriteria.CriteriaList:
                errors.append("PrimaryCriteria has no CriteriaList defined")

            # Check observation window
            if hasattr(cohort.PrimaryCriteria, "ObservationWindow"):
                obs_window = cohort.PrimaryCriteria.ObservationWindow
                if obs_window.PriorDays > 365:
                    warnings.append(f"Long prior observation window ({obs_window.PriorDays} days) may reduce cohort size")

        # Validate inclusion rules
        if cohort.InclusionRules:
            for i, rule in enumerate(cohort.InclusionRules):
                if not rule.name:
                    warnings.append(f"Inclusion rule {i+1} has no name")

                if not hasattr(rule, "expression") or not rule.expression:
                    errors.append(f"Inclusion rule '{rule.name}' has no expression defined")

        # Build validation report
        result = "Cohort Definition Validation Report:\n\n"

        if not errors and not warnings:
            result += "✅ Validation PASSED - No issues found\n\n"
        else:
            if errors:
                result += f"❌ ERRORS ({len(errors)}):\n"
                for error in errors:
                    result += f"  - {error}\n"
                result += "\n"

            if warnings:
                result += f"⚠️  WARNINGS ({len(warnings)}):\n"
                for warning in warnings:
                    result += f"  - {warning}\n"
                result += "\n"

        # Summary statistics
        result += "Cohort Summary:\n"
        result += f"  - Concept Sets: {len(cohort.ConceptSets) if cohort.ConceptSets else 0}\n"
        result += f"  - Inclusion Rules: {len(cohort.InclusionRules) if cohort.InclusionRules else 0}\n"
        result += f"  - Primary Criteria: {'Defined' if cohort.PrimaryCriteria else 'Missing'}\n"

        if cohort.ConceptSets:
            total_concepts = sum(len(cs.expression.items) if cs.expression else 0 for cs in cohort.ConceptSets)
            result += f"  - Total Concepts: {total_concepts}\n"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [
            types.TextContent(
                type="text", text=f"Validation failed with error: {str(e)}\n\nThis may indicate invalid cohort definition structure."
            )
        ]


async def estimate_cohort_size(cohort_definition: dict[str, Any], source_key: str | None = None) -> list[types.TextContent]:
    """Estimate the size of a cohort without generating it.

    Parameters
    ----------
    cohort_definition : Dict[str, Any]
        Cohort definition JSON.
    source_key : Optional[str], optional
        CDM source key, by default None (uses environment variable).

    Returns
    -------
    List[types.TextContent]
        Size estimate formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    if not source_key:
        source_key = os.getenv("WEBAPI_SOURCE_KEY")
    if not source_key:
        raise ValueError("WEBAPI_SOURCE_KEY environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        # This is a simplified estimation - in practice you might want to
        # call the WebAPI's cohort generation preview endpoints
        result = f"""Cohort Size Estimation:

Data Source: {source_key}
Cohort Definition: {len(str(cohort_definition))} characters

⚠️  Note: This is a basic analysis. For accurate size estimates, consider:

1. Concept Set Coverage:
"""

        if "ConceptSets" in cohort_definition:
            total_concepts = 0
            for cs in cohort_definition["ConceptSets"]:
                if "expression" in cs and "items" in cs["expression"]:
                    concept_count = len(cs["expression"]["items"])
                    total_concepts += concept_count
                    result += f"   - '{cs['name']}': {concept_count} concepts\n"

            result += f"\n   Total concepts: {total_concepts}\n"

        result += f"""
2. Time Windows:
   - Broader time windows = larger cohorts
   - Restrictive windows = smaller cohorts

3. Inclusion Rules:
   - Each rule further filters the cohort
   - {len(cohort_definition.get('InclusionRules', []))} inclusion rules defined

4. Observation Requirements:
   - Prior observation requirements reduce cohort size
   - Post observation requirements affect follow-up

💡 For accurate estimates, use WebAPI's cohort generation preview feature or run a test generation on a sample of your data.
"""

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error estimating cohort size: {str(e)}")]
    finally:
        await client.close()
