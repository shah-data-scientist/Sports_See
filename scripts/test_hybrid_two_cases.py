"""
Quick test: Run hybrid evaluation on TWO test cases
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from starlette.testclient import TestClient
from src.api.main import create_app
from src.evaluation.test_cases.hybrid_test_cases import HYBRID_TEST_CASES
from src.evaluation.analysis.hybrid_quality_analysis import analyze_hybrid_results, generate_markdown_report

# Select first 2 hybrid test cases
test_cases = HYBRID_TEST_CASES[:2]

print("=" * 80)
print("HYBRID EVALUATION - TWO TEST CASES")
print("=" * 80)
print(f"\nTest Case 1: {test_cases[0].question}")
print(f"Test Case 2: {test_cases[1].question}")
print("\nRunning evaluation...\n")

# Create app and run tests
app = create_app()
results = []

with TestClient(app) as client:
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/2] Testing: {test_case.question[:60]}...")

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
                # ChatResponse fields: answer, sources, generated_sql, processing_time_ms
                answer = response_data.get("answer", "")
                sources = response_data.get("sources", [])
                processing_time = response_data.get("processing_time_ms", 0)
                generated_sql = response_data.get("generated_sql")

                # Analyze routing using generated_sql (not sql_results)
                has_sql = generated_sql is not None and len(generated_sql) > 0
                has_vector = len(sources) > 0

                if has_sql and has_vector:
                    routing = "both"
                elif has_sql:
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
                    "generated_sql": generated_sql,
                    "sources": sources,
                    "sources_count": len(sources),
                    "processing_time_ms": processing_time,
                    "success": True,
                }

                print(f"  ✓ SUCCESS | Routing: {routing.upper()} | Sources: {len(sources)} | Time: {processing_time:.0f}ms")
                if generated_sql:
                    print(f"  SQL: {generated_sql[:80]}...")
                print(f"  Response: {answer[:150]}...")

            else:
                print(f"  ✗ FAILED: HTTP {response.status_code}")
                result = {
                    "question": test_case.question,
                    "category": test_case.category,
                    "error": f"HTTP {response.status_code}",
                    "success": False,
                }

            results.append(result)

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
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

analysis = analyze_hybrid_results(results, test_cases)

print(f"\nOverall Performance:")
print(f"  Success Rate: {analysis['overall']['success_rate']}%")
print(f"  Successful: {analysis['overall']['successful']}/{analysis['overall']['total_queries']}")
print(f"  Response Quality: {analysis['overall']['has_response_rate']}% have meaningful responses")

print(f"\nRouting Analysis:")
for key, value in analysis["routing"].items():
    if not key.endswith("_pct"):
        print(f"  {key}: {value}")

# SQL Component
if analysis["sql_component"].get("sql_queries", 0) > 0:
    print(f"\nSQL Component:")
    sql = analysis["sql_component"]
    print(f"  SQL Queries: {sql['sql_queries']}")
    print(f"  SQL Generated: {sql['has_generated_sql']} ({sql['sql_generation_rate']}%)")
    if "sql_complexity" in sql:
        print(f"  SQL Complexity: JOIN={sql['sql_complexity']['with_join']}, WHERE={sql['sql_complexity']['with_where']}, LIMIT={sql['sql_complexity']['with_limit']}")

# Vector Component
if analysis["vector_component"].get("vector_queries", 0) > 0:
    print(f"\nVector Component:")
    vec = analysis["vector_component"]
    print(f"  Vector Queries: {vec['vector_queries']}")
    print(f"  Sources Retrieved: {vec['has_sources']} ({vec['sources_rate']}%)")
    print(f"  Avg Sources: {vec['avg_sources']}")
    print(f"  Source Range: {vec['min_sources']} - {vec['max_sources']}")

# Hybrid Combination
if analysis["hybrid_combination"].get("hybrid_queries", 0) > 0:
    print(f"\nHybrid Combination:")
    hyb = analysis["hybrid_combination"]
    print(f"  True Hybrid Queries: {hyb['hybrid_queries']}")
    print(f"  Both Data Present: {hyb['has_both_data']} ({hyb['both_data_rate']}%)")

# Performance
if "avg_processing_time_ms" in analysis["performance"]:
    print(f"\nPerformance:")
    perf = analysis["performance"]
    print(f"  Avg Time: {perf['avg_processing_time_ms']}ms")
    print(f"  Median Time: {perf['median_processing_time_ms']}ms")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Save reports
output_dir = Path("evaluation_results")
output_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

json_file = output_dir / f"hybrid_2cases_{timestamp}.json"
output_data = {
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "test_cases": 2,
        "successful": sum(1 for r in results if r.get("success")),
    },
    "analysis": analysis,
    "results": results,
}
json_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n✓ JSON report saved: {json_file}")

# Generate Markdown report
md_file = output_dir / f"hybrid_2cases_report_{timestamp}.md"
generate_markdown_report(results, analysis, test_cases, md_file)
print(f"✓ Markdown report saved: {md_file}")
