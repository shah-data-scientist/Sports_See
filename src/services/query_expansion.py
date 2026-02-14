"""
FILE: query_expansion.py
STATUS: Active
RESPONSIBILITY: NBA-specific query expansion for better retrieval
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import re
from typing import Dict, List


class QueryExpander:
    """Expand queries with NBA-specific synonyms and abbreviations."""

    # NBA stat abbreviations and their expansions (ENHANCED)
    STAT_EXPANSIONS: Dict[str, List[str]] = {
        "points": ["PTS", "points per game", "scoring", "ppg", "scorer", "scores"],
        "assists": ["AST", "assists per game", "apg", "passing", "playmaking", "dimes"],
        "rebounds": ["REB", "TRB", "total rebounds", "rebounding", "rpg", "rebounds per game", "boards"],
        "steals": ["STL", "steals per game", "spg", "takeaways"],
        "blocks": ["BLK", "blocks per game", "bpg", "rejections", "swats"],
        "three-point": ["3P%", "3PT%", "three point percentage", "3-point shooting", "from three", "3P", "3PM", "threes"],
        "3-point": ["3P%", "3PT%", "three point percentage", "3-point shooting", "from three", "3P", "3PM"],
        "field goal": ["FG%", "shooting percentage", "field goal percentage", "FGM", "FGA"],
        "free throw": ["FT%", "free throw percentage", "from the line", "FTM", "FTA", "charity stripe"],
        "efficiency": ["PER", "player efficiency rating", "efficiency rating", "effective"],
        "true shooting": ["TS%", "true shooting percentage"],
        "offensive rating": ["ORTG", "offensive efficiency", "offense"],
        "defensive rating": ["DRTG", "defensive efficiency", "defense"],
        "turnovers": ["TOV", "TO", "turnovers per game", "giveaways"],
        "minutes": ["MIN", "MPG", "minutes per game", "playing time"],
        "usage": ["USG%", "usage rate", "usage percentage"],
    }

    # Team name variations (ENHANCED)
    TEAM_EXPANSIONS: Dict[str, List[str]] = {
        "lakers": ["Los Angeles Lakers", "LAL", "LA Lakers"],
        "celtics": ["Boston Celtics", "BOS"],
        "warriors": ["Golden State Warriors", "GSW"],
        "heat": ["Miami Heat", "MIA"],
        "knicks": ["New York Knicks", "NYK"],
        "nets": ["Brooklyn Nets", "BKN"],
        "bucks": ["Milwaukee Bucks", "MIL"],
        "nuggets": ["Denver Nuggets", "DEN"],
        "suns": ["Phoenix Suns", "PHX"],
        "mavericks": ["Dallas Mavericks", "DAL", "Mavs"],
        "clippers": ["Los Angeles Clippers", "LAC", "LA Clippers"],
        "cavaliers": ["Cleveland Cavaliers", "CLE", "Cavs"],
        "bulls": ["Chicago Bulls", "CHI"],
        "sixers": ["Philadelphia 76ers", "PHI"],
        "raptors": ["Toronto Raptors", "TOR"],
        "spurs": ["San Antonio Spurs", "SAS"],
    }

    # Common player nicknames (NEW)
    PLAYER_NICKNAMES: Dict[str, List[str]] = {
        "lebron": ["LeBron James", "King James", "Bron"],
        "curry": ["Stephen Curry", "Steph Curry", "Chef Curry"],
        "giannis": ["Giannis Antetokounmpo", "Greek Freak"],
        "jokic": ["Nikola Jokic", "Joker"],
        "embiid": ["Joel Embiid", "The Process"],
        "durant": ["Kevin Durant", "KD", "Slim Reaper"],
        "kawhi": ["Kawhi Leonard", "Klaw", "Board Man"],
        "harden": ["James Harden", "The Beard"],
        "lillard": ["Damian Lillard", "Dame", "Dame Time"],
        "doncic": ["Luka Doncic", "Luka Magic"],
    }

    # Synonyms for common query terms (ENHANCED)
    QUERY_SYNONYMS: Dict[str, List[str]] = {
        "leader": ["top", "best", "highest", "most", "leading", "first", "number one", "#1"],
        "worst": ["lowest", "bottom", "least", "poorest", "weakest"],
        "player": ["athlete", "star", "scorer", "performer"],
        "team": ["squad", "franchise", "club", "organization"],
        "game": ["match", "contest", "matchup"],
        "season": ["year", "campaign", "this year"],
        "average": ["avg", "mean", "per game"],
        "rookie": ["first-year player", "newcomer", "first year"],
        "veteran": ["experienced player", "vet"],
        "injury": ["injured", "hurt", "out", "sidelined"],
        "leading": ["top", "best", "highest", "most", "leader", "first"],
        "compare": ["versus", "vs", "comparison", "difference between"],
    }

    def expand(self, query: str, max_expansions: int = 3) -> str:
        """Expand query with relevant synonyms.

        Args:
            query: Original user query
            max_expansions: Maximum number of expansion terms to add per keyword

        Returns:
            Expanded query string
        """
        query_lower = query.lower()
        expansion_terms = []

        # Find stat-related expansions
        for keyword, expansions in self.STAT_EXPANSIONS.items():
            if keyword in query_lower:
                # Add up to max_expansions terms
                expansion_terms.extend(expansions[:max_expansions])

        # Find team name variations
        for keyword, variations in self.TEAM_EXPANSIONS.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                expansion_terms.extend(variations[:max_expansions])

        # Find player nickname expansions
        for keyword, variations in self.PLAYER_NICKNAMES.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                expansion_terms.extend(variations[:2])  # Limit to 2 for player names

        # Find general query term expansions
        for keyword, synonyms in self.QUERY_SYNONYMS.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                expansion_terms.extend(synonyms[:max_expansions])

        # Return original query + expansion terms
        if expansion_terms:
            # Remove duplicates and limit total additions
            unique_expansions = list(dict.fromkeys(expansion_terms))[:15]  # Increased from 10 to 15
            return f"{query} {' '.join(unique_expansions)}"

        return query

    def expand_smart(self, query: str) -> str:
        """Smart expansion that avoids over-expanding.

        Only expands if query is short (<10 words) to avoid cluttering
        already detailed queries.

        Args:
            query: Original user query

        Returns:
            Expanded or original query
        """
        word_count = len(query.split())

        # More aggressive expansion for better retrieval
        if word_count < 8:
            return self.expand(query, max_expansions=4)  # Increased from 2
        elif word_count < 12:
            return self.expand(query, max_expansions=3)  # Increased from 1
        elif word_count < 15:
            return self.expand(query, max_expansions=2)  # New tier
        else:
            # Query is already detailed, minimal expansion
            return self.expand(query, max_expansions=1)

    def expand_smart_category(self, query: str, category: str = None) -> str:
        """Smart expansion with category awareness (Phase 3 Step 3).

        Different query categories have different expansion needs:
        - "noisy": Minimal expansion (1 term) - avoid matching noise
        - "conversational": Aggressive expansion (5 terms) - catch all synonyms
        - "simple": Balanced expansion (4 terms)
        - "complex": Conservative expansion (2 terms) - focused
        - None/unknown: Use word-count logic (existing expand_smart)

        Args:
            query: Original user query
            category: Query category hint (noisy, conversational, simple, complex)

        Returns:
            Expanded or original query
        """
        # Category-based overrides
        if category == "noisy":
            max_exp = 1  # Conservative - avoid false matches
        elif category == "conversational":
            max_exp = 5  # Aggressive - catch all conversation synonyms
        elif category == "simple":
            max_exp = 4  # Balanced
        elif category == "complex":
            max_exp = 2  # Conservative - focus on core concepts
        else:
            # Default: use word-count logic
            return self.expand_smart(query)

        return self.expand(query, max_expansions=max_exp)

    def expand_weighted(self, query: str, max_expansions: int = 4) -> str:
        """Smart expansion using pre-computed max_expansions from QueryClassifier.

        NOTE: max_expansions is now computed by QueryClassifier._compute_max_expansions()
        using a weighted formula combining category + word count. This method simply
        uses the pre-computed value for consistent expansion.

        Formula (computed in QueryClassifier):
            max_expansions = clamp(category_base + word_count_adjustment, 1, 5)

        Examples:
        - "yo best team lol" (4 words, NOISY) → max_exp=2
        - "Who are the top 5 scorers?" (6 words, SIMPLE) → max_exp=4
        - "What about his assists?" (4 words, CONVERSATIONAL) → max_exp=5
        - "Analyze patterns in playoff efficiency discussions" (6 words, COMPLEX) → max_exp=2
        - "Can you provide comprehensive detailed analysis..." (17 words, COMPLEX) → max_exp=1

        Args:
            query: Original user query
            max_expansions: Pre-computed expansion limit from ClassificationResult

        Returns:
            Expanded or original query
        """
        return self.expand(query, max_expansions=max_expansions)
