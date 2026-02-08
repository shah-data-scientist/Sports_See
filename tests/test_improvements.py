"""
FILE: test_improvements.py
STATUS: Active
RESPONSIBILITY: Test SQL formatting and prompt improvements
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""
import logging
from src.models.chat import ChatRequest
from src.services.chat import ChatService

# Enable logging to see routing decisions
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Initialize service
chat_service = ChatService(enable_sql=True)
chat_service.ensure_ready()

# Test problematic queries
test_queries = [
    "Who's the best rebounder?",  # Previously classified as CONTEXTUAL
    "How many players scored over 1000 points?",  # Previously "cannot find"
    "Who has the best free throw percentage?",  # Previously "cannot find"
    "Who are the top 3 rebounders in the league?",  # Should work well (baseline)
]

print("=" * 80)
print("TESTING SQL FORMATTING IMPROVEMENTS")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n[{i}/{len(test_queries)}] Query: '{query}'")
    print("-" * 80)

    try:
        request = ChatRequest(query=query, k=5, include_sources=False)
        response = chat_service.chat(request)

        print(f"Answer: {response.answer[:200]}...")
        print(f"Processing time: {response.processing_time_ms:.0f}ms")

        # Check if "cannot find" in response
        if "cannot find" in response.answer.lower():
            print("[WARNING] Still says 'cannot find'")
        else:
            print("[OK] Provided an answer")

    except Exception as e:
        print(f"[ERROR] {e}")

print("\n" + "=" * 80)
