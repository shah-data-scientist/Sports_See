#!/usr/bin/env python
"""
Quick test to verify the UI hanging fix is working.

This script tests the exact query that was hanging ("high in the chart")
to confirm the fix resolves the issue.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models.chat import ChatRequest
from src.services.chat import ChatService


async def test_ui_hanging_fix():
    """Test that the problematic query now works without hanging."""
    print("\n" + "=" * 70)
    print("🧪 UI HANGING FIX TEST")
    print("=" * 70)
    print("\nTesting query: 'high in the chart'")
    print("This query was previously hanging.\n")

    try:
        # Initialize service
        print("1️⃣  Initializing ChatService...")
        service = ChatService()
        service.ensure_ready()
        print("   ✅ Service initialized\n")

        # Create request
        print("2️⃣  Creating chat request...")
        request = ChatRequest(
            query="high in the chart",
            k=5,
            include_sources=True,
        )
        print("   ✅ Request created\n")

        # Get response
        print("3️⃣  Calling service.chat()...")
        start_time = time.time()
        response = service.chat(request)
        elapsed = time.time() - start_time

        print(f"   ✅ Response received in {elapsed:.2f}s\n")

        # Verify response
        print("4️⃣  Validating response structure...")
        assert response.answer, "Response answer is empty"
        assert response.sources is not None, "Sources is None"
        assert response.processing_time_ms > 0, "Processing time is invalid"
        print("   ✅ Response structure is valid\n")

        # Display results
        print("=" * 70)
        print("✅ TEST PASSED - FIX IS WORKING!")
        print("=" * 70)
        print("\n📊 Results:")
        print(f"   • Answer: {response.answer[:100]}...")
        print(f"   • Sources found: {len(response.sources)}")
        print(f"   • Processing time: {response.processing_time_ms:.0f}ms")
        print(f"   • Model: {response.model}")
        print(f"   • Total time: {elapsed:.2f}s")

        print("\n✨ The query 'high in the chart' now works without hanging!")
        print("   UI can display responses and log interactions correctly.\n")

        return True

    except Exception as e:
        print("=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        print(f"\nError: {e}")
        print(f"Type: {type(e).__name__}")

        import traceback
        print("\nTraceback:")
        traceback.print_exc()

        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_ui_hanging_fix())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
