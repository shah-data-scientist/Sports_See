"""
FILE: check_coverage_thresholds.py
STATUS: Active
RESPONSIBILITY: Pre-commit hook enforcing per-module coverage thresholds based on tier hierarchy
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu

Usage:
  Pre-commit (fast, reads cached report):
    poetry run python scripts/global_policy/check_coverage_thresholds.py

  Generate fresh report then check:
    poetry run python scripts/global_policy/check_coverage_thresholds.py --run

  Generate report only (e.g., after writing new tests):
    poetry run pytest --cov=src --cov-report=json:.coverage_report.json -q --tb=no
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Default tier thresholds (overridden by coverage_thresholds.toml if present)
# ---------------------------------------------------------------------------
DEFAULT_TIERS = {
    "tier1": 90,  # Critical — services, core, models, api, repositories, tools
    "tier2": 70,  # Standard — pipeline, evaluation, utils
    "tier3": 50,  # Best effort — ui, scripts, evaluation runners/analysis
}

# Default module → tier mapping (generic, works for most Clean Architecture projects)
DEFAULT_MODULE_TIERS: dict[str, str] = {
    "services": "tier1",
    "core": "tier1",
    "models": "tier1",
    "api": "tier1",
    "repositories": "tier1",
    "tools": "tier1",
    "pipeline": "tier2",
    "evaluation": "tier2",
    "utils": "tier2",
    "ui": "tier3",
    "scripts": "tier3",
}

REPORT_FILENAME = ".coverage_report.json"
MAX_REPORT_AGE_HOURS = 24


def load_config(project_root: Path) -> tuple[dict[str, int], dict[str, str], int, set[str]]:
    """Load coverage_thresholds.toml if present, otherwise use defaults.

    Returns:
        Tuple of (tier_thresholds, module_tier_mapping, overall_threshold, excluded_modules).
    """
    config_path = project_root / "coverage_thresholds.toml"
    tiers = dict(DEFAULT_TIERS)
    modules = dict(DEFAULT_MODULE_TIERS)
    excluded = set()
    overall = 80

    if config_path.exists():
        current_section = None
        for line in config_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().strip('"')
                value = value.strip().strip('"')
                if current_section == "thresholds":
                    tiers[key] = int(value)
                elif current_section == "modules":
                    modules[key] = value
                elif current_section == "excluded_modules":
                    if value.lower() in ("true", "yes", "1"):
                        excluded.add(key)
                elif current_section == "overall":
                    if key == "target":
                        overall = int(value)

    return tiers, modules, overall, excluded


def parse_coverage_json(json_path: Path) -> dict[str, float] | None:
    """Parse a coverage JSON report into per-module percentages.

    Returns:
        Dict mapping module names (e.g., "services") to coverage percentages,
        or None if the report cannot be parsed.
    """
    if not json_path.exists():
        return None

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Aggregate coverage by top-level module directory under src/
    module_coverage: dict[str, dict[str, int]] = {}

    for filepath, file_data in data.get("files", {}).items():
        filepath = filepath.replace("\\", "/")

        # Extract module name: src/<module>/... → module
        parts = filepath.split("/")
        if len(parts) >= 2 and parts[0] == "src":
            module = parts[1]
        else:
            continue

        summary = file_data.get("summary", {})
        covered = summary.get("covered_lines", 0)
        total = summary.get("num_statements", 0)

        if module not in module_coverage:
            module_coverage[module] = {"covered": 0, "total": 0}
        module_coverage[module]["covered"] += covered
        module_coverage[module]["total"] += total

    result_pct: dict[str, float] = {}
    for module, counts in module_coverage.items():
        if counts["total"] > 0:
            result_pct[module] = round(100.0 * counts["covered"] / counts["total"], 2)
        else:
            result_pct[module] = 100.0

    return result_pct


def generate_coverage_report(project_root: Path) -> bool:
    """Run pytest --cov and generate JSON report.

    Excludes UI and e2e tests (tier3, require live server/browser).
    Returns:
        True if report was generated successfully.
    """
    json_report = project_root / REPORT_FILENAME

    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src",
        f"--cov-report=json:{json_report}",
        "--cov-report=",
        "-q",
        "--no-header",
        "--tb=no",
        "--ignore=tests/ui",
        "--ignore=tests/e2e",
    ]

    print("Running: pytest --cov=src (excluding ui/, e2e/ — tier3)...")

    try:
        subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("WARNING: Test suite timed out after 600s")
        print("HINT: Some tests may be hanging — check for unmocked time.sleep() or API calls")

    return json_report.exists()


def check_report_age(json_path: Path) -> str | None:
    """Check if the coverage report is stale.

    Returns:
        Warning message if stale, None if fresh enough.
    """
    import time

    if not json_path.exists():
        return None

    age_seconds = time.time() - json_path.stat().st_mtime
    age_hours = age_seconds / 3600

    if age_hours > MAX_REPORT_AGE_HOURS:
        return (
            f"WARNING: Coverage report is {age_hours:.0f}h old (max: {MAX_REPORT_AGE_HOURS}h). "
            f"Refresh with: poetry run python scripts/global_policy/check_coverage_thresholds.py --run"
        )
    return None


def check_thresholds(
    module_coverage: dict[str, float],
    tiers: dict[str, int],
    modules: dict[str, str],
    overall_target: int,
    excluded_modules: set[str],
) -> tuple[list[str], float]:
    """Check each module against its tier threshold.

    Excludes modules marked in excluded_modules config.
    Returns:
        Tuple of (failure_messages, overall_coverage_pct).
    """
    failures = []

    # Check per-module thresholds (excluding specified modules)
    checked_modules = {m: c for m, c in module_coverage.items() if m not in excluded_modules}

    for module, coverage in sorted(checked_modules.items()):
        tier = modules.get(module, "tier2")
        threshold = tiers.get(tier, 70)

        if coverage < threshold:
            failures.append(
                f"  {module:<25} {coverage:6.1f}%  {tier} (>={threshold}%)  "
                f"BELOW THRESHOLD (need +{threshold - coverage:.1f}%)"
            )

    # Calculate overall (simple average of checked module percentages)
    if checked_modules:
        overall = sum(checked_modules.values()) / len(checked_modules)
    else:
        overall = 0.0

    if overall < overall_target:
        failures.append(
            f"\n  OVERALL: {overall:.1f}% (target: {overall_target}%) — BELOW TARGET"
        )

    return failures, overall


def main() -> int:
    """Main entry point for pre-commit hook."""
    project_root = Path.cwd()
    run_mode = "--run" in sys.argv

    if not (project_root / "src").exists():
        print("SKIP: No src/ directory found — coverage check not applicable")
        return 0

    print("=" * 70)
    print("COVERAGE THRESHOLD CHECK")
    print("=" * 70)

    tiers, modules, overall_target, excluded_modules = load_config(project_root)

    config_path = project_root / "coverage_thresholds.toml"
    if config_path.exists():
        print(f"Config: {config_path.name}")
    else:
        print("Config: Using defaults (create coverage_thresholds.toml to customize)")

    print(f"Overall target: {overall_target}%")
    print(f"Tiers: {', '.join(f'{k}={v}%' for k, v in sorted(tiers.items()))}")
    print("-" * 70)

    json_report = project_root / REPORT_FILENAME

    # Mode 1: --run → generate fresh report
    if run_mode:
        success = generate_coverage_report(project_root)
        if not success:
            print("ERROR: Could not generate coverage report")
            print("HINT: Ensure pytest and pytest-cov are installed")
            return 1

    # Mode 2: pre-commit → read cached report
    if not json_report.exists():
        print(f"No coverage report found ({REPORT_FILENAME})")
        print("Generate one with:")
        print(f"  poetry run python scripts/global_policy/check_coverage_thresholds.py --run")
        print("\nSKIPPING coverage check (no data available)")
        return 0

    # Check report age
    age_warning = check_report_age(json_report)
    if age_warning:
        print(age_warning)

    # Parse report
    module_coverage = parse_coverage_json(json_report)
    if module_coverage is None:
        print("ERROR: Could not parse coverage report")
        return 1

    # Display results
    print(f"\n{'Module':<25} {'Coverage':>8}  {'Tier':<18}  {'Status':<10}")
    print("-" * 70)

    for module in sorted(module_coverage.keys()):
        coverage = module_coverage[module]
        tier = modules.get(module, "tier2")
        threshold = tiers.get(tier, 70)

        if module in excluded_modules:
            print(f"  {module:<25} {coverage:6.1f}%  {tier} (excluded)  - SKIP")
        else:
            status = "PASS" if coverage >= threshold else "FAIL"
            marker = "+" if status == "PASS" else "X"
            print(f"  {module:<25} {coverage:6.1f}%  {tier} (>={threshold}%)  {marker} {status}")

    # Check thresholds
    failures, overall = check_thresholds(module_coverage, tiers, modules, overall_target, excluded_modules)

    print("-" * 70)

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f)
        print(f"\n{'=' * 70}")
        print("COVERAGE CHECK FAILED — Fix coverage gaps before committing")
        print(f"{'=' * 70}")
        return 1

    print(f"\nOverall: {overall:.1f}% (target: {overall_target}%)")
    print(f"\n{'=' * 70}")
    print("COVERAGE CHECK PASSED")
    print(f"{'=' * 70}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
