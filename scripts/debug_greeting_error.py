#!/usr/bin/env python3
"""
FILE: debug_greeting_error.py
STATUS: Active
RESPONSIBILITY: Debug greeting 500 error
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

print("="*80)
print("DEBUGGING GREETING 500 ERROR")
print("="*80 + "\n")

test_queries = [
    ("hi", "Simple greeting"),
    ("hello", "Greeting with 'hello'"),
    ("top 5 scorers", "Statistical (for comparison)"),
]

for query, test_name in test_queries:
    print(f"\n[TEST] {test_name}: '{query}'")
    print("-" * 80)

    try:
        payload = {"query": query}
        print(f"Sending payload: {json.dumps(payload)}")

        response = requests.post(
            f"{API_URL}/api/v1/chat",
            json=payload,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")

        try:
            resp_json = response.json()
            print(json.dumps(resp_json, indent=2))
        except:
            print(response.text[:500])

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")

print("\n" + "="*80)
