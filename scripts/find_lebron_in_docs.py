"""Find all LeBron mentions in the vector store document chunks."""
import pickle
import pathlib

chunks = pickle.loads(pathlib.Path("data/vector/document_chunks.pkl").read_bytes())
print(f"Total chunks: {len(chunks)}")

lebron = []
for i, c in enumerate(chunks):
    t = c.get("text", "") if isinstance(c, dict) else str(c)
    low = t.lower()
    if "lebron" in low or "lbj" in low:
        lebron.append((i, t, c.get("metadata", {}) if isinstance(c, dict) else {}))

print(f"LeBron mentions: {len(lebron)}\n")

for idx, (i, t, meta) in enumerate(lebron):
    src = meta.get("source", "unknown") if meta else "unknown"
    print(f"=== Chunk {i} (source: {src}) ===")
    print(t[:600])
    print()
