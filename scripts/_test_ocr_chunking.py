"""
FILE: _test_ocr_chunking.py
STATUS: Active
RESPONSIBILITY: Quick test of Reddit chunking on actual OCR cache files
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import os
import pickle
import sys
from pathlib import Path

# Prevent FAISS/OpenMP crash
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

# UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.pipeline.reddit_chunker import RedditThreadChunker

chunker = RedditThreadChunker(max_comments_per_chunk=5)
ocr_dir = Path("data/vector/_ocr_per_file")

total_comments = 0
total_chunks = 0

for f in sorted(ocr_dir.glob("*.pkl")):
    text = pickle.loads(f.read_bytes())
    chunks = chunker.chunk_reddit_thread(text, f.stem)

    n_comments = chunks[0].metadata.get("num_comments", 0) if chunks else 0
    total_comments += n_comments
    total_chunks += len(chunks)

    print(f"\n{f.name}: {n_comments} comments -> {len(chunks)} chunks", flush=True)

    # Show top comment per chunk
    for i, c in enumerate(chunks):
        meta = c.metadata
        print(
            f"  Chunk {i}: {meta.get('comments_in_chunk', 0)} comments, "
            f"avg_upvotes={meta.get('avg_comment_upvotes', 0)}, "
            f"max_upvotes={meta.get('max_comment_upvotes', 0)}, "
            f"nba_official={meta.get('has_nba_official', 0)}",
            flush=True,
        )
        # Show first 100 chars of chunk text
        print(f"    Preview: {c.text[:120]}...", flush=True)

print(f"\n{'='*60}", flush=True)
print(f"TOTAL: {total_comments} comments across 4 PDFs -> {total_chunks} chunks", flush=True)
print(f"{'='*60}", flush=True)

if total_chunks > 4:
    print("PASS: More chunks than source PDFs (paged chunking works)", flush=True)
else:
    print("FAIL: Expected more than 4 chunks from paged chunking", flush=True)
