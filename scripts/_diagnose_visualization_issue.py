"""
FILE: _diagnose_visualization_issue.py
STATUS: Active - Temporary
RESPONSIBILITY: Comprehensive diagnosis of visualization serialization issue
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.chat import ChatRequest, ChatResponse, Visualization
from src.services.chat import ChatService

print("\n" + "=" * 100)
print("VISUALIZATION ISSUE DIAGNOSIS")
print("=" * 100)

# Test 1: Create hardcoded ChatResponse with visualization
print("\n[TEST 1] Hardcoded ChatResponse with Visualization")
print("-" * 100)

hardcoded_viz = Visualization(
    pattern="top_n",
    viz_type="horizontal_bar",
    plot_json='{"test": "data"}',
    plot_html="<div>test</div>"
)

hardcoded_response = ChatResponse(
    answer="Test answer",
    sources=[],
    query="test query",
    processing_time_ms=100.0,
    model="test-model",
    visualization=hardcoded_viz
)

print(f"Created ChatResponse with visualization: {hardcoded_response.visualization is not None}")
print(f"Visualization pattern: {hardcoded_response.visualization.pattern}")

# Serialize to dict
response_dict = hardcoded_response.model_dump()
print(f"\nmodel_dump() keys: {list(response_dict.keys())}")
print(f"'visualization' in dict: {'visualization' in response_dict}")
print(f"visualization value: {response_dict['visualization']}")

# Serialize to JSON
response_json = hardcoded_response.model_dump_json()
parsed = json.loads(response_json)
print(f"\nmodel_dump_json() parsed keys: {list(parsed.keys())}")
print(f"'visualization' in JSON: {'visualization' in parsed}")
print(f"JSON visualization value: {parsed.get('visualization')}")

# Test 2: Real ChatService
print("\n[TEST 2] Real ChatService.chat()")
print("-" * 100)

service = ChatService()
service.ensure_ready()

request = ChatRequest(query="Who are the top 5 scorers this season?", k=5)
real_response = service.chat(request)

print(f"ChatService returned response: {real_response is not None}")
print(f"Response has visualization: {real_response.visualization is not None}")
if real_response.visualization:
    print(f"Visualization pattern: {real_response.visualization.pattern}")
    print(f"Visualization type: {real_response.visualization.viz_type}")

# Serialize to dict
real_dict = real_response.model_dump()
print(f"\nmodel_dump() keys: {list(real_dict.keys())}")
print(f"'visualization' in dict: {'visualization' in real_dict}")
if 'visualization' in real_dict:
    print(f"visualization value type: {type(real_dict['visualization'])}")
    print(f"visualization is None: {real_dict['visualization'] is None}")

# Serialize to JSON
real_json = real_response.model_dump_json()
real_parsed = json.loads(real_json)
print(f"\nmodel_dump_json() parsed keys: {list(real_parsed.keys())}")
print(f"'visualization' in JSON: {'visualization' in real_parsed}")
if 'visualization' in real_parsed:
    print(f"JSON visualization value is None: {real_parsed['visualization'] is None}")

print("\n" + "=" * 100)
print("DIAGNOSIS COMPLETE")
print("=" * 100)
