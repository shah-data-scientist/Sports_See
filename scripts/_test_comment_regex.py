"""
FILE: _test_comment_regex.py
STATUS: Experimental
RESPONSIBILITY: Verify fixed comment extraction regex on sample OCR text
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Quick test: verify the fixed comment extraction regex on sample OCR text.
"""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.pipeline.reddit_chunker import RedditThreadChunker

chunker = RedditThreadChunker()

# Sample OCR text from Reddit 1.pdf (from diagnostic output)
sample_text = """Trier par:Meilleurs
QRechercher des commentaires
NotWD ·-1 m.
Ant's been a machine as expected, but Randle's genuinely beating the beyblade allegations and it's so
nice to see
186
Repondre
MG_MN ·-1 m.
 Comm. du top 1%
Randle has been a revelation. His bully ball has worked perfectly on offense, and his physically is a big
reason LeBron has run out of gas
↑55
 Répondre
Gbaby245 ·-1 m.
Randle knows he can out muscle most defenders and then makes the correct read when
doubles come. He also plays defense with his chest, not hands so he doesn't get the fouls Kat did.
Luka andBroncan'tjustshoveRandleoutof thewayoneverydrive.
↑32
 Repondre
pacific_plywood ·-10j
Wild to think that he's only a 5-time all star. Less than Kyle Lowry or Joe Johnson.
429
 Repondre
BoogerSugarSovereign·-10 j
Comm.du top 1%
Guard was a lot lowerintheregular season
than the playoffs. His highest regular season average FGA was 15.4. He has 8 playoff runs with a
higher average FGA topping out at 22.5 in the 2000 Finals run.
273
 Repondre
smez86·-10j
not just "guard" either. you have to remember that rosters were constructed by position. sg1 in
the east was guaranteed mj, so you only had 1 or 2 other spots.
136
 Repondre
GrapeGrass-·-15j
 Comm. du top 1%
A lot of nba fans like the popularity contest more than the basketball
756
 Repondre
breighvehart ·-15j
NBA is here for the highlights and promoting superstars, basketball is like the 3rd most important
thing
↑178
Répondre
ForsakenDragonfruit4·-15j
Complaining about the modern game, comparing all time greats and tabloid discussions firmly
pushbasketball out of thetop5basketball related topics
61
 Repondre
55555_55555·-12j
Sixteamshavemade theFinalswith lower thana 4seed and noneof themhavehad homecourtinthe
Finals.Think the answeris none, at least in the modern NBA.
240
 Repondre
rooftopworld·-12j
Good lord, only 6? I knew it was rare, but I didn't think it was that rare.
↑59
 Repondre
"""

# Test comment extraction
comments = chunker.extract_comments(sample_text)
print(f"Extracted {len(comments)} comments from sample text:\n")
for i, c in enumerate(comments, 1):
    print(f"  [{i}] u/{c['author']} ({c['upvotes']} upvotes)")
    print(f"      {c['text'][:100]}...")
    print()

# Test chunking
chunks = chunker.chunk_reddit_thread(sample_text, "test_reddit.pdf")
print(f"\nChunks created: {len(chunks)}")
for chunk in chunks:
    print(f"  Chunk {chunk.metadata.get('chunk_index', '?')}: "
          f"{chunk.metadata.get('comments_in_chunk', 0)} comments, "
          f"{len(chunk.text)} chars")

# Expected: at least 8-10 comments extracted
expected = 10
status = "PASS" if len(comments) >= 8 else "FAIL"
print(f"\n{status}: Extracted {len(comments)} comments (expected >= 8 from {expected} in sample)")
