"""
FILE: test_context_extraction.py
STATUS: Active
RESPONSIBILITY: Quick validation that context extraction works correctly
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Run on 2-3 test cases to verify retrieved contexts are populated.
"""

import io
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES

def test_context_extraction():
    """Test that contexts are properly extracted from API response."""
    print("\n" + "="*80)
    print("  TESTING CONTEXT EXTRACTION (2 test cases)")
    print("="*80 + "\n")

    # Use first 2 test cases
    test_cases = EVALUATION_TEST_CASES[:2]

    app = create_app()
    with TestClient(app) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/2] Testing: {test_case.question[:70]}...")

            response = client.post(
                "/api/v1/chat",
                json={"query": test_case.question, "k": 5, "include_sources": True},
                timeout=30,
            )

            if response.status_code != 200:
                print(f"  ✗ API call failed: {response.status_code}")
                continue

            api_result = response.json()

            # Extract contexts using FIXED method
            retrieved_contexts = [src.get("text", "") for src in api_result.get("sources", [])]

            print(f"  ✓ API call successful")
            print(f"  Sources returned: {len(api_result.get('sources', []))}")
            print(f"  Contexts extracted: {len(retrieved_contexts)}")
            print(f"  Non-empty contexts: {len([c for c in retrieved_contexts if c])}")

            # Show first context preview
            if retrieved_contexts and retrieved_contexts[0]:
                print(f"\n  First context preview (first 150 chars):")
                print(f"  {retrieved_contexts[0][:150]}...")
            else:
                print(f"  ❌ ERROR: Contexts are EMPTY!")

            # Show the raw source structure
            if api_result.get("sources"):
                first_source = api_result["sources"][0]
                print(f"\n  Source structure keys: {list(first_source.keys())}")
                if "text" in first_source:
                    print(f"  ✓ 'text' field exists")
                else:
                    print(f"  ✗ 'text' field MISSING")

    print("\n" + "="*80)
    print("  VALIDATION COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_context_extraction()
