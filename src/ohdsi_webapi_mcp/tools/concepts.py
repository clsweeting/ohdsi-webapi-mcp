"""Tools for concept discovery and search."""

import asyncio
import json
import os

import mcp.types as types
from ohdsi_webapi import WebApiClient


async def search_concepts(
    query: str,
    domain: str | None = None,
    vocabulary: str | None = None,
    concept_class: str | None = None,
    standard_only: bool = True,
    include_invalid: bool = False,
    limit: int = 20,
) -> list[types.TextContent]:
    """Search for medical concepts in OMOP vocabularies.

    Parameters
    ----------
    query : str
        Search term for concepts.
    domain : Optional[str], optional
        Domain filter to restrict search to specific data types.
        Common domains: 'Condition', 'Drug', 'Procedure', 'Measurement', 'Observation', 'Device'.
        Use list_domains() for complete list available in your instance, by default None.
    vocabulary : Optional[str], optional
        Vocabulary filter to restrict search to specific coding systems.
        Common vocabularies: 'SNOMED' (conditions), 'RxNorm' (drugs), 'ICD10CM' (diagnoses),
        'CPT4' (procedures), 'LOINC' (lab tests). Use list_vocabularies() for complete list, by default None.
    concept_class : Optional[str], optional
        Concept class filter for more granular filtering within vocabularies
        (e.g., 'Clinical Finding', 'Ingredient'), by default None.
    standard_only : bool, optional
        If True, return only standard concepts (recommended for analysis), by default True.
    include_invalid : bool, optional
        If True, include invalid/deprecated concepts, by default False.
    limit : int, optional
        Maximum number of results, by default 20.

    Returns
    -------
    List[types.TextContent]
        Search results formatted for MCP client.

    Examples
    --------
    Basic search:
        search_concepts("diabetes")

    Search for conditions only:
        search_concepts("diabetes", domain="Condition")

    Search for SNOMED conditions:
        search_concepts("diabetes", domain="Condition", vocabulary="SNOMED")

    Search for drug ingredients:
        search_concepts("metformin", domain="Drug", concept_class="Ingredient")
    """

    def _sync_search():
        """Synchronous function to run in thread pool."""
        base_url = os.getenv("WEBAPI_BASE_URL")
        if not base_url:
            raise ValueError("WEBAPI_BASE_URL environment variable is required")

        client = WebApiClient(base_url)
        try:
            # Build search parameters
            search_kwargs = {
                "query": query,
                "page_size": min(limit, 100),  # WebAPI typically caps at 100
            }

            # Add optional filters
            if domain:
                search_kwargs["domain_id"] = domain
            if vocabulary:
                search_kwargs["vocabulary_id"] = vocabulary
            if concept_class:
                search_kwargs["concept_class_id"] = concept_class
            if standard_only:
                search_kwargs["standard_concept"] = "S"
            if not include_invalid:
                # Only include valid concepts (exclude deprecated/updated)
                search_kwargs["invalid_reason"] = ""

            # Use the vocabulary search endpoint
            concepts = client.vocab.search(**search_kwargs)
            return concepts
        finally:
            client.close()

    # Run the sync function in a thread pool
    concepts = await asyncio.to_thread(_sync_search)

    # Format results for MCP client
    if not concepts:
        return [types.TextContent(type="text", text=f"No concepts found for query: '{query}'")]

    # Create formatted results
    results = []

    # Add search summary with applied filters
    filter_info = []
    if domain:
        filter_info.append(f"Domain: {domain}")
    if vocabulary:
        filter_info.append(f"Vocabulary: {vocabulary}")
    if concept_class:
        filter_info.append(f"Class: {concept_class}")
    if standard_only:
        filter_info.append("Standard concepts only")
    if not include_invalid:
        filter_info.append("Valid concepts only")

    filter_text = f" ({', '.join(filter_info)})" if filter_info else ""
    results.append(types.TextContent(type="text", text=f"Found {len(concepts)} concepts for '{query}'{filter_text}:"))

    for concept in concepts[:limit]:
        # Enhanced concept info with more details
        standard_flag = "Standard" if concept.standard_concept == "S" else "Non-standard"
        invalid_info = ""
        if concept.invalid_reason:
            invalid_info = f" [INVALID: {concept.invalid_reason}]"

        concept_info = (
            f"• {concept.concept_name} (ID: {concept.concept_id})\n"
            f"  Domain: {concept.domain_id} | Vocabulary: {concept.vocabulary_id}\n"
            f"  Class: {concept.concept_class_id} | Code: {concept.concept_code}\n"
            f"  {standard_flag}{invalid_info}"
        )
        results.append(types.TextContent(type="text", text=concept_info))

    return results


async def get_concept_details(concept_id: int) -> list[types.TextContent]:
    """Get detailed information about a specific concept.

    Parameters
    ----------
    concept_id : int
        The concept ID to retrieve details for.

    Returns
    -------
    List[types.TextContent]
        Concept details formatted for MCP client.

    Examples
    --------
    >>> details = await get_concept_details(201826)
    >>> print(details[0].text)
    Concept Details for 201826:
    Name: Type 2 diabetes mellitus
    Domain: Condition
    Vocabulary: SNOMED
    ...
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        # Get concept details
        concept = await client.vocab.get_concept(concept_id)

        if not concept:
            return [types.TextContent(type="text", text=f"No concept found with ID: {concept_id}")]

        # Format concept details
        details = f"""Concept Details for {concept_id}:

Name: {concept.concept_name}
Domain: {concept.domain_id}
Vocabulary: {concept.vocabulary_id}
Concept Class: {concept.concept_class_id}
Concept Code: {concept.concept_code}
Standard Concept: {'Yes' if concept.standard_concept == 'S' else 'No'}
Valid: {'Yes' if not concept.invalid_reason else f'No ({concept.invalid_reason})'}

Relationships:"""

        # Get relationships if available
        try:
            relationships = await client.vocab.get_concept_relationships(concept_id)
            if relationships:
                for rel in relationships[:10]:  # Limit to first 10
                    details += f"\n  - {rel.relationship_name}: {rel.related_concept_name} ({rel.related_concept_id})"
            else:
                details += "\n  No relationships found"
        except Exception:
            details += "\n  Relationships not available"

        return [types.TextContent(type="text", text=details)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving concept details: {str(e)}")]
    finally:
        await client.close()


async def create_concept_set_from_search(
    name: str,
    search_queries: list[str],
    domain: str | None = None,
    vocabulary: str | None = None,
    include_descendants: bool = True,
    include_mapped: bool = False,
    max_concepts_per_query: int = 10,
) -> list[types.TextContent]:
    """Create a concept set by searching for concepts and assembling them.

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
        Maximum concepts to include per search query, by default 10.

    Returns
    -------
    List[types.TextContent]
        Concept set definition formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        all_concepts = []
        search_summary = []

        for query in search_queries:
            # Search for concepts
            concepts = await client.vocab.search(
                query=query,
                domain_id=domain,
                vocabulary_id=vocabulary,
                page_size=max_concepts_per_query,
                standard_concept="S" if True else None,
                invalid_reason="" if not False else None,
            )

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
        result = f"""Created concept set '{name}':

Search Summary:
{chr(10).join(['  - ' + summary for summary in search_summary])}

Concept Set Contents ({len(unique_concepts)} unique concepts):
"""

        for concept in list(unique_concepts.values())[:10]:  # Show first 10
            result += f"\n  - {concept.concept_name} ({concept.concept_id}) [{concept.domain_id}]"

        if len(unique_concepts) > 10:
            result += f"\n  ... and {len(unique_concepts) - 10} more concepts"

        result += "\n\nSettings:"
        result += f"\n  - Include descendants: {include_descendants}"
        result += f"\n  - Include mapped: {include_mapped}"

        result += f"\n\nConcept Set JSON:\n{json.dumps(concept_set, indent=2)}"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error creating concept set: {str(e)}")]
    finally:
        await client.close()


async def browse_concept_hierarchy(
    concept_id: int, direction: str = "descendants", max_levels: int = 2, limit: int = 20
) -> list[types.TextContent]:
    """Browse concept hierarchy (ancestors/descendants) for a given concept.

    Parameters
    ----------
    concept_id : int
        Starting concept ID.
    direction : str, optional
        Direction to browse: 'descendants', 'ancestors', or 'both', by default "descendants".
    max_levels : int, optional
        Maximum hierarchy levels to traverse, by default 2.
    limit : int, optional
        Maximum concepts to return per level, by default 20.

    Returns
    -------
    List[types.TextContent]
        Concept hierarchy formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        # Get the root concept
        root_concept = await client.vocab.get_concept(concept_id)
        if not root_concept:
            return [types.TextContent(type="text", text=f"No concept found with ID: {concept_id}")]

        result = f"Concept Hierarchy for {root_concept.concept_name} ({concept_id}):\n\n"

        if direction in ["ancestors", "both"]:
            result += "ANCESTORS:\n"
            try:
                ancestors = await client.vocab.get_concept_ancestors(concept_id, limit=limit)
                if ancestors:
                    for i, ancestor in enumerate(ancestors[:limit]):
                        result += f"  {'  ' * min(i // 5, max_levels)}↑ {ancestor.concept_name} ({ancestor.concept_id})\n"
                else:
                    result += "  No ancestors found\n"
            except Exception as e:
                result += f"  Error retrieving ancestors: {str(e)}\n"
            result += "\n"

        result += f"ROOT: {root_concept.concept_name} ({concept_id})\n\n"

        if direction in ["descendants", "both"]:
            result += "DESCENDANTS:\n"
            try:
                descendants = await client.vocab.get_concept_descendants(concept_id, limit=limit)
                if descendants:
                    for i, descendant in enumerate(descendants[:limit]):
                        result += f"  {'  ' * min(i // 5, max_levels)}↓ {descendant.concept_name} ({descendant.concept_id})\n"
                else:
                    result += "  No descendants found\n"
            except Exception as e:
                result += f"  Error retrieving descendants: {str(e)}\n"

        if limit < 20:
            result += f"\n(Limited to {limit} concepts per direction)"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error browsing concept hierarchy: {str(e)}")]
    finally:
        await client.close()


async def list_domains() -> list[types.TextContent]:
    """List all available domains in the OMOP CDM.

    Returns
    -------
    List[types.TextContent]
        List of domains formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        domains = await client.vocab.get_domains()

        if not domains:
            return [types.TextContent(type="text", text="No domains found or domains not available")]

        result = "Available OMOP Domains:\n\n"

        # Group domains by common categories
        clinical_domains = []
        administrative_domains = []
        other_domains = []

        for domain in domains:
            domain_name = domain.domain_id if hasattr(domain, "domain_id") else str(domain)
            if domain_name in ["Condition", "Drug", "Procedure", "Measurement", "Observation", "Device"]:
                clinical_domains.append(domain_name)
            elif domain_name in ["Visit", "Provider", "Payer", "Care Site"]:
                administrative_domains.append(domain_name)
            else:
                other_domains.append(domain_name)

        if clinical_domains:
            result += "Clinical Domains:\n"
            for domain in sorted(clinical_domains):
                result += f"  - {domain}\n"
            result += "\n"

        if administrative_domains:
            result += "Administrative Domains:\n"
            for domain in sorted(administrative_domains):
                result += f"  - {domain}\n"
            result += "\n"

        if other_domains:
            result += "Other Domains:\n"
            for domain in sorted(other_domains):
                result += f"  - {domain}\n"

        result += f"\nTotal: {len(domains)} domains available"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving domains: {str(e)}")]
    finally:
        await client.close()


async def list_vocabularies() -> list[types.TextContent]:
    """List all available vocabularies in the OMOP CDM.

    Returns
    -------
    List[types.TextContent]
        List of vocabularies formatted for MCP client.
    """
    webapi_base_url = os.getenv("WEBAPI_BASE_URL")
    if not webapi_base_url:
        raise ValueError("WEBAPI_BASE_URL environment variable is required")

    client = WebApiClient(webapi_base_url)

    try:
        vocabularies = await client.vocab.get_vocabularies()

        if not vocabularies:
            return [types.TextContent(type="text", text="No vocabularies found or vocabularies not available")]

        result = "Available OMOP Vocabularies:\n\n"

        # Group vocabularies by type
        standard_vocabs = []
        classification_vocabs = []
        other_vocabs = []

        for vocab in vocabularies:
            vocab_id = vocab.vocabulary_id if hasattr(vocab, "vocabulary_id") else str(vocab)
            vocab_name = getattr(vocab, "vocabulary_name", vocab_id)

            if vocab_id in ["SNOMED", "RxNorm", "LOINC", "ICD10CM", "CPT4", "ICD10PCS"]:
                standard_vocabs.append((vocab_id, vocab_name))
            elif vocab_id in ["ICD9CM", "ICD9Proc", "NDC", "HCPCS"]:
                classification_vocabs.append((vocab_id, vocab_name))
            else:
                other_vocabs.append((vocab_id, vocab_name))

        if standard_vocabs:
            result += "Standard Vocabularies:\n"
            for vocab_id, vocab_name in sorted(standard_vocabs):
                result += f"  - {vocab_id}: {vocab_name}\n"
            result += "\n"

        if classification_vocabs:
            result += "Classification Vocabularies:\n"
            for vocab_id, vocab_name in sorted(classification_vocabs):
                result += f"  - {vocab_id}: {vocab_name}\n"
            result += "\n"

        if other_vocabs:
            result += "Other Vocabularies:\n"
            for vocab_id, vocab_name in sorted(other_vocabs)[:20]:  # Limit to 20
                result += f"  - {vocab_id}: {vocab_name}\n"
            if len(other_vocabs) > 20:
                result += f"  ... and {len(other_vocabs) - 20} more\n"

        result += f"\nTotal: {len(vocabularies)} vocabularies available"

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error retrieving vocabularies: {str(e)}")]
    finally:
        await client.close()
