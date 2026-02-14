"""
FILE: check_clean_working_directory.py
STATUS: Active
RESPONSIBILITY: Validates that no ignored files are staged and working directory is clean
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import re
import subprocess
import sys
from pathlib import Path


def load_gitignore_patterns() -> list[str]:
    """Load patterns from .gitignore file.

    Returns:
        List of gitignore patterns (excluding comments and empty lines)
    """
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        return []

    patterns = []
    for line in gitignore_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def should_be_ignored(filepath: str, patterns: list[str]) -> tuple[bool, str | None]:
    """Check if a file matches any gitignore pattern.

    Args:
        filepath: Path to check
        patterns: List of gitignore patterns

    Returns:
        Tuple of (should_be_ignored, matching_pattern)
    """
    path = Path(filepath)

    # Check direct patterns
    for pattern in patterns:
        # Root-level patterns (start with /)
        if pattern.startswith("/"):
            pattern_clean = pattern[1:]
            # Root-level patterns only match files at the repository root
            if len(path.parts) == 1 and path.match(pattern_clean):
                return True, pattern
        # Directory patterns (end with /)
        elif pattern.endswith("/"):
            pattern_clean = pattern.rstrip("/")
            if pattern_clean in path.parts:
                return True, pattern
        # File patterns with wildcards
        elif "*" in pattern:
            if path.match(pattern) or any(part.match(pattern.replace("*", "**")) for part in [path]):
                return True, pattern
        # Exact matches or subdirectory matches
        else:
            if path.name == pattern or pattern in str(path):
                return True, pattern

    return False, None


def get_staged_files() -> list[str]:
    """Get list of staged files from git.

    Returns:
        List of staged file paths
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode != 0:
        return []

    return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]


def check_pattern_rules(filepath: str) -> tuple[bool, str | None]:
    """Check if file matches anti-patterns that should be ignored.

    Args:
        filepath: Path to check

    Returns:
        Tuple of (is_violating, reason)
    """
    path = Path(filepath)
    name = path.name

    # Rule 1: Underscore prefix in root or scripts/ (except __init__.py)
    if name.startswith("_") and name != "__init__.py":
        if path.parts[0] == "scripts" or len(path.parts) == 1:
            return True, f"Underscore prefix file should be ignored: {filepath}"

    # Rule 2: Timestamped evaluation results
    timestamp_pattern = r"_\d{8}_\d{6}\.json$"
    if re.search(timestamp_pattern, name):
        return True, f"Timestamped result file should be ignored: {filepath}"

    # Rule 3: Phase/subset result files
    if any(pattern in name for pattern in ["_subset_results", "_test_subset", "checkpoint", "phase"]):
        if name.endswith(".json"):
            return True, f"Evaluation artifact should be ignored: {filepath}"

    # Rule 4: Runtime artifacts
    runtime_extensions = [".db", ".db-shm", ".db-wal", ".log", ".coverage", ".cache"]
    if any(name.endswith(ext) for ext in runtime_extensions):
        return True, f"Runtime artifact should be ignored: {filepath}"

    # Rule 5: Test/debug files in root
    if len(path.parts) == 1:  # Root level
        if any(name.startswith(prefix) for prefix in ["test_", "check_", "debug_"]):
            if name.endswith(".py"):
                return True, f"Root-level test/debug file should be ignored: {filepath}"

    return False, None


def main() -> int:
    """Main validation function.

    Returns:
        Exit code (0 = success, 1 = validation failed)
    """
    print("🧹 Checking working directory cleanliness...")

    # Load gitignore patterns
    patterns = load_gitignore_patterns()
    print(f"   Loaded {len(patterns)} patterns from .gitignore")

    # Get staged files
    staged_files = get_staged_files()
    if not staged_files:
        print("✅ No staged files to check")
        return 0

    print(f"   Checking {len(staged_files)} staged files...")

    # Check each staged file
    violations = []

    for filepath in staged_files:
        # Check if file should be ignored based on .gitignore patterns
        should_ignore, pattern = should_be_ignored(filepath, patterns)
        if should_ignore:
            violations.append(
                f"  ❌ {filepath}\n"
                f"     Matches .gitignore pattern: {pattern}\n"
                f"     This file should not be committed"
            )
            continue

        # Check pattern rules (anti-patterns)
        is_violating, reason = check_pattern_rules(filepath)
        if is_violating:
            violations.append(
                f"  ❌ {filepath}\n"
                f"     {reason}\n"
                f"     Add to .gitignore to prevent future staging"
            )

    # Report results
    if violations:
        print("\n❌ Working directory cleanliness check FAILED\n")
        print("The following files are staged but should be ignored:\n")
        for violation in violations:
            print(violation)

        print("\n📋 How to fix:")
        print("   1. Unstage the files: git reset HEAD <file>")
        print("   2. Verify .gitignore patterns cover these files")
        print("   3. If files are already tracked, remove from Git:")
        print("      git rm --cached <file>  (removes from Git but keeps local file)")
        print("\n   For files that should never be committed (test/debug files):")
        print("      - Rename to use underscore prefix: scripts/_test_something.py")
        print("      - Or move to _archived/ directory")
        print("\n   For timestamped evaluation results:")
        print("      - Only commit summary reports (*.md files)")
        print("      - Timestamped JSON files are automatically ignored")

        return 1

    print("✅ Working directory is clean - all staged files are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
