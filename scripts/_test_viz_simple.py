"""
FILE: _test_viz_simple.py
STATUS: Active - Temporary
RESPONSIBILITY: Simple test of API visualization integration
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app


print("\n" + "=" * 80)
print("TESTING API VISUALIZATION INTEGRATION")
print("=" * 80)

app = create_app()

with TestClient(app) as client:
    # Test: Top N query
    print("\n[TEST] Who are the top 5 scorers?")

    response = client.post(
        "/api/v1/chat",
        json={"query": "Who are the top 5 scorers this season?"}
    )

    data = response.json()

    print(f"[STATUS] {response.status_code}")
    print(f"[ANSWER] {data['answer'][:150]}...")

    if data.get("visualization"):
        viz = data["visualization"]
        print(f"\n[VIZ FOUND]")
        print(f"  Pattern: {viz['pattern']}")
        print(f"  Type: {viz['viz_type']}")

        # Save HTML
        output_path = Path(__file__).parent.parent / "evaluation_results" / "api_viz_test.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(viz["plot_html"])
        print(f"  Saved: {output_path}")
    else:
        print("\n[NO VIZ] - This is unexpected for a statistical query")

print("\n" + "=" * 80)
print("[COMPLETE]")
print("=" * 80)
