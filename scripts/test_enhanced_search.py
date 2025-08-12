#!/usr/bin/env python3
"""Test the enhanced search_concepts tool."""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ohdsi_webapi_mcp.tools.concepts import get_concept_details, list_domains, list_vocabularies, search_concepts


async def test_enhanced_search():
    """Test the enhanced search functionality."""
    print("=== Testing Enhanced Search Concepts ===\n")

    # Test 1: Basic search
    print("1. Basic search for 'diabetes':")
    try:
        results = await search_concepts("diabetes", limit=5)
        for result in results:
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 2: Domain-filtered search
    print("2. Search for 'diabetes' in Condition domain only:")
    try:
        results = await search_concepts("diabetes", domain="Condition", limit=3)
        for result in results:
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 3: Vocabulary-filtered search
    print("3. Search for 'diabetes' in SNOMED vocabulary:")
    try:
        results = await search_concepts("diabetes", vocabulary="SNOMED", limit=3)
        for result in results:
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 4: Multiple filters
    print("4. Search for 'metformin' in Drug domain, Ingredient class:")
    try:
        results = await search_concepts("metformin", domain="Drug", concept_class="Ingredient", limit=3)
        for result in results:
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 5: Concept details
    print("5. Get details for diabetes concept (201826):")
    try:
        results = await get_concept_details(201826)
        for result in results:
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 6: List domains
    print("6. List available domains:")
    try:
        results = await list_domains()
        for result in results[:10]:  # Show first 10
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Test 7: List vocabularies
    print("7. List available vocabularies:")
    try:
        results = await list_vocabularies()
        for result in results[:15]:  # Show first 15
            print(result.text)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_search())
