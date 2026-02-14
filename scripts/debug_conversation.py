"""Debug conversation response."""
import requests
import json

API = "http://localhost:8000/api/v1"

# Create conversation
conv = requests.post(f"{API}/conversations", json={}).json()
conv_id = conv["id"]
print(f"Conversation ID: {conv_id}\n")

# Query 1
r1 = requests.post(f"{API}/chat", json={
    "query": "Show me stats for the Warriors",
    "conversation_id": conv_id,
    "turn_number": 1,
    "k": 5,
    "include_sources": True
})

print(f"Status Code: {r1.status_code}")
print(f"\nFull Response:")
print(json.dumps(r1.json(), indent=2))
