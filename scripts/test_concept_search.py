#!/usr/bin/env python3
"""Manual integration test for concept search.

This script tests the search_concepts function against a real WebAPI instance.
Run with: poetry run python scripts/test_concept_search.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ohdsi_webapi_mcp.tools.concepts import search_concepts


async def main():
    """Test concept search against Atlas demo."""
    print("🧪 Testing concept search functionality...")

    # Set environment for Atlas demo
    os.environ["WEBAPI_BASE_URL"] = "https://atlas-demo.ohdsi.org/WebAPI"

    try:
        print("\n1. Testing diabetes search...")
        results = await search_concepts("diabetes", domain="Condition", limit=5)
        for result in results:
            print(f"   {result.text}")

        print("\n2. Testing drug search...")
        results = await search_concepts("metformin", domain="Drug", limit=3)
        for result in results:
            print(f"   {result.text}")

        print("\n3. Testing no results...")
        results = await search_concepts("xyzzyx123nonexistent")
        for result in results:
            print(f"   {result.text}")

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
