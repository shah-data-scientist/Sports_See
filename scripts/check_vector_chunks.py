"""Quick script to analyze vector store chunks."""
import pickle
from pathlib import Path
import json

chunks_path = Path("data/vector/document_chunks.pkl")
chunks = pickle.load(open(chunks_path, 'rb'))

print(f"Total chunks: {len(chunks)}\n")

# Show first chunk structure
print("="*80)
print("FIRST CHUNK STRUCTURE")
print("="*80)
if chunks:
    first = chunks[0]
    print(f"Type: {type(first)}")
    if isinstance(first, dict):
        print(f"Keys: {list(first.keys())}")
        print(json.dumps(first, indent=2, default=str)[:1000])
    else:
        print(f"Value: {str(first)[:500]}")

# Count by source field (try different field names)
print("\n" + "="*80)
print("SOURCE FIELD ANALYSIS")
print("="*80)
sources = {}
for c in chunks:
    if isinstance(c, dict):
        # Try different field names
        src = c.get('source') or c.get('metadata', {}).get('source') or c.get('file_path') or 'unknown'
        sources[src] = sources.get(src, 0) + 1

print("Chunk distribution by source:")
for k, v in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {k}: {v}")
