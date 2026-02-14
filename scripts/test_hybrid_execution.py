"""
Test HYBRID query execution to see why SQL component isn't producing results.
"""
from src.services.chat import ChatService
from src.models.chat import ChatRequest
from src.core.config import settings
from src.repositories.nba_database import NBADatabase
from src.repositories.vector_store import VectorStoreRepository
from src.tools.sql_tool import NBAGSQLTool
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
db = NBADatabase(settings.database_path)
vector_store = VectorStoreRepository()
vector_store.load_index()
sql_tool = NBAGSQLTool(database=db)

# Initialize chat service
chat_service = ChatService(
    vector_store=vector_store,
    sql_tool=sql_tool,
)

# Test query
test_query = "What do authoritative voices say about playoff basketball?"

print(f"Testing query: {test_query}")
print("=" * 80)

# Step 1: Check classification
from src.services.query_classifier import QueryClassifier
classifier = QueryClassifier()
classification = classifier.classify(test_query)
print(f"\n1. CLASSIFICATION:")
print(f"   Query Type: {classification.query_type.value}")
print(f"   Is Biographical: {classification.is_biographical}")
print(f"   Complexity K: {classification.complexity_k}")

# Step 2: Test SQL tool directly
print(f"\n2. SQL TOOL TEST:")
sql_result = sql_tool.query(test_query)
print(f"   Generated SQL: {sql_result['sql']}")
print(f"   Error: {sql_result.get('error', 'None')}")
print(f"   Results Count: {len(sql_result['results']) if sql_result['results'] else 0}")
if sql_result['results']:
    print(f"   Sample Result: {sql_result['results'][0]}")

# Step 3: Full chat service call
print(f"\n3. FULL CHAT SERVICE:")
request = ChatRequest(query=test_query, k=5)
response = chat_service.chat(request)

print(f"   Query Type in Response: {response.query_type}")
print(f"   Sources: {len(response.sources)}")
print(f"   Answer Preview: {response.answer[:300]}...")
print(f"   Processing Time: {response.processing_time_ms}ms")

# Step 4: Check if answer contains statistical content
has_stats = any(keyword in response.answer.lower() for keyword in ['points', 'rebounds', 'assists', 'average', 'scored', 'stats'])
print(f"\n4. CONTENT ANALYSIS:")
print(f"   Contains Statistical Keywords: {has_stats}")
print(f"   Answer Length: {len(response.answer)} chars")

print("\n" + "=" * 80)
print("CONCLUSION:")
if response.query_type == "hybrid" and has_stats:
    print("✅ HYBRID query produced both SQL stats and vector context")
elif response.query_type == "hybrid" and not has_stats:
    print("⚠️ HYBRID routing but NO SQL stats in answer (SQL likely failed/empty)")
else:
    print(f"ℹ️ Query routed to {response.query_type} (not hybrid)")
