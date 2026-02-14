"""
Quick UI test - Run this to see what happens when Streamlit processes a query
"""
import sys
import time
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.models.chat import ChatRequest
from src.services.chat import ChatService
from src.services.feedback import FeedbackService

print("\n" + "="*60)
print("TESTING: What Streamlit UI does for 'high in the chart'")
print("="*60)

# Initialize service (exactly like Streamlit does)
print("\n1. Initializing ChatService...")
service = ChatService()
service.ensure_ready()
print(f"   ✓ Ready with {service.vector_store.index_size} vectors")

# Create request (exactly like Streamlit does)
print("\n2. Creating ChatRequest for 'high in the chart'...")
request = ChatRequest(
    query="high in the chart",
    k=settings.search_k,
    include_sources=True,
    conversation_id=None,
    turn_number=1,
)
print(f"   ✓ Request created")

# Call service (exactly like Streamlit does at line 377)
print("\n3. Calling service.chat()...")
start = time.time()
try:
    response = service.chat(request)
    elapsed = time.time() - start
    print(f"   ✓ Got response in {elapsed:.2f}s")
    
    # Check response structure (exactly like Streamlit does)
    print("\n4. Checking response structure...")
    print(f"   • answer: {len(response.answer)} chars")
    print(f"   • sources: {len(response.sources)}")
    print(f"   • chat_type: {response.chat_type}")
    print(f"   • processing_time_ms: {response.processing_time_ms}")
    
    # What Streamlit does with response
    print("\n5. What Streamlit does with the response...")
    print(f"   st.write(response.answer) would display:")
    print(f"   ---")
    print(response.answer)
    print(f"   ---")
    
    # Check sources display
    if response.sources:
        print(f"\n6. Sources display...")
        for i, source in enumerate(response.sources[:2], 1):
            print(f"   Source {i}: {source.source} (Score: {source.score:.1f}%)")
    
    print("\n✅ UI should display the above successfully")
    
except TimeoutError as e:
    elapsed = time.time() - start
    print(f"   ❌ TIMEOUT after {elapsed:.2f}s: {e}")
except Exception as e:
    elapsed = time.time() - start
    print(f"   ❌ ERROR after {elapsed:.2f}s: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
