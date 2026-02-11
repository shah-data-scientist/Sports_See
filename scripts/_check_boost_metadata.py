"""
FILE: _check_boost_metadata.py
STATUS: Experimental
RESPONSIBILITY: Verify new boost metadata fields in chunks
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import pickle
from pathlib import Path

chunks = pickle.loads(Path("data/vector/document_chunks.pkl").read_bytes())
reddit_chunks = [c for c in chunks if c.get("metadata", {}).get("type") == "reddit_thread"]

print(f"Total chunks: {len(chunks)} (Reddit: {len(reddit_chunks)})")
print()

# Show first chunk from each post
seen_posts = set()
for c in reddit_chunks:
    m = c["metadata"]
    post_title = m.get("post_title", "")

    if post_title not in seen_posts and m.get("chunk_index") == 0:
        seen_posts.add(post_title)
        print("=" * 70)
        print(f"{m['source']} (Post upvotes: {m['post_upvotes']})")
        print("=" * 70)
        print(f"Title: {post_title[:60]}...")
        print(f"First comment: u/{m['comment_author']} ({m['comment_upvotes']} upvotes)")
        print()
        print("Boost metadata:")
        print(f"  min_comment_upvotes_in_post: {m.get('min_comment_upvotes_in_post', 'MISSING')}")
        print(f"  max_comment_upvotes_in_post: {m.get('max_comment_upvotes_in_post', 'MISSING')}")
        print(f"  min_post_upvotes_global: {m.get('min_post_upvotes_global', 'MISSING')}")
        print(f"  max_post_upvotes_global: {m.get('max_post_upvotes_global', 'MISSING')}")
        print()

# Verify all Reddit chunks have the new fields
missing_within_post = 0
missing_global = 0

for c in reddit_chunks:
    m = c["metadata"]
    if "min_comment_upvotes_in_post" not in m or "max_comment_upvotes_in_post" not in m:
        missing_within_post += 1
    if "min_post_upvotes_global" not in m or "max_post_upvotes_global" not in m:
        missing_global += 1

print("=" * 70)
print("VERIFICATION")
print("=" * 70)
if missing_within_post == 0:
    print(f"✅ All {len(reddit_chunks)} Reddit chunks have within-post min/max")
else:
    print(f"❌ {missing_within_post} chunks missing within-post min/max")

if missing_global == 0:
    print(f"✅ All {len(reddit_chunks)} Reddit chunks have global post min/max")
else:
    print(f"❌ {missing_global} chunks missing global post min/max")
