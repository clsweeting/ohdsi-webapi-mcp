#!/usr/bin/env python3
"""Simple debug script to test concept search step by step.

Run with: poetry run python scripts/debug_search.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def debug_search():
    """Debug the search function step by step."""
    print("🐛 Debugging concept search...")

    # Step 1: Test environment
    print("\n1. Checking environment...")
    os.environ["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"
    print(f"   WEBAPI_BASE_URL: {os.getenv('WEBAPI_BASE_URL')}")

    # Step 2: Test sync WebAPI client directly
    print("\n2. Testing sync WebAPI client...")
    try:
        from ohdsi_webapi import WebApiClient

        client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")
        concepts = client.vocab.search("diabetes", domain_id="Condition", limit=3)
        print(f"   Found {len(concepts)} concepts directly")
        for concept in concepts[:2]:
            print(f"   - {concept.concept_name} ({concept.concept_id})")
        client.close()

    except Exception as e:
        print(f"   ❌ Direct WebAPI test failed: {e}")
        return

    # Step 3: Test async wrapper
    print("\n3. Testing async wrapper...")
    try:
        from ohdsi_webapi_mcp.tools.concepts import search_concepts

        results = await search_concepts("diabetes", domain="Condition", limit=3)
        print(f"   Got {len(results)} result objects")
        for i, result in enumerate(results):
            print(f"   Result {i}: {result.text[:100]}...")

    except Exception as e:
        print(f"   ❌ Async wrapper test failed: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n✅ All debug steps completed!")


if __name__ == "__main__":
    asyncio.run(debug_search())
