"""
FILE: analyze_vector_store_current.py
STATUS: Active
RESPONSIBILITY: Analyze current vector store contents by source
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Check what's currently in the vector store and from which sheets.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from repositories.vector_store import VectorStoreRepository

def analyze_current_vector_store():
    """Analyze what's currently vectorized."""
    print("Analyzing current vector store...")
    print("=" * 80)

    repo = VectorStoreRepository()
    loaded = repo.load()

    if not loaded:
        print("No vector store found or could not be loaded.")
        return

    chunks = repo.chunks

    if not chunks:
        print("Vector store is empty.")
        return

    # Count by source
    sources = {}
    sheet_sources = {}

    for chunk in chunks:
        source = chunk.metadata.get('source', 'unknown')
        sheet = chunk.metadata.get('sheet', None)

        sources[source] = sources.get(source, 0) + 1

        if sheet:
            key = f"{source} -> {sheet}"
            sheet_sources[key] = sheet_sources.get(key, 0) + 1

    print(f"\nTotal chunks: {len(chunks)}")

    print(f"\n\nBy source file:")
    print("-" * 80)
    for source, count in sorted(sources.items()):
        print(f"  {source}: {count} chunks")

    if sheet_sources:
        print(f"\n\nBy sheet:")
        print("-" * 80)
        for sheet_key, count in sorted(sheet_sources.items()):
            print(f"  {sheet_key}: {count} chunks")

    # Sample some chunks
    print(f"\n\nSample chunks from each Excel sheet:")
    print("=" * 80)

    seen_sheets = set()
    for chunk in chunks:
        sheet = chunk.metadata.get('sheet', None)
        if sheet and sheet not in seen_sheets:
            seen_sheets.add(sheet)
            print(f"\nSheet: {sheet}")
            print(f"Source: {chunk.metadata.get('source', 'unknown')}")
            print(f"Content preview (first 500 chars):")
            print("-" * 80)
            print(chunk.text[:500])
            print("-" * 80)

if __name__ == "__main__":
    analyze_current_vector_store()
