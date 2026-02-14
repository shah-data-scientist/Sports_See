#!/usr/bin/env python3
"""
FILE: test_greeting_direct.py
STATUS: Active
RESPONSIBILITY: Test greeting handler directly to find error
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import asyncio
import sys
sys.path.insert(0, '.')

from src.models.chat import ChatRequest, ChatResponse
from src.api.routes.chat import chat as chat_handler

async def test_greeting():
    """Test greeting handler directly."""
    print("Testing greeting handler directly...\n")

    request = ChatRequest(query="hi")
    print(f"Request: {request}")

    try:
        response = await chat_handler(request)
        print(f"✓ Response successful")
        print(f"Type: {type(response)}")
        print(f"Answer: {response.answer[:100]}")
        print(f"Model: {response.model}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_greeting())
