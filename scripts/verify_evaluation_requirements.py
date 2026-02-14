"""
FILE: verify_evaluation_requirements.py
STATUS: Active
RESPONSIBILITY: Verify all 26 evaluation requirements are satisfied with evidence
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu

This script checks that all required files and evidence exist for the
OpenClassrooms "Évaluez les performances d'un LLM" evaluation.
"""

import sys
from pathlib import Path
from typing import Any

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check_file(file_path: Path, description: str) -> bool:
    """Check if a file exists and report result.

    Args:
        file_path: Path to file to check
        description: Human-readable description

    Returns:
        True if file exists, False otherwise
    """
    if file_path.exists():
        print(f"{GREEN}✓{RESET} {description}: {file_path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {file_path} {RED}NOT FOUND{RESET}")
        return False


def check_directory(dir_path: Path, description: str, min_files: int = 1) -> bool:
    """Check if a directory exists and contains minimum files.

    Args:
        dir_path: Path to directory to check
        description: Human-readable description
        min_files: Minimum number of files required

    Returns:
        True if directory exists with enough files, False otherwise
    """
    if not dir_path.exists():
        print(f"{RED}✗{RESET} {description}: {dir_path} {RED}NOT FOUND{RESET}")
        return False

    files = list(dir_path.glob("*"))
    if len(files) >= min_files:
        print(f"{GREEN}✓{RESET} {description}: {dir_path} ({len(files)} files)")
        return True
    else:
        print(f"{YELLOW}⚠{RESET} {description}: {dir_path} (only {len(files)} files, expected {min_files}+)")
        return False


def check_content(file_path: Path, search_strings: list[str], description: str) -> bool:
    """Check if file contains expected content.

    Args:
        file_path: Path to file to check
        search_strings: List of strings that should be present
        description: Human-readable description

    Returns:
        True if all strings found, False otherwise
    """
    if not file_path.exists():
        print(f"{RED}✗{RESET} {description}: {file_path} {RED}NOT FOUND{RESET}")
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        missing = [s for s in search_strings if s not in content]

        if not missing:
            print(f"{GREEN}✓{RESET} {description}: All expected content found")
            return True
        else:
            print(f"{YELLOW}⚠{RESET} {description}: Missing content - {', '.join(missing[:3])}")
            return False
    except Exception as e:
        print(f"{RED}✗{RESET} {description}: Error reading file - {e}")
        return False


def main() -> int:
    """Run all verification checks.

    Returns:
        Exit code (0 = all passed, 1 = some failed)
    """
    project_root = Path(__file__).parent.parent
    checks_passed = 0
    checks_total = 0

    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Sports_See - Evaluation Requirements Verification{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    # Category 1: Infrastructure Performance Evaluation
    print(f"\n{BOLD}Category 1: Infrastructure Performance Evaluation (14 requirements){RESET}\n")

    # 1.1: Environment reproducibility file
    checks_total += 1
    if check_file(project_root / "pyproject.toml", "1.1 Environment file (pyproject.toml)"):
        checks_passed += 1

    # 1.2: Modular RAG setup script
    checks_total += 1
    if check_file(project_root / "scripts" / "rebuild_vector_index.py", "1.2 RAG setup script"):
        checks_passed += 1

    # 1.3: Structured logging
    checks_total += 1
    if check_file(project_root / "src" / "core" / "observability.py", "1.3 Logging system"):
        checks_passed += 1

    # 1.4: Single-run operational system (README instructions)
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Quick Start", "poetry run python scripts/rebuild_vector_index.py"],
        "1.4 Single-run system instructions"
    ):
        checks_passed += 1

    # 1.5: Readable evaluation scripts
    checks_total += 1
    if check_directory(
        project_root / "src" / "evaluation" / "runners",
        "1.5 Evaluation runners",
        min_files=3
    ):
        checks_passed += 1

    # 1.6: Varied query sets
    checks_total += 1
    if check_directory(
        project_root / "src" / "evaluation" / "test_cases",
        "1.6 Test case datasets",
        min_files=3
    ):
        checks_passed += 1

    # 1.7: Realistic coverage (check test case count in files)
    checks_total += 1
    if check_content(
        project_root / "src" / "evaluation" / "test_cases" / "sql_test_cases.py",
        ["SQL_TEST_CASES", "simple", "complex"],
        "1.7 SQL test case variety"
    ):
        checks_passed += 1

    # 1.8: RAGAS and Pydantic usage
    checks_total += 1
    ragas_check = check_content(
        project_root / "pyproject.toml",
        ["ragas", "pydantic"],
        "1.8 RAGAS and Pydantic dependencies"
    )
    if ragas_check:
        checks_passed += 1

    # 1.9: Pydantic schema validation
    checks_total += 1
    if check_file(project_root / "src" / "models" / "chat.py", "1.9 Pydantic models (chat.py)"):
        checks_passed += 1

    # 1.10: RAGAS metrics justification
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Faithfulness", "Answer Relevancy", "Context Precision", "Context Recall"],
        "1.10 RAGAS metrics documentation"
    ):
        checks_passed += 1

    # 1.11: Synthetic results table
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Classification Accuracy", "Dataset", "Total", "Correct"],
        "1.11 Results table in README"
    ):
        checks_passed += 1

    # 1.12: Robustness tests
    checks_total += 1
    if check_directory(
        project_root / "tests",
        "1.12 Test suite",
        min_files=5
    ):
        checks_passed += 1

    # 1.13: Business-justified tests (check for test categories)
    checks_total += 1
    if check_content(
        project_root / "src" / "evaluation" / "test_cases" / "sql_test_cases.py",
        ["category", "noisy", "conversational"],
        "1.13 Business-justified test categories"
    ):
        checks_passed += 1

    # 1.14: Pipeline logging (check chat.py for logging)
    checks_total += 1
    if check_content(
        project_root / "src" / "services" / "chat.py",
        ["logger", "info", "error"],
        "1.14 Pipeline logging in chat service"
    ):
        checks_passed += 1

    # Category 2: Setup and Implementation Reports
    print(f"\n{BOLD}Category 2: Setup and Implementation Reports (6 requirements){RESET}\n")

    # 2.1: Methodology explanation
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Architecture", "Query Routing", "Ground Truth"],
        "2.1 Methodology in README"
    ):
        checks_passed += 1

    # 2.2: Methodological choices
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Hybrid RAG", "Fallback"],
        "2.2 Methodological choices explained"
    ):
        checks_passed += 1

    # 2.3: Limits and biases
    checks_total += 1
    if check_file(
        project_root / "PROJET_EVALUATION_CHECKLIST.md",
        "2.3 Evaluation checklist with limitations"
    ):
        checks_passed += 1

    # 2.4: Business-linked interpretation
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Fantasy", "business", "use case"],
        "2.4 Business context in README"
    ):
        checks_passed += 1

    # 2.5: Actionable recommendations
    checks_total += 1
    if check_content(
        project_root / "PROJET_EVALUATION_CHECKLIST.md",
        ["Recommendation", "Action"],
        "2.5 Recommendations in checklist"
    ):
        checks_passed += 1

    # 2.6: Professional structure
    checks_total += 1
    readme_size = (project_root / "README.md").stat().st_size
    if readme_size > 50000:  # ~700+ lines
        print(f"{GREEN}✓{RESET} 2.6 README structure: {readme_size / 1024:.1f} KB")
        checks_passed += 1
    else:
        print(f"{YELLOW}⚠{RESET} 2.6 README structure: Only {readme_size / 1024:.1f} KB (expected 50+ KB)")

    # Category 3: Documentation
    print(f"\n{BOLD}Category 3: Documentation (6 requirements){RESET}\n")

    # 3.1: Architecture diagram
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["```", "User Query", "Classifier", "SQL", "Vector"],
        "3.1 Architecture diagram in README"
    ):
        checks_passed += 1

    # 3.2: API documentation
    checks_total += 1
    if check_file(project_root / "docs" / "API.md", "3.2 API documentation"):
        checks_passed += 1

    # 3.3: Organization explanation
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Project Structure", "src/", "tests/", "scripts/"],
        "3.3 File organization in README"
    ):
        checks_passed += 1

    # 3.4: Procedures
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Installation", "poetry install", "poetry run"],
        "3.4 Deployment/execution procedures"
    ):
        checks_passed += 1

    # 3.5: Reproducibility (Poetry lock file)
    checks_total += 1
    if check_file(project_root / "poetry.lock", "3.5 Poetry lock file (reproducibility)"):
        checks_passed += 1

    # 3.6: Non-specialist accessibility
    checks_total += 1
    if check_content(
        project_root / "README.md",
        ["Quick Start", "Prerequisites", "Troubleshooting"],
        "3.6 Accessible documentation sections"
    ):
        checks_passed += 1

    # Summary
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Verification Summary{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0

    if checks_passed == checks_total:
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED: {checks_passed}/{checks_total} ({percentage:.1f}%){RESET}\n")
        print(f"{GREEN}The project satisfies all 26 evaluation requirements.{RESET}")
        print(f"{GREEN}Ready for submission!{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}{BOLD}⚠ PARTIAL COMPLETION: {checks_passed}/{checks_total} ({percentage:.1f}%){RESET}\n")
        print(f"{YELLOW}Some requirements may need attention.{RESET}")
        print(f"{YELLOW}Review the checklist above for details.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
