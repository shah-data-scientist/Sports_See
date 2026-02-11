"""
FILE: _check_post_body.py
STATUS: Experimental
RESPONSIBILITY: Check if post body is extracted and included in Reddit chunks
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

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 1) Check what extract_post_info returns for each PDF
from src.pipeline.reddit_chunker import RedditThreadChunker

chunker = RedditThreadChunker()
ocr_dir = Path("data/vector/_ocr_per_file")

print("=" * 70)
print("PART 1: extract_post_info() output for each Reddit PDF")
print("=" * 70)

for ocr_file in sorted(ocr_dir.glob("Reddit*.pkl")):
    text = pickle.loads(ocr_file.read_bytes())
    post_info = chunker.extract_post_info(text)
    print(f"\n--- {ocr_file.name} ---")
    print(f"  title: {post_info.get('title', 'N/A')[:80]}")
    print(f"  author: {post_info.get('author', 'N/A')}")
    print(f"  upvotes: {post_info.get('upvotes', 'N/A')}")
    print(f"  num_comments: {post_info.get('num_comments', 'N/A')}")
    body = post_info.get("body", "")
    if body:
        print(f"  body ({len(body)} chars): {body[:200]}...")
    else:
        print(f"  body: EMPTY (not extracted)")

# 2) Check actual chunk content - first chunk of each Reddit PDF
print("\n" + "=" * 70)
print("PART 2: First 400 chars of chunk 0 from each Reddit PDF")
print("=" * 70)

chunks = pickle.loads(Path("data/vector/document_chunks.pkl").read_bytes())
reddit_chunks = [c for c in chunks if c.get("metadata", {}).get("type") == "reddit_thread"]

seen_sources = set()
for c in reddit_chunks:
    src = c["metadata"].get("source", "")
    if src not in seen_sources and c["metadata"].get("chunk_index") == 0:
        seen_sources.add(src)
        print(f"\n--- {src} (chunk 0) ---")
        print(c["text"][:400])
        print(f"... [{len(c['text'])} total chars]")

# 3) Check if "Post:" line exists in chunks (indicates body was included)
print("\n" + "=" * 70)
print("PART 3: Does 'Post:' line exist in chunks?")
print("=" * 70)

with_body = 0
without_body = 0
for c in reddit_chunks:
    if "Post:" in c["text"]:
        with_body += 1
    else:
        without_body += 1

print(f"  Chunks WITH 'Post:' line: {with_body}/{len(reddit_chunks)}")
print(f"  Chunks WITHOUT 'Post:' line: {without_body}/{len(reddit_chunks)}")
