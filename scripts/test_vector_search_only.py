"""
FILE: test_vector_search_only.py
STATUS: Active
RESPONSIBILITY: Test vector search functionality with Mistral embeddings
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.services.chat import ChatService


def main():
    """Test vector search with Mistral embeddings."""
    print("\n" + "="*80)
    print("  VECTOR SEARCH TEST")
    print("  FAISS + Mistral Embeddings")
    print("="*80 + "\n")

    try:
        # Initialize chat service
        print("Initializing ChatService...")
        chat_service = ChatService()
        print("✓ ChatService initialized\n")

        # Test query
        question = "What are the key principles of basketball defense?"
        print(f"Query: {question}\n")

        # Perform vector search
        print("Performing vector search with Mistral embeddings...")
        results = chat_service.search(question, k=3)

        if not results:
            print("✗ FAILED - No results returned\n")
            return 1

        print(f"✓ Vector search successful - Retrieved {len(results)} documents\n")

        # Display results
        print("Search Results:")
        print("-"*80)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.score:.4f}")
            print(f"   Source: {result.source}")
            print(f"   Content: {result.text[:200]}...")

        print("\n" + "="*80)
        print("✓ VECTOR SEARCH WORKING")
        print("="*80)
        print("  ✓ Mistral embeddings → Working")
        print("  ✓ FAISS vector store → Working")
        print("  ✓ Query embedding → Working")
        print("  ✓ Similarity search → Working")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        print(f"\n✗ FAILED - Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
