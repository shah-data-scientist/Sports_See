"""
FILE: rebuild_vector_index.py
STATUS: Active
RESPONSIBILITY: Rebuild FAISS vector index with Reddit-aware chunking
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import DataPipeline
from src.pipeline.models import LoadStageInput

def main():
    """Rebuild vector index with Reddit chunking."""

    print("=" * 80, file=sys.stdout, flush=True)
    print("REBUILDING VECTOR INDEX WITH REDDIT CHUNKING", file=sys.stdout, flush=True)
    print("=" * 80, file=sys.stdout, flush=True)
    print(flush=True)

    # Initialize pipeline
    pipeline = DataPipeline()

    # [1/4] Load documents
    print("[1/4] Loading documents from inputs/...", file=sys.stdout, flush=True)
    load_input = LoadStageInput(input_dir="inputs")
    load_output = pipeline.load(load_input)
    print(f"Loaded {len(load_output.documents)} documents", file=sys.stdout, flush=True)
    print(flush=True)

    # [2/4] Clean documents
    print("[2/4] Cleaning documents...", file=sys.stdout, flush=True)
    clean_output = pipeline.clean(load_output.documents)
    print(f"Cleaned {len(clean_output.documents)} documents", file=sys.stdout, flush=True)
    print(flush=True)

    # [3/4] Chunk documents (with Reddit-aware chunking)
    print("[3/4] Chunking documents (Reddit-aware)...", file=sys.stdout, flush=True)
    chunk_output = pipeline.chunk(clean_output.documents)
    print(f"Created {len(chunk_output.chunks)} chunks", file=sys.stdout, flush=True)

    # Show Reddit chunk statistics
    reddit_chunks = [c for c in chunk_output.chunks if c.metadata.get("type") == "reddit_thread"]
    standard_chunks = [c for c in chunk_output.chunks if c.metadata.get("type") != "reddit_thread"]
    print(f"  - Reddit chunks: {len(reddit_chunks)}", file=sys.stdout, flush=True)
    print(f"  - Standard chunks: {len(standard_chunks)}", file=sys.stdout, flush=True)
    print(flush=True)

    # [4/4] Embed and index
    print("[4/4] Generating embeddings and building FAISS index...", file=sys.stdout, flush=True)

    # Extract chunk texts for embedding
    chunk_texts = [chunk.text for chunk in chunk_output.chunks]
    embed_output, embeddings = pipeline.embed(chunk_texts)

    # Build and save index
    pipeline._vector_store.build_index(chunk_output.chunks, embeddings)
    pipeline._vector_store.save()

    print(f"FAISS index created with {len(chunk_output.chunks)} vectors", file=sys.stdout, flush=True)
    print(flush=True)

    print("=" * 80, file=sys.stdout, flush=True)
    print("SUCCESS - Vector index rebuilt!", file=sys.stdout, flush=True)
    print("=" * 80, file=sys.stdout, flush=True)
    print(f"Total documents: {len(load_output.documents)}", file=sys.stdout, flush=True)
    print(f"Total chunks: {len(chunk_output.chunks)}", file=sys.stdout, flush=True)
    print(f"Reddit threads: {len(reddit_chunks)}", file=sys.stdout, flush=True)
    print(f"Index location: vector_db/", file=sys.stdout, flush=True)

if __name__ == "__main__":
    # Force UTF-8 encoding for stdout
    if sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    main()
