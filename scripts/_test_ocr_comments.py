"""
FILE: _test_ocr_comments.py
STATUS: Experimental
RESPONSIBILITY: Diagnostic test for OCR comment extraction on Reddit PDFs
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Diagnostic: Test OCR comment extraction on Reddit PDFs.
Shows full OCR text for page 2 of each PDF (page 1 is usually the post)
and counts how many 'Répondre'/'Rpondre' markers exist vs extracted comments.
"""
import sys
import io
import re
from pathlib import Path

import numpy as np
from PIL import Image

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from rapidocr_onnxruntime import RapidOCR
from src.pipeline.reddit_chunker import RedditThreadChunker

import fitz

reader = RapidOCR()
chunker = RedditThreadChunker()

pdf_dir = Path("data/inputs")
pdfs = sorted(pdf_dir.glob("Reddit*.pdf"))

for pdf_path in pdfs:
    print(f"\n{'=' * 80}")
    print(f"  {pdf_path.name}")
    print(f"{'=' * 80}")

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    # Extract ALL pages' text
    full_text = ""
    for page_num in range(total_pages):
        page = doc[page_num]

        # Try standard extraction first
        text = page.get_text()
        if text and len(text.strip()) > 50:
            full_text += text + "\n"
            continue

        # Fallback to OCR
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_np = np.array(img)
        result, _elapsed = reader(img_np)
        if result:
            page_text = "\n".join([line[1] for line in result])
            full_text += page_text + "\n"

    doc.close()

    print(f"  Total OCR text: {len(full_text)} chars, {len(full_text.splitlines())} lines")

    # Count Répondre/Rpondre markers (max possible comments)
    repondre_count = len(re.findall(r"R[ée]pondre", full_text, re.IGNORECASE))
    partager_count = len(re.findall(r"Partager", full_text, re.IGNORECASE))
    print(f"  'Répondre/Rpondre' markers: {repondre_count}")
    print(f"  'Partager' markers: {partager_count}")

    # Test the chunker's comment extraction
    cleaned = chunker.filter_advertisements(full_text)
    comments = chunker.extract_comments(cleaned)
    print(f"  Extracted comments: {len(comments)}")

    if comments:
        for c in comments[:3]:
            print(f"    - u/{c['author']} ({c['upvotes']} upvotes): {c['text'][:80]}...")

    # Show a sample of the OCR text around "Répondre" to debug pattern matching
    print(f"\n  --- Sample OCR around 'Répondre' markers ---")
    for m in list(re.finditer(r"R[ée]pondre", full_text, re.IGNORECASE))[:3]:
        start = max(0, m.start() - 200)
        end = min(len(full_text), m.end() + 50)
        snippet = full_text[start:end]
        print(f"  ...{repr(snippet)}...")
        print()

    # Also show chunks that would be created
    chunks = chunker.chunk_reddit_thread(full_text, str(pdf_path))
    print(f"  Chunks created: {len(chunks)}")
    for chunk in chunks:
        print(f"    Chunk {chunk.metadata.get('chunk_index', '?')}: "
              f"{chunk.metadata.get('comments_in_chunk', 0)} comments, "
              f"{len(chunk.text)} chars")

print(f"\n{'=' * 80}")
print("  DIAGNOSTIC COMPLETE")
print(f"{'=' * 80}")
