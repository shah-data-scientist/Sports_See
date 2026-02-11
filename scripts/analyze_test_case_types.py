"""
FILE: analyze_test_case_types.py
STATUS: Active
RESPONSIBILITY: Analyze test cases to identify pure SQL, pure Vector, and true Hybrid queries
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import re
from src.evaluation.hybrid_test_cases import HYBRID_TEST_CASES
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES
from src.evaluation.models import TestCategory


def classify_query_intent(question: str, ground_truth: str = "") -> str:
    """Classify a query as SQL, Vector, or Hybrid based on its intent.

    Args:
        question: The query text
        ground_truth: The expected behavior description

    Returns:
        "SQL" for pure statistical queries
        "VECTOR" for pure contextual/analytical queries
        "HYBRID" for queries requiring both
    """
    question_lower = question.lower()
    ground_truth_lower = ground_truth.lower()

    # SQL-only indicators (no explanation/analysis requested)
    pure_sql_patterns = [
        r"^who (is|are|has|scored|leads|recorded)",  # Direct stat queries
        r"^which (player|team|players|teams) (has|have|scored|leads)",
        r"^show me (the )?(top|best|leading|stats|statistics)",
        r"^list (the )?(top|best|players|teams)",
        r"^what (is|are) (the )?(average|total|sum|stats|statistics)",
        r"^(top|best|most|highest|lowest) \d+",  # "top 5 scorers"
        r"stats? (for|of|plz|please)",  # "curry stats plz"
        r"^how many (points|rebounds|assists|games)",
        r"^(compare|show).*(stats|statistics|numbers)$",  # Compare stats (no explanation)
    ]

    # Vector-only indicators (no statistics requested)
    pure_vector_patterns = [
        r"(why|explain|discuss|describe).*(important|effective|successful|good)",
        r"^explain (the|how|why)",
        r"^describe (the|how)",
        r"^discuss (the )?",
        r"(evolution|history|changed|transformation) of",
        r"(strategies?|tactics?|approach|technique|style|system)",
        r"(impact|influence|effect) (of|on)",
        r"what (makes|do).*(think|consider|believe|say)",
        r"according to (fans|coaches|analysts|experts)",
    ]

    # Hybrid indicators (explicitly requests both stats AND analysis)
    hybrid_patterns = [
        r"(stats|statistics|numbers).*(and|then).*(why|explain|analysis|makes)",
        r"(why|explain|analysis).*(and|then).*(stats|statistics|numbers)",
        r"(who|which|what).*(most|top|best).*(and|then).*(why|explain|makes)",
        r"(and|then).*(why|explain|what makes|how)",
        r"compare.*and.*(explain|why|makes|better)",
        r"(based on|according to).*(stats|data).*(why|explain|strategy)",
    ]

    # Check ground truth for strong signals
    if ground_truth_lower:
        if "sql" in ground_truth_lower and "vector" in ground_truth_lower:
            return "HYBRID"
        if "combines" in ground_truth_lower or "both" in ground_truth_lower:
            return "HYBRID"
        if "plus" in ground_truth_lower and ("document" in ground_truth_lower or "discussion" in ground_truth_lower):
            return "HYBRID"
        if "primarily vector" in ground_truth_lower or "minimal stats" in ground_truth_lower:
            return "VECTOR"
        if "query" in ground_truth_lower and not ("document" in ground_truth_lower or "discussion" in ground_truth_lower):
            return "SQL"

    # Check patterns
    if any(re.search(p, question_lower) for p in hybrid_patterns):
        return "HYBRID"

    sql_matches = sum(1 for p in pure_sql_patterns if re.search(p, question_lower))
    vector_matches = sum(1 for p in pure_vector_patterns if re.search(p, question_lower))

    if sql_matches > 0 and vector_matches > 0:
        return "HYBRID"
    elif sql_matches > vector_matches:
        return "SQL"
    elif vector_matches > sql_matches:
        return "VECTOR"
    else:
        # Ambiguous - check for keywords
        has_stats_keywords = any(kw in question_lower for kw in [
            "stat", "point", "rebound", "assist", "score", "ppg", "rpg", "apg",
            "percentage", "leader", "top", "most", "highest", "average"
        ])
        has_context_keywords = any(kw in question_lower for kw in [
            "why", "explain", "strategy", "style", "impact", "evolution", "discuss"
        ])

        if has_stats_keywords and has_context_keywords:
            return "HYBRID"
        elif has_stats_keywords:
            return "SQL"
        elif has_context_keywords:
            return "VECTOR"
        else:
            return "HYBRID"  # Default to hybrid if unclear


def analyze_hybrid_test_cases():
    """Analyze HYBRID_TEST_CASES to identify which should be moved."""

    print("="*100)
    print("  HYBRID TEST CASES ANALYSIS")
    print("="*100)

    sql_only = []
    vector_only = []
    true_hybrid = []

    for tc in HYBRID_TEST_CASES:
        classification = classify_query_intent(tc.question, tc.ground_truth)

        if classification == "SQL":
            sql_only.append(tc)
        elif classification == "VECTOR":
            vector_only.append(tc)
        else:
            true_hybrid.append(tc)

    print(f"\nTotal HYBRID_TEST_CASES: {len(HYBRID_TEST_CASES)}")
    print(f"  Pure SQL (should move to SQL_TEST_CASES): {len(sql_only)}")
    print(f"  Pure Vector (should move to vector cases): {len(vector_only)}")
    print(f"  True Hybrid (keep in HYBRID_TEST_CASES): {len(true_hybrid)}")

    # Show pure SQL queries
    if sql_only:
        print(f"\n{'='*100}")
        print(f"  PURE SQL QUERIES TO MOVE ({len(sql_only)} cases)")
        print(f"{'='*100}")
        for i, tc in enumerate(sql_only[:10], 1):
            print(f"\n[{i}] Category: {tc.category.value}")
            print(f"    Question: {tc.question}")
            print(f"    Ground Truth: {tc.ground_truth[:100]}...")

    # Show pure Vector queries
    if vector_only:
        print(f"\n{'='*100}")
        print(f"  PURE VECTOR QUERIES TO MOVE ({len(vector_only)} cases)")
        print(f"{'='*100}")
        for i, tc in enumerate(vector_only[:10], 1):
            print(f"\n[{i}] Category: {tc.category.value}")
            print(f"    Question: {tc.question}")
            print(f"    Ground Truth: {tc.ground_truth[:100]}...")

    print(f"\n{'='*100}")
    print(f"  TRUE HYBRID QUERIES TO KEEP ({len(true_hybrid)} cases)")
    print(f"{'='*100}")
    print(f"First 5 examples:")
    for i, tc in enumerate(true_hybrid[:5], 1):
        print(f"\n[{i}] Category: {tc.category.value}")
        print(f"    Question: {tc.question[:120]}...")

    return sql_only, vector_only, true_hybrid


def analyze_evaluate_hybrid_additions():
    """Analyze SIMPLE cases from EVALUATION_TEST_CASES added to hybrid."""

    print(f"\n\n{'='*100}")
    print("  EVALUATE_HYBRID.PY ADDITIONS ANALYSIS")
    print(f"{'='*100}")

    # Simulate what get_hybrid_test_cases() adds
    added_cases = []
    for tc in EVALUATION_TEST_CASES:
        if tc.category in [TestCategory.SIMPLE, TestCategory.COMPLEX, TestCategory.CONVERSATIONAL]:
            added_cases.append(tc)

    print(f"\nTotal cases added from EVALUATION_TEST_CASES: {len(added_cases)}")

    # Count by category
    from collections import Counter
    category_counts = Counter(tc.category for tc in added_cases)

    print(f"\nBreakdown:")
    for cat, count in category_counts.most_common():
        print(f"  {cat.value}: {count}")

    # Analyze SIMPLE cases
    simple_cases = [tc for tc in added_cases if tc.category == TestCategory.SIMPLE]
    if simple_cases:
        print(f"\n{'='*100}")
        print(f"  SIMPLE CASES (PURE SQL - SHOULD NOT BE IN HYBRID): {len(simple_cases)}")
        print(f"{'='*100}")
        print(f"These are statistical queries that should only be in SQL evaluation.")
        print(f"\nFirst 5 examples:")
        for i, tc in enumerate(simple_cases[:5], 1):
            print(f"\n[{i}] Question: {tc.question}")


def main():
    """Run analysis and provide recommendations."""

    # Analyze HYBRID_TEST_CASES
    sql_only, vector_only, true_hybrid = analyze_hybrid_test_cases()

    # Analyze additions from evaluate_hybrid.py
    analyze_evaluate_hybrid_additions()

    # Recommendations
    print(f"\n\n{'='*100}")
    print("  RECOMMENDATIONS")
    print(f"{'='*100}")

    print(f"\n1. Move {len(sql_only)} pure SQL queries from HYBRID_TEST_CASES to SQL_TEST_CASES")
    print(f"   - These queries only need statistics, no contextual analysis")
    print(f"   - Example: 'whos got most asists???' → Pure SQL query")

    print(f"\n2. Move {len(vector_only)} pure Vector queries from HYBRID_TEST_CASES to vector test cases")
    print(f"   - These queries only need contextual analysis, no statistics")
    print(f"   - Example: 'Explain the evolution of the point guard position'")

    print(f"\n3. Keep {len(true_hybrid)} true hybrid queries in HYBRID_TEST_CASES")
    print(f"   - These genuinely require both SQL stats AND contextual analysis")
    print(f"   - Example: 'Compare Jokic and Embiid stats AND explain who is more valuable'")

    print(f"\n4. Remove SIMPLE from get_hybrid_test_cases() in evaluate_hybrid.py")
    print(f"   - SIMPLE cases are pure SQL queries")
    print(f"   - They should ONLY be in SQL evaluation, not hybrid")

    print(f"\n5. Update evaluate_hybrid.py to only include:")
    print(f"   - True hybrid queries from HYBRID_TEST_CASES")
    print(f"   - COMPLEX cases from EVALUATION_TEST_CASES (many are hybrid)")
    print(f"   - CONVERSATIONAL cases (if they involve both stats and context)")

    print(f"\n{'='*100}")
    print(f"  SUMMARY")
    print(f"{'='*100}")
    print(f"\nCurrent state: Hybrid evaluation mixes pure SQL, pure Vector, and true Hybrid")
    print(f"Desired state: Each evaluation contains only its query type")
    print(f"  - SQL evaluation: Pure statistical queries")
    print(f"  - Vector evaluation: Pure contextual/analytical queries")
    print(f"  - Hybrid evaluation: Queries requiring both SQL + Vector")

    print(f"\nNext steps:")
    print(f"  1. Run this analysis to identify which queries to move")
    print(f"  2. Update HYBRID_TEST_CASES to remove pure SQL/Vector queries")
    print(f"  3. Add removed SQL queries to SQL_TEST_CASES")
    print(f"  4. Add removed Vector queries to vector test selection")
    print(f"  5. Update evaluate_hybrid.py to exclude SIMPLE cases")
    print(f"  6. Re-run all three evaluations to verify correct distribution")


if __name__ == "__main__":
    main()
