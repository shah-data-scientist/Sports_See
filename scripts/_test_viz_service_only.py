"""
FILE: _test_viz_service_only.py
STATUS: Active - Temporary
RESPONSIBILITY: Test visualization service in isolation
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.visualization_service import VisualizationService

# Test data (simulating SQL results)
test_data = [
    {"name": "Shai Gilgeous-Alexander", "pts": 2485},
    {"name": "Anthony Edwards", "pts": 2180},
    {"name": "Nikola Jokić", "pts": 2072},
    {"name": "Giannis Antetokounmpo", "pts": 2037},
    {"name": "Jayson Tatum", "pts": 1930},
]

print("\n" + "=" * 80)
print("TESTING VISUALIZATION SERVICE")
print("=" * 80)

try:
    service = VisualizationService()
    print("✓ VisualizationService initialized")

    query = "Who are the top 5 scorers this season?"
    print(f"\nQuery: {query}")
    print(f"Data: {len(test_data)} rows")

    result = service.generate_visualization(
        query=query,
        sql_result=test_data
    )

    print(f"\n✓ Visualization generated!")
    print(f"  Pattern: {result['pattern']}")
    print(f"  Type: {result['viz_type']}")
    print(f"  JSON length: {len(result['plot_json'])} chars")
    print(f"  HTML length: {len(result['plot_html'])} chars")

    # Save HTML to verify
    output_path = Path(__file__).parent.parent / "evaluation_results" / "viz_service_test.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["plot_html"])
    print(f"  Saved to: {output_path}")

    print("\n" + "=" * 80)
    print("✓ TEST PASSED")
    print("=" * 80)

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 80)
    print("✗ TEST FAILED")
    print("=" * 80)
