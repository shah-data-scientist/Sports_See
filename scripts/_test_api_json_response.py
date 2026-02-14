"""
FILE: _test_api_json_response.py
STATUS: Active - Temporary
RESPONSIBILITY: Test API JSON response structure
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import json
import requests

API_URL = "http://localhost:8000/api/v1/chat"

print("\n" + "=" * 80)
print("TESTING API JSON RESPONSE")
print("=" * 80)

# Make request
payload = {"query": "Who are the top 5 scorers this season?", "k": 5}
print(f"\nSending request: {payload}")

response = requests.post(API_URL, json=payload)

print(f"\nStatus Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")

# Parse JSON
data = response.json()

# Pretty print the response
print("\nJSON Response:")
print(json.dumps(data, indent=2))

# Check for visualization
if "visualization" in data:
    print("\n✓ Visualization field present!")
    if data["visualization"]:
        print(f"  Pattern: {data['visualization']['pattern']}")
        print(f"  Type: {data['visualization']['viz_type']}")
    else:
        print("  But value is null/None")
else:
    print("\n✗ Visualization field MISSING from JSON response")

print("\n" + "=" * 80)
print(f"Total fields in response: {len(data)}")
print(f"Fields: {list(data.keys())}")
print("=" * 80)
