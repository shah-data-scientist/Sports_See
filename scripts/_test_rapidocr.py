"""
FILE: _test_rapidocr.py
STATUS: Experimental
RESPONSIBILITY: Test RapidOCR extraction quality on Reddit PDFs
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Test RapidOCR extraction quality on Reddit PDFs.
Tests: initialization, text extraction, content quality verification.
"""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path

print("=" * 70)
print("  RapidOCR EXTRACTION QUALITY TEST")
print("=" * 70)

# Step 1: Test RapidOCR initialization
print("\n[1] Testing RapidOCR initialization...")
try:
    from rapidocr_onnxruntime import RapidOCR
    reader = RapidOCR()
    print("  OK: RapidOCR initialized successfully")
except Exception as e:
    print(f"  FAIL: RapidOCR init error: {e}")
    sys.exit(1)

# Step 2: Test PyMuPDF (fitz) for PDF → image conversion
print("\n[2] Testing PyMuPDF (fitz)...")
try:
    import fitz
    print(f"  OK: PyMuPDF version {fitz.version[0]}")
except Exception as e:
    print(f"  FAIL: fitz import error: {e}")
    sys.exit(1)

# Step 3: Test extraction on each Reddit PDF
import numpy as np
from PIL import Image

pdf_dir = Path("data/inputs")
pdfs = sorted(pdf_dir.glob("Reddit*.pdf"))
print(f"\n[3] Found {len(pdfs)} Reddit PDFs")

for pdf_path in pdfs:
    print(f"\n{'─' * 70}")
    print(f"  PDF: {pdf_path.name} ({pdf_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"{'─' * 70}")

    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        print(f"  Pages: {total_pages}")

        total_chars = 0
        total_lines = 0
        sample_texts = []

        for page_num in range(min(total_pages, 3)):  # Test first 3 pages only
            page = doc[page_num]

            # First try standard text extraction
            text = page.get_text()
            if text and len(text.strip()) > 50:
                print(f"  Page {page_num + 1}: Standard extraction = {len(text)} chars")
                total_chars += len(text)
                total_lines += len(text.strip().splitlines())
                if page_num == 0:
                    sample_texts.append(text[:300])
                continue

            # Fallback to OCR
            mat = fitz.Matrix(2, 2)  # 2x upscale
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img)

            result, elapsed = reader(img_np)
            if result:
                page_text = "\n".join([line[1] for line in result])
                elapsed_str = f"{elapsed[0]:.2f}" if isinstance(elapsed, list) else f"{elapsed:.2f}"
                print(f"  Page {page_num + 1}: OCR extraction = {len(page_text)} chars, "
                      f"{len(result)} text regions, {elapsed_str}s")
                total_chars += len(page_text)
                total_lines += len(result)
                if page_num == 0:
                    sample_texts.append(page_text[:300])
            else:
                print(f"  Page {page_num + 1}: OCR returned NO text!")

        doc.close()

        print(f"\n  Summary (first 3 pages): {total_chars} chars, {total_lines} lines")

        # Show sample text
        if sample_texts:
            print(f"  Sample (first 300 chars of page 1):")
            print(f"  {'─' * 50}")
            for line in sample_texts[0][:300].split("\n")[:10]:
                print(f"    {line[:80]}")
            print(f"  {'─' * 50}")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 70}")
print("  TEST COMPLETE")
print(f"{'=' * 70}")
