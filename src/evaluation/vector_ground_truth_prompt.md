# Vector Ground Truth Establishment — Methodology & Prompt

## Purpose

This document describes the methodology used to establish ground truth for the 75 vector (contextual) test cases in `src/evaluation/test_cases/vector_test_cases.py`. Unlike SQL and Hybrid test cases whose ground truth is verified against the database, vector test cases use **descriptive expectations** grounded in the actual document content stored in the FAISS vector index.

## Source Documents

The vector store contains OCR-extracted content from 4 Reddit PDF files:

| Document | Post Title | Author | Upvotes | Comments |
|----------|-----------|--------|---------|----------|
| Reddit 1.pdf | "Who are teams in the playoffs that have impressed you?" | u/MannerSuperb | 31 | 236 |
| Reddit 2.pdf | "How is it that the two best teams in the playoffs..." | u/mokaloca82 | 457 | 440 |
| Reddit 3.pdf | "Reggie Miller is the most efficient first option..." | u/hqppp | 1,300 | 11,515 max comment upvotes |
| Reddit 4.pdf | "Which NBA team did not have home court advantage..." | u/DonT012 | 272 | 51 |

Source location: `data/inputs/` (PDF files processed through OCR pipeline)

## Methodology

Ground truth was established using an **LLM-assisted approach**:

1. **Extract**: OCR-extracted text from all 4 Reddit PDFs was provided to an LLM (Claude)
2. **Analyze**: The LLM read the full content of each document, including post text, comments, upvote counts, and user metadata
3. **Generate**: For each test question, the LLM generated a ground truth description based solely on what exists in the documents
4. **Validate**: Each ground truth was manually reviewed to ensure it accurately references content present in the source documents

## Prompt Template

The following prompt was used to generate ground truth expectations. Provide this prompt along with the full OCR content of all 4 Reddit PDFs:

```
You are helping establish ground truth for a RAG (Retrieval-Augmented Generation) evaluation system. I will provide you with the full text content of 4 Reddit discussion PDFs that have been OCR-extracted and stored in a FAISS vector index.

Your task: For each test question I provide, generate a ground truth description that specifies:

1. **Expected source document(s)**: Which Reddit PDF(s) should the retrieval system find? Reference by filename (e.g., "Reddit 1.pdf") and include the post title.
2. **Expected content themes**: What specific topics, names, statistics, or arguments from the source document should appear in the retrieved context?
3. **Expected metadata**: Include post author, upvote count, and comment count where relevant — these are used for retrieval boosting.
4. **Expected similarity range**: Estimate a cosine similarity percentage range (e.g., "75-85%") based on how directly the question maps to the source content.
5. **Expected retrieval behavior**: How many chunks should be retrieved (e.g., "2-5 chunks"), and should boosting (upvotes, engagement) affect ranking?

IMPORTANT RULES:
- ONLY reference content that actually exists in the provided documents
- Do NOT invent or assume content not present in the OCR text
- If a question asks about something not covered in any document, state that explicitly
- Include specific names, numbers, and quotes from the documents to make ground truth verifiable
- For engagement-related questions, reference the actual upvote/comment counts

FORMAT each ground truth as a single paragraph starting with "Should retrieve..." that can be used directly as the `ground_truth` field in an EvaluationTestCase.

Here are the source documents:
[PASTE FULL OCR CONTENT OF ALL 4 REDDIT PDFs HERE]

Here are the test questions:
[LIST OF QUESTIONS]
```

## Ground Truth Format

Each test case ground truth follows this structure:

```python
EvaluationTestCase(
    question="What do Reddit users think about teams that impressed in the playoffs?",
    ground_truth=(
        "Should retrieve Reddit 1.pdf: 'Who are teams in the playoffs that have impressed you?' "
        "by u/MannerSuperb (31 upvotes, 236 comments). Expected teams mentioned: Magic "
        "(Paolo Banchero, Franz Wagner), Indiana Pacers, Minnesota Timberwolves (Anthony Edwards), "
        "Pistons. Comments discuss exceeding expectations, young talent, and surprising playoff "
        "performances. Expected sources: 2-5 chunks from Reddit 1.pdf with 75-85% similarity."
    ),
    category=TestCategory.SIMPLE,
)
```

Key elements in every ground truth:
- Source document identification (filename + post title + author)
- Engagement metadata (upvotes, comments) for boosting verification
- Specific content expectations (names, stats, themes)
- Similarity range estimate
- Expected chunk count

## Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| SIMPLE | 20 | Direct retrieval from a single document |
| COMPLEX | 18 | Multi-document retrieval, cross-referencing, or analytical |
| NOISY | 25 | Off-topic, adversarial, XSS, or slang queries |
| CONVERSATIONAL | 12 | Follow-up queries with pronouns requiring context |

## How to Update Ground Truth

If the vector store content changes (new documents added, chunks re-processed):

1. Re-extract OCR text from all source documents in `data/inputs/`
2. Use the prompt template above with the updated document content
3. Generate new ground truth descriptions for affected test cases
4. Review each generated ground truth against the actual document content
5. Update `src/evaluation/test_cases/vector_test_cases.py` with revised ground truth
6. Run vector evaluation to verify retrieval quality: `poetry run python -m src.evaluation.runners.run_vector_evaluation`

## Validation

Vector ground truth is validated during evaluation via RAGAS metrics:
- **Faithfulness**: Does the LLM response stay faithful to retrieved context?
- **Answer Relevancy**: Is the response relevant to the question?
- **Context Precision**: Are the retrieved chunks relevant to the question?
- **Context Recall**: Did retrieval find all relevant chunks?

See `src/evaluation/analysis/vector_quality_analysis.py` for metric calculation details.
