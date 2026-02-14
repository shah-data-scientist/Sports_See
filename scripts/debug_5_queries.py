"""Debug the 5 hybrid→contextual misclassifications."""
import re
from src.services.query_classifier import QueryClassifier, BASKETBALL_GLOSSARY_TERMS

c = QueryClassifier()

queries = [
    "Find players averaging triple-double stats and explain what makes this achievement so rare and valuable.",
    "Which current players match the historical playoff dominance that fans discuss on Reddit?",
    "Are there players with modest scoring but exceptional all-around impact, and what does this reveal about value?",
    "Why do fans on Reddit consider him an MVP favorite?",
    "What do fans think about their chances of repeating as champions?",
]

for q in queries:
    qn = q.strip().lower()
    print()
    print("=" * 70)
    print(f"Q: {q[:80]}")

    # Check glossary
    glossary_hit = any(re.search(rf"\b{re.escape(t)}\b", qn) for t in BASKETBALL_GLOSSARY_TERMS)
    if glossary_hit:
        si = re.search(
            r"\b(who\s+has|top|highest|lowest|most|fewest|how\s+many|over|above|below|under)\b|\d+",
            qn,
        )
        print(f"  GLOSSARY HIT, stat_intent={bool(si)}")

    stat = sum(1 for p in c.statistical_regex if p.search(qn))
    ctx = sum(1 for p in c.contextual_regex if p.search(qn))
    hyb = sum(1 for p in c.hybrid_regex if p.search(qn))

    stat_idx = [i for i, p in enumerate(c.statistical_regex) if p.search(qn)]
    ctx_idx = [i for i, p in enumerate(c.contextual_regex) if p.search(qn)]
    hyb_idx = [i for i, p in enumerate(c.hybrid_regex) if p.search(qn)]

    print(f"  STAT={stat} indices: {stat_idx}")
    print(f"  CTX={ctx} indices: {ctx_idx}")
    print(f"  HYB={hyb} indices: {hyb_idx}")

    # Show which stat patterns matched
    for i in stat_idx:
        print(f"    stat[{i}]: {c.STATISTICAL_PATTERNS[i][:60]}")
    for i in ctx_idx:
        print(f"    ctx[{i}]: {c.CONTEXTUAL_PATTERNS[i][:60]}")
    for i in hyb_idx:
        print(f"    hyb[{i}]: {c.HYBRID_PATTERNS[i][:60]}")
