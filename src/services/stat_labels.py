"""
FILE: stat_labels.py
STATUS: Active
RESPONSIBILITY: Map stat abbreviations to full descriptive names
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

# NBA Stat Abbreviation to Full Name Mapping
STAT_LABELS = {
    # Basic counting stats
    "pts": "PTS (Points)",
    "reb": "REB (Rebounds)",
    "ast": "AST (Assists)",
    "stl": "STL (Steals)",
    "blk": "BLK (Blocks)",
    "tov": "TOV (Turnovers)",
    "pf": "PF (Personal Fouls)",
    "gp": "GP (Games Played)",

    # Shooting stats
    "fgm": "FGM (Field Goals Made)",
    "fga": "FGA (Field Goals Attempted)",
    "fg_pct": "FG% (Field Goal Percentage)",
    "ftm": "FTM (Free Throws Made)",
    "fta": "FTA (Free Throws Attempted)",
    "ft_pct": "FT% (Free Throw Percentage)",

    # Three-point stats
    "3pm": "3PM (3-Pointers Made)",
    "3pa": "3PA (3-Pointers Attempted)",
    "three_pct": "3P% (3-Point Percentage)",
    "3p_pct": "3P% (3-Point Percentage)",

    # Rebound breakdown
    "oreb": "OREB (Offensive Rebounds)",
    "dreb": "DREB (Defensive Rebounds)",
    "oreb_pct": "OREB% (Offensive Rebound Percentage)",
    "dreb_pct": "DREB% (Defensive Rebound Percentage)",
    "reb_pct": "REB% (Total Rebound Percentage)",

    # Advanced stats
    "efg_pct": "eFG% (Effective Field Goal Percentage)",
    "ts_pct": "TS% (True Shooting Percentage)",
    "usg_pct": "USG% (Usage Percentage)",
    "ast_pct": "AST% (Assist Percentage)",
    "ast_to": "AST/TO (Assist-to-Turnover Ratio)",
    "to_ratio": "TO Ratio (Turnover Ratio)",

    # Ratings
    "offrtg": "OffRtg (Offensive Rating)",
    "defrtg": "DefRtg (Defensive Rating)",
    "netrtg": "NetRtg (Net Rating)",

    # Other stats
    "fp": "FP (Fantasy Points)",
    "dd2": "DD2 (Double-Doubles)",
    "td3": "TD3 (Triple-Doubles)",
    "pie": "PIE (Player Impact Estimate)",
    "pace": "PACE (Possessions Per 48 Minutes)",
    "poss": "POSS (Possessions)",
    "ppg": "PPG (Points Per Game)",
    "rpg": "RPG (Rebounds Per Game)",
    "apg": "APG (Assists Per Game)",
    "spg": "SPG (Steals Per Game)",
    "bpg": "BPG (Blocks Per Game)",
    "mpg": "MPG (Minutes Per Game)",

    # Common variations
    "minutes": "MIN (Minutes)",
    "min": "MIN (Minutes)",
    "points": "PTS (Points)",
    "rebounds": "REB (Rebounds)",
    "assists": "AST (Assists)",
    "steals": "STL (Steals)",
    "blocks": "BLK (Blocks)",
    "turnovers": "TOV (Turnovers)",
    "fouls": "PF (Personal Fouls)",
    "games": "GP (Games Played)",
}


def get_stat_label(stat_key: str) -> str:
    """Get full descriptive label for a stat abbreviation.

    Args:
        stat_key: The stat abbreviation (e.g., "pts", "reb", "ast")

    Returns:
        Full label with description (e.g., "PTS (Points)")
        If not found, returns uppercase version of key
    """
    stat_lower = stat_key.lower().strip()

    # Check if we have a mapping
    if stat_lower in STAT_LABELS:
        return STAT_LABELS[stat_lower]

    # Fallback: just uppercase the key
    return stat_key.upper()


def format_stat_labels(columns: list[str]) -> list[str]:
    """Format a list of stat column names with full descriptions.

    Args:
        columns: List of stat abbreviations

    Returns:
        List of formatted labels with descriptions
    """
    return [get_stat_label(col) for col in columns]


# Example usage
if __name__ == "__main__":
    test_stats = ["pts", "reb", "ast", "fg_pct", "three_pct", "ts_pct"]

    print("Stat Label Formatting Test")
    print("=" * 60)

    for stat in test_stats:
        label = get_stat_label(stat)
        print(f"{stat:15} → {label}")

    print("=" * 60)
    print("\nFormatted list:")
    print(format_stat_labels(test_stats))
