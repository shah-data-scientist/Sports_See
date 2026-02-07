"""
FILE: test_hybrid_agent.py
STATUS: Active
RESPONSIBILITY: Test hybrid RAG agent (SQL + Vector Search)
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

from src.models.chat import ChatRequest
from src.services.chat import ChatService


def test_hybrid_agent():
    """Test hybrid agent with different query types."""
    print("=" * 80)
    print("HYBRID RAG AGENT TEST")
    print("=" * 80)

    # Initialize chat service with SQL enabled
    chat_service = ChatService(enable_sql=True)

    # Test queries
    test_cases = [
        ("Who are the top 3 scorers?", "STATISTICAL"),
        ("Why is LeBron considered the GOAT?", "CONTEXTUAL"),
        ("Compare Jokic and Giannis stats and explain who's better", "HYBRID"),
    ]

    for i, (query, expected_type) in enumerate(test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"Test {i}: {expected_type} Query")
        print(f"{'-' * 80}")
        print(f"Query: {query}")

        try:
            # Create request
            request = ChatRequest(query=query, k=3, include_sources=True)

            # Get response
            response = chat_service.chat(request)

            print(f"\nAnswer:\n{response.answer}")
            print(f"\nSources: {len(response.sources)}")
            print(f"Processing time: {response.processing_time_ms:.0f}ms")
            print(f"Model: {response.model}")

        except Exception as e:
            print(f"\nERROR: {e}")

    print(f"\n{'=' * 80}")
    print("Test complete!")


if __name__ == "__main__":
    test_hybrid_agent()
