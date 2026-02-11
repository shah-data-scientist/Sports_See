"""
FILE: _test_clean_chunking.py
STATUS: Experimental
RESPONSIBILITY: Test OCR cleaning + 1-comment-per-chunk on all 4 PDFs
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import io
import os
import pickle
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.reddit_chunker import RedditThreadChunker

chunker = RedditThreadChunker()
ocr_dir = Path("data/vector/_ocr_per_file")

total_chunks = 0
total_comments = 0

for ocr_file in sorted(ocr_dir.glob("Reddit*.pkl")):
    text = pickle.loads(ocr_file.read_bytes())
    source = ocr_file.stem.replace("Reddit ", "Reddit ") + ".pdf"

    # Measure cleaning effect
    ad_cleaned = chunker.filter_advertisements(text)
    noise_cleaned = chunker.clean_ocr_noise(ad_cleaned)
    lines_before = len(ad_cleaned.split("\n"))
    lines_after = len(noise_cleaned.split("\n"))
    removed = lines_before - lines_after

    print("=" * 70)
    print(f"{ocr_file.stem}")
    print("=" * 70)
    print(f"  Raw: {len(text)} chars, {len(text.split(chr(10)))} lines")
    print(f"  After ad filter: {len(ad_cleaned)} chars, {lines_before} lines")
    print(f"  After noise clean: {len(noise_cleaned)} chars, {lines_after} lines")
    print(f"  Lines removed by noise cleaner: {removed} ({removed/max(lines_before,1)*100:.1f}%)")

    # Test chunking
    chunks = chunker.chunk_reddit_thread(text, source)
    total_chunks += len(chunks)
    total_comments += len(chunks)  # 1 comment per chunk

    print(f"  Chunks created: {len(chunks)}")

    # Post info check
    if chunks:
        first = chunks[0]
        m = first.metadata
        print(f"  Post: {m.get('post_title', 'N/A')[:60]}")
        print(f"  Author: u/{m.get('post_author', 'N/A')}")
        print(f"  Post upvotes: {m.get('post_upvotes', 0)}")

        # Check body in first chunk
        has_body = "Post:" in first.text
        print(f"  Body in chunks: {'YES' if has_body else 'NO'}")

        # Show first chunk text
        print(f"\n  --- Chunk 0 (highest upvotes) ---")
        print(f"  Comment author: u/{m.get('comment_author', 'N/A')}")
        print(f"  Comment upvotes: {m.get('comment_upvotes', 0)}")
        print(f"  Text preview ({len(first.text)} chars):")
        for line in first.text.split("\n")[:10]:
            print(f"    {line}")
        print(f"    ...")

        # Show last chunk (lowest upvotes)
        last = chunks[-1]
        lm = last.metadata
        print(f"\n  --- Chunk {len(chunks)-1} (lowest upvotes) ---")
        print(f"  Comment author: u/{lm.get('comment_author', 'N/A')}")
        print(f"  Comment upvotes: {lm.get('comment_upvotes', 0)}")
    print()

print("=" * 70)
print(f"TOTAL: {total_chunks} chunks across 4 PDFs ({total_comments} comments)")
print("=" * 70)
