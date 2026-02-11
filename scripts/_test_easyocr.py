"""
FILE: _test_easyocr.py
STATUS: Experimental
RESPONSIBILITY: Test easyOCR extraction on Reddit PDFs
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Test easyOCR extraction on first Reddit PDF (page 1 only).
"""
import sys
import io
import os

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

print("=" * 60)
print("  easyOCR EXTRACTION TEST")
print("=" * 60)

# Step 1: Test easyOCR initialization
print("\n[1] Testing easyOCR initialization...")
try:
    import easyocr
    reader = easyocr.Reader(["en", "fr"], gpu=False)
    print("  OK: easyOCR initialized (en, fr)")
except Exception as e:
    print(f"  FAIL: easyOCR init error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test PyMuPDF
print("\n[2] Testing PyMuPDF (fitz)...")
try:
    import fitz
    print(f"  OK: PyMuPDF version {fitz.version[0]}")
except Exception as e:
    print(f"  FAIL: fitz import error: {e}")
    sys.exit(1)

# Step 3: Extract page 1 of Reddit 1.pdf
import numpy as np
from PIL import Image
from pathlib import Path

pdf_path = Path("data/inputs/Reddit 1.pdf")
print(f"\n[3] Extracting page 1 of {pdf_path.name}...")

try:
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_np = np.array(img)

    print(f"  Image size: {img_np.shape}")
    result = reader.readtext(img_np)
    print(f"  Text regions found: {len(result)}")

    if result:
        page_text = "\n".join([line[1] for line in result])
        print(f"  Total chars: {len(page_text)}")
        print(f"\n  --- First 500 chars ---")
        for line in page_text[:500].split("\n")[:15]:
            print(f"    {line[:80]}")
        print(f"  --- End ---")
    else:
        print("  WARNING: No text extracted!")

    doc.close()
    print("\n  PASS: easyOCR extraction works")
except Exception as e:
    print(f"\n  FAIL: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'=' * 60}")
print("  TEST COMPLETE")
print(f"{'=' * 60}")
