"""
FILE: _test_chat_service_viz.py
STATUS: Active - Temporary
RESPONSIBILITY: Test ChatService visualization generation with debug output
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

from src.models.chat import ChatRequest
from src.services.chat import ChatService

print("\n" + "=" * 80)
print("TESTING CHATSERVICE VISUALIZATION GENERATION")
print("=" * 80)

# Initialize ChatService
service = ChatService()
service.ensure_ready()

# Test query
query = "Who are the top 5 scorers this season?"
request = ChatRequest(query=query, k=5, include_sources=False)

print(f"\nQuery: {query}")
print(f"Request: {request}")

# Process query
response = service.chat(request)

print(f"\n" + "-" * 80)
print("RESPONSE:")
print(f"  Answer: {response.answer[:100]}...")
print(f"  Model: {response.model}")
print(f"  Processing time: {response.processing_time_ms:.1f}ms")
print(f"  Generated SQL: {response.generated_sql}")
print(f"  Visualization: {response.visualization}")

if response.visualization:
    print(f"\n  ✓ Visualization generated!")
    print(f"    Pattern: {response.visualization.pattern}")
    print(f"    Type: {response.visualization.viz_type}")
    print(f"    JSON length: {len(response.visualization.plot_json)}")
    print(f"    HTML length: {len(response.visualization.plot_html)}")
else:
    print(f"\n  ✗ NO VISUALIZATION GENERATED")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
