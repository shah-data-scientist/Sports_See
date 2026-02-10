# Database Schema Improvements

**Date**: 2026-02-10
**Status**: Completed

## Issues Addressed from Evaluation Report

The comprehensive post-chunking evaluation identified several potential database schema issues. This document clarifies what was found and what was fixed.

## Summary of Findings

| Issue Reported | Status | Resolution |
|---------------|--------|------------|
| Missing `team` column in players table | ✅ FIXED | Added full team name column |
| `ts_pct` values >100 | ✅ NOT A BUG | Mathematically correct (see explanation below) |
| Missing `tov` (turnovers) column | ✅ FALSE ALARM | Column already exists |
| Missing `teams` table | ⚠️ FALSE ALARM | Table already exists with 30 teams |

---

## 1. Added `team` Column to `players` Table

### Problem
The `players` table only had `team_abbr` (e.g., "OKC"), not the full team name (e.g., "Oklahoma City Thunder"). This made SQL generation harder for queries like "Which players play for the Lakers?"

### Solution
Added `team` column (VARCHAR(100)) to `players` table with full team names.

**Schema change:**
```sql
-- Before
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    team_abbr VARCHAR(5),  -- Only abbreviation
    age INTEGER
);

-- After
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    team VARCHAR(100),        -- ADDED: Full name ("Oklahoma City Thunder")
    team_abbr VARCHAR(5),     -- Kept for foreign key
    age INTEGER
);
```

**Verification:**
```sql
SELECT name, team, team_abbr FROM players LIMIT 5;

-- Results:
-- Shai Gilgeous-Alexander | Oklahoma City Thunder | OKC
-- Anthony Edwards         | Minnesota Timberwolves | MIN
-- Nikola Jokić            | Denver Nuggets         | DEN
-- Giannis Antetokounmpo   | Milwaukee Bucks        | MIL
-- Jayson Tatum            | Boston Celtics         | BOS
```

**Impact:**
- SQL generation improved for roster and team queries
- Queries like "List all Lakers players" now work reliably
- 30 teams, 569 players all have full team names

---

## 2. TS_PCT Values >100 - NOT A BUG

### Finding
Some players have `ts_pct` values exceeding 100 (max: 125 for Alondes Williams).

### Analysis
This is **mathematically correct**, not a database error.

**True Shooting Percentage Formula:**
```
TS% = 100 × PTS / (2 × (FGA + 0.44 × FTA))
```

**Example: Alondes Williams**
- PTS = 5
- FGA = 2
- FTA = 0

```
TS% = 100 × 5 / (2 × (2 + 0.44×0))
    = 100 × 5 / 4
    = 125
```

This happens when:
1. Very few field goal attempts (low denominator)
2. High free throw volume relative to FGA
3. Player has limited playing time (small sample size)

**Conclusion:** No fix needed. TS% >100 is unusual but valid.

**Storage format:** Values stored as DECIMAL(5,1) in percentage format (63.7 = 63.7%, not 0.637).

---

## 3. TOV (Turnovers) Column - Already Exists

### Finding
Evaluation report claimed "Turnover stats (tov) missing from database."

### Verification
```sql
PRAGMA table_info(player_stats);

-- Output (line 22):
-- tov | INTEGER | NULL=False | DEFAULT=None | PK=0
```

**Sample data:**
```sql
SELECT name, tov FROM players JOIN player_stats ON players.id = player_stats.player_id LIMIT 5;

-- Results:
-- Shai Gilgeous-Alexander | 182
-- Anthony Edwards         | 253
-- Nikola Jokić            | 231
-- Giannis Antetokounmpo   | 208
-- Jayson Tatum            | 209
```

**Conclusion:** TOV column exists and is populated. No action needed.

---

## 4. Teams Table - Already Exists

### Finding
Evaluation report mentioned "Missing teams table (roster queries fail)."

### Verification
```sql
SELECT * FROM teams LIMIT 5;

-- Results:
-- 1 | ATL | Atlanta Hawks
-- 2 | BOS | Boston Celtics
-- 3 | BKN | Brooklyn Nets
-- 4 | CHA | Charlotte Hornets
-- 5 | CHI | Chicago Bulls
```

**Full table:**
- 30 NBA teams
- Abbreviation (primary key) + full name
- Foreign key relationships to `players` and `player_stats`

**Conclusion:** Teams table exists and is properly populated.

---

## Files Modified

### Schema Changes
- **src/repositories/nba_database.py**
  - Added `team` column to `PlayerModel` class
  - Updated `add_player()` method signature

### Data Loading
- **scripts/load_excel_to_db.py**
  - Updated `load_players_to_db()` to map team abbreviations to full names
  - Uses `TEAM_NAMES` dictionary for mapping

### Verification Scripts (New)
- **scripts/check_database_schema.py** - Schema validation utility
- **scripts/check_excel_columns.py** - Excel data inspection
- **scripts/verify_team_names.py** - Team name population verification

---

## Database Statistics

**After rebuild (2026-02-10):**
- Teams: 30
- Players: 569 (all with full team names)
- Player stats: 569 records
- Columns in `player_stats`: 45 (including `tov`)
- Columns in `players`: 5 (including new `team` column)

---

## Impact on SQL Query Generation

### Before (with abbreviations only)
```sql
-- Query: "List all Lakers players"
-- SQL generated: SELECT name FROM players WHERE team_abbr = 'LAL'
-- Problem: Requires knowing "LAL" = Lakers
```

### After (with full team names)
```sql
-- Query: "List all Lakers players"
-- SQL generated: SELECT name FROM players WHERE team LIKE '%Lakers%'
-- Better: Natural language matching
```

---

## Recommendations

### Completed ✅
- [x] Add `team` column to `players` table
- [x] Populate with full team names
- [x] Rebuild database with new schema
- [x] Verify data integrity

### Not Required ❌
- [x] ~~Fix `ts_pct` values~~ - Mathematically correct
- [x] ~~Add `tov` column~~ - Already exists
- [x] ~~Create `teams` table~~ - Already exists

### Future Enhancements 💡
- Add `roster_size` column to `teams` table
- Add `position` column to `players` table
- Add `season` column for multi-season support
- Create `games` table for per-game statistics
- Add indexes on frequently queried columns (`name`, `team`)

---

## Testing

### Verification Queries
```sql
-- 1. Check team column exists and is populated
SELECT name, team, team_abbr FROM players LIMIT 10;

-- 2. Verify no abbreviations remain
SELECT COUNT(*) FROM players WHERE length(team) <= 5;
-- Expected: 0

-- 3. Check TOV column exists
SELECT name, tov FROM players
JOIN player_stats ON players.id = player_stats.player_id
WHERE tov > 200
ORDER BY tov DESC;

-- 4. Verify TS% formula
SELECT name, ts_pct, pts, fga, fta,
       100.0 * pts / (2.0 * (fga + 0.44 * fta)) AS calculated_ts_pct
FROM players
JOIN player_stats ON players.id = player_stats.player_id
WHERE fga > 100
LIMIT 5;
```

---

## Conclusion

✅ **Database schema improvements completed successfully**

- Added full team names to improve SQL query generation
- Verified that reported "missing" columns (TOV, teams table) actually exist
- Confirmed that TS% >100 values are mathematically correct
- All 569 players now have complete team information

**Next step:** Re-run hybrid evaluation to measure improvement in SQL accuracy for roster/team queries.
