"""
FILE: vector_models.py
STATUS: Active
RESPONSIBILITY: Pydantic models for Vector/RAGAS evaluation (test cases, samples, metrics, reports)
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu
"""

from enum import Enum

from pydantic import BaseModel, Field


class TestCategory(str, Enum):
    """Category of evaluation test case."""

    SIMPLE = "simple"
    COMPLEX = "complex"
    NOISY = "noisy"
    CONVERSATIONAL = "conversational"


class EvaluationTestCase(BaseModel):
    """A single RAGAS evaluation test case."""

    question: str = Field(min_length=1, description="NBA business question")
    ground_truth: str = Field(min_length=1, description="Reference answer")
    category: TestCategory = Field(description="Difficulty category")
    conversation_thread: str | None = Field(
        default=None,
        description="Conversation thread ID (queries with same ID belong to same conversation)"
    )


class EvaluationSample(BaseModel):
    """A fully populated sample ready for RAGAS evaluation."""

    user_input: str
    response: str
    retrieved_contexts: list[str]
    reference: str
    category: TestCategory


class MetricScores(BaseModel):
    """Scores for RAGAS metrics."""

    faithfulness: float | None = None
    answer_relevancy: float | None = None
    context_precision: float | None = None
    context_recall: float | None = None


class CategoryResult(BaseModel):
    """Aggregated results for a test category."""

    category: TestCategory
    count: int = Field(ge=0)
    avg_faithfulness: float | None = None
    avg_answer_relevancy: float | None = None
    avg_context_precision: float | None = None
    avg_context_recall: float | None = None


class EvaluationReport(BaseModel):
    """Complete evaluation report with category breakdown."""

    overall_scores: MetricScores
    category_results: list[CategoryResult]
    sample_count: int = Field(ge=0)
    model_used: str
