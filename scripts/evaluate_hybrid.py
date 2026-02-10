"""
FILE: evaluate_hybrid.py
STATUS: Active
RESPONSIBILITY: Master Hybrid evaluation - Tests intelligent SQL + Vector routing
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.core.config import settings
from src.evaluation.test_cases import EVALUATION_TEST_CASES
from src.evaluation.hybrid_test_cases import HYBRID_TEST_CASES
from src.evaluation.models import TestCategory
from src.services.chat import ChatService
from src.services.conversation import ConversationService
from src.repositories.conversation import ConversationRepository
from src.models.chat import ChatRequest

logger = logging.getLogger(__name__)


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context."""
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def get_hybrid_test_cases():
    """
    Get test cases suitable for hybrid evaluation.

    Includes:
    - HYBRID_TEST_CASES: Dedicated hybrid queries
    - COMPLEX from EVALUATION_TEST_CASES: Multi-step queries
    - SIMPLE from EVALUATION_TEST_CASES: Statistical queries (for SQL routing)
    - CONVERSATIONAL: Testing routing with conversation context

    This combines statistical queries (SQL), contextual queries (Vector),
    and complex queries requiring both.
    """
    hybrid_cases = []

    # Add all dedicated hybrid test cases
    hybrid_cases.extend(HYBRID_TEST_CASES)

    # Add COMPLEX and SIMPLE cases from main evaluation set
    for tc in EVALUATION_TEST_CASES:
        if tc.category in [TestCategory.COMPLEX, TestCategory.SIMPLE, TestCategory.CONVERSATIONAL]:
            hybrid_cases.append(tc)

    return hybrid_cases


def run_hybrid_evaluation():
    """
    Master Hybrid evaluation.

    Tests intelligent routing between SQL and Vector search.
    Uses SIMPLE (SQL), COMPLEX (both), CONVERSATIONAL (both), and HYBRID test cases.
    """
    hybrid_cases = get_hybrid_test_cases()

    print("\n" + "="*80)
    print("  HYBRID EVALUATION (SQL + VECTOR)")
    print("  Tests: Intelligent routing between SQL and Vector search")
    print("  Mode: HYBRID (SQL enabled with Vector fallback)")
    print(f"  Test Cases: {len(hybrid_cases)} from multiple sources")
    print("="*80 + "\n")

    # Initialize chat service with SQL ENABLED (hybrid mode)
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    # Initialize conversation tracking
    conversation_repo = ConversationRepository()
    conversation_service = ConversationService(repository=conversation_repo)

    current_conversation_id = None
    current_turn_number = 0

    results = []
    category_counts = {}
    routing_stats = {"sql": 0, "vector": 0, "both": 0, "unknown": 0}

    for i, test_case in enumerate(hybrid_cases, 1):
        category = test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category)
        category_counts[category] = category_counts.get(category, 0) + 1

        logger.info(f"[{i}/{len(hybrid_cases)}] {category}: {test_case.question[:60]}...")

        # Handle conversational test cases
        is_conversational = (
            (hasattr(test_case.category, 'value') and test_case.category == TestCategory.CONVERSATIONAL) or
            (isinstance(test_case.category, str) and "conversational" in test_case.category.lower())
        )

        if is_conversational:
            if _is_followup_question(test_case.question):
                if current_conversation_id is None:
                    conversation = conversation_service.start_conversation()
                    current_conversation_id = conversation.id
                    current_turn_number = 1
                else:
                    current_turn_number += 1
            else:
                conversation = conversation_service.start_conversation()
                current_conversation_id = conversation.id
                current_turn_number = 1
        else:
            current_conversation_id = None
            current_turn_number = 0

        try:
            # Execute hybrid query through chat service
            request = ChatRequest(
                query=test_case.question,
                k=5,
                include_sources=True,
                conversation_id=current_conversation_id,
                turn_number=current_turn_number if current_conversation_id else 1
            )

            response = chat_service.chat(request)

            # Determine which component was used
            has_sql_data = any(
                kw in response.answer.lower()
                for kw in ["pts", "reb", "ast", "points", "rebounds", "assists", "ppg", "rpg"]
            )
            has_vector_context = len(response.sources) > 0 if response.sources else False

            if has_sql_data and has_vector_context:
                routing = "both"
            elif has_sql_data:
                routing = "sql"
            elif has_vector_context:
                routing = "vector"
            else:
                routing = "unknown"

            routing_stats[routing] += 1

            results.append({
                "question": test_case.question,
                "category": category,
                "response": response.answer,
                "routing": routing,
                "sources_count": len(response.sources) if response.sources else 0,
                "processing_time_ms": response.processing_time_ms,
                "success": True
            })

            logger.info(f"  [PASS] Routing: {routing.upper()} | "
                       f"Sources: {len(response.sources) if response.sources else 0} | "
                       f"Time: {response.processing_time_ms}ms")

        except Exception as e:
            logger.error(f"  [FAIL] Error: {e}")
            results.append({
                "question": test_case.question,
                "category": category,
                "error": str(e),
                "success": False
            })

    # Print summary
    print("\n" + "="*80)
    print("  EVALUATION SUMMARY")
    print("="*80)
    print(f"\nTotal Test Cases: {len(hybrid_cases)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    print(f"\nCategory Breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    print(f"\nRouting Statistics:")
    print(f"  SQL only: {routing_stats['sql']}")
    print(f"  Vector only: {routing_stats['vector']}")
    print(f"  Both (Hybrid): {routing_stats['both']}")
    print(f"  Unknown: {routing_stats['unknown']}")

    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"hybrid_evaluation_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(hybrid_cases),
        "successful": sum(1 for r in results if r['success']),
        "failed": sum(1 for r in results if not r['success']),
        "category_counts": category_counts,
        "routing_stats": routing_stats,
        "results": results
    }

    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        run_hybrid_evaluation()
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
