#!/usr/bin/env python3
"""Trace the exact greeting execution path."""
import sys, os, traceback
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

print('1: Imports starting'); sys.stdout.flush()
from src.models.chat import ChatRequest, ChatResponse
print('2: Models imported'); sys.stdout.flush()
from src.core.security import sanitize_query
print('3: Security imported'); sys.stdout.flush()
from src.services.query_classifier import QueryClassifier
print('4: QueryClassifier imported'); sys.stdout.flush()

qc = QueryClassifier()
print('5: QC created'); sys.stdout.flush()

# Test greeting detection
result = qc._is_greeting('hi')
print(f'6: is_greeting(hi) = {result}'); sys.stdout.flush()

# Test sanitize
query = sanitize_query('hi')
print(f'7: sanitize(hi) = "{query}"'); sys.stdout.flush()

# Test ChatResponse
try:
    resp = ChatResponse(
        answer='Hi there!',
        query=query,
        sources=[],
        processing_time_ms=10,
        model='test-model',
        conversation_id=None,
        turn_number=1
    )
    print(f'8: ChatResponse created OK, answer={resp.answer}'); sys.stdout.flush()
except Exception as e:
    print(f'8: FAIL: {type(e).__name__}: {e}'); sys.stdout.flush()
    traceback.print_exc()

print('9: All steps passed!'); sys.stdout.flush()
