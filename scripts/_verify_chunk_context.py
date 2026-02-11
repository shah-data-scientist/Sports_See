"""
FILE: _verify_chunk_context.py
STATUS: Active
RESPONSIBILITY: Verify Reddit chunks contain post context in every chunk
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

print(f"Total chunks: {len(chunks)} (Reddit: {len(reddit_chunks)}, Standard: {len(chunks) - len(reddit_chunks)})")
print()

# Show chunk 0 and chunk 3 from Reddit 1 to prove post context is in EVERY chunk
for target_idx in [0, 3, 13]:
    for c in reddit_chunks:
        if c["metadata"].get("source") == "Reddit 1.pdf" and c["metadata"].get("chunk_index") == target_idx:
            total = c["metadata"]["total_chunks"]
            print(f"{'='*70}", flush=True)
            print(f"Reddit 1.pdf - Chunk {target_idx}/{total}", flush=True)
            print(f"{'='*70}", flush=True)
            print(c["text"][:600], flush=True)
            print(f"... [{len(c['text'])} total chars]", flush=True)
            print(flush=True)
            break

# Verify ALL Reddit chunks have post context
missing = 0
for c in reddit_chunks:
    if "=== REDDIT POST ===" not in c["text"]:
        missing += 1
        print(f"MISSING post context: {c['metadata']['source']} chunk {c['metadata']['chunk_index']}")

if missing == 0:
    print(f"VERIFIED: All {len(reddit_chunks)} Reddit chunks contain post context header", flush=True)
else:
    print(f"FAIL: {missing} chunks missing post context", flush=True)
