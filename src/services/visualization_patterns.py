"""
FILE: visualization_patterns.py
STATUS: Active
RESPONSIBILITY: Detect query patterns for automatic visualization selection
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import re
from enum import Enum
from typing import Any


class VisualizationPattern(Enum):
    """Query pattern types that map to specific visualization types."""

    # Rankings and leaderboards
    TOP_N = "top_n"  # Top 5 scorers, bottom 3 teams

    # Comparisons
    PLAYER_COMPARISON = "player_comparison"  # Compare 2-4 specific entities
    MULTI_ENTITY_COMPARISON = "multi_entity_comparison"  # Compare many entities

    # Single entity lookup
    SINGLE_ENTITY = "single_entity"  # LeBron's stats, Lakers team stats

    # Distributions and aggregations
    DISTRIBUTION = "distribution"  # League-wide averages, ranges

    # Correlations
    CORRELATION = "correlation"  # Relationship between two stats

    # Filtered lists
    THRESHOLD_FILTER = "threshold_filter"  # Players with >25 PPG

    # Percentage breakdowns
    COMPOSITION = "composition"  # Shot distribution, stat breakdown

    # Fallback
    GENERIC_TABLE = "generic_table"  # Default table view


class QueryPatternDetector:
    """Detect query patterns for visualization selection."""

    # Pattern detection rules (order matters - most specific first)
    PATTERNS = {
        # PLAYER_COMPARISON first - "compare" should take priority over "top" in TOP_N
        VisualizationPattern.PLAYER_COMPARISON: [
            r"\bcompare\b",  # Any query with "compare" is a comparison
            r"\b(jokic|lebron|curry|durant|embiid|giannis|harden|tatum|luka|morant)\b.*\b(vs|versus|and|or)\b.*\b(jokic|lebron|curry|durant|embiid|giannis|harden|tatum|luka|morant)\b",
            r"\b(who\s+is\s+better|which\s+is\s+better)\b",
            r"\b(him|her)\s+(vs|versus|compared to)\b",
        ],

        VisualizationPattern.TOP_N: [
            r"\b(top|bottom|best|worst|leading|leader)\s+\d+",
            r"\b(first|last)\s+\d+",
            r"\b(highest|lowest)\s+\d+",
            r"\blimit\s+\d+\b.*\border\s+by\b",  # SQL LIMIT with ORDER BY
        ],

        VisualizationPattern.CORRELATION: [
            r"\b(relationship|correlation)\s+(between|with)\b",
            r"\bcorrelated\b",  # Standalone "correlated" at end of sentence
            r"\b(versus|vs)\b(?!.*\b(player|team|jokic|lebron|curry|durant|embiid|giannis|harden|tatum|luka|morant)\b)",
            r"\b(impact|effect)\s+of\b.*\bon\b",
        ],

        # COMPOSITION before DISTRIBUTION - "breakdown/composition of" is more specific
        VisualizationPattern.COMPOSITION: [
            r"\b(breakdown|composition)\s+(of|from)\b",  # "breakdown of/from X"
            r"\b(percentage|proportion)\s+of\b",  # Any "proportion of" is composition
            r"\bfrom\s+(2|3|the\s+line|free\s+throws?)\b.*\b(vs|versus)\b",
        ],

        VisualizationPattern.DISTRIBUTION: [
            r"\b(distribution|spread|range)\b",
            r"\b(average|mean|median)\b.*\b(league.wide|across\s+the\s+league|all\s+players)\b",
            r"\b(league.wide|across\s+the\s+league|all\s+players)\b.*\b(average|mean|median)\b",
            r"\bhow\s+(many|much)\b.*\b(on\s+average|typically)\b",
        ],

        VisualizationPattern.THRESHOLD_FILTER: [
            r"\b(players?|teams?)\s+with\b.*\b(over|under|above|below|more\s+than|less\s+than)\b.*\d+",
            r"\b(players?|teams?)\s+(over|under|above|below)\s+\d+",  # Without "with"
            r"\b(having|that\s+have)\b.*\b(over|above|more\s+than)\b.*\d+",
            r"\bwhere\b.*[><]=?\s*\d+",  # SQL WHERE with comparison
        ],

        VisualizationPattern.SINGLE_ENTITY: [
            r"\b(what|show|tell\s+me|get)\b.*\b(is|are)\b.*\b('s|'s)\b",  # "What is LeBron's"
            r"\b(his|her|their|its)\s+\w+",  # Any "his/her/their" + noun is single entity
            r"^[A-Z][a-z]+.*'s?\s+(stats?|numbers?|averages?|points?|rebounds?|assists?)",  # "LeBron's stats"
        ],
    }

    @classmethod
    def detect_pattern(cls, query: str, sql_result: list[dict[str, Any]] | None = None) -> VisualizationPattern:
        """Detect the query pattern for visualization selection.

        Args:
            query: The user's original query text
            sql_result: Optional SQL results to help with pattern detection

        Returns:
            VisualizationPattern enum
        """
        query_lower = query.lower().strip()

        # Check each pattern in priority order
        for pattern_type, regex_list in cls.PATTERNS.items():
            for regex_str in regex_list:
                if re.search(regex_str, query_lower, re.IGNORECASE):
                    # Additional validation based on result data
                    if sql_result is not None:
                        result_count = len(sql_result)

                        # Override: If pattern says comparison but we have many results
                        if pattern_type == VisualizationPattern.PLAYER_COMPARISON and result_count > 4:
                            return VisualizationPattern.MULTI_ENTITY_COMPARISON

                        # Override: If pattern says top_n but we have exactly 1 result
                        if pattern_type == VisualizationPattern.TOP_N and result_count == 1:
                            return VisualizationPattern.SINGLE_ENTITY

                        # Override: If we only have 1 result, it's a single entity lookup
                        if result_count == 1 and pattern_type not in [
                            VisualizationPattern.SINGLE_ENTITY,
                            VisualizationPattern.DISTRIBUTION,
                        ]:
                            return VisualizationPattern.SINGLE_ENTITY

                    return pattern_type

        # Fallback: Use result count to infer pattern
        if sql_result is not None:
            result_count = len(sql_result)

            if result_count == 0:
                return VisualizationPattern.GENERIC_TABLE
            elif result_count == 1:
                return VisualizationPattern.SINGLE_ENTITY
            elif 2 <= result_count <= 4:
                return VisualizationPattern.PLAYER_COMPARISON
            elif 5 <= result_count <= 10:
                return VisualizationPattern.TOP_N
            else:
                return VisualizationPattern.MULTI_ENTITY_COMPARISON

        # Ultimate fallback
        return VisualizationPattern.GENERIC_TABLE

    @classmethod
    def get_recommended_viz_type(cls, pattern: VisualizationPattern, result_count: int = 0) -> str:
        """Get recommended visualization type for a pattern.

        Args:
            pattern: The detected query pattern
            result_count: Number of rows in SQL result

        Returns:
            String describing the recommended visualization type
        """
        recommendations = {
            VisualizationPattern.TOP_N: "horizontal_bar" if result_count <= 10 else "vertical_bar",
            VisualizationPattern.PLAYER_COMPARISON: "radar" if result_count <= 4 else "grouped_bar",
            VisualizationPattern.MULTI_ENTITY_COMPARISON: "bar",
            VisualizationPattern.SINGLE_ENTITY: "stat_card",
            VisualizationPattern.DISTRIBUTION: "histogram",
            VisualizationPattern.CORRELATION: "scatter",
            VisualizationPattern.THRESHOLD_FILTER: "highlighted_table",
            VisualizationPattern.COMPOSITION: "pie",
            VisualizationPattern.GENERIC_TABLE: "table",
        }
        return recommendations.get(pattern, "table")


# Example usage and testing
if __name__ == "__main__":
    detector = QueryPatternDetector()

    test_cases = [
        # Top N
        ("Who are the top 5 scorers?", None, VisualizationPattern.TOP_N),
        ("Show me the bottom 3 teams by wins", None, VisualizationPattern.TOP_N),

        # Comparisons
        ("Compare LeBron and Durant", None, VisualizationPattern.PLAYER_COMPARISON),
        ("Jokic vs Embiid stats", None, VisualizationPattern.PLAYER_COMPARISON),

        # Single entity
        ("What is LeBron's PPG?", [{"name": "LeBron James", "ppg": 24.4}], VisualizationPattern.SINGLE_ENTITY),
        ("Show me his assists", [{"ast": 486}], VisualizationPattern.SINGLE_ENTITY),

        # Correlation
        ("Relationship between 3P% and PPG", None, VisualizationPattern.CORRELATION),
        ("Does higher usage rate lead to more turnovers?", None, VisualizationPattern.CORRELATION),

        # Distribution
        ("What's the league-wide average PPG?", None, VisualizationPattern.DISTRIBUTION),
        ("Show distribution of player heights", None, VisualizationPattern.DISTRIBUTION),

        # Threshold filter
        ("Players with over 25 PPG", None, VisualizationPattern.THRESHOLD_FILTER),
        ("Teams with more than 40 wins", None, VisualizationPattern.THRESHOLD_FILTER),

        # Composition
        ("LeBron's shot breakdown from 2P, 3P, and FT", None, VisualizationPattern.COMPOSITION),
        ("Percentage of points from three", None, VisualizationPattern.COMPOSITION),
    ]

    print("Query Pattern Detection Test")
    print("=" * 100)
    print(f"{'STATUS':<8} {'DETECTED':<25} {'EXPECTED':<25} {'VIZ TYPE':<20} {'QUERY':<40}")
    print("=" * 100)

    correct = 0
    for query, mock_result, expected in test_cases:
        detected = detector.detect_pattern(query, mock_result)
        result_count = len(mock_result) if mock_result else 0
        viz_type = detector.get_recommended_viz_type(detected, result_count)

        match = "✓ OK" if detected == expected else "✗ FAIL"
        print(f"{match:<8} {detected.value:<25} {expected.value:<25} {viz_type:<20} {query[:38]:<40}")

        if detected == expected:
            correct += 1

    print("=" * 100)
    print(f"Accuracy: {correct}/{len(test_cases)} ({100*correct/len(test_cases):.1f}%)")
