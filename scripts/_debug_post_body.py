"""
FILE: _debug_post_body.py
STATUS: Experimental
RESPONSIBILITY: Debug post body extraction in Reddit chunker
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import io
import os
import pickle
import re
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

for ocr_file in sorted(ocr_dir.glob("Reddit*.pkl")):
    text = pickle.loads(ocr_file.read_bytes())

    # Apply ad filtering (same as pipeline)
    cleaned = chunker.filter_advertisements(text)

    print("=" * 70)
    print(f"{ocr_file.name} — First 1500 chars of CLEANED text")
    print("=" * 70)
    print(cleaned[:1500])
    print()

    # Show regex matches
    post_match = re.search(
        r"r/nba[^\n]*\n"
        r"([A-Za-z0-9_-]+)[^\n]*\n"
        r"([^\n]+)",
        cleaned,
        re.IGNORECASE,
    )
    stats_match = re.search(r"[↑]?(\d+)\s*\n(\d+)\s*\nPartager", cleaned)

    if post_match:
        print(f"  post_match: author={post_match.group(1)}, title={post_match.group(2)[:60]}")
        print(f"  post_match span: {post_match.start()}-{post_match.end()}")
    else:
        print("  post_match: NOT FOUND")

    if stats_match:
        print(f"  stats_match: upvotes={stats_match.group(1)}, comments={stats_match.group(2)}")
        print(f"  stats_match span: {stats_match.start()}-{stats_match.end()}")
    else:
        print("  stats_match: NOT FOUND")

    if post_match and stats_match:
        body_region = cleaned[post_match.end():stats_match.start()].strip()
        print(f"  body region ({len(body_region)} chars): {body_region[:300]}")
    elif post_match:
        print(f"  body: NO stats_match, can't determine body end")
        # Show what's after post_match
        after = cleaned[post_match.end():post_match.end()+300]
        print(f"  text after post_match: {after[:300]}")
    print()

    # Also check for "Partager" in text
    partager_pos = cleaned.find("Partager")
    if partager_pos >= 0:
        print(f"  First 'Partager' at position {partager_pos}")
        context = cleaned[max(0, partager_pos-80):partager_pos+20]
        print(f"  Context around Partager: ...{context}...")
    else:
        print(f"  'Partager' NOT found in cleaned text")
    print()
