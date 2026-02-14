#!/usr/bin/env python3
"""
FILE: trace_greeting_api.py
STATUS: Active
RESPONSIBILITY: Trace greeting 500 error using FastAPI TestClient with proper lifespan
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import traceback
import sys

print("=" * 80)
print("TRACE: Greeting 500 Error via FastAPI TestClient (with lifespan)")
print("=" * 80)

# Step 1: Import TestClient and app
print("\n[1] Importing...")
try:
    from fastapi.testclient import TestClient
    from src.api.main import app
    print("    OK: TestClient and app imported")
except Exception as e:
    print(f"    FAIL: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 2: Use TestClient as context manager (triggers lifespan → initializes service)
print("\n[2] Creating TestClient with lifespan context...")
with TestClient(app, raise_server_exceptions=False) as client:
    print("    OK: TestClient created, lifespan triggered")

    # Step 3: Send greeting request
    print("\n[3] POST /api/v1/chat {query: 'hi'}")
    print("-" * 80)
    try:
        response = client.post("/api/v1/chat", json={"query": "hi"})
        print(f"    Status: {response.status_code}")
        print(f"    Body: {response.text[:1000]}")
    except Exception as e:
        print(f"    EXCEPTION: {type(e).__name__}: {e}")
        traceback.print_exc()

    # Step 4: Try with raise_server_exceptions to get actual traceback
    print("\n[4] POST /api/v1/chat {query: 'hi'} (raise_server_exceptions=True)")
    print("-" * 80)

# Need a new client for raise_server_exceptions=True
with TestClient(app, raise_server_exceptions=True) as client2:
    try:
        response2 = client2.post("/api/v1/chat", json={"query": "hi"})
        print(f"    Status: {response2.status_code}")
        print(f"    Body: {response2.text[:1000]}")
    except Exception as e:
        print(f"    EXCEPTION CAUGHT: {type(e).__name__}: {e}")
        traceback.print_exc()

    # Step 5: Compare with working query
    print("\n[5] POST /api/v1/chat {query: 'hello'}")
    print("-" * 80)
    try:
        response3 = client2.post("/api/v1/chat", json={"query": "hello"})
        print(f"    Status: {response3.status_code}")
        print(f"    Body: {response3.text[:1000]}")
    except Exception as e:
        print(f"    EXCEPTION: {type(e).__name__}: {e}")
        traceback.print_exc()

    # Step 6: Test a statistical query for comparison
    print("\n[6] POST /api/v1/chat {query: 'top 5 scorers'}")
    print("-" * 80)
    try:
        response4 = client2.post("/api/v1/chat", json={"query": "top 5 scorers"})
        print(f"    Status: {response4.status_code}")
        print(f"    Body: {response4.text[:500]}")
    except Exception as e:
        print(f"    EXCEPTION: {type(e).__name__}: {e}")
        traceback.print_exc()

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
