"""
FILE: hybrid_models.py
STATUS: Active
RESPONSIBILITY: Pydantic models for Hybrid evaluation (vector retrieval, hybrid samples, integration metrics, reports)
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu
"""

from typing import Any

from pydantic import BaseModel, Field

from src.evaluation.models.sql_models import QueryType, SQLAccuracyMetrics, SQLExecutionResult


class VectorRetrievalResult(BaseModel):
    """Result of vector search."""

    retrieved_contexts: list[str] = Field(default_factory=list, description="Retrieved chunks")
    retrieval_scores: list[float] = Field(default_factory=list, description="Similarity scores")
    sources: list[str] = Field(default_factory=list, description="Source files")


class HybridEvaluationSample(BaseModel):
    """Complete evaluation sample for hybrid queries."""

    user_input: str = Field(description="User question")
    query_type: QueryType = Field(description="Detected query type")

    # SQL component
    sql_result: SQLExecutionResult | None = Field(
        default=None, description="SQL execution result (if applicable)"
    )

    # Vector component
    vector_result: VectorRetrievalResult | None = Field(
        default=None, description="Vector retrieval result (if applicable)"
    )

    # Final response
    response: str = Field(description="Final generated answer")
    reference: str = Field(description="Ground truth answer")

    # Metadata
    category: str = Field(description="Test case category")


class HybridIntegrationMetrics(BaseModel):
    """Metrics for hybrid query integration quality."""

    sql_component_used: bool = Field(
        description="SQL results were used in final answer"
    )
    vector_component_used: bool = Field(
        description="Vector context was used in final answer"
    )
    components_blended: bool = Field(
        description="Both components integrated coherently (not just concatenated)"
    )
    answer_complete: bool = Field(
        description="Answer addresses both statistical and contextual aspects"
    )

    @property
    def integration_score(self) -> float:
        """Compute integration quality score (0-1)."""
        scores = [
            self.sql_component_used,
            self.vector_component_used,
            self.components_blended,
            self.answer_complete,
        ]
        return sum(scores) / len(scores)


class HybridEvaluationMetrics(BaseModel):
    """Complete metrics for hybrid query evaluation."""

    # SQL component (if applicable)
    sql_accuracy: SQLAccuracyMetrics | None = Field(
        default=None, description="SQL accuracy metrics"
    )

    # Vector component (if applicable)
    vector_faithfulness: float | None = Field(
        default=None, description="RAGAS faithfulness score"
    )
    vector_context_precision: float | None = Field(
        default=None, description="RAGAS context precision"
    )
    vector_context_recall: float | None = Field(
        default=None, description="RAGAS context recall"
    )

    # Integration metrics (for HYBRID queries)
    integration: HybridIntegrationMetrics | None = Field(
        default=None, description="Integration quality metrics"
    )

    # Overall metrics
    answer_relevancy: float = Field(description="Answer relevancy (RAGAS or custom)")
    answer_correctness: float = Field(
        description="Overall answer correctness (0-1, human or LLM-judged)"
    )

    @property
    def overall_score(self) -> float:
        """Compute overall evaluation score."""
        scores = []

        # SQL component (weight: 0.4 if present)
        if self.sql_accuracy:
            scores.append(self.sql_accuracy.overall_score * 0.4)

        # Vector component (weight: 0.4 if present)
        if self.vector_faithfulness is not None:
            vector_score = (
                self.vector_faithfulness * 0.5
                + (self.vector_context_precision or 0) * 0.25
                + (self.vector_context_recall or 0) * 0.25
            )
            scores.append(vector_score * 0.4)

        # Integration (weight: 0.2 for HYBRID queries)
        if self.integration:
            scores.append(self.integration.integration_score * 0.2)

        # Answer quality (always included, weight: 0.2-0.6 depending on components)
        answer_weight = 1.0 - sum([0.4 if self.sql_accuracy else 0,
                                   0.4 if self.vector_faithfulness else 0,
                                   0.2 if self.integration else 0])
        scores.append((self.answer_relevancy + self.answer_correctness) / 2 * answer_weight)

        return sum(scores) if scores else 0.0


class HybridEvaluationReport(BaseModel):
    """Complete evaluation report for SQL/Hybrid queries."""

    overall_metrics: HybridEvaluationMetrics
    category_results: list[dict[str, Any]] = Field(default_factory=list)
    sample_count: int = Field(ge=0)
    sql_query_count: int = Field(ge=0, description="Number of SQL queries evaluated")
    hybrid_query_count: int = Field(ge=0, description="Number of hybrid queries evaluated")
    contextual_query_count: int = Field(ge=0, description="Number of vector-only queries")
