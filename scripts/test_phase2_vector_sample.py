"""
Quick test of Phase 2 vector improvements on sample queries.
Tests: 3-signal scoring, adaptive k, query expansion effects
"""
import asyncio
import json
from pathlib import Path
from src.services.chat import ChatService
from src.models.chat import ChatRequest

async def test_vector_sample():
    """Test vector queries with Phase 2 improvements."""
    chat_service = ChatService()

    # Sample queries that were problematic in previous evaluation
    test_queries = [
        "What are the strengths and weaknesses of LeBron James' playstyle?",
        "Compare the defensive strategies of the Celtics and Warriors",
        "Explain what makes Jokic an efficient player",
        "Who are the top scorers this season?",
        "What is a pick and roll in basketball?",
    ]

    results = []

    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n{'='*70}")
            print(f"Query {i}: {query}")
            print('='*70)

            # Estimate complexity
            k_value = chat_service._estimate_question_complexity(query)
            print(f"Estimated complexity: k={k_value}")

            # Test vector search
            search_results = chat_service.search(query=query, k=k_value)

            print(f"Retrieved {len(search_results)} results:")
            for j, result in enumerate(search_results[:3], 1):
                print(f"  {j}. Score: {result.score:.1f}% | Source: {result.source}")
                print(f"     Text preview: {result.text[:100]}...")

            results.append({
                "query": query,
                "k_value": k_value,
                "num_results": len(search_results),
                "top_scores": [r.score for r in search_results[:3]],
                "status": "success"
            })

        except Exception as e:
            print(f"Error: {e}")
            results.append({
                "query": query,
                "status": "error",
                "error": str(e)
            })

    # Summary
    print(f"\n{'='*70}")
    print("PHASE 2 VERIFICATION SUMMARY")
    print('='*70)

    successes = [r for r in results if r.get("status") == "success"]
    print(f"✓ Successful queries: {len(successes)}/{len(test_queries)}")

    for result in results:
        if result.get("status") == "success":
            print(f"  • {result['query'][:50]}... (k={result['k_value']}, {result['num_results']} results)")

    # Save results
    output_file = Path("evaluation_results/phase2_vector_sample.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(test_vector_sample())
