import pickle
import os

def check_vector_db_detailed(vector_db_path):
    chunks_path = os.path.join(vector_db_path, "document_chunks.pkl")
    if not os.path.exists(chunks_path):
        print("Chunks file not found.")
        return

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    
    print(f"Total Chunks in DB: {len(chunks)}")
    print("-" * 40)
    for i, chunk in enumerate(chunks):
        # Handle dict or object
        metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else getattr(chunk, "metadata", {})
        text = chunk.get("text", "") if isinstance(chunk, dict) else getattr(chunk, "text", "")
        
        source = metadata.get("source", "Unknown")
        char_count = len(text)
        chunk_type = metadata.get("type", "standard")
        print(f"Chunk {i}: Source={source} | Type={chunk_type} | Chars={char_count}")

check_vector_db_detailed("data/vector")