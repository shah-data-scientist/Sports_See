"""
FILE: _test_api_visualization.py
STATUS: Active - Temporary
RESPONSIBILITY: Test FastAPI visualization integration
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app


def test_statistical_query_with_viz():
    """Test that statistical queries return visualizations."""
    print("\n" + "=" * 80)
    print("TESTING API VISUALIZATION INTEGRATION")
    print("=" * 80)

    # Create app and test client
    app = create_app()
    client = TestClient(app)

    # Test 1: Top N query (should return bar chart)
    print("\n" + "-" * 80)
    print("TEST 1: Top N Query - 'Who are the top 5 scorers?'")
    print("-" * 80)

    response = client.post(
        "/api/v1/chat",
        json={"query": "Who are the top 5 scorers this season?", "k": 5}
    )

    data = response.json()

    print(f"\n[STATUS] {response.status_code}")
    print(f"[QUERY] {data['query']}")
    print(f"[ANSWER] {data['answer'][:200]}...")

    if "visualization" in data and data["visualization"]:
        viz = data["visualization"]
        print(f"\n[VIZ] Visualization generated!")
        print(f"  - Pattern: {viz['pattern']}")
        print(f"  - Type: {viz['viz_type']}")
        print(f"  - JSON length: {len(viz['plot_json'])} chars")
        print(f"  - HTML length: {len(viz['plot_html'])} chars")

        # Save HTML for viewing
        output_path = Path(__file__).parent.parent / "evaluation_results" / "api_test_top_n.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(viz["plot_html"])
        print(f"  - Saved to: {output_path}")
    else:
        print("\n[VIZ] No visualization returned")

    # Test 2: Player comparison (should return radar chart)
    print("\n" + "-" * 80)
    print("TEST 2: Comparison Query - 'Compare Jokic and Embiid stats'")
    print("-" * 80)

    response = client.post(
        "/api/v1/chat",
        json={"query": "Compare Jokic and Embiid's stats", "k": 5}
    )

    data = response.json()

    print(f"\n[STATUS] {response.status_code}")
    print(f"[QUERY] {data['query']}")
    print(f"[ANSWER] {data['answer'][:200]}...")

    if "visualization" in data and data["visualization"]:
        viz = data["visualization"]
        print(f"\n[VIZ] Visualization generated!")
        print(f"  - Pattern: {viz['pattern']}")
        print(f"  - Type: {viz['viz_type']}")

        # Save HTML for viewing
        output_path = Path(__file__).parent.parent / "evaluation_results" / "api_test_comparison.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(viz["plot_html"])
        print(f"  - Saved to: {output_path}")
    else:
        print("\n[VIZ] No visualization returned")

    # Test 3: Contextual query (should NOT return visualization)
    print("\n" + "-" * 80)
    print("TEST 3: Contextual Query - 'What is the team culture like?'")
    print("-" * 80)

    response = client.post(
        "/api/v1/chat",
        json={"query": "What is the team culture like for the Lakers?", "k": 5}
    )

    data = response.json()

    print(f"\n[STATUS] {response.status_code}")
    print(f"[QUERY] {data['query']}")
    print(f"[ANSWER] {data['answer'][:200]}...")

    if "visualization" in data and data["visualization"]:
        print("\n[VIZ] Visualization generated (unexpected for contextual query)")
    else:
        print("\n[VIZ] No visualization returned (expected for contextual query)")

    print("\n" + "=" * 80)
    print("API VISUALIZATION INTEGRATION TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_statistical_query_with_viz()
