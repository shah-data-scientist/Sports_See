"""
FILE: data_pipeline.py
STATUS: Active
RESPONSIBILITY: Validated data preparation pipeline with Pydantic models at each stage
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import argparse
import logging
import random
import sys
import time

import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.core.config import settings
from src.core.observability import logfire
from src.models.document import DocumentChunk
from src.pipeline.models import (
    ChunkData,
    ChunkStageOutput,
    CleanedDocument,
    CleanStageOutput,
    EmbedStageOutput,
    IndexStageOutput,
    LoadStageInput,
    LoadStageOutput,
    PipelineResult,
    QualityCheckResult,
    RawDocument,
)
from src.repositories.vector_store import VectorStoreRepository
from src.services.embedding import EmbeddingService
from src.utils.data_loader import download_and_extract_zip, load_and_parse_files

logger = logging.getLogger(__name__)


class DataPipeline:
    """Validated data preparation pipeline.

    Each stage accepts and returns Pydantic models, ensuring
    type safety and validation at every boundary. All stages
    are instrumented with Logfire for observability.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStoreRepository | None = None,
        enable_quality_check: bool = False,
        quality_sample_size: int = 10,
    ):
        """Initialize the pipeline.

        Args:
            embedding_service: Service for generating embeddings.
            vector_store: Repository for FAISS index operations.
            enable_quality_check: Run LLM-powered chunk quality validation.
            quality_sample_size: Number of chunks to sample for quality check.
        """
        self._embedding_service = embedding_service or EmbeddingService()
        self._vector_store = vector_store or VectorStoreRepository()
        self._enable_quality_check = enable_quality_check
        self._quality_sample_size = quality_sample_size

    @logfire.instrument("Pipeline.load")
    def load(self, input_data: LoadStageInput) -> LoadStageOutput:
        """Stage 1: Load and parse documents from directory.

        Args:
            input_data: Validated load stage input with directory path.

        Returns:
            LoadStageOutput with parsed documents.
        """
        errors: list[str] = []

        if input_data.data_url:
            logger.info("Downloading data from: %s", input_data.data_url)
            success = download_and_extract_zip(input_data.data_url, input_data.input_dir)
            if not success:
                errors.append(f"Failed to download from {input_data.data_url}")

        raw_docs = load_and_parse_files(input_data.input_dir)

        documents = []
        for doc in raw_docs:
            content = doc.get("page_content", "")
            if not content or not content.strip():
                continue
            documents.append(
                RawDocument(
                    page_content=content,
                    metadata={
                        k: v
                        for k, v in doc.get("metadata", {}).items()
                        if isinstance(v, str | int | float)
                    },
                )
            )

        return LoadStageOutput(
            documents=documents,
            document_count=len(documents),
            errors=errors,
        )

    @logfire.instrument("Pipeline.clean")
    def clean(self, documents: list[RawDocument]) -> CleanStageOutput:
        """Stage 2: Clean and validate document text.

        Args:
            documents: Raw documents to clean.

        Returns:
            CleanStageOutput with cleaned documents.
        """
        cleaned: list[CleanedDocument] = []
        removed = 0

        for doc in documents:
            text = doc.page_content.strip()

            if len(text) < 10:
                removed += 1
                continue

            cleaned.append(
                CleanedDocument(
                    page_content=text,
                    metadata=doc.metadata,
                    char_count=len(text),
                )
            )

        total_chars = sum(d.char_count for d in cleaned)
        return CleanStageOutput(
            documents=cleaned,
            removed_count=removed,
            total_chars=total_chars,
        )

    @logfire.instrument("Pipeline.chunk")
    def chunk(
        self,
        documents: list[CleanedDocument],
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> ChunkStageOutput:
        """Stage 3: Split documents into overlapping chunks.

        Args:
            documents: Cleaned documents to split.
            chunk_size: Characters per chunk (default from settings).
            chunk_overlap: Overlap between chunks (default from settings).

        Returns:
            ChunkStageOutput with text chunks.
        """
        chunk_size = chunk_size or settings.chunk_size
        chunk_overlap = chunk_overlap or settings.chunk_overlap

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )

        all_chunks: list[ChunkData] = []
        doc_counter = 0

        for doc in documents:
            texts = splitter.split_text(doc.page_content)
            for i, chunk_text in enumerate(texts):
                all_chunks.append(
                    ChunkData(
                        id=f"{doc_counter}_{i}",
                        text=chunk_text,
                        metadata={
                            **doc.metadata,
                            "chunk_id_in_doc": i,
                            "total_chunks_in_doc": len(texts),
                        },
                    )
                )
            doc_counter += 1

        return ChunkStageOutput(
            chunks=all_chunks,
            chunk_count=len(all_chunks),
        )

    @logfire.instrument("Pipeline.quality_check")
    def quality_check(self, chunks: list[ChunkData]) -> list[QualityCheckResult]:
        """Stage 3b (optional): LLM-powered chunk quality validation.

        Samples a subset of chunks and validates them using a Pydantic AI Agent.

        Args:
            chunks: Chunks to validate.

        Returns:
            List of quality check results for sampled chunks.
        """
        from src.pipeline.quality_agent import check_chunk_quality

        sample = random.sample(
            chunks,
            min(self._quality_sample_size, len(chunks)),
        )

        results: list[QualityCheckResult] = []
        for chunk in sample:
            result = check_chunk_quality(chunk.id, chunk.text)
            results.append(result)
            logger.info(
                "Chunk %s quality: score=%.2f coherent=%s",
                chunk.id,
                result.quality_score,
                result.is_coherent,
            )

        return results

    @logfire.instrument("Pipeline.embed")
    def embed(self, texts: list[str]) -> tuple[EmbedStageOutput, "np.ndarray"]:
        """Stage 4: Generate embeddings for chunk texts.

        Args:
            texts: List of chunk texts to embed.

        Returns:
            Tuple of (metadata output, embeddings numpy array).
        """
        embeddings = self._embedding_service.embed_batch(texts)

        output = EmbedStageOutput(
            embedding_count=embeddings.shape[0],
            embedding_dimension=embeddings.shape[1],
        )
        return output, embeddings

    @logfire.instrument("Pipeline.index")
    def index(
        self,
        chunks: list[ChunkData],
        embeddings: "np.ndarray",
    ) -> IndexStageOutput:
        """Stage 5: Build and save FAISS index.

        Args:
            chunks: Document chunks to index.
            embeddings: Embeddings array (n_chunks x dim).

        Returns:
            IndexStageOutput with index metadata.
        """
        doc_chunks = [DocumentChunk(id=c.id, text=c.text, metadata=c.metadata) for c in chunks]

        self._vector_store.build_index(doc_chunks, embeddings)
        self._vector_store.save()

        return IndexStageOutput(
            index_size=self._vector_store.index_size,
            index_path=str(settings.faiss_index_path),
            chunks_path=str(settings.document_chunks_path),
        )

    @logfire.instrument("Pipeline.run")
    def run(
        self,
        input_dir: str | None = None,
        data_url: str | None = None,
    ) -> PipelineResult:
        """Run the complete data preparation pipeline.

        Args:
            input_dir: Directory containing source documents.
            data_url: Optional URL to download documents.

        Returns:
            PipelineResult with full execution summary.
        """
        start = time.time()
        errors: list[str] = []

        # Stage 1: Load
        load_input = LoadStageInput(
            input_dir=input_dir or settings.input_dir,
            data_url=data_url,
        )
        load_out = self.load(load_input)
        errors.extend(load_out.errors)

        if not load_out.documents:
            elapsed = (time.time() - start) * 1000
            return PipelineResult(
                documents_loaded=0,
                documents_cleaned=0,
                chunks_created=0,
                embeddings_generated=0,
                index_size=0,
                processing_time_ms=elapsed,
                errors=errors + ["No documents found"],
            )

        # Stage 2: Clean
        clean_out = self.clean(load_out.documents)

        # Stage 3: Chunk
        chunk_out = self.chunk(clean_out.documents)

        # Stage 3b: Quality check (optional)
        quality_passed = None
        quality_total = None
        if self._enable_quality_check and chunk_out.chunks:
            quality_results = self.quality_check(chunk_out.chunks)
            quality_total = len(quality_results)
            quality_passed = sum(1 for r in quality_results if r.is_coherent)

        # Stage 4: Embed
        texts = [c.text for c in chunk_out.chunks]
        embed_out, embeddings = self.embed(texts)

        # Stage 5: Index
        index_out = self.index(chunk_out.chunks, embeddings)

        elapsed = (time.time() - start) * 1000
        return PipelineResult(
            documents_loaded=load_out.document_count,
            documents_cleaned=len(clean_out.documents),
            chunks_created=chunk_out.chunk_count,
            embeddings_generated=embed_out.embedding_count,
            index_size=index_out.index_size,
            quality_checks_passed=quality_passed,
            quality_checks_total=quality_total,
            processing_time_ms=elapsed,
            errors=errors,
        )


def main() -> int:
    """CLI entry point for the data preparation pipeline.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Run the validated data preparation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  poetry run python -m src.pipeline.data_pipeline
  poetry run python -m src.pipeline.data_pipeline --input-dir custom/inputs
  poetry run python -m src.pipeline.data_pipeline --rebuild
  poetry run python -m src.pipeline.data_pipeline --data-url https://example.com/data.zip
        """,
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=settings.input_dir,
        help=f"Directory containing source documents (default: {settings.input_dir})",
    )
    parser.add_argument(
        "--data-url",
        type=str,
        default=None,
        help="URL to download documents from (ZIP file)",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild index from scratch (delete existing)",
    )

    args = parser.parse_args()

    try:
        repository = VectorStoreRepository()

        if not args.rebuild and repository.load():
            logger.info(
                "Existing index loaded with %d vectors. Use --rebuild to rebuild.",
                repository.index_size,
            )
            return 0

        if args.rebuild:
            logger.info("Rebuild requested - deleting existing index")
            repository.delete_files()

        pipeline = DataPipeline(vector_store=repository)
        result = pipeline.run(input_dir=args.input_dir, data_url=args.data_url)

        if result.errors:
            for err in result.errors:
                logger.warning("Pipeline warning: %s", err)

        logger.info("=" * 60)
        logger.info("Pipeline completed!")
        logger.info("  Documents loaded: %d", result.documents_loaded)
        logger.info("  Documents cleaned: %d", result.documents_cleaned)
        logger.info("  Chunks created: %d", result.chunks_created)
        logger.info("  Embeddings generated: %d", result.embeddings_generated)
        logger.info("  Index size: %d vectors", result.index_size)
        logger.info("  Time elapsed: %.2f seconds", result.processing_time_ms / 1000)
        logger.info("=" * 60)

        return 0 if result.documents_loaded > 0 else 1

    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return 130

    except Exception as e:
        logger.exception("Pipeline failed with error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
