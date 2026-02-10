"""
FILE: conversation_test_cases.py
STATUS: Active
RESPONSIBILITY: Multi-turn conversation test cases for context-aware evaluation
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

from dataclasses import dataclass


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    query: str
    expected_contains: list[str]  # Key terms that should appear in response
    expected_entity: str | None = None  # Entity that should be referenced (for pronoun resolution)


@dataclass
class ConversationTestCase:
    """A multi-turn conversation test case."""

    conversation_id: str  # Unique ID for this conversation
    title: str  # Description of what this conversation tests
    turns: list[ConversationTurn]
    tests_pronoun_resolution: bool = False
    tests_context_carryover: bool = False


# Test Case 1: Pronoun Resolution - Player Stats
PRONOUN_PLAYER_STATS = ConversationTestCase(
    conversation_id="test_pronoun_player_stats",
    title="Pronoun resolution for player statistics",
    turns=[
        ConversationTurn(
            query="Who scored the most points this season?",
            expected_contains=["Shai Gilgeous-Alexander", "2,485", "points"],
            expected_entity="Shai Gilgeous-Alexander",
        ),
        ConversationTurn(
            query="What about his assists?",  # "his" refers to Shai
            expected_contains=["Shai", "assists"],
            expected_entity="Shai Gilgeous-Alexander",
        ),
        ConversationTurn(
            query="How does he compare to Anthony Edwards?",  # "he" refers to Shai
            expected_contains=["Shai", "Anthony Edwards", "comparison"],
            expected_entity="Shai Gilgeous-Alexander",
        ),
    ],
    tests_pronoun_resolution=True,
    tests_context_carryover=True,
)

# Test Case 2: Pronoun Resolution - Team Context
PRONOUN_TEAM_CONTEXT = ConversationTestCase(
    conversation_id="test_pronoun_team",
    title="Pronoun resolution for team queries",
    turns=[
        ConversationTurn(
            query="Which team has the best record?",
            expected_contains=["team", "record", "wins"],
            expected_entity=None,  # Will depend on actual data
        ),
        ConversationTurn(
            query="Who are their top scorers?",  # "their" refers to best team
            expected_contains=["points", "scorer"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="What's their home arena?",  # "their" still refers to same team
            expected_contains=["arena", "stadium"],
            expected_entity=None,
        ),
    ],
    tests_pronoun_resolution=True,
    tests_context_carryover=True,
)

# Test Case 3: Context Carryover - Statistical Comparison
CONTEXT_STAT_COMPARISON = ConversationTestCase(
    conversation_id="test_context_comparison",
    title="Context carryover for statistical comparisons",
    turns=[
        ConversationTurn(
            query="Compare Nikola Jokic and Giannis Antetokounmpo scoring",
            expected_contains=["Jokic", "Giannis", "points"],
            expected_entity="Nikola Jokic",
        ),
        ConversationTurn(
            query="Now compare their rebounds",  # Continues same comparison
            expected_contains=["Jokic", "Giannis", "rebounds"],
            expected_entity="Nikola Jokic",
        ),
        ConversationTurn(
            query="Who has more assists?",  # Still comparing same two players
            expected_contains=["assists"],
            expected_entity="Nikola Jokic",
        ),
    ],
    tests_pronoun_resolution=False,
    tests_context_carryover=True,
)

# Test Case 4: Follow-up Question Refinement
CONTEXT_REFINEMENT = ConversationTestCase(
    conversation_id="test_context_refinement",
    title="Follow-up questions refining previous query",
    turns=[
        ConversationTurn(
            query="Show me players with good three-point shooting",
            expected_contains=["three", "point", "percentage"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="Only from the Lakers",  # Refines previous query
            expected_contains=["Lakers", "three"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="Sort by attempts",  # Further refinement
            expected_contains=["attempts", "sorted"],
            expected_entity=None,
        ),
    ],
    tests_pronoun_resolution=False,
    tests_context_carryover=True,
)

# Test Case 5: Multi-Entity Context Tracking
CONTEXT_MULTI_ENTITY = ConversationTestCase(
    conversation_id="test_multi_entity",
    title="Tracking multiple entities across conversation",
    turns=[
        ConversationTurn(
            query="Tell me about Jayson Tatum's scoring",
            expected_contains=["Jayson Tatum", "points", "scoring"],
            expected_entity="Jayson Tatum",
        ),
        ConversationTurn(
            query="How does LeBron James compare?",
            expected_contains=["LeBron", "comparison"],
            expected_entity="LeBron James",
        ),
        ConversationTurn(
            query="Between the two, who has more rebounds?",  # Refers to both entities
            expected_contains=["rebounds"],
            expected_entity="Jayson Tatum",  # Either entity is acceptable
        ),
    ],
    tests_pronoun_resolution=True,
    tests_context_carryover=True,
)

# Test Case 6: Implicit Context - Same Category
IMPLICIT_CONTEXT_CATEGORY = ConversationTestCase(
    conversation_id="test_implicit_category",
    title="Implicit context continuation in same category",
    turns=[
        ConversationTurn(
            query="Who leads in steals?",
            expected_contains=["steals", "leader"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="And blocks?",  # Implicitly continues "who leads in..." pattern
            expected_contains=["blocks"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="What about turnovers?",  # Same pattern
            expected_contains=["turnovers"],
            expected_entity=None,
        ),
    ],
    tests_pronoun_resolution=False,
    tests_context_carryover=True,
)

# Test Case 7: Clarification and Correction
CONTEXT_CLARIFICATION = ConversationTestCase(
    conversation_id="test_clarification",
    title="Handling clarifications and corrections",
    turns=[
        ConversationTurn(
            query="Show me stats for the Warriors",
            expected_contains=["Warriors", "stats"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="Actually, I meant the Celtics",  # Corrects previous query
            expected_contains=["Celtics"],
            expected_entity=None,
        ),
        ConversationTurn(
            query="What's their win-loss record?",  # "their" = Celtics, not Warriors
            expected_contains=["wins", "losses", "record"],
            expected_entity=None,
        ),
    ],
    tests_pronoun_resolution=True,
    tests_context_carryover=True,
)


# All conversation test cases
ALL_CONVERSATION_TEST_CASES = [
    PRONOUN_PLAYER_STATS,
    PRONOUN_TEAM_CONTEXT,
    CONTEXT_STAT_COMPARISON,
    CONTEXT_REFINEMENT,
    CONTEXT_MULTI_ENTITY,
    IMPLICIT_CONTEXT_CATEGORY,
    CONTEXT_CLARIFICATION,
]


def get_pronoun_test_cases() -> list[ConversationTestCase]:
    """Get test cases that specifically test pronoun resolution."""
    return [tc for tc in ALL_CONVERSATION_TEST_CASES if tc.tests_pronoun_resolution]


def get_context_test_cases() -> list[ConversationTestCase]:
    """Get test cases that test context carryover."""
    return [tc for tc in ALL_CONVERSATION_TEST_CASES if tc.tests_context_carryover]
