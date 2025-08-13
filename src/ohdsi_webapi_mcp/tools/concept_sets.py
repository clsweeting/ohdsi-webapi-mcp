"""Tools for concept set creation and management."""

import asyncio
import json
import os

import mcp.types as types
from ohdsi_webapi import WebApiClient


async def create_concept_set(
    name: str, concept_ids: list[int], include_descendants: bool = True, include_mapped: bool = False
) -> list[types.TextContent]:
    """Create a concept set for use in cohort definitions.

    Parameters
    ----------
    name : str
        Name for the concept set.
    concept_ids : List[int]
        List of concept IDs to include.
    include_descendants : bool, optional
        Include descendant concepts, by default True.
    include_mapped : bool, optional
        Include mapped concepts, by default False.

    Returns
    -------
    List[types.TextContent]
        Concept set definition formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_create_concept_set():
        client = WebApiClient(webapi_base_url)
        try:
            # Get concept details for all provided IDs
            concepts = []
            for concept_id in concept_ids:
                try:
                    concept = client.vocabulary.get_concept(concept_id)
                    if concept:
                        concepts.append(concept)
                    else:
                        return [types.TextContent(type="text", text=f"Concept not found: {concept_id}")]
                except Exception as e:
                    return [types.TextContent(type="text", text=f"Error retrieving concept {concept_id}: {str(e)}")]

            # Build concept set using ohdsi_cohort_schemas format
            concept_set_items = []
            for concept in concepts:
                concept_item = {
                    "concept": {
                        "CONCEPT_ID": concept.concept_id,
                        "CONCEPT_NAME": concept.concept_name,
                        "STANDARD_CONCEPT": concept.standard_concept,
                        "CONCEPT_CODE": concept.concept_code,
                        "DOMAIN_ID": concept.domain_id,
                        "VOCABULARY_ID": concept.vocabulary_id,
                        "CONCEPT_CLASS_ID": concept.concept_class_id,
                        "INVALID_REASON": concept.invalid_reason,
                    },
                    "isExcluded": False,
                    "includeDescendants": include_descendants,
                    "includeMapped": include_mapped,
                }
                concept_set_items.append(concept_item)

            concept_set = {
                "id": 0,  # Will be assigned when used in cohort
                "name": name,
                "expression": {"items": concept_set_items},
            }

            # Format response
            result = f"""Created concept set '{name}' with {len(concepts)} concepts:

Concepts included:
"""
            for concept in concepts:
                result += f"  - {concept.concept_name} ({concept.concept_id}) [{concept.domain_id}/{concept.vocabulary_id}]\n"

            result += "\nSettings:"
            result += f"\n  - Include descendants: {include_descendants}"
            result += f"\n  - Include mapped: {include_mapped}"

            result += f"\n\nConcept Set JSON:\n{json.dumps(concept_set, indent=2)}"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating concept set: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_create_concept_set)


async def create_concept_set_from_search(
    name: str,
    search_queries: list[str],
    domain: str | None = None,
    vocabulary: str | None = None,
    include_descendants: bool = True,
    include_mapped: bool = False,
    max_concepts_per_query: int = 10,
) -> list[types.TextContent]:
    """Create a concept set by searching for concepts with multiple terms.

    Parameters
    ----------
    name : str
        Name for the concept set.
    search_queries : List[str]
        List of search terms to find concepts.
    domain : Optional[str], optional
        Domain filter, by default None.
    vocabulary : Optional[str], optional
        Vocabulary filter, by default None.
    include_descendants : bool, optional
        Include descendant concepts, by default True.
    include_mapped : bool, optional
        Include mapped concepts, by default False.
    max_concepts_per_query : int, optional
        Maximum concepts to retrieve per search query, by default 10.

    Returns
    -------
    List[types.TextContent]
        Concept set definition formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_create_concept_set():
        client = WebApiClient(webapi_base_url)
        try:
            all_concepts = []
            search_summary = []

            for query in search_queries:
                # Search for concepts (sync call)
                search_kwargs = {
                    "query": query,
                    "page_size": max_concepts_per_query,
                }

                if domain:
                    search_kwargs["domain_id"] = domain
                if vocabulary:
                    search_kwargs["vocabulary_id"] = vocabulary

                # Add standard concept filter
                search_kwargs["standard_concept"] = "S"
                search_kwargs["invalid_reason"] = ""

                concepts = client.vocabulary.search(**search_kwargs)

                if concepts:
                    all_concepts.extend(concepts[:max_concepts_per_query])
                    search_summary.append(f"'{query}': found {len(concepts)} concepts")
                else:
                    search_summary.append(f"'{query}': no concepts found")

            # Remove duplicates
            unique_concepts = {}
            for concept in all_concepts:
                unique_concepts[concept.concept_id] = concept

            # Build concept set definition
            concept_set = {
                "id": 0,  # Will be assigned by WebAPI
                "name": name,
                "expression": {"items": []},
            }

            for concept in unique_concepts.values():
                concept_item = {
                    "concept": {
                        "CONCEPT_ID": concept.concept_id,
                        "CONCEPT_NAME": concept.concept_name,
                        "STANDARD_CONCEPT": concept.standard_concept,
                        "CONCEPT_CODE": concept.concept_code,
                        "DOMAIN_ID": concept.domain_id,
                        "VOCABULARY_ID": concept.vocabulary_id,
                        "CONCEPT_CLASS_ID": concept.concept_class_id,
                        "INVALID_REASON": concept.invalid_reason,
                    },
                    "isExcluded": False,
                    "includeDescendants": include_descendants,
                    "includeMapped": include_mapped,
                }
                concept_set["expression"]["items"].append(concept_item)

            # Format response
            result = f"""Created concept set '{name}' with {len(unique_concepts)} unique concepts:

Search Summary:
{chr(10).join(f"  - {summary}" for summary in search_summary)}

Concept Set Configuration:
  - Include descendants: {'Yes' if include_descendants else 'No'}
  - Include mapped: {'Yes' if include_mapped else 'No'}
  - Domain filter: {domain or 'None'}
  - Vocabulary filter: {vocabulary or 'None'}

Concepts included:"""

            for concept in list(unique_concepts.values())[:10]:  # Show first 10
                result += f"\n  - {concept.concept_name} ({concept.concept_id}) [{concept.vocabulary_id}]"

            if len(unique_concepts) > 10:
                result += f"\n  ... and {len(unique_concepts) - 10} more concepts"

            result += f"\n\nConcept Set JSON:\n{json.dumps(concept_set, indent=2)}"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error creating concept set: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_create_concept_set)


async def list_concept_sets() -> list[types.TextContent]:
    """List all concept sets available in the WebAPI.

    Returns
    -------
    List[types.TextContent]
        List of concept sets formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_list_concept_sets():
        client = WebApiClient(webapi_base_url)
        try:
            concept_sets = client.concept_sets.list()

            if not concept_sets:
                return [types.TextContent(type="text", text="No concept sets found")]

            result = f"Available Concept Sets ({len(concept_sets)} total):\n\n"

            for cs in concept_sets:
                # Format concept set info
                cs_info = f"• {cs.name} (ID: {cs.id})"
                if hasattr(cs, "description") and cs.description:
                    cs_info += f"\n  Description: {cs.description}"
                if hasattr(cs, "created_date"):
                    cs_info += f"\n  Created: {cs.created_date}"
                result += cs_info + "\n\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving concept sets: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_list_concept_sets)


async def get_concept_set_details(concept_set_id: int) -> list[types.TextContent]:
    """Get detailed information about a specific concept set.

    Parameters
    ----------
    concept_set_id : int
        The concept set ID to retrieve details for.

    Returns
    -------
    List[types.TextContent]
        Concept set details formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    def _sync_get_concept_set_details():
        client = WebApiClient(webapi_base_url)
        try:
            # Get concept set details
            concept_set = client.concept_sets.get(concept_set_id)

            if not concept_set:
                return [types.TextContent(type="text", text=f"No concept set found with ID: {concept_set_id}")]

            # Get concept set expression (the actual concepts)
            expression = client.concept_sets.expression(concept_set_id)

            result = f"""Concept Set Details for {concept_set_id}:

Name: {concept_set.name}
ID: {concept_set.id}"""

            if hasattr(concept_set, "description") and concept_set.description:
                result += f"\nDescription: {concept_set.description}"

            if expression and hasattr(expression, "items"):
                result += f"\n\nConcepts ({len(expression.items)} total):"
                for item in expression.items[:10]:  # Show first 10
                    concept = item.get("concept", {})
                    descendants = "with descendants" if item.get("includeDescendants", False) else "no descendants"
                    mapped = "with mapped" if item.get("includeMapped", False) else "no mapped"
                    excluded = " [EXCLUDED]" if item.get("isExcluded", False) else ""

                    result += f"\n  - {concept.get('CONCEPT_NAME', 'Unknown')} ({concept.get('CONCEPT_ID', 'Unknown')})"
                    result += f"\n    Domain: {concept.get('DOMAIN_ID', 'Unknown')} | Vocabulary: {concept.get('VOCABULARY_ID', 'Unknown')}"
                    result += f"\n    Settings: {descendants}, {mapped}{excluded}"

                if len(expression.items) > 10:
                    result += f"\n  ... and {len(expression.items) - 10} more concepts"

            else:
                result += "\n\nNo concept expression found"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving concept set details: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_concept_set_details)
