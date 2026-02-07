"""
FILE: check_eval_progress.py
STATUS: Active
RESPONSIBILITY: Quick progress checker for Phase 2/5 evaluations
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""
import json
from pathlib import Path

def check_progress():
    """Check evaluation progress."""
    print("\n" + "=" * 60)
    print("  EVALUATION PROGRESS")
    print("=" * 60)

    # Check Phase 2
    p2_checkpoint = Path("evaluation_checkpoint_phase2.json")
    if p2_checkpoint.exists():
        data = json.loads(p2_checkpoint.read_text(encoding="utf-8"))
        progress = len(data)
        total = 47
        pct = (progress / total) * 100
        print(f"\n  Phase 2: {progress}/{total} samples ({pct:.1f}%)")
        print(f"  [{'#' * int(pct / 2)}{'-' * (50 - int(pct / 2))}] {pct:.0f}%")

        if progress == total:
            print("  [COMPLETE] Phase 2")
        else:
            remaining = total - progress
            eta_min = (remaining * 6) / 60  # ~6 sec per sample
            print(f"  ETA: ~{eta_min:.1f} minutes")
    else:
        print("\n  Phase 2: Not started")

    # Check Phase 5
    p5_checkpoint = Path("evaluation_checkpoint_phase5.json")
    if p5_checkpoint.exists():
        data = json.loads(p5_checkpoint.read_text(encoding="utf-8"))
        progress = len(data)
        total = 75  # 47 + 28 hybrid
        pct = (progress / total) * 100
        print(f"\n  Phase 5: {progress}/{total} samples ({pct:.1f}%)")
        print(f"  [{'#' * int(pct / 2)}{'-' * (50 - int(pct / 2))}] {pct:.0f}%")

        if progress == total:
            print("  [COMPLETE] Phase 5")
    else:
        print("\n  Phase 5: Not started")

    # Check results
    results_dir = Path("evaluation_results")
    print("\n  " + "-" * 56)
    print("  Results Available:")

    if (results_dir / "ragas_baseline.json").exists():
        print("  [OK] Baseline (Phase 1)")
    if (results_dir / "ragas_phase2.json").exists():
        print("  [OK] Phase 2")
    if (results_dir / "ragas_phase5_extended.json").exists():
        print("  [OK] Phase 5")

    print("=" * 60 + "\n")

if __name__ == "__main__":
    check_progress()
