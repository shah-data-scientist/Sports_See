"""
FILE: evaluate_vector.py
STATUS: Active
RESPONSIBILITY: Master Vector-only evaluation - Tests FAISS vector search with Mistral embeddings
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.core.config import settings
from src.evaluation.test_cases import EVALUATION_TEST_CASES
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


def get_vector_test_cases():
    """
    Get test cases suitable for vector-only evaluation.

    Includes:
    - NOISY: Contextual, opinion-based queries
    - CONVERSATIONAL: Follow-up questions
    - Some COMPLEX: Queries needing contextual understanding

    Excludes:
    - SIMPLE: Statistical queries (better for SQL)
    """
    vector_cases = []

    for tc in EVALUATION_TEST_CASES:
        # Include NOISY (contextual/opinion queries)
        if tc.category == TestCategory.NOISY:
            vector_cases.append(tc)
        # Include CONVERSATIONAL (follow-up questions)
        elif tc.category == TestCategory.CONVERSATIONAL:
            vector_cases.append(tc)
        # Include COMPLEX queries that need context (not just stats)
        elif tc.category == TestCategory.COMPLEX:
            # Filter: Include if question has contextual keywords
            contextual_keywords = [
                "why", "explain", "analysis", "discuss", "opinion",
                "strategy", "style", "valuable", "effective", "impact"
            ]
            if any(kw in tc.question.lower() for kw in contextual_keywords):
                vector_cases.append(tc)

    return vector_cases


def run_vector_evaluation():
    """
    Master Vector-only evaluation.

    Tests FAISS vector search with conversation support.
    Uses NOISY, CONVERSATIONAL, and contextual COMPLEX test cases.
    """
    vector_cases = get_vector_test_cases()

    print("\n" + "="*80)
    print("  VECTOR-ONLY EVALUATION")
    print("  Tests: FAISS vector search + Mistral embeddings")
    print("  Mode: VECTOR ONLY (SQL disabled)")
    print(f"  Test Cases: {len(vector_cases)} selected from EVALUATION_TEST_CASES")
    print("="*80 + "\n")

    # Initialize chat service with SQL DISABLED
    chat_service = ChatService(enable_sql=False)
    chat_service.ensure_ready()

    # Initialize conversation tracking
    conversation_repo = ConversationRepository()
    conversation_service = ConversationService(repository=conversation_repo)

    current_conversation_id = None
    current_turn_number = 0

    results = []
    category_counts = {}

    for i, test_case in enumerate(vector_cases, 1):
        category = test_case.category.value
        category_counts[category] = category_counts.get(category, 0) + 1

        logger.info(f"[{i}/{len(vector_cases)}] {category}: {test_case.question[:60]}...")

        # Handle conversational test cases
        if test_case.category == TestCategory.CONVERSATIONAL:
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
            # Execute vector search through chat service
            request = ChatRequest(
                query=test_case.question,
                k=5,
                include_sources=True,
                conversation_id=current_conversation_id,
                turn_number=current_turn_number if current_conversation_id else 1
            )

            response = chat_service.chat(request)

            # Evaluate vector search quality
            has_sources = len(response.sources) > 0 if response.sources else False
            has_context = len(response.answer) > 100  # Contextual answers are longer

            results.append({
                "question": test_case.question,
                "category": category,
                "response": response.answer,
                "sources_count": len(response.sources) if response.sources else 0,
                "has_context": has_context,
                "processing_time_ms": response.processing_time_ms,
                "success": True
            })

            status = "[PASS]" if has_sources else "[WARN]"
            logger.info(f"  {status} Sources: {len(response.sources) if response.sources else 0} | "
                       f"Context: {'Y' if has_context else 'N'} | Time: {response.processing_time_ms}ms")

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
    print(f"\nTotal Test Cases: {len(vector_cases)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    print(f"\nCategory Breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"vector_evaluation_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(vector_cases),
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
        run_vector_evaluation()
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
