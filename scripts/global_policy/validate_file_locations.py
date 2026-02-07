"""
FILE: validate_file_locations.py
STATUS: Active
RESPONSIBILITY: Enforces file placement rules to prevent repository clutter
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

# Markdown files allowed in root
ROOT_ALLOWED_MD = {"README.md", "PROJECT_MEMORY.md", "CHANGELOG.md"}

# Python files allowed in root
ROOT_ALLOWED_PY = {"setup.py", "conftest.py", "manage.py"}

# Directories to skip
SKIP_DIRS = {
    ".venv", "venv", "env", ".env", "node_modules", "__pycache__",
    ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", "_archived", "htmlcov",
}


def validate_file_locations() -> list[str]:
    """Check all files are in correct locations.

    Returns:
        List of error messages
    """
    errors = []
    root = Path(".")

    # Check root-level .md files
    for md_file in root.glob("*.md"):
        if md_file.name not in ROOT_ALLOWED_MD:
            errors.append(
                f"  {md_file.name} -> Should be in docs/{md_file.name} "
                f"(only {', '.join(sorted(ROOT_ALLOWED_MD))} allowed in root)"
            )

    # Check root-level .py files
    for py_file in root.glob("*.py"):
        if py_file.name not in ROOT_ALLOWED_PY and py_file.name != "__init__.py":
            if py_file.name.startswith("test_"):
                errors.append(f"  {py_file.name} -> Should be in tests/{py_file.name}")
            elif py_file.name.startswith(("check_", "debug_")):
                errors.append(f"  {py_file.name} -> Should be in scripts/{py_file.name}")
            else:
                errors.append(f"  {py_file.name} -> Should be in src/ or scripts/")

    return errors


def main():
    """Run file location validation."""
    print("Validating file locations...")
    print()

    errors = validate_file_locations()

    if errors:
        print("FAIL - Files in wrong locations:")
        for error in errors:
            print(error)
        print()
        print(f"{'=' * 60}")
        print(f"FAILED: {len(errors)} file(s) in wrong location")
        print(f"{'=' * 60}")
        sys.exit(1)
    else:
        print("PASSED: All files in correct locations")
        sys.exit(0)


if __name__ == "__main__":
    main()
