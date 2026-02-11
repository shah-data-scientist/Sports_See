"""
FILE: _check_chunk_metadata.py
STATUS: Experimental
RESPONSIBILITY: Check all metadata fields stored per Reddit chunk
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

chunks = pickle.loads(Path("data/vector/document_chunks.pkl").read_bytes())
reddit_chunks = [c for c in chunks if c.get("metadata", {}).get("type") == "reddit_thread"]
standard_chunks = [c for c in chunks if c.get("metadata", {}).get("type") != "reddit_thread"]

print("=" * 70)
print(f"Total: {len(chunks)} chunks ({len(reddit_chunks)} Reddit, {len(standard_chunks)} standard)")
print("=" * 70)

# Show all metadata keys from Reddit chunks
print("\nReddit chunk metadata keys (from chunk 0):")
if reddit_chunks:
    for k, v in sorted(reddit_chunks[0]["metadata"].items()):
        print(f"  {k}: {v}")

# Show a few chunks with different sources
print("\n" + "=" * 70)
print("Sample Reddit chunks (chunk 0 from each source):")
print("=" * 70)
seen = set()
for c in reddit_chunks:
    src = c["metadata"].get("source", "")
    if src not in seen and c["metadata"].get("chunk_index") == 0:
        seen.add(src)
        m = c["metadata"]
        print(f"\n  {src}:")
        for k, v in sorted(m.items()):
            print(f"    {k}: {v}")

# Check if individual comment metadata (author, upvotes) is in chunk text
print("\n" + "=" * 70)
print("Comment-level metadata in chunk text:")
print("=" * 70)
sample = reddit_chunks[0]["text"]
# Count [N] u/username (upvotes) patterns
import re
comment_entries = re.findall(r"\[(\d+)\] u/(\S+) \((\d+) upvotes\)", sample)
print(f"  Chunk 0 has {len(comment_entries)} comment entries with metadata")
for idx, author, upvotes in comment_entries[:5]:
    print(f"    [{idx}] u/{author} ({upvotes} upvotes)")

# Check chunk-level metadata for comment stats
print("\n" + "=" * 70)
print("All unique metadata keys across ALL Reddit chunks:")
print("=" * 70)
all_keys = set()
for c in reddit_chunks:
    all_keys.update(c["metadata"].keys())
for k in sorted(all_keys):
    # Show a sample value
    for c in reddit_chunks:
        if k in c["metadata"]:
            print(f"  {k}: {c['metadata'][k]} (example)")
            break
