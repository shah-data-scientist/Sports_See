"""
FILE: check_orphaned_files.py
STATUS: Active
RESPONSIBILITY: Detects potentially outdated or orphaned files (warning only)
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import ast
import os
import sys
import time
from pathlib import Path

# Age thresholds (in days)
DEBUG_MAX_AGE = 30
STALE_MAX_AGE = 90

# Debug/temporary file patterns
DEBUG_PATTERNS = {"debug_", "temp_", "scratch_", "dump_"}
SCAN_DIRS = ["scripts", "src", "tests"]
EXCLUDE_DIRS = {"_archived", "global_policy", "__pycache__", ".venv", "venv"}


def get_file_age_days(filepath: Path) -> int:
    """Get file age in days based on modification time."""
    mtime = filepath.stat().st_mtime
    return int((time.time() - mtime) / 86400)


def has_docstring(filepath: Path) -> bool:
    """Check if a Python file has a module docstring."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
        return ast.get_docstring(tree) is not None
    except Exception:
        return False


def count_lines(filepath: Path) -> int:
    """Count non-blank lines of code in a file."""
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
        return sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))
    except Exception:
        return 0


def check_orphaned_files(verbose: bool = False) -> list[str]:
    """Detect orphaned or outdated files.

    Args:
        verbose: Show detailed output

    Returns:
        List of warning messages
    """
    warnings = []
    root = Path(".")

    for scan_dir in SCAN_DIRS:
        dir_path = root / scan_dir
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            if any(part in EXCLUDE_DIRS for part in py_file.parts):
                continue
            if py_file.name == "__init__.py":
                continue

            age = get_file_age_days(py_file)

            # Check debug/temp files over 30 days
            for pattern in DEBUG_PATTERNS:
                if py_file.name.startswith(pattern) and age > DEBUG_MAX_AGE:
                    warnings.append(
                        f"  {py_file}: Debug script is {age} days old "
                        f"(threshold: {DEBUG_MAX_AGE})"
                    )

            # Check stale scripts (not modified in 90+ days)
            if age > STALE_MAX_AGE and verbose:
                warnings.append(
                    f"  {py_file}: Not modified in {age} days "
                    f"- consider archiving if obsolete"
                )

            # Check scripts without documentation
            if not has_docstring(py_file) and verbose:
                warnings.append(f"  {py_file}: No module docstring")

            # Check large files without tests
            loc = count_lines(py_file)
            if loc > 100 and "test" not in str(py_file):
                test_name = f"test_{py_file.stem}.py"
                test_exists = any(
                    (root / "tests").rglob(test_name)
                ) if (root / "tests").exists() else False

                if not test_exists and verbose:
                    warnings.append(
                        f"  {py_file}: {loc} LOC, no test file found ({test_name})"
                    )

    return warnings


def main():
    """Run orphaned file check."""
    verbose = "--verbose" in sys.argv

    print("Checking for orphaned files...")
    print()

    warnings = check_orphaned_files(verbose=verbose)

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(warning)
        print()

    print(f"Check complete: {len(warnings)} warning(s)")
    # Always exit 0 - warnings only, never blocks commits
    sys.exit(0)


if __name__ == "__main__":
    main()
