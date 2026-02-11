"""
FILE: _test_sql_fixes.py
STATUS: Experimental
RESPONSIBILITY: Test SQL generation for failing queries after prompt fixes
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Quick test of SQL generation for the 4 failing SQL queries after prompt fixes.
Tests ONLY SQL generation (not full chat pipeline) to verify prompt changes.
"""
import io
import os
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from src.tools.sql_tool import NBAGSQLTool

tool = NBAGSQLTool()

test_queries = [
    ("Who has the highest true shooting percentage?", "should have WHERE gp >= 20"),
    ("Who are the top 2 players by true shooting percentage?", "should have WHERE gp >= 20"),
    ("What is the average rebounds per game league-wide?", "should divide by gp"),
    ("How many players have a true shooting percentage over 60%?", "should use correct count"),
    ("What percentage of players have a true shooting percentage above 60%?", "should use correct pct"),
    ("Find players averaging double-digits in points, rebounds, and assists", "should calculate per-game"),
]

print("=" * 80)
print("  SQL GENERATION TEST (post-prompt-fix)")
print("=" * 80)

for q, expected in test_queries:
    print(f"\nQ: {q}")
    print(f"   Expected: {expected}")
    try:
        sql = tool.generate_sql(q)
        print(f"   SQL: {sql.strip()}")
        # Check for key patterns
        has_gp_filter = "gp" in sql.lower() and (">" in sql or ">=" in sql)
        has_division = "/" in sql and "gp" in sql.lower()
        print(f"   Has GP filter: {has_gp_filter}")
        print(f"   Has division by GP: {has_division}")
    except Exception as e:
        print(f"   ERROR: {e}")
