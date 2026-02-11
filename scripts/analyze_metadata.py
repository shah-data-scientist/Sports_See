"""
FILE: analyze_metadata.py
STATUS: Active
RESPONSIBILITY: Analyze metadata distribution and test simple queries
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import pickle
import logging
from pathlib import Path

from src.core.config import settings
from src.services.chat import ChatService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def analyze_metadata_distribution():
    """Analyze data_type distribution in FAISS index."""
    index_path = Path("data/vector/document_chunks.pkl")

    with index_path.open("rb") as f:
        chunks = pickle.load(f)

    data_types = {}
    for chunk in chunks:
        # Handle both dict and object structures
        if isinstance(chunk, dict):
            metadata = chunk.get("metadata", {})
        else:
            metadata = getattr(chunk, "metadata", {})

        dt = metadata.get("data_type", "unknown") if isinstance(metadata, dict) else "unknown"
        data_types[dt] = data_types.get(dt, 0) + 1

    print("\n" + "=" * 60)
    print("  METADATA DISTRIBUTION IN FAISS INDEX")
    print("=" * 60)
    for dt, count in sorted(data_types.items()):
        pct = count / len(chunks) * 100
        print(f"  {dt:20s}: {count:3d} chunks ({pct:5.1f}%)")
    print(f"\n  Total: {len(chunks)} chunks")
    print("=" * 60 + "\n")

    return data_types


def test_simple_query(chat_service: ChatService, query: str):
    """Test a simple query with and without metadata filtering."""
    print(f"\n{'=' * 80}")
    print(f"  TESTING: {query}")
    print("=" * 80)

    # Get query embedding
    query_embedding = chat_service.embedding_service.embed_query(query)

    # Test WITHOUT metadata filters
    print("\n  WITHOUT metadata filters:")
    results_no_filter = chat_service.vector_store.search(
        query_embedding,
        k=5,
        metadata_filters=None
    )
    for i, (chunk, score) in enumerate(results_no_filter):
        dt = chunk.metadata.get("data_type", "unknown") if isinstance(chunk.metadata, dict) else "unknown"
        print(f"    {i+1}. [{dt}] Score={score*100:.1f}% - {chunk.text[:100]}...")

    # Test WITH metadata filters (as Phase 6 does)
    query_lower = query.lower()
    metadata_filters = {}
    if any(word in query_lower for word in ["player", "who", "lebron", "jokic", "curry"]):
        metadata_filters["data_type"] = "player_stats"
    elif any(word in query_lower for word in ["team", "lakers", "celtics", "warriors"]):
        metadata_filters["data_type"] = "team_stats"

    if metadata_filters:
        print(f"\n  WITH metadata filters: {metadata_filters}")
        results_with_filter = chat_service.vector_store.search(
            query_embedding,
            k=5,
            metadata_filters=metadata_filters
        )
        for i, (chunk, score) in enumerate(results_with_filter):
            dt = chunk.metadata.get("data_type", "unknown") if isinstance(chunk.metadata, dict) else "unknown"
            print(f"    {i+1}. [{dt}] Score={score*100:.1f}% - {chunk.text[:100]}...")

        print(f"\n  IMPACT: {'SAME' if len(results_with_filter) == 5 else f'{len(results_with_filter)}/5 chunks found'}")
    else:
        print("\n  No metadata filters would be applied")

    print("=" * 80)


def main():
    # Analyze metadata distribution
    data_types = analyze_metadata_distribution()

    # Initialize ChatService
    logger.info("Initializing ChatService...")
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    # Test problematic simple queries from Phase 6
    simple_queries = [
        "Which player has the best 3-point percentage over the last 5 games?",
        "What are LeBron James' average points, rebounds, and assists this season?",
        "Which team leads the league in rebounds per game?",
    ]

    for query in simple_queries:
        test_simple_query(chat_service, query)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
