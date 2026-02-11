"""
FILE: _classify_vector_test_cases.py
STATUS: Experimental
RESPONSIBILITY: Classify all 47 vector test cases into Statistical/Hybrid/Vector categories
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import io
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES
from src.evaluation.models import TestCategory

# Statistical keywords (should go to SQL)
STATISTICAL_KEYWORDS = [
    "ppg", "points per game", "scoring", "scored", "rebounds", "assists", "steals", "blocks",
    "percentage", "fg%", "3pt%", "ft%", "ts%", "efg%", "per",
    "top 3", "top 5", "top 10", "leading", "leader", "most", "highest", "best",
    "average", "total", "season", "stats", "numbers", "record", "win-loss",
    "compare", "comparison", "who has more", "better rebounder", "more efficient",
    "players averaging", "how many players", "count"
]

# Hybrid indicators (needs both SQL data + context)
HYBRID_KEYWORDS = [
    "why", "explain why", "what makes", "based on", "according to",
    "compared to", "impact", "effectiveness", "strategy", "style",
    "discussions", "reddit", "stats and", "numbers say", "debate",
    "improvement", "changed", "trend"
]

# Pure vector indicators (contextual/opinion/qualitative)
VECTOR_KEYWORDS = [
    "discuss", "opinion", "debate", "argue", "think", "consider",
    "what do fans", "reddit", "discussions", "community",
    "out of scope", "video game", "weather", "off-topic",
    "vague", "unclear", "typo"
]


def classify_test_case(question: str, category: str) -> str:
    """Classify test case into Statistical/Hybrid/Vector.

    Args:
        question: Test question text
        category: Original test category (SIMPLE, COMPLEX, NOISY, CONVERSATIONAL)

    Returns:
        "STATISTICAL", "HYBRID", or "VECTOR"
    """
    q_lower = question.lower()

    # Check for statistical patterns
    stat_count = sum(1 for kw in STATISTICAL_KEYWORDS if kw in q_lower)

    # Check for hybrid patterns
    hybrid_count = sum(1 for kw in HYBRID_KEYWORDS if kw in q_lower)

    # Check for pure vector patterns
    vector_count = sum(1 for kw in VECTOR_KEYWORDS if kw in q_lower)

    # Decision logic
    if stat_count > 0 and hybrid_count == 0:
        return "STATISTICAL"  # Pure stats question → SQL
    elif stat_count > 0 and hybrid_count > 0:
        return "HYBRID"  # Stats + context → SQL + Vector
    elif vector_count > 0 or "?" == question.strip():
        return "VECTOR"  # Contextual/noisy/off-topic → Vector only
    elif category == "simple":
        return "STATISTICAL"  # SIMPLE category is statistical by definition
    elif category == "conversational":
        # Conversational is tricky - check content
        if stat_count > 0:
            return "STATISTICAL"  # "Who is the leading scorer?" → SQL
        else:
            return "VECTOR"  # "What do fans think?" → Vector
    elif category == "complex":
        # Complex can be either
        if hybrid_count > 0:
            return "HYBRID"
        else:
            return "VECTOR"
    else:
        return "VECTOR"  # Default to vector for unclear cases


# Classify all test cases
statistical = []
hybrid = []
vector = []

for i, tc in enumerate(EVALUATION_TEST_CASES, 1):
    classification = classify_test_case(tc.question, tc.category.value)

    if classification == "STATISTICAL":
        statistical.append((i, tc.category.value, tc.question))
    elif classification == "HYBRID":
        hybrid.append((i, tc.category.value, tc.question))
    else:
        vector.append((i, tc.category.value, tc.question))

# Print results
print("=" * 80)
print("VECTOR TEST CASE CLASSIFICATION")
print("=" * 80)
print(f"\nTotal test cases: {len(EVALUATION_TEST_CASES)}")
print(f"  STATISTICAL (should go to SQL): {len(statistical)}")
print(f"  HYBRID (needs SQL + Vector): {len(hybrid)}")
print(f"  VECTOR (pure contextual/opinion): {len(vector)}")
print()

print("=" * 80)
print("STATISTICAL QUERIES (Recommend moving to sql_test_cases.py)")
print("=" * 80)
for idx, category, question in statistical:
    print(f"\n{idx}. [{category.upper()}]")
    print(f"   Q: {question}")

print("\n" + "=" * 80)
print("HYBRID QUERIES (Recommend moving to hybrid_test_cases.py)")
print("=" * 80)
for idx, category, question in hybrid:
    print(f"\n{idx}. [{category.upper()}]")
    print(f"   Q: {question}")

print("\n" + "=" * 80)
print("PURE VECTOR QUERIES (Keep in vector_test_cases.py)")
print("=" * 80)
for idx, category, question in vector:
    print(f"\n{idx}. [{category.upper()}]")
    print(f"   Q: {question}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
Test Suite Reorganization Recommendation:
- sql_test_cases.py: Add {len(statistical)} statistical queries from vector tests
- hybrid_test_cases.py: Add {len(hybrid)} hybrid queries from vector tests
- vector_test_cases.py: Keep only {len(vector)} pure contextual/opinion queries

This will align test expectations with actual routing behavior.
""")
