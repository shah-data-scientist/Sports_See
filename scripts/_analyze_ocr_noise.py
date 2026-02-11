"""
FILE: _analyze_ocr_noise.py
STATUS: Experimental
RESPONSIBILITY: Comprehensive analysis of OCR noise patterns across all 4 Reddit PDFs
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import io
import os
import pickle
import re
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ocr_dir = Path("data/vector/_ocr_per_file")

# Collect all lines from all PDFs
all_lines = []
per_pdf_lines = {}

for ocr_file in sorted(ocr_dir.glob("Reddit*.pkl")):
    text = pickle.loads(ocr_file.read_bytes())
    lines = text.split("\n")
    per_pdf_lines[ocr_file.stem] = lines
    all_lines.extend([(ocr_file.stem, i, line) for i, line in enumerate(lines)])

total_lines = len(all_lines)
print(f"Total lines across all 4 PDFs: {total_lines}")
print()

# ============================================================
# CATEGORY 1: Page headers / dates
# ============================================================
print("=" * 70)
print("CATEGORY 1: Page headers / date stamps")
print("=" * 70)
date_pattern = re.compile(r"^\d{2}/\d{2}/\d{4}\s+\d{2}[:.]\d{2}")
date_lines = [(src, i, l) for src, i, l in all_lines if date_pattern.match(l)]
print(f"Found {len(date_lines)} date header lines")
for src, i, l in date_lines[:5]:
    print(f"  [{src}:{i}] {l}")

# ============================================================
# CATEGORY 2: Subreddit markers (rInba, r/nba)
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 2: Subreddit markers (rInba / r/nba)")
print("=" * 70)
sub_pattern = re.compile(r"^r/?I?n?ba\s*$", re.IGNORECASE)
sub_lines = [(src, i, l) for src, i, l in all_lines if sub_pattern.match(l.strip())]
print(f"Found {len(sub_lines)} standalone subreddit markers")
for src, i, l in sub_lines[:5]:
    print(f"  [{src}:{i}] '{l.strip()}'")

# ============================================================
# CATEGORY 3: Reddit UI elements
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 3: Reddit UI elements")
print("=" * 70)
ui_patterns = {
    "Partager": re.compile(r"^Partager\s*$"),
    "Répondre": re.compile(r"^R[éeè]pondre\s*$", re.IGNORECASE),
    "upvotes/commentaires": re.compile(r"^\d[\d,.\s]*k?\s+(upvote|commentaire|comment)", re.IGNORECASE),
    "Sponsorisé": re.compile(r"Sponsoris", re.IGNORECASE),
    "En savoir plus": re.compile(r"^En savoir plus\s*$", re.IGNORECASE),
    "Officiel": re.compile(r"^Officiel\s*$", re.IGNORECASE),
    "Comm. du top": re.compile(r"^Comm\.\s*du", re.IGNORECASE),
    "Auteur-rice": re.compile(r"^Auteur", re.IGNORECASE),
    "réponses supplémentaires": re.compile(r"r[ée]ponses?\s+suppl[ée]mentaire", re.IGNORECASE),
    "Afficher": re.compile(r"^Afficher\s", re.IGNORECASE),
    "Voir": re.compile(r"^Voir\s+\d+", re.IGNORECASE),
    "supprimé": re.compile(r"^\[supprim", re.IGNORECASE),
}
for name, pat in ui_patterns.items():
    matches = [(src, i, l) for src, i, l in all_lines if pat.search(l)]
    print(f"  {name}: {len(matches)} lines")
    for src, i, l in matches[:3]:
        print(f"    [{src}:{i}] {l.strip()[:80]}")

# ============================================================
# CATEGORY 4: Ad/sponsor content
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 4: Advertisements / sponsors")
print("=" * 70)
ad_patterns = {
    "Xometry": re.compile(r"xometry", re.IGNORECASE),
    "IBM": re.compile(r"^IBM\s*$|^ibm\s*$"),
    "adidas": re.compile(r"adidas", re.IGNORECASE),
    "doubleclick": re.compile(r"doubleclick", re.IGNORECASE),
    "ad URLs": re.compile(r"^(pages|ad)\.\w+\.\w+", re.IGNORECASE),
    "S'inscrire": re.compile(r"^S'inscrire\s*$", re.IGNORECASE),
    "Wishlist": re.compile(r"^Wishlist\s*$", re.IGNORECASE),
}
for name, pat in ad_patterns.items():
    matches = [(src, i, l) for src, i, l in all_lines if pat.search(l)]
    print(f"  {name}: {len(matches)} lines")
    for src, i, l in matches[:3]:
        print(f"    [{src}:{i}] {l.strip()[:80]}")

# ============================================================
# CATEGORY 5: URL fragments
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 5: URL fragments")
print("=" * 70)
url_pattern = re.compile(r"https?://|www\.|\.com/|\.eu/|\.net/|\.fr/")
url_lines = [(src, i, l) for src, i, l in all_lines if url_pattern.search(l)]
print(f"Found {len(url_lines)} lines with URLs")
for src, i, l in url_lines[:8]:
    print(f"  [{src}:{i}] {l.strip()[:80]}")

# ============================================================
# CATEGORY 6: Page numbers / navigation
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 6: Page numbers (e.g., '1/36', '23/36')")
print("=" * 70)
page_pattern = re.compile(r"^\d{1,3}/\d{1,3}\s*$")
page_lines = [(src, i, l) for src, i, l in all_lines if page_pattern.match(l.strip())]
print(f"Found {len(page_lines)} page number lines")
for src, i, l in page_lines[:5]:
    print(f"  [{src}:{i}] {l.strip()}")

# ============================================================
# CATEGORY 7: Timestamps (il y a, ily a, ~15 j, -1 m)
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 7: Timestamps")
print("=" * 70)
ts_patterns = {
    "il y a / ily a": re.compile(r"^(?:il\s*y?\s*a|ily?\s*a)\s+\d", re.IGNORECASE),
    "~Nj / -Nm": re.compile(r"^[~\-·]\s*\d+\s*[jm]\.?\s*$"),
}
for name, pat in ts_patterns.items():
    matches = [(src, i, l) for src, i, l in all_lines if pat.match(l.strip())]
    print(f"  {name}: {len(matches)} lines")
    for src, i, l in matches[:5]:
        print(f"    [{src}:{i}] {l.strip()}")

# ============================================================
# CATEGORY 8: Garbled OCR text (high consonant ratio, short nonsense)
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 8: Garbled OCR text (nonsense tokens)")
print("=" * 70)

def is_garbled(line: str) -> bool:
    """Detect likely OCR garbage: high ratio of unusual char sequences."""
    cleaned = line.strip()
    if len(cleaned) < 5:
        return False
    # Count lowercase vowels vs consonants
    vowels = sum(1 for c in cleaned.lower() if c in "aeiou")
    alpha = sum(1 for c in cleaned if c.isalpha())
    if alpha == 0:
        return False
    vowel_ratio = vowels / alpha
    # Very low vowel ratio + mostly alpha = garbled
    if vowel_ratio < 0.15 and alpha > 5:
        return True
    return False

garbled = [(src, i, l) for src, i, l in all_lines if is_garbled(l)]
print(f"Found {len(garbled)} potentially garbled lines")
for src, i, l in garbled[:15]:
    print(f"  [{src}:{i}] {l.strip()[:80]}")

# ============================================================
# CATEGORY 9: Single-character or very short lines
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 9: Very short lines (1-2 chars, non-numeric)")
print("=" * 70)
short_lines = [(src, i, l) for src, i, l in all_lines
               if 0 < len(l.strip()) <= 2 and not l.strip().isdigit()]
print(f"Found {len(short_lines)} very short lines")
# Show frequency
short_counter = Counter(l.strip() for _, _, l in short_lines)
for val, count in short_counter.most_common(15):
    print(f"  '{val}': {count} occurrences")

# ============================================================
# CATEGORY 10: Standalone numbers (not upvotes in comments)
# ============================================================
print("\n" + "=" * 70)
print("CATEGORY 10: Standalone numbers (potential noise)")
print("=" * 70)
standalone_num = [(src, i, l) for src, i, l in all_lines
                  if re.match(r"^\d{1,6}\s*$", l.strip())]
print(f"Found {len(standalone_num)} standalone number lines")
# Show distribution
nums = [int(l.strip()) for _, _, l in standalone_num]
if nums:
    print(f"  Range: {min(nums)} - {max(nums)}")
    print(f"  Most common: {Counter(nums).most_common(10)}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("NOISE SUMMARY")
print("=" * 70)

noise_count = (
    len(date_lines) + len(sub_lines) + len(page_lines) +
    sum(len([(s, i, l) for s, i, l in all_lines if pat.search(l)])
        for pat in ui_patterns.values()) +
    sum(len([(s, i, l) for s, i, l in all_lines if pat.search(l)])
        for pat in ad_patterns.values()) +
    len(url_lines) + len(garbled) + len(short_lines)
)
print(f"Total lines: {total_lines}")
print(f"Estimated noise lines: ~{noise_count}")
print(f"Noise ratio: ~{noise_count/total_lines*100:.1f}%")
