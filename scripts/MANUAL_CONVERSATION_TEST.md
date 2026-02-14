# Manual SQL Conversation Test

## Thread: correction_celtics (User Correction + Pronoun Resolution)

This test demonstrates:
- User correction ("Actually, I meant...")
- Pronoun resolution ("their" → "Celtics")
- Conversation context maintenance across 3 turns

---

## Instructions

1. **Start a new conversation** in the UI (create fresh conversation)

2. **Run these 3 queries in sequence** (same conversation):

---

### Query 1: Initial Request (Warriors)
```
Show me stats for the Warriors
```

**Expected Result:**
- Should return Golden State Warriors statistics
- SQL query should filter for Warriors (GSW/Golden State)
- Response should show Warriors team stats

---

### Query 2: User Correction (Celtics)
```
Actually, I meant the Celtics
```

**Expected Result:**
- LLM should understand this is a correction
- Should now return Boston Celtics statistics instead
- SQL query should filter for Celtics (BOS/Boston)
- Demonstrates conversation awareness (knows you asked about Warriors before)

---

### Query 3: Pronoun Resolution
```
Who is their top scorer?
```

**Expected Result:**
- "their" should resolve to "Celtics" (from Query 2)
- Should return top Celtics scorer (likely Jayson Tatum)
- SQL query should filter for Celtics players and order by points
- Demonstrates context retention (remembers we're talking about Celtics)

---

## What to Verify

For each query, check:
1. ✅ **Response** - Does it make sense in context?
2. ✅ **SQL Query** - Does it reference the correct team?
3. ✅ **Query Type** - Should be SQL_ONLY or HYBRID
4. ✅ **Context Awareness** - Does it reference previous turns?

## Expected Conversation Flow

```
Turn 1: Warriors stats → Returns Warriors data
Turn 2: "Actually, Celtics" → Returns Celtics data (correction understood)
Turn 3: "their top scorer" → Returns Celtics top scorer (pronoun resolved)
```

---

## Other Test Threads Available

### progressive_filtering_1
1. "Show me players with good three-point shooting"
2. "Only from the Lakers"
3. "Sort them by attempts"

### stats_continuation
1. "Who leads the league in steals?"
2. "And blocks?"
3. "What about turnovers?"

### multi_entity_tatum_lebron
1. "Tell me about Jayson Tatum's scoring"
2. "How does his scoring compare to LeBron James?"
3. "Who has more rebounds between the two?"

### team_pronoun_pistons
1. "Which team has the highest total points?"
2. "Who are their top scorers?"
3. "What is the average age of their players?"

---

**Status**: Ready for manual testing
**Date**: 2026-02-13
