#!/usr/bin/env python3
"""Test the webapi client search functionality directly."""

import asyncio
import os

from ohdsi_webapi import WebApiClient


async def test_enhanced_search_direct():
    """Test the enhanced search functionality directly with webapi_client."""
    print("=== Testing Enhanced Search with webapi_client ===\n")

    base_url = os.getenv("WEBAPI_BASE_URL", "https://atlas-demo.ohdsi.org/WebAPI")
    client = WebApiClient(base_url)

    try:
        # Test 1: Basic search
        print("1. Basic search for 'diabetes':")
        concepts = client.vocab.search("diabetes", page_size=5)
        print(f"   Found {len(concepts)} concepts")
        for concept in concepts[:3]:
            print(f"   • {concept.concept_name} (ID: {concept.concept_id})")
            print(f"     Domain: {concept.domain_id} | Vocabulary: {concept.vocabulary_id}")

        print("\n" + "=" * 50 + "\n")

        # Test 2: Domain-filtered search
        print("2. Search for 'diabetes' in Condition domain only:")
        concepts = client.vocab.search("diabetes", domain_id="Condition", page_size=3)
        print(f"   Found {len(concepts)} concepts")
        for concept in concepts:
            print(f"   • {concept.concept_name} (ID: {concept.concept_id})")
            print(f"     Standard: {concept.standard_concept or 'N'} | Class: {concept.concept_class_id}")

        print("\n" + "=" * 50 + "\n")

        # Test 3: Vocabulary-filtered search
        print("3. Search for 'diabetes' in SNOMED vocabulary:")
        concepts = client.vocab.search("diabetes", vocabulary_id="SNOMED", page_size=3)
        print(f"   Found {len(concepts)} concepts")
        for concept in concepts:
            print(f"   • {concept.concept_name} (ID: {concept.concept_id})")
            print(f"     Code: {concept.concept_code} | Standard: {concept.standard_concept or 'N'}")

        print("\n" + "=" * 50 + "\n")

        # Test 4: Multiple filters
        print("4. Search for 'metformin' in Drug domain, standard concepts only:")
        concepts = client.vocab.search("metformin", domain_id="Drug", standard_concept="S", page_size=3)
        print(f"   Found {len(concepts)} concepts")
        for concept in concepts:
            print(f"   • {concept.concept_name} (ID: {concept.concept_id})")
            print(f"     Class: {concept.concept_class_id} | Code: {concept.concept_code}")

        print("\n" + "=" * 50 + "\n")

        # Test 5: Concept details
        print("5. Get details for diabetes concept (201826):")
        concept = client.vocab.concept(201826)
        print(f"   Name: {concept.concept_name}")
        print(f"   ID: {concept.concept_id}")
        print(f"   Domain: {concept.domain_id}")
        print(f"   Vocabulary: {concept.vocabulary_id}")
        print(f"   Class: {concept.concept_class_id}")
        print(f"   Code: {concept.concept_code}")
        print(f"   Standard: {concept.standard_concept or 'N'}")

        print("\n" + "=" * 50 + "\n")

        # Test 6: Descendants
        print("6. Get descendants for diabetes concept (201826):")
        descendants = client.vocab.descendants(201826)
        print(f"   Found {len(descendants)} descendants")
        for desc in descendants[:5]:
            print(f"   • {desc.concept_name} (ID: {desc.concept_id})")

        print("\n" + "=" * 50 + "\n")

        # Test 7: List domains
        print("7. List available domains:")
        domains = client.vocab.domains()
        print(f"   Found {len(domains)} domains")
        for domain in domains[:10]:
            domain_id = domain.get("domainId", "Unknown")
            domain_name = domain.get("domainName", "No description")
            print(f"   • {domain_id} - {domain_name}")

        print("\n" + "=" * 50 + "\n")

        # Test 8: List vocabularies
        print("8. List available vocabularies:")
        vocabularies = client.vocab.vocabularies()
        print(f"   Found {len(vocabularies)} vocabularies")
        for vocab in vocabularies[:10]:
            vocab_id = vocab.get("vocabularyId", "Unknown")
            vocab_name = vocab.get("vocabularyName", "No description")
            print(f"   • {vocab_id} - {vocab_name}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(test_enhanced_search_direct())
