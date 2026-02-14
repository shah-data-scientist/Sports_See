#!/usr/bin/env python3
"""Trace the exact ChatService greeting execution path."""
import sys, os, traceback
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

print('1: Starting'); sys.stdout.flush()
from src.services.chat import ChatService
print('2: ChatService imported'); sys.stdout.flush()
from src.models.chat import ChatRequest
print('3: ChatRequest imported'); sys.stdout.flush()

try:
    service = ChatService()
    print(f'4: Service created, model={service.model}'); sys.stdout.flush()
except Exception as e:
    print(f'4: FAIL creating service: {type(e).__name__}: {e}'); sys.stdout.flush()
    traceback.print_exc()
    sys.exit(1)

try:
    service.ensure_ready()
    print('5: ensure_ready OK'); sys.stdout.flush()
except Exception as e:
    print(f'5: ensure_ready warning: {type(e).__name__}: {e}'); sys.stdout.flush()

print('6: Calling service.chat(hi)...'); sys.stdout.flush()
request = ChatRequest(query='hi')
try:
    response = service.chat(request)
    print(f'7: SUCCESS! answer="{response.answer}"'); sys.stdout.flush()
    print(f'   model={response.model}'); sys.stdout.flush()
    print(f'   sources={len(response.sources)}'); sys.stdout.flush()
except Exception as e:
    print(f'7: FAIL: {type(e).__name__}: {e}'); sys.stdout.flush()
    traceback.print_exc()
    sys.stdout.flush()
