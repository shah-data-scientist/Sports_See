"""
FILE: vector_test_cases.py
STATUS: Active
RESPONSIBILITY: Pure vector test cases for Reddit discussions, glossary, and contextual queries
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

NOTES:
- Contains 75 test cases for PURE VECTOR retrieval (no SQL needed)
- Based on actual Reddit content from 4 PDFs in vector store
- Includes boosting logic tests (upvotes, NBA official, post engagement)
- Follows evaluation best practices: variety, edge cases, adversarial inputs
- Ground truth established from actual vector DB contents
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

# ==============================================================================
# REDDIT DISCUSSION QUERIES (Based on actual 4 Reddit posts in vector store)
# ==============================================================================
# Reddit 1: "Who are teams in the playoffs that have impressed you?" (31 upvotes)
# Reddit 2: "How is it that the two best teams in the playoffs..." (457 upvotes)
# Reddit 3: "Reggie Miller is the most efficient first option..." (1300 upvotes, 11515 max comment upvotes)
# Reddit 4: "Which NBA team did not have home court advantage..." (272 upvotes)
# ==============================================================================

EVALUATION_TEST_CASES: list[EvaluationTestCase] = [
    # ==========================================================================
    # REDDIT OPINION & DISCUSSION QUERIES (11 cases)
    # ==========================================================================
    EvaluationTestCase(
        question="What do Reddit users think about teams that have impressed in the playoffs?",
        ground_truth=(
            "Should retrieve Reddit 1.pdf: 'Who are teams in the playoffs that have impressed you?' by u/MannerSuperb "
            "(31 upvotes, 236 comments). Expected teams mentioned: Magic (Paolo Banchero, Franz Wagner), Indiana Pacers, "
            "Minnesota Timberwolves (Anthony Edwards), Pistons. Comments discuss exceeding expectations, young talent, "
            "and surprising playoff performances. Expected sources: 2-5 chunks from Reddit 1.pdf with 75-85% similarity."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What are the most popular opinions about the two best playoff teams?",
        ground_truth=(
            "Should retrieve Reddit 2.pdf: 'How is it that the two best teams in the playoffs based on stats, having a chance "
            "of playing against each other in the Finals, is considered to be a snoozefest?' by u/mokaloca82 (457 upvotes, "
            "440 comments). Top comment (756 upvotes): 'A lot of nba fans like the popularity contest more than the basketball'. "
            "Discussion themes: ratings decline, small market teams (OKC, Pacers), popularity vs quality. Expected sources: "
            "Reddit 2.pdf chunks with 75-85% similarity."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do fans debate about Reggie Miller's efficiency?",
        ground_truth=(
            "Should retrieve Reddit 3.pdf: 'Reggie Miller is the most efficient first option in NBA playoffs' by u/hqppp "
            "(1300 post upvotes, up to 11515 comment upvotes - HIGHEST engagement). Expected discussion: True Shooting "
            "percentage (TS%), playoff efficiency metrics, historical comparisons to other playoff scorers (table with 20 players "
            "including Kawhi 112%, Curry 110%, LeBron 107%, Jordan 106%). Due to high engagement, boosting should prioritize "
            "this post (rank in top 3). Expected sources: Reddit 3.pdf with 80-90% similarity for efficiency-related queries."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which NBA teams didn't have home court advantage in finals according to discussions?",
        ground_truth=(
            "Should retrieve Reddit 4.pdf: 'Which NBA team did not have home court advantage until the NBA Finals?' by u/DonT012 "
            "(272 upvotes, 51 comments). Top answer (240 upvotes): 'Six teams have made the Finals with lower than a 4 seed and "
            "none of them have had home court in the Finals'. Specific examples mentioned: 2020 Lakers, 1995 Rockets (47-35 record), "
            "Knicks in lockout season. Expected sources: Reddit 4.pdf chunks with 75-85% similarity."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do fans think about home court advantage in the playoffs?",
        ground_truth=(
            "Should retrieve Reddit 4.pdf about home court advantage. Comments discuss: play-in tournament implications, "
            "how lower-seeded teams (below 4 seed) never had home court in Finals, importance of seeding for playoff success. "
            "Discussion about 2020 Lakers example and how modern play-in affects scenarios. Expected sources: Reddit 4.pdf "
            "chunks discussing home court importance with 72-82% similarity."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="According to basketball discussions, what makes a player efficient in playoffs?",
        ground_truth=(
            "Should retrieve Reddit 3.pdf discussion about playoff efficiency. Content includes TS% metric (True Shooting %), "
            "comparison table of 20 players' playoff efficiency, discussion of what qualifies as 'efficient' first option. "
            "May also retrieve comments explaining TS% calculation and why it matters for playoff performance. Expected sources: "
            "Reddit 3.pdf chunks discussing efficiency metrics with 75-85% similarity."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Do fans debate about historical playoff performances?",
        ground_truth=(
            "Should retrieve Reddit 3.pdf (historical efficiency comparison of 20 players across playoff history) and Reddit 4.pdf "
            "(historical home court examples: 2020 Lakers, 1995 Rockets). Both posts contain debates about past playoff performances. "
            "Expected sources: Chunks from Reddit 3 and Reddit 4 with historical references. Similarity: 73-83%."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Which playoff topics generate the most discussion on Reddit?",
        ground_truth=(
            "Should retrieve chunks prioritized by post engagement boosting (0-1%): (1) Reddit 3 (1300 upvotes) - efficiency, "
            "(2) Reddit 2 (457 upvotes) - two best teams debate, (3) Reddit 4 (272 upvotes) - home court, (4) Reddit 1 (31 upvotes) "
            "- impressive teams. Boosting should rank Reddit 3 content highest. Expected sources: Chunks from all 4 posts ranked "
            "by engagement. Similarity: 70-80%. Tests post engagement boosting logic."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What do NBA fans consider surprising about playoff results?",
        ground_truth=(
            "Should retrieve Reddit 1.pdf (teams that impressed: Magic, Wolves, Pacers exceeding expectations) and potentially "
            "Reddit 2.pdf (debate about whether 'two best teams' being a 'snoozefest' is surprising). Expected themes: underdog "
            "performance, young players stepping up, unexpected competitiveness. Expected sources: Reddit 1 primarily, possibly "
            "Reddit 2. Similarity: 75-85%."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do fans think about NBA trades?",
        ground_truth=(
            "Should retrieve Reddit discussions that mention trades or player movement. Reddit 1.pdf may contain "
            "comments about team roster changes and trades. Reddit 2.pdf discusses team composition. If no direct trade "
            "discussion exists in the vector store, LLM should acknowledge limited information on trades and reference "
            "available discussions about team performance and roster composition. Expected sources: Reddit chunks mentioning "
            "trades, roster changes, or player movement. Similarity: 68-78%."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What did u/MannerSuperb post about?",
        ground_truth=(
            "Should retrieve Reddit 1.pdf: post by u/MannerSuperb titled 'Who are teams in the playoffs that have "
            "impressed you?' (31 upvotes, 236 comments). This tests user-specific retrieval — the username 'MannerSuperb' "
            "appears in Reddit 1 metadata. Expected sources: Reddit 1.pdf chunks containing username or post title. "
            "Similarity: 70-80%. If system cannot find user, it should acknowledge the post content without identifying the author."
        ),
        category=TestCategory.SIMPLE,
    ),

    # ==========================================================================
    # BOOSTING LOGIC TESTS (9 cases)
    # Test metadata-based re-ranking: upvotes, NBA official, post engagement
    # ==========================================================================
    EvaluationTestCase(
        question="Tell me about the most discussed playoff efficiency topic.",
        ground_truth=(
            "Should retrieve Reddit 3.pdf: 'Reggie Miller is the most efficient first option in NBA playoffs' which has HIGHEST "
            "engagement (1300 post upvotes, 11515 max comment upvotes). Post engagement boosting (0-1%) should rank Reddit 3 content "
            "as #1 result above all other posts. Contains TS% comparison table with 20 players. Expected: Reddit 3.pdf chunks ranked "
            "FIRST. Similarity: 82-92%. If Reddit 3 not ranked #1, boosting is broken."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What's the most popular Reddit discussion about playoffs?",
        ground_truth=(
            "Post engagement boosting (0-1% based on upvotes) should create ranking: (1) Reddit 3 (1300 upvotes) >> (2) Reddit 2 "
            "(457) > (3) Reddit 4 (272) > (4) Reddit 1 (31). Tests post-level boosting. Expected: Reddit 3.pdf chunk ranked FIRST "
            "regardless of query. Similarity: 68-78% (general query). Failure mode: If Reddit 3 not first, post boosting broken."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Show me highly upvoted comments about basketball.",
        ground_truth=(
            "Comment upvote boosting (0-2% relative within each post) should prioritize: (1) Reddit 2 comment (756 upvotes), "
            "(2) Reddit 4 comment (240 upvotes), (3) Reddit 1 comment (186 upvotes). Within-post relative boosting means comments "
            "are boosted relative to other comments in same post. Expected sources: Chunks containing these top comments ranked "
            "by comment upvotes. Similarity: 70-80%. Tests comment-level boosting logic."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do authoritative voices say about playoff basketball?",
        ground_truth=(
            "Should prioritize: (1) NBA official accounts (if present, 2% boost), (2) highly-upvoted comments (756, 240, 186 upvotes "
            "from Reddit 2, 4, 1 respectively), (3) high-engagement posts (Reddit 3 with 1300 upvotes). Tests COMBINED boosting: "
            "is_nba_official + comment upvotes + post engagement. Expected sources: Top-boosted chunks from multiple posts. "
            "Similarity: 68-78%. Failure mode: If low-engagement, low-upvote content ranks higher, combined boosting broken."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Compare opinions on efficiency from high-engagement vs low-engagement posts.",
        ground_truth=(
            "Query about 'efficiency' should retrieve: (1) Reddit 3 (1300 upvotes, explicitly about efficiency) ranked MUCH HIGHER "
            "than (2) Reddit 1 (31 upvotes, mentions efficiency indirectly). Post engagement boost creates ~43x difference in "
            "engagement weighting. Expected: Reddit 3 chunks with 'efficiency' ranked top 3, Reddit 1 (if any) ranked lower. "
            "Similarity: Reddit 3 (82-90%), Reddit 1 (70-78%). Tests post-level boost discrimination."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What are the consensus views on playoff performance?",
        ground_truth=(
            "Highly-upvoted comments represent community consensus: (1) Reddit 2 top comment (756 upvotes) about popularity contest, "
            "(2) Reddit 4 top comment (240 upvotes) about six teams without home court, (3) Reddit 1 top comment (186 upvotes) about "
            "Ant being a machine. Comment boosting should surface these popular opinions above lower-upvoted 'niche takes'. Expected "
            "sources: Top 3-5 chunks with highest comment upvotes. Similarity: 70-80%."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Find the most engaged discussion about NBA history.",
        ground_truth=(
            "Should retrieve Reddit 3.pdf (historical playoff efficiency comparison across 20 players) with 1300 upvotes - highest "
            "engagement. Contains historical data: Reggie Miller (115 TS%), Kawhi (112%), Curry (110%), Jordan (106%), etc. Post "
            "engagement boosting should rank Reddit 3 FIRST above Reddit 4 (272 upvotes, also historical: 2020 Lakers, 1995 Rockets). "
            "Expected: Reddit 3 ranked #1. Similarity: 78-88%. Tests post boosting for historical queries."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do the top comments say about playoff success?",
        ground_truth=(
            "Should retrieve chunks containing highest-upvoted comments: (1) Reddit 2 (756 upvotes) - fans prefer popularity over "
            "basketball quality, (2) Reddit 4 (240 upvotes) - six teams below 4 seed never had home court advantage, (3) Reddit 1 "
            "(186 upvotes) - Ant being a machine, Randle beating beyblade allegations. Comment upvote boosting (0-2% relative) should "
            "prioritize these. Expected sources: 3-5 chunks with top comment content. Similarity: 72-82%."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Show me verified or official perspectives on basketball.",
        ground_truth=(
            "NBA official accounts (is_nba_official=1) receive 2% boost. Expected: If NBA official chunks exist in vector store, "
            "they rank in top 3 results regardless of lower semantic similarity. If NO NBA official content exists, system should "
            "return regular high-quality content (high-upvote comments) and clarify no official sources available. Similarity: 70-82%. "
            "Tests NBA official boosting. Note: Verify if current vector store contains any is_nba_official=1 chunks."
        ),
        category=TestCategory.SIMPLE,
    ),

    # ==========================================================================
    # GLOSSARY / TERMINOLOGY QUERIES (8 cases)
    # Based on basketball dictionary/glossary in vector store
    # ==========================================================================
    EvaluationTestCase(
        question="What is a pick and roll?",
        ground_truth=(
            "Should retrieve regular NBA.xlsx (glossary/reference document), NOT Reddit discussions. Expected definition: Pick and roll "
            "is an offensive play where a player sets a screen (pick) and then moves toward the basket (roll). Glossary should rank "
            "HIGHEST (85-95% similarity) for terminology queries. If Reddit content ranks higher than glossary, this indicates boosting "
            "problem - terminology queries should prioritize reference documents over discussion posts. Expected source: glossary chunk "
            "ranked #1."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Explain what PER means in basketball.",
        ground_truth=(
            "Should retrieve regular NBA.xlsx glossary defining PER (Player Efficiency Rating) as an advanced statistic measuring per-minute "
            "performance. Glossary should rank HIGHEST (85-95% similarity). If Reddit 3 discussion about efficiency ranks higher, boosting "
            "is broken - definition queries must prioritize glossary over discussions. Expected source: glossary chunk ranked #1 with "
            "PER definition."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What does zone defense mean?",
        ground_truth=(
            "Should retrieve regular NBA.xlsx glossary. Expected definition: Zone defense is a defensive strategy where players guard "
            "court areas/zones rather than specific opponents. Glossary should rank HIGHEST (85-95% similarity) for exact term definitions. "
            "Failure mode: If Reddit discussions rank higher, indicates glossary boosting insufficient. Expected source: glossary chunk "
            "ranked #1."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Define true shooting percentage.",
        ground_truth=(
            "Should retrieve regular NBA.xlsx glossary. Expected definition: True Shooting Percentage (TS%) accounts for 2-pointers, "
            "3-pointers, and free throws in efficiency calculation. May include formula: TS% = Points / (2 * (FGA + 0.44*FTA)). "
            "Glossary should rank HIGHEST (85-95% similarity). Note: Reddit 3 discusses TS% but glossary MUST rank higher for "
            "definition query. Expected source: glossary chunk #1, not Reddit discussion. Tests glossary prioritization."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What is a triple-double?",
        ground_truth=(
            "Should retrieve regular NBA.xlsx glossary. Expected definition: Triple-double means achieving double-digit totals (10+) "
            "in three statistical categories in a single game (e.g., points, rebounds, assists). Glossary should rank HIGHEST (85-95% "
            "similarity) for exact term definition. Expected source: glossary chunk ranked #1."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Explain the difference between man-to-man and zone defense.",
        ground_truth=(
            "Should retrieve regular NBA.xlsx glossary, NOT Reddit discussions. Expected definition: Man-to-man = each defender guards "
            "specific opponent; Zone defense = defenders guard court areas/zones. Glossary should rank HIGHEST (85-95% similarity) for "
            "terminology queries. If Reddit content ranks higher than glossary, this indicates boosting problem - terminology queries "
            "should prioritize reference documents over discussion posts. Expected source: glossary chunk ranked #1."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What basketball terms are important for understanding efficiency?",
        ground_truth=(
            "Should retrieve regular NBA.xlsx glossary chunks defining multiple efficiency metrics: TS% (True Shooting %), eFG% (Effective "
            "Field Goal %), PER (Player Efficiency Rating), usage rate. May retrieve 2-3 glossary chunks covering these terms. Glossary "
            "should rank HIGHEST (85-93% similarity per chunk). If Reddit 3 (efficiency discussion) ranks higher than glossary definitions, "
            "boosting is broken. Expected sources: 2-4 glossary chunks in top 5 results."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What does 'first option' mean in basketball?",
        ground_truth=(
            "May retrieve: (1) regular NBA.xlsx glossary definition if available ('first option = team's primary scorer/go-to offensive player'), "
            "or (2) Reddit 3.pdf contextual usage ('Reggie Miller is the most efficient first option'). If glossary has definition, it should "
            "rank HIGHEST (85-95%). If glossary lacks this term, Reddit 3 context is acceptable (75-85%). Expected source: glossary if available, "
            "otherwise Reddit 3 with contextual explanation."
        ),
        category=TestCategory.SIMPLE,
    ),

    # ==========================================================================
    # OUT-OF-SCOPE / TRICK QUESTIONS (12 cases)
    # Test system's ability to recognize irrelevant queries
    # ==========================================================================
    EvaluationTestCase(
        question="What is the weather forecast for Los Angeles tomorrow?",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve irrelevant chunks (likely Reddit PDFs with ~65-70% similarity due to "
            "semantic overlap with 'Los Angeles'). However, LLM should recognize retrieved content is basketball-related, NOT weather, "
            "and respond with 'I don't have information about weather forecasts. My knowledge base contains NBA basketball discussions "
            "only.' Tests LLM's ability to reject irrelevant context despite retrieval. Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="How do I bake a chocolate cake?",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve irrelevant Reddit chunks with ~62-68% similarity (weakest match due to "
            "no semantic overlap). LLM should recognize content is basketball-related, NOT cooking, and respond with 'I don't have "
            "information about baking. My knowledge base covers NBA basketball only.' Tests LLM filtering of completely unrelated queries. "
            "Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Tell me about the latest political election results.",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve irrelevant Reddit chunks (likely Reddit 1-4 with ~68-72% similarity due to "
            "semantic overlap with 'results', 'latest'). However, LLM should recognize content is basketball-related, NOT political, and "
            "respond with 'I don't have information about political elections. My knowledge base contains NBA basketball discussions only.' "
            "Tests LLM's ability to reject irrelevant context despite retrieval. Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="What is the stock price of Apple Inc.?",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve irrelevant chunks (~63-68% similarity). LLM should recognize content is "
            "basketball-related, NOT financial data, and respond with 'I don't have information about stock prices. My knowledge base "
            "covers NBA basketball only.' Tests LLM filtering of financial queries. Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Best strategy for winning in NBA 2K24 video game?",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve basketball-related chunks (~72-78% similarity due to 'NBA' keyword match), "
            "possibly Reddit discussions about strategies. However, LLM should recognize query asks about VIDEO GAME, not real NBA, and "
            "respond with 'I don't have information about NBA 2K video games. My knowledge base covers real NBA basketball only.' Tests "
            "LLM's ability to distinguish video game vs real basketball. Expected: LLM declines or clarifies only real NBA covered."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="How to fix my computer's blue screen error?",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve irrelevant chunks (~60-67% similarity - very weak). LLM should recognize "
            "content is basketball-related, NOT tech support, and respond with 'I don't have information about computer issues. My "
            "knowledge base covers NBA basketball only.' Tests LLM filtering of tech support queries. Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="What are the best restaurants in New York City?",
        ground_truth=(
            "Out-of-scope query. Vector search WILL retrieve irrelevant chunks (~64-69% similarity, possibly New York Knicks mentions). "
            "LLM should recognize content is basketball-related, NOT restaurant recommendations, and respond with 'I don't have information "
            "about restaurants. My knowledge base covers NBA basketball only.' Tests LLM filtering. Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="?",
        ground_truth=(
            "Single punctuation mark is not meaningful query. Vector search WILL retrieve random chunks (~55-65% similarity - very weak, "
            "essentially random). LLM should recognize lack of coherent question and respond with 'Could you please provide a more specific "
            "question?' or 'I need more information to help you.' Tests LLM's handling of non-queries. Expected: LLM asks for clarification."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="asdfghjkl qwerty12345",
        ground_truth=(
            "Random keyboard mashing. Vector search WILL retrieve random chunks (~50-60% similarity - essentially random match). LLM should "
            "recognize lack of coherent query intent and respond with 'I don't understand this query. Could you rephrase your question?' "
            "Tests LLM's handling of gibberish input. Expected: LLM asks for clarification or states it cannot understand."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Give me a 10000 word essay on the history of the universe.",
        ground_truth=(
            "Out-of-scope (cosmology) + unreasonable request (10000 words). Vector search WILL retrieve irrelevant chunks (~65-70% similarity "
            "due to 'history'). LLM should: (1) recognize topic is out of scope (universe history, not NBA), AND (2) decline to generate "
            "excessively long response. Expected: LLM responds 'I don't have information about universe history. My knowledge base covers NBA "
            "basketball only.'"
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Translate 'hello' to 50 different languages.",
        ground_truth=(
            "Out-of-scope query (translation service). Vector search WILL retrieve irrelevant chunks (~60-68% similarity - weak match). LLM "
            "should recognize content is basketball-related, NOT translation service, and respond with 'I don't provide translation services. "
            "My knowledge base covers NBA basketball only.' Tests LLM filtering. Expected: LLM declines to answer."
        ),
        category=TestCategory.NOISY,
    ),

    # ==========================================================================
    # ADVERSARIAL / SECURITY TESTS (5 cases)
    # Test input sanitization and security
    # ==========================================================================
    EvaluationTestCase(
        question="<script>alert('XSS')</script> Who won the MVP?",
        ground_truth=(
            "XSS injection attempt + legitimate query. System should: (1) sanitize/escape HTML tags (no script execution), (2) extract "
            "legitimate query portion ('Who won the MVP?'), (3) respond about MVP if data available. Vector search should process sanitized "
            "query and retrieve relevant chunks (~70-80% similarity if MVP discussed in Reddit). Tests input sanitization + query extraction. "
            "Expected: Safe response about MVP, no script execution."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="'; DROP TABLE players; --",
        ground_truth=(
            "SQL injection attempt. System should: (1) treat as literal text string, NOT SQL command, (2) not execute any database operations, "
            "(3) vector search processes it as gibberish text (~55-65% similarity - very weak, random chunks). LLM should respond with "
            "'I don't understand this query' or similar. Tests SQL injection prevention. Expected: No database modification, safe error handling."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="../../../etc/passwd",
        ground_truth=(
            "Path traversal attempt. System should: (1) treat as literal text, NOT file path, (2) not access file system, (3) vector search "
            "processes as text string (~50-60% similarity - essentially random). LLM should respond with 'I don't understand this query' or "
            "ask for clarification. Tests path traversal prevention. Expected: No file system access, safe error handling."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="{{7*7}} ${7*7} <%= 7*7 %>",
        ground_truth=(
            "Template injection attempts (Jinja, JavaScript, ERB). System should: (1) treat as literal text, NOT execute templates, (2) no "
            "evaluation of expressions (result should NOT be '49'), (3) vector search processes as text (~55-65% similarity - weak match). "
            "Tests template injection prevention. Expected: Literal text response or 'I don't understand', no code execution."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="A" * 10000,
        ground_truth=(
            "Excessively long input (10,000 'A' characters). System should: (1) handle gracefully without crashing, (2) possibly truncate "
            "input to reasonable length (e.g., first 500-1000 chars), or (3) reject with 'Query too long' error. Vector search may process "
            "truncated version (~50-60% similarity - random match). Tests DoS protection and input length limits. Expected: Graceful handling, "
            "no crash, reasonable response or error message."
        ),
        category=TestCategory.NOISY,
    ),

    # ==========================================================================
    # CONVERSATIONAL / MULTI-STEP QUERIES (12 cases)
    # Test context maintenance across turns
    # ==========================================================================
    # Conversation Thread 1: Lakers
    EvaluationTestCase(
        question="What do fans say about the Lakers?",
        ground_truth=(
            "Should retrieve Reddit discussions mentioning Lakers. Most likely source: Reddit 4.pdf mentions '2020 Lakers' as example of "
            "team without home court advantage in Finals. May also appear in Reddit 1 or 2 if discussing playoff teams. Expected sources: "
            "1-2 chunks from Reddit PDFs mentioning Lakers. Similarity: 72-82%. Tests Lakers-specific retrieval. Note: This is FIRST turn "
            "of conversation - establishes context for follow-ups."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What are their biggest strengths?",
        ground_truth=(
            "Follow-up question referencing 'their' = Lakers from Turn 1. System should: (1) maintain conversation context (Lakers = subject), "
            "(2) retrieve Lakers-specific content about strengths. Expected sources: Same Reddit chunks mentioning Lakers, focused on positive "
            "attributes. Similarity: 70-80%. Tests context maintenance across turns. NOTE: Evaluation should provide Turn 1 question as context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="And their weaknesses?",
        ground_truth=(
            "Second follow-up still referencing Lakers from Turn 1 and 2. System should: (1) maintain conversation context across THREE turns, "
            "(2) retrieve Lakers content about weaknesses/limitations. Expected sources: Reddit chunks mentioning Lakers challenges. Similarity: "
            "68-78%. Tests multi-turn context maintenance. NOTE: Evaluation should provide Turn 1 AND Turn 2 as context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # Conversation Thread 2: Playoff teams
    EvaluationTestCase(
        question="Tell me about playoff teams that surprised people.",
        ground_truth=(
            "Should retrieve Reddit 1.pdf: 'Who are teams in the playoffs that have impressed you?' discussing Magic (Paolo/Franz), Wolves "
            "(Ant), Pacers, Pistons. Top comment (186 upvotes) about Ant being a machine and Randle beating allegations. Expected sources: "
            "2-4 chunks from Reddit 1.pdf. Similarity: 78-86%. Tests retrieval of surprising teams. NOTE: FIRST turn - establishes team context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Why were they surprising?",
        ground_truth=(
            "Follow-up referencing 'they' = surprising teams from Turn 1 (Magic, Wolves, Pacers, Pistons). System should: (1) maintain context "
            "of which teams were mentioned, (2) retrieve Reddit 1.pdf chunks explaining WHY teams were surprising (young talent, exceeding "
            "expectations, Randle's performance). Expected sources: Reddit 1.pdf chunks with reasoning. Similarity: 75-85%. Tests context "
            "maintenance. NOTE: Evaluation should provide Turn 1 as context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Compare them to the top-seeded teams.",
        ground_truth=(
            "Third-level follow-up referencing 'them' = surprising teams from Turn 1-2. System should: (1) maintain conversation context across "
            "THREE turns, (2) retrieve content comparing underdogs (Magic, Wolves, Pacers) to top seeds. May retrieve Reddit 2.pdf discussion "
            "about 'two best teams'. Expected sources: Reddit 1 + potentially Reddit 2. Similarity: 70-80%. Tests multi-turn context + comparison. "
            "NOTE: Evaluation should provide Turn 1 AND Turn 2 as context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # Conversation Thread 3: Efficiency discussion
    EvaluationTestCase(
        question="What makes a player efficient in the playoffs?",
        ground_truth=(
            "Should retrieve Reddit 3.pdf discussing playoff efficiency metrics: TS% (True Shooting %), scoring volume, comparison of 20 players. "
            "Expected definition: efficiency = high TS% (115% for Miller, 112% Kawhi, 110% Curry). Expected sources: 2-3 chunks from Reddit 3.pdf "
            "explaining efficiency metrics. Similarity: 76-86%. Tests efficiency concept retrieval. NOTE: FIRST turn - establishes efficiency context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Who is the most efficient according to fans?",
        ground_truth=(
            "Follow-up asking for specific player. Should retrieve Reddit 3.pdf: 'Reggie Miller is the most efficient first option in NBA playoff "
            "history' (1300 upvotes). Post engagement boosting should rank Reddit 3 HIGHEST. Expected sources: Reddit 3.pdf chunks about Reggie "
            "Miller with 115 TS%. Similarity: 82-92%. Tests context maintenance + boosting. NOTE: Evaluation should provide Turn 1 as context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What do people debate about his efficiency?",
        ground_truth=(
            "Second follow-up referencing 'his' = Reggie Miller from Turn 2. System should: (1) maintain context across THREE turns (efficiency "
            "→ Reggie Miller → debate about him), (2) retrieve Reddit 3.pdf comment debates about Miller's efficiency: TS% validity, era comparisons, "
            "whether he's truly #1. Expected sources: Reddit 3 comment chunks with debate content. Similarity: 75-85%. Tests multi-turn context "
            "maintenance. NOTE: Evaluation should provide Turn 1 AND Turn 2 as context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # Conversation Thread 4: Topic switching
    EvaluationTestCase(
        question="Tell me about home court advantage in playoffs.",
        ground_truth=(
            "Should retrieve Reddit 4.pdf: 'Which NBA team did not have home court advantage until the NBA Finals?' (272 upvotes, 51 comments). "
            "Top answer (240 upvotes): Six teams below 4 seed never had home court in Finals. Examples: 2020 Lakers, 1995 Rockets. Expected "
            "sources: 2-3 chunks from Reddit 4.pdf. Similarity: 78-86%. Tests home court topic retrieval. NOTE: FIRST turn - establishes "
            "home court context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Going back to efficiency, who else is considered efficient?",
        ground_truth=(
            "TOPIC SWITCH from home court (Turn 1) back to efficiency. Phrase 'Going back to' indicates explicit topic change. System should: "
            "(1) recognize topic switch, (2) retrieve Reddit 3.pdf efficiency discussion about players OTHER than Reggie Miller: Kawhi (112 TS%), "
            "Curry (110%), Durant (109%), LeBron (107%), Jordan (106%). Expected sources: Reddit 3.pdf with efficiency table. Similarity: 75-85%. "
            "Tests topic switching and explicit 'going back to' handling."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Returning to home court, which teams historically lacked it?",
        ground_truth=(
            "SECOND topic switch, back to home court from Turn 1. Phrase 'Returning to' indicates explicit topic change. System should: (1) recognize "
            "topic switch back to home court, (2) retrieve Reddit 4.pdf with historical examples: 2020 Lakers, 1995 Rockets (47-35 record), Knicks "
            "in lockout season. Expected sources: Reddit 4.pdf chunks with specific team examples. Similarity: 76-86%. Tests non-linear conversation "
            "flow and explicit topic switching."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # ==========================================================================
    # NOISY / INFORMAL LANGUAGE QUERIES (9 cases)
    # Test robustness to typos, slang, abbreviations
    # ==========================================================================
    EvaluationTestCase(
        question="whos da best playa in playoffs acording 2 reddit",
        ground_truth=(
            "Noisy query with typos and text-speak. Should map to: 'Who is the best player in playoffs according to Reddit?'. Should retrieve "
            "Reddit discussions mentioning top players: Ant (Anthony Edwards) from Reddit 1 top comment (186 upvotes), or players from Reddit 3 "
            "efficiency discussion. Vector search should be robust to typos ('whos'→'who is', 'playa'→'player', '2'→'to'). Expected sources: "
            "Reddit 1 or 3 with player mentions. Similarity: 70-80% (lower due to noise). Tests typo robustness."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="reggie milr effishency debat",
        ground_truth=(
            "Heavy typos but clear intent: 'Reggie Miller efficiency debate'. Should retrieve Reddit 3.pdf: 'Reggie Miller is the most efficient "
            "first option in NBA playoffs' (1300 upvotes). Vector search should be robust to typos ('milr'→'Miller', 'effishency'→'efficiency', "
            "'debat'→'debate'). High engagement boosting should still prioritize Reddit 3. Expected sources: Reddit 3.pdf chunks. Similarity: "
            "72-82% (lower due to typos). Tests typo robustness + boosting."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="lmao bro playoff teams are wild this year fr fr",
        ground_truth=(
            "Informal slang expressing opinion about surprising playoff teams. Should map to Reddit 1.pdf: 'Who are teams in the playoffs that "
            "have impressed you?' discussing Magic, Wolves, Pacers, Pistons. Vector search should understand 'wild'='impressive'/'surprising', "
            "ignore slang filler ('lmao', 'bro', 'fr fr'). Expected sources: Reddit 1.pdf chunks about impressive teams. Similarity: 70-80% "
            "(lower due to slang). Tests informal language understanding."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="imho home court dont matter much tbh",
        ground_truth=(
            "Abbreviations + informal grammar expressing opinion on home court advantage. Should map to Reddit 4.pdf discussing home court "
            "importance. Vector search should: (1) expand abbreviations (imho='in my humble opinion', tbh='to be honest'), (2) handle grammar "
            "('dont'→'doesn't'), (3) understand 'doesn't matter much'='not important'. Expected sources: Reddit 4.pdf chunks. Similarity: "
            "68-78%. Tests abbreviation expansion and informal grammar."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="playoff playoff playoff teams teams impressive impressive",
        ground_truth=(
            "Keyword stuffing/repetition but clear intent: 'playoff teams impressive'. Should map to Reddit 1.pdf: 'Who are teams in the playoffs "
            "that have impressed you?'. Vector search should handle repetition and extract core meaning. Expected sources: Reddit 1.pdf chunks "
            "about impressive teams (Magic, Wolves, Pacers). Similarity: 72-82%. Tests keyword repetition robustness."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="reddit nba thoughts???",
        ground_truth=(
            "Extremely vague query with excessive punctuation. Vector search WILL retrieve random Reddit chunks (~68-75% similarity). LLM should: "
            "(1) recognize query is too vague, AND (2) either ask 'What specific NBA topic would you like to know about?' OR provide general summary "
            "of available Reddit topics (impressive teams, efficiency, home court, two best teams). Tests handling of vague queries. Expected: "
            "Clarification request or topic overview."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="yo what ppl saying bout top teams",
        ground_truth=(
            "Casual slang asking about top teams. Should map to Reddit 2.pdf: 'How is it that the two best teams in the playoffs...' (457 upvotes). "
            "Vector search should understand: 'yo what'='what are', 'ppl'='people', 'bout'='about', 'top teams'='best teams'. Expected sources: "
            "Reddit 2.pdf chunks about two best teams. Similarity: 72-82%. Tests slang understanding."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="nba",
        ground_truth=(
            "Single word, extremely vague. Vector search WILL retrieve random Reddit chunks (~65-75% similarity - all have 'nba' keyword). LLM "
            "should recognize query lacks specificity and respond with: 'What would you like to know about the NBA? I can help with playoff discussions, "
            "team performance, player efficiency, or basketball terminology.' Tests vague single-word query handling. Expected: Clarification request "
            "with topic examples."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="hello",
        ground_truth=(
            "Non-question greeting input. Vector search WILL retrieve random chunks (~60-70% similarity - weak semantic match). "
            "LLM should recognize this is a greeting, not a question, and respond with something like 'Hello! How can I help you "
            "with NBA basketball information today?' or ask what topic the user is interested in. Tests handling of non-question "
            "greetings vs gibberish (different from '?' or 'asdfghjkl' which are unintelligible). Expected: Friendly greeting "
            "response with topic suggestions."
        ),
        category=TestCategory.NOISY,
    ),

    # ==========================================================================
    # COMPLEX ANALYTICAL QUERIES (10 cases)
    # Test retrieval for multi-faceted analytical questions
    # ==========================================================================
    EvaluationTestCase(
        question="Analyze the evolution of playoff strategies based on fan discussions.",
        ground_truth=(
            "Complex multi-document synthesis query. Should retrieve chunks from: (1) Reddit 1 (young talent strategies: Magic with Paolo/Franz, "
            "Wolves with Ant), (2) Reddit 2 (discussion of stats-based vs popularity-based team evaluation), (3) Reddit 3 (efficiency-focused "
            "strategies: TS% emphasis). Expected sources: 4-6 chunks from 2-3 different Reddit PDFs synthesizing strategic themes. Similarity: "
            "68-78% per chunk. Tests cross-document synthesis and analytical retrieval."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What patterns emerge from Reddit debates about playoff performance?",
        ground_truth=(
            "Meta-analysis requiring identification of recurring themes across ALL 4 Reddit posts. Patterns: (1) Efficiency metrics emphasis "
            "(Reddit 3: TS%, comparison tables), (2) Surprising/impressive teams (Reddit 1: Magic, Wolves, Pacers), (3) Home court importance "
            "(Reddit 4: six teams without home court), (4) Popularity vs quality debate (Reddit 2: 'snoozefest' discussion). Expected sources: "
            "5-7 chunks from 3-4 different Reddit PDFs. Similarity: 66-76%. Tests pattern recognition across documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="How do fan perceptions of efficiency differ from statistical measures?",
        ground_truth=(
            "Requires contrasting qualitative opinions vs quantitative stats. Should retrieve: (1) Reddit 3.pdf quantitative table (Miller 115 TS%, "
            "Kawhi 112%, etc.) showing STATISTICAL measures, AND (2) Reddit 3 comment debates showing fan PERCEPTIONS (debates about era adjustment, "
            "whether TS% is right metric). Expected sources: 3-5 chunks from Reddit 3 showing both stats and fan debates. Similarity: 70-80%. "
            "Tests qualitative vs quantitative distinction."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What controversies exist in evaluating playoff success?",
        ground_truth=(
            "Should identify debated topics across multiple Reddit posts: (1) Reddit 3: Is TS% the right efficiency metric? Era-adjusted vs raw stats, "
            "(2) Reddit 4: Does home court advantage really matter? Six teams succeeded without it, (3) Reddit 2: Popularity vs basketball quality "
            "(top comment: fans prefer popularity contest), (4) Reddit 1: Which teams truly 'impressed' (subjective evaluation). Expected sources: "
            "4-6 chunks from 3-4 Reddit PDFs showing controversy/debate. Similarity: 68-78%. Tests controversy identification."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Synthesize fan wisdom about what makes teams succeed in playoffs.",
        ground_truth=(
            "High-level synthesis requiring integration from ALL 4 Reddit posts. Success factors: (1) Reddit 1: Young talent development (Paolo, "
            "Franz, Ant), exceeding expectations, (2) Reddit 2: Statistical excellence vs popularity ('two best teams'), (3) Reddit 3: Offensive "
            "efficiency (high TS%), scoring ability, (4) Reddit 4: Ability to win without home court advantage. Expected sources: 6-8 chunks from "
            "ALL 4 Reddit PDFs synthesizing success themes. Similarity: 66-76%. Tests comprehensive multi-document synthesis. Highest complexity query."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What basketball strategies do fans discuss for playoff success?",
        ground_truth=(
            "Should retrieve Reddit discussions about playoff strategies and team approaches. Reddit 1.pdf discusses "
            "what makes teams impressive (young talent, team composition). Reddit 3.pdf discusses offensive efficiency "
            "as a strategy metric. May also retrieve glossary definitions of strategic terms (pick and roll, zone defense) "
            "from regular NBA.xlsx. Expected sources: Reddit 1 and 3 chunks about team strategies, possibly glossary. "
            "Similarity: 70-80%."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="How has the NBA changed over the years according to fan discussions?",
        ground_truth=(
            "Should retrieve Reddit discussions referencing NBA history and evolution. Reddit 3.pdf contains historical "
            "playoff efficiency comparison across 20 players spanning different eras (Reggie Miller, Jordan, LeBron, Curry). "
            "Reddit 4.pdf discusses historical home court advantage examples (2020 Lakers, 1995 Rockets). Expected sources: "
            "Reddit 3 and 4 chunks with historical context. Similarity: 68-78%. Tests broad historical synthesis across "
            "multiple documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="How many points did LeBron score and why do fans love him?",
        ground_truth=(
            "Mixed query combining statistical ask ('how many points') with opinion ask ('why do fans love him'). For vector "
            "evaluation, the system should retrieve Reddit discussions mentioning LeBron. Reddit 1.pdf and Reddit 2.pdf may "
            "contain LeBron-related fan opinions. The statistical portion may not be answerable from vector store alone (SQL "
            "would be needed). Expected: LLM should address the fan opinion portion from Reddit sources and may note that exact "
            "statistics require the database. Expected sources: Reddit chunks mentioning LeBron. Similarity: 72-82%."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What is the overall sentiment about NBA playoffs on Reddit?",
        ground_truth=(
            "Sentiment analysis across all 4 Reddit posts: (1) Reddit 1 (31 upvotes): Positive sentiment — excitement about "
            "impressive teams (Magic, Wolves), admiration for young talent. (2) Reddit 2 (457 upvotes): Mixed/critical sentiment — "
            "frustration about popularity over quality, 'snoozefest' framing. (3) Reddit 3 (1300 upvotes): Analytical/positive — "
            "respect for Reggie Miller's efficiency, debating historical greatness. (4) Reddit 4 (272 upvotes): Neutral/informative — "
            "factual discussion about home court advantage. Overall: predominantly positive about NBA quality, with critique of fan "
            "culture and media attention. Expected sources: 4-6 chunks from 2-3 Reddit PDFs. Similarity: 68-78%."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Can you give me a direct quote from the Reddit discussions about efficiency?",
        ground_truth=(
            "Should retrieve Reddit 3.pdf containing direct quotes about efficiency. Key quotes: (1) Post title: 'Reggie Miller "
            "is the most efficient first option in NBA playoff history' by u/hqppp. (2) Top comment discussing TS% comparison "
            "table showing Miller at 115 TS%. System should provide verbatim or near-verbatim text from actual Reddit chunks — "
            "NOT paraphrased content. Tests faithfulness to source material. Expected sources: Reddit 3.pdf chunks with direct "
            "quote content. Similarity: 80-90% for efficiency-related content."
        ),
        category=TestCategory.COMPLEX,
    ),
]


def get_test_case_statistics() -> dict:
    """Compute statistics about the evaluation test cases.

    Returns:
        Dictionary with category counts, total, and distribution percentages.
    """
    from collections import Counter

    counts = Counter(tc.category for tc in EVALUATION_TEST_CASES)
    total = len(EVALUATION_TEST_CASES)

    return {
        "total": total,
        "by_category": {cat.value: counts.get(cat, 0) for cat in TestCategory},
        "distribution": {
            cat.value: round(counts.get(cat, 0) / total * 100, 1) if total else 0
            for cat in TestCategory
        },
    }


def print_test_case_statistics() -> None:
    """Print formatted test case statistics to stdout."""
    stats = get_test_case_statistics()

    print("\n" + "=" * 50)
    print(f"  PURE VECTOR TEST CASES: {stats['total']} total")
    print("=" * 50)
    print(f"  {'Category':<20} {'Count':>6} {'Distribution':>14}")
    print("  " + "-" * 44)
    for cat in TestCategory:
        count = stats["by_category"][cat.value]
        pct = stats["distribution"][cat.value]
        print(f"  {cat.value:<20} {count:>6} {pct:>12.1f}%")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    print_test_case_statistics()
