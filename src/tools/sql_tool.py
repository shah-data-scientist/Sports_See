"""
FILE: sql_tool.py
STATUS: Active
RESPONSIBILITY: LangChain SQL agent for querying NBA statistics database
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

import logging
from pathlib import Path

from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_mistralai import ChatMistralAI

from src.core.config import settings

logger = logging.getLogger(__name__)


# Few-shot examples for SQL query generation
FEW_SHOT_EXAMPLES = [
    {
        "input": "Who are the top 5 scorers in the league?",
        "query": """SELECT p.name, p.team_abbr, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DESC
LIMIT 5;""",
    },
    {
        "input": "What is LeBron James' average points per game?",
        "query": """SELECT p.name, CAST(ps.pts AS FLOAT) / ps.gp AS ppg
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name LIKE '%LeBron James%';""",
    },
    {
        "input": "Which teams have the most wins?",
        "query": """SELECT t.name, t.abbreviation, SUM(ps.w) AS total_wins
FROM teams t
JOIN player_stats ps ON t.abbreviation = ps.team_abbr
GROUP BY t.abbreviation, t.name
ORDER BY total_wins DESC
LIMIT 10;""",
    },
    {
        "input": "Show me players with more than 100 three-pointers made",
        "query": """SELECT p.name, p.team_abbr, ps.three_pm
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.three_pm > 100
ORDER BY ps.three_pm DESC;""",
    },
    {
        "input": "What is the average field goal percentage for the Lakers?",
        "query": """SELECT AVG(ps.fg_pct) AS avg_fg_pct
FROM player_stats ps
WHERE ps.team_abbr = 'LAL';""",
    },
    {
        "input": "Which player has the most rebounds?",
        "query": """SELECT p.name, p.team_abbr, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.reb DESC
LIMIT 1;""",
    },
    {
        "input": "Compare scoring efficiency between Curry and Durant",
        "query": """SELECT p.name,
       CAST(ps.pts AS FLOAT) / ps.gp AS ppg,
       ps.fg_pct,
       ps.three_pct,
       ps.ts_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name LIKE '%Curry%' OR p.name LIKE '%Durant%';""",
    },
    {
        "input": "Who are the most efficient scorers (TS% > 60)?",
        "query": """SELECT p.name, p.team_abbr,
       CAST(ps.pts AS FLOAT) / ps.gp AS ppg,
       ps.ts_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.ts_pct > 60 AND ps.gp > 40
ORDER BY ps.ts_pct DESC;""",
    },
]


class NBAGSQLTool:
    """SQL query tool for NBA statistics database using LangChain."""

    def __init__(self, db_path: str | None = None, mistral_api_key: str | None = None):
        """Initialize SQL tool.

        Args:
            db_path: Path to SQLite database (default: database/nba_stats.db)
            mistral_api_key: Mistral API key (default from settings)
        """
        if db_path is None:
            db_path = str(Path(settings.database_dir) / "nba_stats.db")

        self.db_path = db_path
        self._api_key = mistral_api_key or settings.mistral_api_key

        # Initialize SQLDatabase
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

        # Initialize LLM
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            temperature=0.0,  # Deterministic for SQL generation
            api_key=self._api_key,
        )

        # Build prompts
        self.example_prompt = PromptTemplate(
            input_variables=["input", "query"],
            template="User question: {input}\nSQL query: {query}",
        )

        self.few_shot_prompt = FewShotPromptTemplate(
            examples=FEW_SHOT_EXAMPLES,
            example_prompt=self.example_prompt,
            prefix="""You are an NBA statistics SQL expert. Given a user question about NBA player or team statistics, write a SQLite query to answer it.

The database schema is:
- teams(id, abbreviation, name)
- players(id, name, team_abbr, age)
- player_stats(id, player_id, team_abbr, gp, w, l, min, pts, fgm, fga, fg_pct, three_pm, three_pa, three_pct, ftm, fta, ft_pct, oreb, dreb, reb, ast, tov, stl, blk, pf, fp, dd2, td3, plus_minus, off_rtg, def_rtg, net_rtg, ast_pct, ast_to, ast_ratio, oreb_pct, dreb_pct, reb_pct, to_ratio, efg_pct, ts_pct, usg_pct, pace, pie, poss)

Key abbreviations:
- GP = Games Played, W = Wins, L = Losses
- PTS = Points, FGM/FGA = Field Goals Made/Attempted
- 3PM/3PA = 3-Point Made/Attempted
- FTM/FTA = Free Throws Made/Attempted
- REB = Rebounds, AST = Assists, STL = Steals, BLK = Blocks
- TS% = True Shooting %, EFG% = Effective FG %

Here are some examples:""",
            suffix="\n\nNow generate a SQL query for this question:\nUser question: {input}\nSQL query:",
            input_variables=["input"],
            example_separator="\n\n",
        )

        self.sql_chain = self.few_shot_prompt | self.llm

        logger.info(f"NBA SQL Tool initialized with database: {db_path}")

    def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question.

        Args:
            question: Natural language question about NBA stats

        Returns:
            Generated SQL query string
        """
        logger.info(f"Generating SQL for question: {question}")

        # Generate SQL using LLM
        response = self.sql_chain.invoke({"input": question})

        # Extract SQL from response
        sql = response.content.strip()

        # Remove markdown code blocks if present
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]

        sql = sql.strip()

        logger.info(f"Generated SQL: {sql}")

        return sql

    def execute_sql(self, sql: str) -> list[dict]:
        """Execute SQL query and return results.

        Args:
            sql: SQL query string

        Returns:
            List of result rows as dictionaries

        Raises:
            Exception: If SQL execution fails
        """
        logger.info(f"Executing SQL: {sql}")

        try:
            # Execute query
            result = self.db.run(sql, include_columns=True)

            # Parse result (format: [(col1, col2, ...), (val1, val2, ...), ...])
            if not result or len(result) < 2:
                return []

            columns = result[0]  # First tuple is column names
            rows = result[1:]  # Remaining tuples are data rows

            # Convert to list of dicts
            results = [dict(zip(columns, row)) for row in rows]

            logger.info(f"Query returned {len(results)} rows")

            return results

        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            raise

    def query(self, question: str) -> dict:
        """Query NBA database with natural language.

        Args:
            question: Natural language question about NBA statistics

        Returns:
            Dictionary with:
                - question: Original question
                - sql: Generated SQL query
                - results: Query results (list of dicts)
                - error: Error message if query failed

        Example:
            >>> tool = NBAGSQLTool()
            >>> result = tool.query("Who are the top 5 scorers?")
            >>> print(result['results'])
            [{'name': 'Player1', 'pts': 2500}, ...]
        """
        try:
            # Generate SQL
            sql = self.generate_sql(question)

            # Execute SQL
            results = self.execute_sql(sql)

            return {
                "question": question,
                "sql": sql,
                "results": results,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "question": question,
                "sql": None,
                "results": [],
                "error": str(e),
            }

    def format_results(self, results: list[dict]) -> str:
        """Format query results as natural language response.

        Args:
            results: Query results from execute_sql()

        Returns:
            Formatted string response
        """
        if not results:
            return "No results found."

        # Format as table-like text
        if len(results) == 1:
            # Single row - format as key-value pairs
            row = results[0]
            lines = [f"{key}: {value}" for key, value in row.items()]
            return "\n".join(lines)

        # Multiple rows - format as table
        columns = list(results[0].keys())
        lines = []

        # Header
        header = " | ".join(columns)
        lines.append(header)
        lines.append("-" * len(header))

        # Rows
        for row in results:
            row_str = " | ".join(str(row.get(col, "")) for col in columns)
            lines.append(row_str)

        return "\n".join(lines)
