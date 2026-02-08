"""
FILE: test_phase8_prompts.py
STATUS: Active
RESPONSIBILITY: Test Phase 8 faithfulness-constrained prompt variations
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import logging
import time
from pathlib import Path

from src.core.config import settings
from src.evaluation.test_cases import EVALUATION_TEST_CASES
from src.services.chat import ChatService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Phase 8 Prompt Variations
def _build_gemini_client():
    """Build Gemini client for response generation."""
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY required for Phase 8 testing (uses Gemini like Phase 5/7)")

    from google import genai
    logger.info("Using Gemini 2.0 Flash Lite for response generation")
    return genai.Client(api_key=settings.google_api_key)


def _generate_with_gemini(client, prompt: str) -> str:
    """Generate response with Gemini with retry logic."""
    max_retries = 6
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "resource" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt * 10, 120)  # Exponential backoff, max 2min
                    logger.warning(f"Gemini rate limit (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {max_retries} retries: {error_msg}")
                    raise
            else:
                logger.error(f"Gemini generation error: {error_msg}")
                raise


# Phase 8 Prompt Variations
PHASE8_PROMPTS = {
    "strict_constraints": """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

CRITICAL RULES - FOLLOW EXACTLY:
1. ONLY use facts explicitly stated in the CONTEXT below
2. NEVER add information from your general knowledge
3. If the CONTEXT doesn't contain the answer, say: "I don't have that information in the current data."
4. Quote statistics EXACTLY as they appear in the CONTEXT
5. Be direct and concise

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

ANSWER (following rules above):""",

    "citation_required": """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

You MUST follow these rules:
- Answer ONLY using information from the CONTEXT below
- When stating a fact or statistic, cite it as: [Source: <source_name>]
- If unsure or information is missing, say: "The available data doesn't specify this."
- Never infer or extrapolate beyond what's explicitly stated
- Keep answers factual and concise

CONTEXT:
---
{context}
---

QUESTION:
{question}

ANSWER WITH CITATIONS:""",

    "verification_layer": """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

STEP 1: Read the CONTEXT carefully
STEP 2: Answer the QUESTION using ONLY information from the CONTEXT
STEP 3: Verify each claim in your answer against the CONTEXT
STEP 4: Remove any claim not directly supported by the CONTEXT

CONTEXT:
---
{context}
---

QUESTION:
{question}

INSTRUCTIONS:
- Base your answer entirely on the context above
- If the context lacks necessary information, explicitly state what's missing
- Be precise with numbers and names
- Cite sources when mentioning statistics

ANSWER:""",
}


def test_prompt_on_subset(prompt_name: str, prompt_template: str, test_cases: list, gemini_client) -> dict:
    """Test a prompt variation on subset of queries using Gemini."""
    logger.info(f"\nTesting prompt: {prompt_name}")

    # ChatService only used for search (FAISS + query expansion)
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    results = []
    for tc in test_cases:
        query = tc.question
        category = tc.category.value

        # Search (uses Phase 7 query expansion)
        search_results = chat_service.search(query, k=5)

        # Build context
        context = "\n\n".join([
            f"[Source: {r.source}]\n{r.text}"
            for r in search_results
        ])

        # Generate response with Phase 8 prompt using Gemini
        prompt = prompt_template.format(
            app_name=settings.app_name,
            context=context,
            question=query
        )

        # Generate with Gemini (same LLM as Phase 5/7 evaluations)
        response = _generate_with_gemini(gemini_client, prompt)

        results.append({
            "question": query,
            "category": category,
            "ground_truth": tc.ground_truth,
            "response": response,
            "context_length": len(context),
            "search_results_count": len(search_results)
        })

        logger.info(f"  [{category}] {query[:60]}... → {len(response)} chars")

        # Small delay between requests to avoid rate limits
        time.sleep(2)

    return {
        "prompt_name": prompt_name,
        "prompt_template": prompt_template,
        "sample_count": len(results),
        "results": results
    }


def select_test_subset() -> list:
    """Select 12 diverse test cases for quick evaluation."""
    # Select 3 from each category, focusing on cases where Phase 7 had low faithfulness
    subset = []

    # Simple queries (indices 0-11)
    subset.extend([EVALUATION_TEST_CASES[i] for i in [0, 1, 2]])  # 3 simple

    # Complex queries (indices 12-23)
    subset.extend([EVALUATION_TEST_CASES[i] for i in [12, 13, 14]])  # 3 complex

    # Noisy queries (indices 24-34)
    subset.extend([EVALUATION_TEST_CASES[i] for i in [24, 25, 26]])  # 3 noisy

    # Conversational queries (indices 35-46)
    subset.extend([EVALUATION_TEST_CASES[i] for i in [35, 40, 45]])  # 3 conversational

    return subset


def main():
    """Test all Phase 8 prompt variations on subset."""
    print("\n" + "=" * 80)
    print("  PHASE 8: FAITHFULNESS-CONSTRAINED PROMPT TESTING")
    print("  (Using Gemini 2.0 Flash Lite - same as Phase 5/7)")
    print("=" * 80)

    # Build Gemini client (consistent with Phase 5/7 evaluations)
    gemini_client = _build_gemini_client()

    subset = select_test_subset()
    print(f"\nSelected {len(subset)} test cases (3 per category)")

    all_results = {}

    for prompt_name, prompt_template in PHASE8_PROMPTS.items():
        print(f"\n{'-' * 80}")
        print(f"  Testing: {prompt_name}")
        print(f"{'-' * 80}")

        result = test_prompt_on_subset(prompt_name, prompt_template, subset, gemini_client)
        all_results[prompt_name] = result

        # Save intermediate results
        output_path = Path(f"phase8_{prompt_name}_subset.json")
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Saved: {output_path}")

    print("\n" + "=" * 80)
    print("  SUBSET TEST COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Manually review responses in phase8_*_subset.json")
    print("2. Check if responses are more faithful (fewer hallucinations)")
    print("3. Select best prompt for full 47-sample evaluation")
    print("\nNote: Actual RAGAS faithfulness scores require running full evaluation")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
