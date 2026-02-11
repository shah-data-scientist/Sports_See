"""
FILE: _quick_api_validation.py
STATUS: Active
RESPONSIBILITY: Quick validation of API-based SQL evaluation (6 test cases) with ground truth comparison
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import os
import re
import sys
import time
from pathlib import Path

from starlette.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.dependencies import get_chat_service
from src.api.main import create_app
from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.models.feedback import ChatInteractionCreate

# Rate limit delay (Gemini free tier: 15 RPM)
RATE_LIMIT_DELAY = 12  # seconds between requests


def _check_ground_truth(answer: str, ground_truth_data: dict | list) -> tuple[bool, str]:
    """Check if the API answer contains the expected ground truth values.

    Returns (match, details_string).
    """
    answer_lower = answer.lower()
    checks = []
    all_pass = True

    if isinstance(ground_truth_data, dict):
        items = [ground_truth_data]
    else:
        items = ground_truth_data

    for item in items:
        for key, expected in item.items():
            if key == "player_count":
                # Just check the number appears
                if str(expected) in answer:
                    checks.append(f"  ✓ {key}={expected} found")
                else:
                    checks.append(f"  ✗ {key}={expected} NOT FOUND")
                    all_pass = False
            elif key == "name":
                # Check name (case-insensitive, partial match for last name)
                parts = str(expected).lower().split()
                last_name = parts[-1] if parts else str(expected).lower()
                if last_name in answer_lower:
                    checks.append(f"  ✓ name='{expected}' found")
                else:
                    checks.append(f"  ✗ name='{expected}' NOT FOUND")
                    all_pass = False
            elif isinstance(expected, (int, float)):
                # Check numeric value (allow comma-formatted: "2,485" matches 2485)
                str_val = str(expected)
                # Also check comma-formatted version (e.g., 2485 -> "2,485")
                if expected >= 1000:
                    comma_val = f"{expected:,}"
                else:
                    comma_val = str_val
                if str_val in answer or comma_val in answer:
                    checks.append(f"  ✓ {key}={expected} found")
                else:
                    checks.append(f"  ✗ {key}={expected} NOT FOUND in answer")
                    all_pass = False

    return all_pass, "\n".join(checks)


def _run_validation(client: TestClient) -> None:
    """Run validation tests with given client."""

    # Test cases: (index_in_SQL_TEST_CASES, needs_conv, turn_number, description)
    test_specs = [
        (0, None, None, "Simple query"),
        (7, None, None, "Player stats with unicode"),
        (19, None, None, "Comparison query"),
        (40, True, 1, "Conversational initial"),
        (41, True, 1, "Conversational casual"),
        (44, "use_conv_40", 2, "Conversational follow-up"),
    ]

    # Store conversation IDs
    conversation_ids = {}
    results = []

    for spec_idx, (tc_idx, needs_conv, turn_number, description) in enumerate(test_specs):
        tc = SQL_TEST_CASES[tc_idx]
        question = tc.question
        ground_truth = tc.ground_truth_data
        ground_truth_answer = tc.ground_truth_answer

        print(f"\n{'=' * 80}")
        print(f"Test Case {tc_idx}: {description}")
        print(f"Question: {question}")
        print(f"Expected: {ground_truth_answer[:120]}")
        print("-" * 80)

        # Handle conversation creation or reuse
        conversation_id = None
        if needs_conv is True:
            conv_response = client.post("/api/v1/conversations", json={})
            if conv_response.status_code == 201:
                conversation_id = conv_response.json()["id"]
                conversation_ids[f"conv_{tc_idx}"] = conversation_id
                print(f"Created conversation: {conversation_id}")
            else:
                print(f"ERROR: Failed to create conversation: {conv_response.status_code}")
                continue
        elif needs_conv == "use_conv_40":
            conversation_id = conversation_ids.get("conv_40")
            if not conversation_id:
                print("ERROR: Conversation from case 40 not found!")
                continue
            print(f"Using existing conversation: {conversation_id}")

        # Build request payload
        payload = {"query": question}
        if conversation_id:
            payload["conversation_id"] = conversation_id

        # Make API request with retry for 429
        max_retries = 2
        for attempt in range(max_retries + 1):
            start_time = time.time()
            response = client.post("/api/v1/chat", json=payload)
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 500 and "429" in response.text and attempt < max_retries:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited (429). Retrying in {wait}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
                continue
            break

        # Parse response
        status_code = response.status_code
        if status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            processing_time = data.get("processing_time_ms", 0)

            print(f"Status: {status_code} ✓")
            print(f"Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"Processing time: {processing_time:.0f}ms | Total: {elapsed_ms:.0f}ms")

            # Check ground truth
            if ground_truth:
                gt_match, gt_details = _check_ground_truth(answer, ground_truth)
                print(f"Ground Truth Match: {'✓ PASS' if gt_match else '✗ FAIL'}")
                print(gt_details)
            else:
                gt_match = True
                print("Ground Truth: N/A (no ground_truth_data)")

            # Store interaction for conversational follow-ups
            if conversation_id and needs_conv is True:
                try:
                    chat_service = get_chat_service()
                    interaction = ChatInteractionCreate(
                        query=question,
                        response=answer,
                        sources=[s.get("source", "") for s in sources],
                        processing_time_ms=int(processing_time),
                        conversation_id=conversation_id,
                        turn_number=turn_number or 1,
                    )
                    chat_service.feedback_repository.save_interaction(interaction)
                    print(f"Stored interaction (turn {turn_number})")
                except Exception as e:
                    print(f"WARNING: Failed to store interaction: {e}")

            results.append({
                "case": tc_idx,
                "description": description,
                "success": True,
                "gt_match": gt_match,
                "answer": answer[:100],
                "expected": ground_truth_answer[:100] if ground_truth_answer else "",
                "processing_time": processing_time,
            })
        else:
            error_msg = response.text if response.text else "No error message"
            print(f"Status: {status_code} ✗")
            print(f"Error: {error_msg[:200]}")

            results.append({
                "case": tc_idx,
                "description": description,
                "success": False,
                "gt_match": False,
                "answer": "",
                "expected": ground_truth_answer[:100] if ground_truth_answer else "",
                "processing_time": 0,
                "error": error_msg[:100],
            })

        # Rate limiting
        if spec_idx < len(test_specs) - 1:
            print(f"\nWaiting {RATE_LIMIT_DELAY} seconds (rate limiting)...")
            time.sleep(RATE_LIMIT_DELAY)

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY — API vs Ground Truth")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    gt_matches = sum(1 for r in results if r["gt_match"])
    total = len(results)

    print(f"\nAPI Success Rate: {successful}/{total}")
    print(f"Ground Truth Match: {gt_matches}/{total}")
    print()

    for r in results:
        api_icon = "✓" if r["success"] else "✗"
        gt_icon = "✓" if r["gt_match"] else "✗"
        print(f"  Case {r['case']:2d} | API:{api_icon} GT:{gt_icon} | {r['description']:30s}")
        if r["success"]:
            print(f"         | Answer:   {r['answer']}")
            print(f"         | Expected: {r['expected']}")
        else:
            print(f"         | Error: {r.get('error', 'Unknown')}")
        print()

    print("=" * 80)
    if gt_matches == total:
        print("✓ ALL GROUND TRUTH CHECKS PASSED — API results match expected data")
    else:
        print(f"✗ {total - gt_matches} GROUND TRUTH CHECK(S) FAILED")
    print("=" * 80)


def main():
    """Main entry point."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

    print("=" * 80)
    print("API-Based SQL Evaluation — Ground Truth Validation")
    print("=" * 80)
    print()

    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        _run_validation(client)


if __name__ == "__main__":
    main()
