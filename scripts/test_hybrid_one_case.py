"""
Quick test: Run hybrid evaluation on ONE test case
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from starlette.testclient import TestClient
from src.api.main import create_app
from src.evaluation.sql_test_cases import HYBRID_TEST_CASES
from src.evaluation.hybrid_quality_analysis import analyze_hybrid_results, generate_markdown_report

# Select first hybrid test case
test_case = HYBRID_TEST_CASES[0]

print("=" * 80)
print("HYBRID EVALUATION - SINGLE TEST CASE")
print("=" * 80)
print(f"\nTest Case: {test_case.question}")
print(f"Category: {test_case.category}")
print(f"Expected SQL: {test_case.expected_sql[:100]}...")
print("\nRunning evaluation...\n")

# Create app and run test
app = create_app()
results = []

with TestClient(app) as client:
    try:
        # Make API request
        payload = {
            "query": test_case.question,
            "k": 5,
            "include_sources": True,
        }

        response = client.post("/api/v1/chat", json=payload)

        if response.status_code == 200:
            response_data = response.json()
            answer = response_data.get("response", "")
            sources = response_data.get("sources", [])
            processing_time = response_data.get("processing_time_ms", 0)

            # Analyze routing
            has_sql_data = "sql_results" in response_data and response_data["sql_results"]
            has_vector = len(sources) > 0

            if has_sql_data and has_vector:
                routing = "both"
            elif has_sql_data:
                routing = "sql"
            elif has_vector:
                routing = "vector"
            else:
                routing = "unknown"

            result = {
                "question": test_case.question,
                "category": test_case.category,
                "response": answer,
                "routing": routing,
                "sql_data": response_data.get("sql_results"),
                "sources": sources,
                "sources_count": len(sources),
                "processing_time_ms": processing_time,
                "success": True,
            }

            print("✅ SUCCESS")
            print(f"\nRouting: {routing.upper()}")
            print(f"Sources: {len(sources)}")
            print(f"Processing Time: {processing_time}ms")
            print(f"\nResponse ({len(answer)} chars):")
            print("-" * 80)
            print(answer[:500] + ("..." if len(answer) > 500 else ""))
            print("-" * 80)

            if sources:
                print(f"\nSources Retrieved ({len(sources)}):")
                for i, source in enumerate(sources[:3], 1):
                    source_name = source.get("source", "Unknown")
                    score = source.get("score", 0)
                    print(f"  {i}. {source_name} ({score}% similarity)")

        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(response.text[:300])
            result = {
                "question": test_case.question,
                "category": test_case.category,
                "error": f"HTTP {response.status_code}",
                "success": False,
            }

        results.append(result)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        result = {
            "question": test_case.question,
            "category": test_case.category,
            "error": str(e),
            "success": False,
        }
        results.append(result)

# Generate analysis
print("\n" + "=" * 80)
print("QUALITY ANALYSIS")
print("=" * 80)

analysis = analyze_hybrid_results(results, [test_case])

print(f"\nOverall Performance:")
print(f"  Success Rate: {analysis['overall']['success_rate']}%")

print(f"\nRouting Analysis:")
for key, value in analysis["routing"].items():
    if not key.endswith("_pct"):
        print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
