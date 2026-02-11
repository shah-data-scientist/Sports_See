"""
FILE: _test_post_extraction.py
STATUS: Experimental
RESPONSIBILITY: Test fixed extract_post_info against all 4 Reddit PDFs
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

print("=" * 70)
print("Testing FIXED extract_post_info() on all Reddit PDFs")
print("=" * 70)

for ocr_file in sorted(ocr_dir.glob("Reddit*.pkl")):
    text = pickle.loads(ocr_file.read_bytes())
    # Apply ad filtering first (same as pipeline)
    cleaned = chunker.filter_advertisements(text)
    post_info = chunker.extract_post_info(cleaned)

    print(f"\n--- {ocr_file.name} ---")
    print(f"  title: {post_info['title'][:80]}")
    print(f"  author: {post_info['author']}")
    print(f"  upvotes: {post_info['upvotes']}")
    print(f"  num_comments: {post_info['num_comments']}")
    body = post_info.get("body", "")
    if body:
        print(f"  body ({len(body)} chars): {body[:300]}...")
    else:
        print(f"  body: EMPTY")

    # Also show what _build_post_context would produce
    context = chunker._build_post_context(post_info)
    print(f"\n  Post context block:\n  {context.replace(chr(10), chr(10) + '  ')}")

print("\n" + "=" * 70)
print("Test complete")
print("=" * 70)
