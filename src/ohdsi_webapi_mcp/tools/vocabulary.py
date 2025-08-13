"""Tools for vocabulary and concept search."""

import asyncio
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
            concepts = client.vocabulary.search(**search_kwargs)
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

    def _sync_get_concept_details():
        client = WebApiClient(webapi_base_url)
        try:
            # Get concept details (sync call)
            concept = client.vocabulary.get_concept(concept_id)

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

Related Concepts:"""

            # Get related concepts if available
            try:
                related_concepts = client.vocabulary.concept_related(concept_id)
                if related_concepts:
                    for rel in related_concepts[:10]:  # Limit to first 10
                        details += f"\n  - {rel.concept_name} ({rel.concept_id})"
                else:
                    details += "\n  No related concepts found"
            except Exception:
                details += "\n  Related concepts not available"

            return [types.TextContent(type="text", text=details)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving concept details: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_get_concept_details)


async def browse_concept_hierarchy(
    concept_id: int,
    direction: str = "descendants",
    max_levels: int = 2,
    limit: int = 20,
) -> list[types.TextContent]:
    """Browse concept hierarchy to find related concepts.

    Parameters
    ----------
    concept_id : int
        The starting concept ID.
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

    def _sync_browse_hierarchy():
        client = WebApiClient(webapi_base_url)
        try:
            # Get the root concept
            root_concept = client.vocabulary.get_concept(concept_id)
            if not root_concept:
                return [types.TextContent(type="text", text=f"No concept found with ID: {concept_id}")]

            result = f"Concept Hierarchy for {root_concept.concept_name} ({concept_id}):\n\n"

            if direction in ["ancestors", "both"]:
                result += "ANCESTORS:\n"
                try:
                    # Use concept_related since get_concept_ancestors might not exist
                    ancestors = client.vocabulary.concept_related(concept_id)
                    if ancestors:
                        # Filter and limit ancestors
                        filtered_ancestors = ancestors[:limit]
                        for i, ancestor in enumerate(filtered_ancestors):
                            result += f"  {'  ' * min(i // 5, max_levels)}↑ {ancestor.concept_name} ({ancestor.concept_id})\n"
                    else:
                        result += "  No related concepts found\n"
                except Exception as e:
                    result += f"  Error retrieving related concepts: {str(e)}\n"
                result += "\n"

            result += f"ROOT: {root_concept.concept_name} ({concept_id})\n\n"

            if direction in ["descendants", "both"]:
                result += "DESCENDANTS:\n"
                try:
                    descendants = client.vocabulary.concept_descendants(concept_id)
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
            return [types.TextContent(type="text", text=f"Error browsing hierarchy: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_browse_hierarchy)


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

    def _sync_list_domains():
        client = WebApiClient(webapi_base_url)
        try:
            domains = client.vocabulary.list_domains()

            if not domains:
                return [types.TextContent(type="text", text="No domains found or domains not available")]

            result = "Available OMOP Domains:\n\n"

            # Group domains by common categories
            clinical_domains = []
            administrative_domains = []
            other_domains = []

            for domain in domains:
                domain_name = domain.get("domainId") if isinstance(domain, dict) else getattr(domain, "domain_id", str(domain))
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
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_list_domains)


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

    def _sync_list_vocabularies():
        client = WebApiClient(webapi_base_url)
        try:
            vocabularies = client.vocabulary.list_vocabularies()

            if not vocabularies:
                return [types.TextContent(type="text", text="No vocabularies found or vocabularies not available")]

            result = "Available OMOP Vocabularies:\n\n"

            # Group vocabularies by type
            standard_vocabs = []
            classification_vocabs = []
            other_vocabs = []

            for vocab in vocabularies:
                vocab_id = vocab.get("vocabularyId") if isinstance(vocab, dict) else getattr(vocab, "vocabulary_id", str(vocab))
                vocab_name = (
                    vocab.get("vocabularyName", vocab_id) if isinstance(vocab, dict) else getattr(vocab, "vocabulary_name", vocab_id)
                )

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
                # Show first 20 to avoid overwhelming output
                for vocab_id, vocab_name in sorted(other_vocabs)[:20]:
                    result += f"  - {vocab_id}: {vocab_name}\n"
                if len(other_vocabs) > 20:
                    result += f"  ... and {len(other_vocabs) - 20} more\n"

            result += f"\nTotal: {len(vocabularies)} vocabularies available"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving vocabularies: {str(e)}")]
        finally:
            client.close()

    # Run the sync function in a thread pool
    return await asyncio.to_thread(_sync_list_vocabularies)
