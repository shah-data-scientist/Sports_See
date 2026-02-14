"""Read ALL LeBron mentions from the OCR'd document chunks (full text)."""
import pickle
import pathlib

chunks = pickle.loads(pathlib.Path("data/vector/document_chunks.pkl").read_bytes())

# Also search for "Bron" (nickname) and "James" (last name in context)
lebron = []
for i, c in enumerate(chunks):
    t = c.get("text", "") if isinstance(c, dict) else str(c)
    low = t.lower()
    if "lebron" in low or "lbj" in low:
        src = c.get("metadata", {}).get("source", "?") if isinstance(c, dict) else "?"
        lebron.append((i, t, src))

print(f"Total document chunks: {len(chunks)}")
print(f"Chunks mentioning LeBron: {len(lebron)}")
print()

for idx, (i, text, src) in enumerate(lebron):
    print(f"{'='*70}")
    print(f"CHUNK {i} | Source: {src}")
    print(f"{'='*70}")
    print(text)
    print()
