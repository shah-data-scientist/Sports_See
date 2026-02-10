"""
FILE: evaluate_conversation_aware.py
STATUS: Active
RESPONSIBILITY: Evaluate conversation-aware query performance (pronoun resolution, context carryover)
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import sys
import io
import time
from datetime import datetime

# Force UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.services.chat import ChatService
from src.services.conversation import ConversationService
from src.repositories.conversation import ConversationRepository
from src.models.chat import ChatRequest
from src.evaluation.conversation_test_cases import (
    ALL_CONVERSATION_TEST_CASES,
    get_pronoun_test_cases,
    get_context_test_cases,
    ConversationTestCase,
    ConversationTurn,
)


class ConversationEvaluator:
    """Evaluates conversation-aware query performance."""

    def __init__(self):
        """Initialize evaluator with services."""
        self.chat_service = ChatService()
        self.chat_service.ensure_ready()

        self.conversation_repo = ConversationRepository()
        self.conversation_service = ConversationService(repository=self.conversation_repo)

    def evaluate_turn(
        self,
        turn: ConversationTurn,
        response_text: str,
        turn_number: int,
    ) -> dict:
        """
        Evaluate a single conversation turn.

        Returns dict with success metrics.
        """
        # Check if expected terms appear in response
        terms_found = sum(
            1 for term in turn.expected_contains
            if term.lower() in response_text.lower()
        )
        total_terms = len(turn.expected_contains)

        term_coverage = terms_found / total_terms if total_terms > 0 else 0.0

        # Entity resolution check (for pronoun resolution)
        entity_resolved = False
        if turn.expected_entity:
            entity_resolved = turn.expected_entity.lower() in response_text.lower()

        return {
            "turn_number": turn_number,
            "query": turn.query,
            "term_coverage": term_coverage,
            "terms_found": terms_found,
            "total_terms": total_terms,
            "entity_resolved": entity_resolved,
            "expected_entity": turn.expected_entity,
            "response_length": len(response_text),
        }

    def evaluate_conversation(
        self,
        test_case: ConversationTestCase,
        use_conversation_context: bool = True,
    ) -> dict:
        """
        Evaluate a full multi-turn conversation.

        Args:
            test_case: The conversation test case to evaluate
            use_conversation_context: If True, use conversation_id (context-aware).
                                     If False, run each query standalone.

        Returns dict with conversation-level metrics.
        """
        print(f"\n{'='*80}")
        print(f"Evaluating: {test_case.title}")
        print(f"Mode: {'CONTEXT-AWARE' if use_conversation_context else 'STANDALONE'}")
        print(f"{'='*80}")

        # Create conversation if using context
        conversation_id = None
        if use_conversation_context:
            conversation = self.conversation_service.start_conversation()
            conversation_id = conversation.id
            print(f"  Created conversation: {conversation_id}")

        turn_results = []
        total_time_ms = 0

        for turn_num, turn in enumerate(test_case.turns, start=1):
            print(f"\n[Turn {turn_num}/{len(test_case.turns)}]")
            print(f"  Query: {turn.query}")

            # Build request
            request = ChatRequest(
                query=turn.query,
                k=5,
                conversation_id=conversation_id if use_conversation_context else None,
                turn_number=turn_num,  # Always use turn_num (defaults to 1 in standalone)
            )

            try:
                # Execute query
                response = self.chat_service.chat(request)

                print(f"  Response: {response.answer[:100]}...")
                print(f"  Time: {response.processing_time_ms}ms")

                # Evaluate turn
                turn_result = self.evaluate_turn(turn, response.answer, turn_num)
                turn_result["success"] = True
                turn_result["error"] = None
                turn_result["processing_time_ms"] = response.processing_time_ms
                turn_result["response_text"] = response.answer

                total_time_ms += response.processing_time_ms

                # Print evaluation
                print(f"  ✓ Term coverage: {turn_result['term_coverage']:.1%} ({turn_result['terms_found']}/{turn_result['total_terms']})")
                if turn.expected_entity:
                    status = "✓" if turn_result["entity_resolved"] else "✗"
                    print(f"  {status} Entity '{turn.expected_entity}': {'resolved' if turn_result['entity_resolved'] else 'NOT resolved'}")

                # Rate limit cooldown
                time.sleep(2)

            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                turn_result = {
                    "turn_number": turn_num,
                    "query": turn.query,
                    "success": False,
                    "error": str(e),
                    "term_coverage": 0.0,
                    "entity_resolved": False,
                    "processing_time_ms": 0,
                }

            turn_results.append(turn_result)

        # Calculate conversation-level metrics
        successful_turns = [r for r in turn_results if r.get("success", False)]

        avg_term_coverage = (
            sum(r["term_coverage"] for r in successful_turns) / len(successful_turns)
            if successful_turns else 0.0
        )

        # Pronoun resolution accuracy (turns with expected_entity)
        pronoun_turns = [
            r for r in successful_turns
            if test_case.turns[r["turn_number"] - 1].expected_entity is not None
        ]
        pronoun_resolution_rate = (
            sum(r["entity_resolved"] for r in pronoun_turns) / len(pronoun_turns)
            if pronoun_turns else None
        )

        return {
            "test_case_id": test_case.conversation_id,
            "title": test_case.title,
            "mode": "context_aware" if use_conversation_context else "standalone",
            "total_turns": len(test_case.turns),
            "successful_turns": len(successful_turns),
            "failed_turns": len(test_case.turns) - len(successful_turns),
            "avg_term_coverage": avg_term_coverage,
            "pronoun_resolution_rate": pronoun_resolution_rate,
            "total_time_ms": total_time_ms,
            "turn_results": turn_results,
            "conversation_id": conversation_id,
        }

    def run_evaluation(
        self,
        test_cases: list[ConversationTestCase] | None = None,
        compare_modes: bool = True,
    ) -> dict:
        """
        Run full evaluation on conversation test cases.

        Args:
            test_cases: List of test cases to evaluate (default: all)
            compare_modes: If True, run both context-aware and standalone modes

        Returns evaluation results with metrics.
        """
        if test_cases is None:
            test_cases = ALL_CONVERSATION_TEST_CASES

        print(f"\n{'#'*80}")
        print(f"# CONVERSATION-AWARE EVALUATION")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# Test cases: {len(test_cases)}")
        print(f"# Compare modes: {compare_modes}")
        print(f"{'#'*80}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": len(test_cases),
            "context_aware_results": [],
            "standalone_results": [],
        }

        # Evaluate in context-aware mode
        print(f"\n{'='*80}")
        print("PHASE 1: CONTEXT-AWARE MODE")
        print(f"{'='*80}")

        for test_case in test_cases:
            result = self.evaluate_conversation(test_case, use_conversation_context=True)
            results["context_aware_results"].append(result)

            # Cooldown between conversations
            time.sleep(3)

        # Evaluate in standalone mode (for comparison)
        if compare_modes:
            print(f"\n{'='*80}")
            print("PHASE 2: STANDALONE MODE (NO CONTEXT)")
            print(f"{'='*80}")

            for test_case in test_cases:
                result = self.evaluate_conversation(test_case, use_conversation_context=False)
                results["standalone_results"].append(result)

                # Cooldown between test cases
                time.sleep(3)

        # Generate summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """Print evaluation summary."""
        print(f"\n{'#'*80}")
        print("# EVALUATION SUMMARY")
        print(f"{'#'*80}")

        # Context-aware metrics
        context_results = results["context_aware_results"]

        total_turns_context = sum(r["total_turns"] for r in context_results)
        successful_turns_context = sum(r["successful_turns"] for r in context_results)

        avg_term_coverage_context = (
            sum(r["avg_term_coverage"] for r in context_results) / len(context_results)
            if context_results else 0.0
        )

        pronoun_results_context = [
            r for r in context_results
            if r["pronoun_resolution_rate"] is not None
        ]
        avg_pronoun_rate_context = (
            sum(r["pronoun_resolution_rate"] for r in pronoun_results_context) / len(pronoun_results_context)
            if pronoun_results_context else None
        )

        print("\n## CONTEXT-AWARE MODE")
        print(f"  Total turns: {total_turns_context}")
        print(f"  Successful turns: {successful_turns_context}/{total_turns_context} ({successful_turns_context/total_turns_context:.1%})")
        print(f"  Avg term coverage: {avg_term_coverage_context:.1%}")
        if avg_pronoun_rate_context is not None:
            print(f"  Pronoun resolution rate: {avg_pronoun_rate_context:.1%}")

        # Standalone metrics (if available)
        if results["standalone_results"]:
            standalone_results = results["standalone_results"]

            total_turns_standalone = sum(r["total_turns"] for r in standalone_results)
            successful_turns_standalone = sum(r["successful_turns"] for r in standalone_results)

            avg_term_coverage_standalone = (
                sum(r["avg_term_coverage"] for r in standalone_results) / len(standalone_results)
                if standalone_results else 0.0
            )

            pronoun_results_standalone = [
                r for r in standalone_results
                if r["pronoun_resolution_rate"] is not None
            ]
            avg_pronoun_rate_standalone = (
                sum(r["pronoun_resolution_rate"] for r in pronoun_results_standalone) / len(pronoun_results_standalone)
                if pronoun_results_standalone else None
            )

            print("\n## STANDALONE MODE (NO CONTEXT)")
            print(f"  Total turns: {total_turns_standalone}")
            print(f"  Successful turns: {successful_turns_standalone}/{total_turns_standalone} ({successful_turns_standalone/total_turns_standalone:.1%})")
            print(f"  Avg term coverage: {avg_term_coverage_standalone:.1%}")
            if avg_pronoun_rate_standalone is not None:
                print(f"  Pronoun resolution rate: {avg_pronoun_rate_standalone:.1%}")

            # Comparison
            print("\n## IMPROVEMENT WITH CONTEXT")
            coverage_improvement = avg_term_coverage_context - avg_term_coverage_standalone
            print(f"  Term coverage: {coverage_improvement:+.1%}")

            if avg_pronoun_rate_context is not None and avg_pronoun_rate_standalone is not None:
                pronoun_improvement = avg_pronoun_rate_context - avg_pronoun_rate_standalone
                print(f"  Pronoun resolution: {pronoun_improvement:+.1%}")

        print(f"\n{'#'*80}")
        print(f"# Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}\n")


def main():
    """Run conversation-aware evaluation."""
    evaluator = ConversationEvaluator()

    # Option 1: Evaluate all test cases
    # results = evaluator.run_evaluation(compare_modes=True)

    # Option 2: Evaluate only pronoun resolution test cases
    pronoun_cases = get_pronoun_test_cases()
    print(f"\nRunning {len(pronoun_cases)} pronoun resolution test cases...")
    results = evaluator.run_evaluation(test_cases=pronoun_cases, compare_modes=True)

    # Option 3: Evaluate only context carryover test cases
    # context_cases = get_context_test_cases()
    # results = evaluator.run_evaluation(test_cases=context_cases, compare_modes=True)

    return results


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
