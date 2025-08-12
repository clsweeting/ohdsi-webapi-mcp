"""Tools for persistence and data management."""

import json
import os
from typing import Any

import mcp.types as types
from ohdsi_webapi import WebApiClient


async def save_cohort_definition(name: str, cohort_definition: dict[str, Any], description: str | None = None) -> list[types.TextContent]:
    """Save a cohort definition to the WebAPI.

    Parameters
    ----------
    name : str
        Name for the cohort.
    cohort_definition : Dict[str, Any]
        Cohort definition JSON.
    description : Optional[str], optional
        Description of the cohort, by default None.

    Returns
    -------
    List[types.TextContent]
        Save confirmation formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        # Prepare cohort definition for saving
        cohort_data = {
            "name": name,
            "description": description or f"Cohort created via MCP: {name}",
            "expressionType": "SIMPLE_EXPRESSION",
            "expression": cohort_definition,
        }

        # Save to WebAPI
        saved_cohort = await client.cohort_definitions.create(cohort_data)

        result = f"""✅ Cohort Definition Saved Successfully!

Cohort ID: {saved_cohort.id}
Name: {saved_cohort.name}
Description: {saved_cohort.description}
Created: {saved_cohort.created_date}

WebAPI URL: {webapi_base_url}/cohortdefinition/{saved_cohort.id}

You can now:
1. Generate this cohort on your CDM data sources
2. View and edit it in the ATLAS interface
3. Use it as input for other analyses

Cohort Definition Summary:
- Concept Sets: {len(cohort_definition.get('ConceptSets', []))}
- Inclusion Rules: {len(cohort_definition.get('InclusionRules', []))}
- Primary Criteria: {'Defined' if cohort_definition.get('PrimaryCriteria') else 'Missing'}
"""

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error saving cohort definition: {str(e)}")]
    finally:
        await client.close()


async def load_existing_cohort(cohort_id: int | None = None, cohort_name: str | None = None) -> list[types.TextContent]:
    """Load an existing cohort definition from WebAPI.

    Parameters
    ----------
    cohort_id : Optional[int], optional
        Cohort ID to load, by default None.
    cohort_name : Optional[str], optional
        Cohort name to search for, by default None.

    Returns
    -------
    List[types.TextContent]
        Cohort definition formatted for MCP client.

    Raises
    ------
    ValueError
        If neither cohort_id nor cohort_name is provided.
    """
    if not cohort_id and not cohort_name:
        raise ValueError("Either cohort_id or cohort_name must be provided")

    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        cohort = None

        if cohort_id:
            # Load by ID
            cohort = await client.cohort_definitions.get(cohort_id)
        else:
            # Search by name
            cohorts = await client.cohort_definitions.list()
            matching_cohorts = [c for c in cohorts if c.name.lower() == cohort_name.lower()]

            if not matching_cohorts:
                # Try partial match
                matching_cohorts = [c for c in cohorts if cohort_name.lower() in c.name.lower()]

            if not matching_cohorts:
                return [types.TextContent(type="text", text=f"No cohort found with name containing: '{cohort_name}'")]
            elif len(matching_cohorts) > 1:
                result = f"Multiple cohorts found matching '{cohort_name}':\n\n"
                for c in matching_cohorts[:10]:  # Limit to 10
                    result += f"  - ID {c.id}: {c.name}\n"
                result += "\nPlease specify a cohort_id or use a more specific name."
                return [types.TextContent(type="text", text=result)]
            else:
                cohort = matching_cohorts[0]

        if not cohort:
            return [types.TextContent(type="text", text=f"Cohort not found: {cohort_id or cohort_name}")]

        # Get full definition
        full_definition = await client.cohort_definitions.get_definition(cohort.id)

        result = f"""Loaded Cohort Definition:

ID: {cohort.id}
Name: {cohort.name}
Description: {cohort.description or 'No description'}
Created: {cohort.created_date}
Modified: {cohort.modified_date}

WebAPI URL: {webapi_base_url}/cohortdefinition/{cohort.id}

Definition Summary:
"""

        if full_definition:
            concept_sets = full_definition.get("ConceptSets", [])
            inclusion_rules = full_definition.get("InclusionRules", [])
            primary_criteria = full_definition.get("PrimaryCriteria")

            result += f"- Concept Sets: {len(concept_sets)}\n"
            if concept_sets:
                for cs in concept_sets[:5]:  # Show first 5
                    concept_count = len(cs.get("expression", {}).get("items", []))
                    result += f"  * {cs.get('name')}: {concept_count} concepts\n"
                if len(concept_sets) > 5:
                    result += f"  ... and {len(concept_sets) - 5} more\n"

            result += f"- Inclusion Rules: {len(inclusion_rules)}\n"
            if inclusion_rules:
                for rule in inclusion_rules[:5]:  # Show first 5
                    result += f"  * {rule.get('name', 'Unnamed rule')}\n"
                if len(inclusion_rules) > 5:
                    result += f"  ... and {len(inclusion_rules) - 5} more\n"

            result += f"- Primary Criteria: {'Defined' if primary_criteria else 'Missing'}\n"

            result += f"\nFull Definition JSON:\n{json.dumps(full_definition, indent=2)}"
        else:
            result += "Definition details not available"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error loading cohort: {str(e)}")]
    finally:
        await client.close()


async def compare_cohorts(
    cohort_a: dict[str, Any], cohort_b: dict[str, Any], cohort_a_name: str = "Cohort A", cohort_b_name: str = "Cohort B"
) -> list[types.TextContent]:
    """Compare two cohort definitions and analyze differences.

    Parameters
    ----------
    cohort_a : Dict[str, Any]
        First cohort definition.
    cohort_b : Dict[str, Any]
        Second cohort definition.
    cohort_a_name : str, optional
        Name for first cohort, by default "Cohort A".
    cohort_b_name : str, optional
        Name for second cohort, by default "Cohort B".

    Returns
    -------
    List[types.TextContent]
        Comparison results formatted for MCP client.
    """
    try:
        result = f"Cohort Comparison: {cohort_a_name} vs {cohort_b_name}\n\n"

        # Compare concept sets
        cs_a = cohort_a.get("ConceptSets", [])
        cs_b = cohort_b.get("ConceptSets", [])

        result += "Concept Sets:\n"
        result += f"  {cohort_a_name}: {len(cs_a)} sets\n"
        result += f"  {cohort_b_name}: {len(cs_b)} sets\n\n"

        # Find concept set differences
        cs_names_a = {cs.get("name", f"Unnamed_{i}") for i, cs in enumerate(cs_a)}
        cs_names_b = {cs.get("name", f"Unnamed_{i}") for i, cs in enumerate(cs_b)}

        only_a = cs_names_a - cs_names_b
        only_b = cs_names_b - cs_names_a
        common = cs_names_a & cs_names_b

        if only_a:
            result += f"Concept sets only in {cohort_a_name}: {', '.join(only_a)}\n"
        if only_b:
            result += f"Concept sets only in {cohort_b_name}: {', '.join(only_b)}\n"
        if common:
            result += f"Common concept sets: {', '.join(common)}\n"

        result += "\n"

        # Compare inclusion rules
        ir_a = cohort_a.get("InclusionRules", [])
        ir_b = cohort_b.get("InclusionRules", [])

        result += "Inclusion Rules:\n"
        result += f"  {cohort_a_name}: {len(ir_a)} rules\n"
        result += f"  {cohort_b_name}: {len(ir_b)} rules\n\n"

        # Find inclusion rule differences
        ir_names_a = {rule.get("name", f"Rule_{i}") for i, rule in enumerate(ir_a)}
        ir_names_b = {rule.get("name", f"Rule_{i}") for i, rule in enumerate(ir_b)}

        only_a_rules = ir_names_a - ir_names_b
        only_b_rules = ir_names_b - ir_names_a
        common_rules = ir_names_a & ir_names_b

        if only_a_rules:
            result += f"Rules only in {cohort_a_name}: {', '.join(only_a_rules)}\n"
        if only_b_rules:
            result += f"Rules only in {cohort_b_name}: {', '.join(only_b_rules)}\n"
        if common_rules:
            result += f"Common rules: {', '.join(common_rules)}\n"

        result += "\n"

        # Compare primary criteria
        pc_a = cohort_a.get("PrimaryCriteria")
        pc_b = cohort_b.get("PrimaryCriteria")

        result += "Primary Criteria:\n"
        result += f"  {cohort_a_name}: {'Defined' if pc_a else 'Not defined'}\n"
        result += f"  {cohort_b_name}: {'Defined' if pc_b else 'Not defined'}\n"

        if pc_a and pc_b:
            # Compare observation windows
            ow_a = pc_a.get("ObservationWindow", {})
            ow_b = pc_b.get("ObservationWindow", {})

            if ow_a != ow_b:
                result += "\nObservation Window Differences:\n"
                result += f"  {cohort_a_name}: {ow_a.get('PriorDays', 0)} prior, {ow_a.get('PostDays', 0)} post days\n"
                result += f"  {cohort_b_name}: {ow_b.get('PriorDays', 0)} prior, {ow_b.get('PostDays', 0)} post days\n"

        # High-level similarity assessment
        result += "\n📊 Similarity Assessment:\n"

        structure_score = 0
        total_checks = 4

        if len(cs_a) == len(cs_b):
            structure_score += 1
        if len(ir_a) == len(ir_b):
            structure_score += 1
        if bool(pc_a) == bool(pc_b):
            structure_score += 1
        if len(common) > 0:
            structure_score += 1

        similarity_pct = (structure_score / total_checks) * 100
        result += f"Structural similarity: {similarity_pct:.0f}%\n"

        if similarity_pct > 80:
            result += "✅ Cohorts are very similar"
        elif similarity_pct > 60:
            result += "⚠️  Cohorts have some differences"
        else:
            result += "❌ Cohorts are quite different"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error comparing cohorts: {str(e)}")]


async def clone_cohort(
    source_cohort_id: int, new_name: str, modifications: dict[str, Any] | None = None, new_description: str | None = None
) -> list[types.TextContent]:
    """Clone an existing cohort with optional modifications.

    Parameters
    ----------
    source_cohort_id : int
        ID of the cohort to clone.
    new_name : str
        Name for the cloned cohort.
    modifications : Optional[Dict[str, Any]], optional
        Modifications to apply to the cloned cohort, by default None.
    new_description : Optional[str], optional
        Description for the cloned cohort, by default None.

    Returns
    -------
    List[types.TextContent]
        Cloned cohort definition formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        # Load source cohort
        source_cohort = await client.cohort_definitions.get(source_cohort_id)
        if not source_cohort:
            return [types.TextContent(type="text", text=f"Source cohort not found: {source_cohort_id}")]

        # Get full definition
        source_definition = await client.cohort_definitions.get_definition(source_cohort_id)
        if not source_definition:
            return [types.TextContent(type="text", text=f"Could not load definition for cohort {source_cohort_id}")]

        # Clone the definition
        cloned_definition = json.loads(json.dumps(source_definition))  # Deep copy

        # Apply modifications if provided
        if modifications:
            for key, value in modifications.items():
                if key in cloned_definition:
                    cloned_definition[key] = value

        # Create new cohort
        cohort_data = {
            "name": new_name,
            "description": new_description or f"Clone of {source_cohort.name}",
            "expressionType": "SIMPLE_EXPRESSION",
            "expression": cloned_definition,
        }

        cloned_cohort = await client.cohort_definitions.create(cohort_data)

        result = f"""✅ Cohort Cloned Successfully!

Source Cohort:
  ID: {source_cohort.id}
  Name: {source_cohort.name}

Cloned Cohort:
  ID: {cloned_cohort.id}
  Name: {cloned_cohort.name}
  Description: {cloned_cohort.description}

WebAPI URL: {webapi_base_url}/cohortdefinition/{cloned_cohort.id}

Modifications Applied:
"""

        if modifications:
            for key, _value in modifications.items():
                result += f"  - {key}: Modified\n"
        else:
            result += "  - No modifications (exact clone)\n"

        result += f"""
Clone Summary:
- Concept Sets: {len(cloned_definition.get('ConceptSets', []))}
- Inclusion Rules: {len(cloned_definition.get('InclusionRules', []))}
- Primary Criteria: {'Defined' if cloned_definition.get('PrimaryCriteria') else 'Missing'}

The cloned cohort is now available for generation and analysis.
"""

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error cloning cohort: {str(e)}")]
    finally:
        await client.close()


async def list_cohorts(limit: int = 20, search_term: str | None = None) -> list[types.TextContent]:
    """List available cohort definitions from WebAPI.

    Parameters
    ----------
    limit : int, optional
        Maximum number of cohorts to return, by default 20.
    search_term : Optional[str], optional
        Filter cohorts by name containing this term, by default None.

    Returns
    -------
    List[types.TextContent]
        List of cohorts formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        # Get all cohorts
        cohorts = await client.cohort_definitions.list()

        # Filter by search term if provided
        if search_term:
            cohorts = [c for c in cohorts if search_term.lower() in c.name.lower()]

        # Limit results
        cohorts = cohorts[:limit]

        if not cohorts:
            message = "No cohorts found"
            if search_term:
                message += f" matching '{search_term}'"
            return [types.TextContent(type="text", text=message)]

        result = "Available Cohort Definitions"
        if search_term:
            result += f" (matching '{search_term}')"
        result += ":\n\n"

        for cohort in cohorts:
            result += f"ID {cohort.id}: {cohort.name}\n"
            if cohort.description:
                # Truncate long descriptions
                desc = cohort.description[:100] + "..." if len(cohort.description) > 100 else cohort.description
                result += f"  Description: {desc}\n"
            result += f"  Created: {cohort.created_date}\n"
            result += f"  URL: {webapi_base_url}/cohortdefinition/{cohort.id}\n\n"

        if len(cohorts) == limit:
            result += f"(Showing first {limit} results)\n"

        result += f"\nTotal: {len(cohorts)} cohorts"
        if search_term:
            result += f" matching '{search_term}'"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error listing cohorts: {str(e)}")]
    finally:
        await client.close()
