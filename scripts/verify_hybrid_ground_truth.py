"""
FILE: verify_hybrid_ground_truth.py
STATUS: Active
RESPONSIBILITY: Verify ground truth for hybrid test cases by performing actual vector search + SQL queries
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import json
import logging
import sqlite3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.chat import ChatRequest
from src.services.chat import ChatService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def inspect_vector_store():
    """Inspect vector store to understand available contextual information."""
    logger.info("=" * 80)
    logger.info("VECTOR STORE INSPECTION")
    logger.info("=" * 80)

    # Initialize chat service with SQL disabled to get pure vector results
    chat_service = ChatService(enable_sql=False)
    chat_service.ensure_ready()

    # Sample queries to understand available context
    sample_queries = [
        "LeBron James playstyle",
        "Nikola Jokić passing ability",
        "Stephen Curry shooting",
        "Giannis Antetokounmpo defense",
        "Joel Embiid scoring",
        "Warriors dynasty impact",
        "Lakers team strategy",
        "NBA three-point evolution"
    ]

    print("\nSample Vector Search Results:")
    print("-" * 80)

    for query in sample_queries:
        try:
            # Use search method with string query (not ChatRequest object)
            sources = chat_service.search(query, k=3)

            print(f"\nQuery: {query}")
            print(f"Sources retrieved: {len(sources)}")

            if sources:
                for i, source in enumerate(sources[:2], 1):
                    print(f"  [{i}] {source.source} (score: {source.score:.1f}%)")
                    print(f"      {source.text[:150]}...")

        except Exception as e:
            logger.error(f"Error searching '{query}': {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80 + "\n")


def inspect_database():
    """Inspect database to understand available statistics."""
    logger.info("=" * 80)
    logger.info("DATABASE INSPECTION")
    logger.info("=" * 80)

    db_path = project_root / "database" / "nba_stats.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get total player count
    cursor.execute("SELECT COUNT(*) FROM player_stats")
    total_players = cursor.fetchone()[0]
    print(f"\nTotal players in database: {total_players}")

    # Get top scorers
    print("\nTop 10 Scorers:")
    print("-" * 80)
    cursor.execute("""
        SELECT p.name, ps.pts, ps.reb, ps.ast, ps.gp,
               ROUND(ps.pts * 1.0 / ps.gp, 1) as ppg
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        ORDER BY ps.pts DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        name, pts, reb, ast, gp, ppg = row
        print(f"  {name}: {pts} PTS, {reb} REB, {ast} AST, {gp} GP ({ppg} PPG)")

    # Get defensive stats leaders
    print("\nTop 10 Defenders (BLK + STL):")
    print("-" * 80)
    cursor.execute("""
        SELECT p.name, ps.blk, ps.stl, (ps.blk + ps.stl) as defensive_actions
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        ORDER BY (ps.blk + ps.stl) DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        name, blk, stl, total = row
        print(f"  {name}: {blk} BLK, {stl} STL ({total} total)")

    # Get 3-point shooting leaders
    print("\nTop 10 3-Point Shooters (min 100 attempts):")
    print("-" * 80)
    cursor.execute("""
        SELECT p.name, ps.three_pm, ps.three_pa, ps.three_pct
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        WHERE ps.three_pa >= 100
        ORDER BY ps.three_pct DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        name, made, attempts, pct = row
        pct_display = f"{pct:.1f}%" if pct else "N/A"
        print(f"  {name}: {made}/{attempts} 3PM/3PA ({pct_display})")

    # Get assist leaders
    print("\nTop 10 Playmakers (AST):")
    print("-" * 80)
    cursor.execute("""
        SELECT p.name, ps.ast, ps.gp, ROUND(ps.ast * 1.0 / ps.gp, 1) as apg
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        ORDER BY ps.ast DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        name, ast, gp, apg = row
        print(f"  {name}: {ast} AST, {gp} GP ({apg} APG)")

    # Get rebounding leaders
    print("\nTop 10 Rebounders (REB):")
    print("-" * 80)
    cursor.execute("""
        SELECT p.name, ps.reb, ps.gp, ROUND(ps.reb * 1.0 / ps.gp, 1) as rpg
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        ORDER BY ps.reb DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        name, reb, gp, rpg = row
        print(f"  {name}: {reb} REB, {gp} GP ({rpg} RPG)")

    # Get efficiency leaders (PER available?)
    print("\nTop 10 Efficient Players (FG%):")
    print("-" * 80)
    cursor.execute("""
        SELECT p.name, ps.fgm, ps.fga, ps.fg_pct
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        WHERE ps.fga >= 100
        ORDER BY ps.fg_pct DESC
        LIMIT 10
    """)

    for row in cursor.fetchall():
        name, fgm, fga, pct = row
        pct_display = f"{pct:.1f}%" if pct else "N/A"
        print(f"  {name}: {fgm}/{fga} FGM/FGA ({pct_display})")

    conn.close()
    print("\n" + "=" * 80 + "\n")


def verify_test_case(question: str, expected_sql: str = None, query_type: str = "HYBRID"):
    """Verify ground truth for a single test case.

    Args:
        question: Test question
        expected_sql: Expected SQL query (if applicable)
        query_type: Query type (SQL_ONLY, HYBRID, CONTEXTUAL_ONLY)

    Returns:
        Verification results
    """
    logger.info(f"\nVerifying: {question}")
    logger.info("-" * 80)

    results = {
        "question": question,
        "query_type": query_type,
        "sql_results": None,
        "vector_results": None,
        "recommended_ground_truth": None
    }

    # Execute SQL query if applicable
    if expected_sql and query_type in ["SQL_ONLY", "HYBRID"]:
        try:
            db_path = project_root / "database" / "nba_stats.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute(expected_sql)

            # Get column names
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Format results
            sql_data = []
            for row in rows:
                sql_data.append(dict(zip(columns, row)))

            results["sql_results"] = sql_data
            logger.info(f"SQL Results: {json.dumps(sql_data, indent=2, ensure_ascii=False)[:200]}...")

            conn.close()

        except Exception as e:
            logger.error(f"SQL Error: {e}")
            results["sql_error"] = str(e)

    # Perform vector search if applicable
    if query_type in ["HYBRID", "CONTEXTUAL_ONLY"]:
        try:
            chat_service = ChatService(enable_sql=False)
            chat_service.ensure_ready()

            # Use search method with string query
            sources = chat_service.search(question, k=5)

            vector_data = []
            for source in sources[:3]:
                vector_data.append({
                    "source": source.source,
                    "score": source.score,
                    "text": source.text[:200]
                })

            results["vector_results"] = vector_data
            logger.info(f"Vector Results: {len(sources)} sources retrieved")

        except Exception as e:
            logger.error(f"Vector Search Error: {e}")
            import traceback
            traceback.print_exc()
            results["vector_error"] = str(e)

    return results


def main():
    """Run ground truth verification for hybrid test cases."""
    # Configure UTF-8 encoding for Windows console
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    print("\n" + "=" * 80)
    print("  PHASE 10: HYBRID QUERY GROUND TRUTH VERIFICATION")
    print("  Verify SQL + Vector search results for 22 hybrid test cases")
    print("=" * 80 + "\n")

    # Step 1: Inspect vector store and database
    inspect_vector_store()
    inspect_database()

    # Step 2: Verify hybrid test cases (sample from each tier)
    print("\n" + "=" * 80)
    print("VERIFYING PHASE 10 HYBRID TEST CASES (Sample from each tier)")
    print("=" * 80)

    # Import test cases from the actual file
    from src.evaluation.sql_test_cases import HYBRID_TEST_CASES

    # Select representative samples from each tier (2 per tier = 8 total)
    tiers = {}
    for tc in HYBRID_TEST_CASES:
        tier = tc.category.split('_')[0]
        tiers.setdefault(tier, []).append(tc)

    sample_cases = []
    for tier in sorted(tiers.keys()):
        # Take first 2 cases from each tier
        sample_cases.extend(tiers[tier][:2])

    print(f"\nVerifying {len(sample_cases)} representative cases (2 per tier):\n")

    verification_results = []

    for i, tc in enumerate(sample_cases, 1):
        print(f"[{i}/{len(sample_cases)}] {tc.category}: {tc.question[:70]}...")
        result = verify_test_case(tc.question, tc.expected_sql, "HYBRID")
        result["category"] = tc.category
        result["ground_truth_answer"] = tc.ground_truth_answer
        verification_results.append(result)
        print()

    # Save verification results
    output_path = project_root / "evaluation_results" / "phase10_ground_truth_verification.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "verification_type": "phase10_hybrid_ground_truth",
        "total_test_cases": 22,
        "cases_verified": len(verification_results),
        "verification_note": "Sample verification of 2 cases per tier (8 total)",
        "results": verification_results
    }

    output_path.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\n{'-' * 80}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'-' * 80}")
    print(f"Total hybrid test cases: 22")
    print(f"Cases verified (sample): {len(verification_results)}")
    print(f"Verification results saved to: {output_path}")
    print("\n" + "=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
