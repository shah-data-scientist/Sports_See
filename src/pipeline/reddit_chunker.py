"""
FILE: reddit_chunker.py
STATUS: Active
RESPONSIBILITY: Reddit-specific chunking with ad filtering and thread preservation
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import hashlib
import logging
import re
from typing import Any

from src.pipeline.models import ChunkData

logger = logging.getLogger(__name__)


class RedditThreadChunker:
    """
    Chunk Reddit threads preserving post + comment structure.

    Key Features:
    - Filters advertisements (Sponsoris(e), promotional URLs)
    - Preserves thread context (post + top comments together)
    - Parses nested comment structure
    - Supports NBA official content weighting
    """

    # Advertisement patterns (compiled for performance)
    AD_PATTERNS = [
        r"Sponsoris\(e\).*?(?=\n\n|\Z)",  # French "Sponsored" marker
        r"Sponsored.*?(?=\n\n|\Z)",  # English "Sponsored"
        r"xometry_europe.*?Xometry",  # Specific sponsor blocks
        r"(?:En savoir plus|Learn more)\s+pages\.[a-z]+\.[a-z]+",  # CTA + URL
        r"Rejoindre la conversation",  # Reddit UI: "Join conversation"
        r"Accéder au contenu principal",  # Reddit UI: "Access main content"
        r"Accder au contenu principal",  # OCR variant
        r"Se connecter",  # Reddit UI: "Sign in"
        r"Rechercher dans r/\w+",  # Reddit UI: "Search in r/subreddit"
        r"Trier par\s+\w+",  # Reddit UI: "Sort by"
        r"Rechercher des commentaires",  # Reddit UI: "Search comments"
        r"réponses supplémentaires",  # Reddit UI: "Additional replies"
        r"rponses supplmentaires",  # OCR variant
    ]

    # NBA official account patterns
    NBA_OFFICIAL_ACCOUNTS = [
        "NBA",
        "NBAOfficial",
        "nba",
        "Lakers",
        "Celtics",
        "Warriors",
        "Bulls",
        "Heat",
        "Knicks",
        "Nets",
        "Mavericks",
        "Rockets",
        "Suns",
        "Clippers",
        "Nuggets",
        "Bucks",
        "Sixers",
        "Raptors",
        "Pacers",
        "Cavaliers",
    ]

    def __init__(self, max_comments_per_chunk: int = 5):
        """
        Initialize Reddit thread chunker.

        Args:
            max_comments_per_chunk: Number of top comments to include per chunk
        """
        self.max_comments = max_comments_per_chunk
        self.ad_regex = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.AD_PATTERNS]

    def filter_advertisements(self, text: str) -> str:
        """
        Remove advertisements and Reddit UI noise from text.

        Args:
            text: Raw OCR text from Reddit PDF

        Returns:
            Cleaned text with ads removed
        """
        cleaned = text

        for pattern in self.ad_regex:
            cleaned = pattern.sub("", cleaned)

        # Remove excessive whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r" {2,}", " ", cleaned)

        return cleaned.strip()

    def extract_post_info(self, text: str) -> dict[str, Any]:
        """
        Extract main post information from Reddit thread.

        Args:
            text: Cleaned Reddit thread text

        Returns:
            Dictionary with post metadata
        """
        # Try to extract post title (usually after r/nba and before author)
        title_match = re.search(
            r"r/nba.*?\n(.+?)\n(?:il y a|ago|posted by)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        # Try to extract author (username before "Who are" or similar)
        author_match = re.search(
            r"\n([A-Za-z0-9_-]+)\n(?:Who|What|How|Why|Is|Are|Do|Does|Can|Should)",
            text,
        )

        # Try to extract upvotes and comment count
        stats_match = re.search(r"\n(\d+)\s*\n(\d+)\s*\nPartager", text)

        title = "Unknown Title"
        if title_match:
            title = title_match.group(1).strip()
            # Clean up multi-line titles
            title = " ".join(title.split())

        author = author_match.group(1) if author_match else "Unknown"
        upvotes = int(stats_match.group(1)) if stats_match else 0
        num_comments = int(stats_match.group(2)) if stats_match else 0

        return {
            "title": title,
            "author": author,
            "upvotes": upvotes,
            "num_comments": num_comments,
        }

    def extract_comments(self, text: str) -> list[dict[str, Any]]:
        """
        Extract comments from Reddit thread.

        Pattern: Username, comment text, upvote count, "Répondre"

        Args:
            text: Cleaned Reddit thread text

        Returns:
            List of comment dictionaries
        """
        comments = []

        # Pattern: Username → text → upvotes → "Répondre" or "Rpondre" (OCR variant)
        comment_pattern = r"([A-Za-z0-9_-]+)\s*\n(.+?)\n(\d+)\s*\nR[ée]pondre"

        for match in re.finditer(comment_pattern, text, re.DOTALL):
            username = match.group(1).strip()
            comment_text = match.group(2).strip()
            upvotes_str = match.group(3).strip()

            # Skip if username is too short (likely OCR noise)
            if len(username) < 3:
                continue

            # Skip if comment is too short
            if len(comment_text) < 10:
                continue

            # Clean up comment text (remove excessive whitespace)
            comment_text = " ".join(comment_text.split())

            try:
                upvotes = int(upvotes_str)
            except ValueError:
                upvotes = 0

            comments.append({
                "author": username,
                "text": comment_text,
                "upvotes": upvotes,
                "is_nba_official": username in self.NBA_OFFICIAL_ACCOUNTS,
            })

        return comments

    def chunk_reddit_thread(self, text: str, source: str) -> list[ChunkData]:
        """
        Create chunks from Reddit thread preserving context.

        Strategy:
        1. Filter advertisements
        2. Extract post metadata
        3. Extract all comments
        4. Create chunk: Post + top N comments (by upvotes)

        Args:
            text: Raw OCR text from Reddit PDF
            source: Source file path

        Returns:
            List of ChunkData objects
        """
        # Step 1: Filter ads
        cleaned_text = self.filter_advertisements(text)

        # Step 2: Extract post info
        post_info = self.extract_post_info(cleaned_text)

        # Step 3: Extract comments
        comments = self.extract_comments(cleaned_text)

        if not comments:
            logger.warning(f"No comments extracted from {source}")
            # Return basic chunk with just post info
            basic_text = f"REDDIT POST: {post_info['title']}"
            chunk_id = hashlib.sha256(basic_text.encode("utf-8")).hexdigest()[:16]
            return [
                ChunkData(
                    id=chunk_id,
                    text=basic_text,
                    metadata={
                        "source": source,
                        "type": "reddit_thread",
                        "post_title": post_info["title"],
                        "post_author": post_info["author"],
                        "num_comments": 0,
                    },
                )
            ]

        # Step 4: Sort comments by upvotes (top comments first)
        top_comments = sorted(comments, key=lambda c: c["upvotes"], reverse=True)[
            : self.max_comments
        ]

        # Step 5: Build chunk text
        chunk_text = f"""=== REDDIT POST ===
Title: {post_info['title']}
Author: u/{post_info['author']}
Upvotes: {post_info['upvotes']} | Total Comments: {post_info['num_comments']}

=== TOP COMMENTS ({len(top_comments)}) ===
"""

        for i, comment in enumerate(top_comments, 1):
            nba_tag = " [NBA OFFICIAL]" if comment["is_nba_official"] else ""
            chunk_text += (
                f"\n[{i}] u/{comment['author']}{nba_tag} ({comment['upvotes']} upvotes):\n"
            )
            chunk_text += f"{comment['text']}\n"

        # Step 5.5: Truncate if exceeds token limit
        # Conservative estimate for Reddit content: 1 token ≈ 3 characters
        # (Reddit threads are more token-dense due to formatting, usernames, etc.)
        MAX_TOKENS = 6500  # Leave safe buffer below 8192 limit
        MAX_CHARS = MAX_TOKENS * 3  # = 19,500 chars
        if len(chunk_text) > MAX_CHARS:
            logger.warning(
                f"Chunk from {source} exceeds {MAX_TOKENS} tokens "
                f"({len(chunk_text)} chars), truncating to {MAX_CHARS} chars"
            )
            chunk_text = chunk_text[:MAX_CHARS] + "\n\n[...truncated for length]"

        # Step 6: Create chunk with metadata
        # Generate unique ID from chunk text hash
        chunk_id = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:16]

        chunk = ChunkData(
            id=chunk_id,
            text=chunk_text,
            metadata={
                "source": source,
                "type": "reddit_thread",
                "post_title": post_info["title"],
                "post_author": post_info["author"],
                "post_upvotes": post_info["upvotes"],
                "num_comments": len(comments),
                "top_comments_included": len(top_comments),
                "has_nba_official": any(c["is_nba_official"] for c in top_comments),
            },
        )

        logger.info(
            f"Created Reddit chunk from {source}: "
            f"{post_info['title'][:50]}... "
            f"({len(comments)} comments, top {len(top_comments)} included)"
        )

        return [chunk]

    def is_reddit_content(self, text: str) -> bool:
        """
        Detect if text is from a Reddit PDF.

        Args:
            text: OCR extracted text

        Returns:
            True if text appears to be from Reddit
        """
        reddit_indicators = [
            r"r/nba",
            r"r/\w+",
            r"Répondre",
            r"Rpondre",  # OCR variant
            r"Partager",
            r"upvotes?",
            r"commentaires?",
        ]

        # Check if at least 2 Reddit indicators are present
        matches = sum(
            1 for pattern in reddit_indicators if re.search(pattern, text, re.IGNORECASE)
        )

        return matches >= 2
