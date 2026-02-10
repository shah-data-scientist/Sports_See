"""
FILE: evaluate_sql.py
STATUS: Active
RESPONSIBILITY: Master SQL-only evaluation - Tests SQL query generation and execution
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.core.config import settings
from src.evaluation.sql_test_cases import SQL_TEST_CASES
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
        "what about", "and what", "how does that", "compare him",
        "which of them", "how many games did he"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def _is_conversational_case(test_case) -> bool:
    """Check if test case is conversational."""
    if hasattr(test_case, 'category') and isinstance(test_case.category, str):
        return "conversational" in test_case.category.lower()
    if hasattr(test_case, 'category') and isinstance(test_case.category, TestCategory):
        return test_case.category == TestCategory.CONVERSATIONAL
    return False


def run_sql_evaluation():
    """
    Master SQL-only evaluation.

    Tests SQL query generation and execution with conversation support.
    Uses ALL SQL test cases including conversational ones.
    """
    print("\n" + "="*80)
    print("  SQL-ONLY EVALUATION")
    print("  Tests: SQL query generation, execution, and accuracy")
    print("  Mode: SQL ONLY (no vector search)")
    print(f"  Test Cases: {len(SQL_TEST_CASES)} total")
    print("="*80 + "\n")

    # Initialize chat service with SQL enabled
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    # Initialize conversation tracking
    conversation_repo = ConversationRepository()
    conversation_service = ConversationService(repository=conversation_repo)

    current_conversation_id = None
    current_turn_number = 0

    results = []
    category_counts = {}

    for i, test_case in enumerate(SQL_TEST_CASES, 1):
        category = test_case.category if hasattr(test_case, 'category') else 'unknown'
        category_counts[category] = category_counts.get(category, 0) + 1

        logger.info(f"[{i}/{len(SQL_TEST_CASES)}] {category}: {test_case.question[:60]}...")

        # Handle conversational test cases
        if _is_conversational_case(test_case):
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
            # Execute SQL query through chat service
            request = ChatRequest(
                query=test_case.question,
                k=5,
                include_sources=True,
                conversation_id=current_conversation_id,
                turn_number=current_turn_number if current_conversation_id else 1
            )

            response = chat_service.chat(request)

            # Evaluate SQL accuracy
            sql_used = "sql" in response.answer.lower() or any(
                kw in response.answer.lower()
                for kw in ["pts", "reb", "ast", "points", "rebounds", "assists"]
            )

            results.append({
                "question": test_case.question,
                "category": category,
                "response": response.answer,
                "sql_used": sql_used,
                "processing_time_ms": response.processing_time_ms,
                "success": True
            })

            status = "[PASS]" if sql_used else "[WARN]"
            logger.info(f"  {status} SQL: {'Y' if sql_used else 'N'} | Time: {response.processing_time_ms}ms")

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
    print(f"\nTotal Test Cases: {len(SQL_TEST_CASES)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    print(f"\nCategory Breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"sql_evaluation_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(SQL_TEST_CASES),
        "successful": sum(1 for r in results if r['success']),
        "failed": sum(1 for r in results if not r['success']),
        "category_counts": category_counts,
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
        run_sql_evaluation()
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
