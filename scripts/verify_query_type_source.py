"""
Verify that query_type in API response comes from QueryClassifier.
Tests multiple queries to confirm direct mapping.
"""
import requests
from src.services.query_classifier import QueryClassifier

# Initialize classifier
classifier = QueryClassifier()

# Test queries covering all types
test_queries = [
    "Who are the top 5 scorers?",                                    # STATISTICAL
    "Explain the pick and roll strategy",                            # CONTEXTUAL
    "What do authoritative voices say about playoff basketball?",    # HYBRID
    "hi",                                                            # GREETING
]

print("=" * 80)
print("VERIFICATION: query_type comes from QueryClassifier")
print("=" * 80)
print()

API_URL = "http://localhost:8000/api/v1/chat"

all_match = True

for query in test_queries:
    print(f"Query: '{query}'")
    print("-" * 80)

    # Step 1: Get classification directly from QueryClassifier
    classification = classifier.classify(query)
    classifier_result = classification.query_type.value

    print(f"  Classifier Result: {classifier_result}")

    # Step 2: Get query_type from API response
    response = requests.post(API_URL, json={"query": query, "k": 3}, timeout=30)

    if response.status_code == 200:
        data = response.json()
        api_result = data.get("query_type")

        print(f"  API Response:      {api_result}")

        # Compare
        if classifier_result == api_result:
            print(f"  ✅ MATCH")
        else:
            print(f"  ❌ MISMATCH! Classifier says '{classifier_result}', API says '{api_result}'")
            all_match = False
    else:
        print(f"  ❌ API Error: {response.status_code}")
        all_match = False

    print()

print("=" * 80)
if all_match:
    print("✅ CONFIRMED: query_type in API response comes directly from QueryClassifier")
    print("   All test queries show perfect match between classifier and API.")
else:
    print("❌ MISMATCH DETECTED: query_type may not be coming from QueryClassifier")
    print("   or there's a transformation issue in the pipeline.")
print("=" * 80)
