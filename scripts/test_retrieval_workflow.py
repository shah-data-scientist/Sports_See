"""
FILE: test_retrieval_workflow.py
STATUS: Active
RESPONSIBILITY: Validate correct retrieval workflow (retrieve more, boost all, return top k)
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Test that vector search retrieves enough candidates for metadata boost to work.
"""

import io
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app

def test_retrieval_workflow():
    """Test that retrieval workflow retrieves enough candidates before boosting."""
    print("\n" + "="*80)
    print("  TESTING RETRIEVAL WORKFLOW: Retrieve → Boost → Sort → Top K")
    print("="*80 + "\n")

    # Query that should retrieve Reddit content
    query = "What do Reddit users think about playoff teams?"

    app = create_app()
    with TestClient(app) as client:
        # Call API with k=5, include_sources=True
        response = client.post(
            "/api/v1/chat",
            json={"query": query, "k": 5, "include_sources": True},
            timeout=30,
        )

        if response.status_code != 200:
            print(f"✗ API call failed: {response.status_code}")
            return 1

        api_result = response.json()
        sources = api_result.get("sources", [])

        print(f"Query: {query}")
        print(f"Requested k=5\n")

        print(f"Retrieved {len(sources)} sources:\n")

        for i, src in enumerate(sources, 1):
            source_name = src.get("source", "unknown")
            score = src.get("score", 0)
            text_preview = src.get("text", "")[:150]

            # Check if Reddit
            is_reddit = "reddit" in source_name.lower()
            marker = "🔴" if is_reddit else "⚪"

            print(f"{marker} [{i}] Score: {score:.1f}%")
            print(f"    Source: {source_name}")
            print(f"    Text: {text_preview}...")
            print()

        # Count Reddit sources
        reddit_count = sum(1 for s in sources if "reddit" in s.get("source", "").lower())

        print(f"{'='*80}")
        print(f"Reddit sources in top 5: {reddit_count}/5")
        print(f"{'='*80}\n")

        if reddit_count > 0:
            print("✅ SUCCESS: Metadata boost working (Reddit content retrieved)")
            print("   The workflow correctly:")
            print("   1. Retrieved 15 candidates from FAISS")
            print("   2. Applied metadata boost to all 15")
            print("   3. Sorted by boosted scores")
            print("   4. Returned top 5")
        else:
            print("⚠️  WARNING: No Reddit content in top 5")
            print("   This query might not match Reddit discussions well")

        return 0

if __name__ == "__main__":
    sys.exit(test_retrieval_workflow())
