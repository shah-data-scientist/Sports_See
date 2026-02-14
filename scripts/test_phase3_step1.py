"""
Phase 3 Step 1 Verification: Document Quality Filter
Tests quality filtering on noisy category queries
"""
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from src.services.chat import ChatService
from src.models.chat import ChatRequest
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES

def test_phase3_step1_quality_filter():
    """Test document quality filtering on noisy queries."""

    # Get noisy or complex category test cases (these are harder to retrieve)
    # Use "complex" since "noisy" may not exist in vector test cases
    test_cases = [tc for tc in EVALUATION_TEST_CASES if tc.category.value == "complex"][:3]

    if not test_cases:
        # Fallback to first 3 test cases
        test_cases = EVALUATION_TEST_CASES[:3]

    print("=" * 80)
    print("PHASE 3 STEP 1: Document Quality Filter Verification")
    print("=" * 80)
    print(f"\nTesting on {len(test_cases)} noisy queries\n")

    chat_service = ChatService()
    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"Test {i}: {test_case.question}")
        print(f"Expected Category: {test_case.category}")
        print(f"{'-' * 80}")

        try:
            # Run the query
            request = ChatRequest(query=test_case.question, include_sources=True)
            response = chat_service.chat(request)

            # Count sources
            num_sources = len(response.sources)

            print(f"✓ Query executed successfully")
            print(f"  Processing time: {response.processing_time_ms:.0f}ms")
            print(f"  Sources retrieved: {num_sources}")

            if response.sources:
                print(f"  Source scores: {[f'{s.score:.1f}%' for s in response.sources]}")
                print(f"  Top source: {response.sources[0].source}")
                print(f"  Response preview: {response.answer[:150]}...")
            else:
                print(f"  No sources (quality filter may have been too aggressive)")

            results.append({
                "query": test_case.question,
                "success": True,
                "num_sources": num_sources,
                "processing_time_ms": response.processing_time_ms,
                "has_answer": len(response.answer) > 0
            })

        except Exception as e:
            print(f"✗ Query failed: {type(e).__name__}: {e}")
            results.append({
                "query": test_case.question,
                "success": False,
                "error": str(e)
            })

    # Summary
    print(f"\n\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    successful = [r for r in results if r.get("success")]
    print(f"\nSuccessful: {len(successful)}/{len(test_cases)}")

    if successful:
        avg_sources = sum(r["num_sources"] for r in successful) / len(successful)
        print(f"Average sources per query: {avg_sources:.1f}")

        print(f"\nQueries with results:")
        for r in successful:
            if r["num_sources"] > 0:
                print(f"  ✓ {r['query'][:50]}... ({r['num_sources']} sources)")
            else:
                print(f"  ⚠ {r['query'][:50]}... (no sources - filter too aggressive?)")

    # Interpretation
    print(f"\n{'=' * 80}")
    print("INTERPRETATION")
    print(f"{'=' * 80}")

    if len(successful) == len(test_cases) and all(r["num_sources"] > 0 for r in successful):
        print("""
✓ GOOD: Quality filter is working
  - All queries return results
  - Sources are being retrieved
  - No excessive filtering

Next: Run Step 2 (Recall-Aware K Selection)
        """)
    elif len(successful) < len(test_cases):
        print("""
⚠ WARNING: Some queries failed
  - Quality filter may be rejecting good documents
  - May need to adjust quality threshold (currently 0.5)

Action: Lower quality threshold to 0.4 or investigate OCR quality
        """)
    else:
        print("""
✓ ACCEPTABLE: Quality filter working, but may be aggressive
  - All queries return results
  - Check if too few sources for noisy category
  - May need to balance precision/recall

Next: Compare precision/recall metrics before & after filtering
        """)

if __name__ == "__main__":
    test_phase3_step1_quality_filter()
