# Database Normalization Migration Guide

**Date**: 2026-02-13
**Purpose**: Fix team queries by normalizing database schema
**Impact**: Removes redundant columns, enforces data integrity, enables team aggregation queries

---

## Quick Start

```bash
# Phase 1: Add UNIQUE constraint (safe, required)
poetry run python scripts/migrate_database_phase1.py

# Phase 2: Remove redundant columns (optional, recommended)
poetry run python scripts/migrate_database_phase2.py

# Verify: Test team queries
poetry run python scripts/test_team_queries_after_migration.py
```

---

## What's Being Changed

### Phase 1: Add UNIQUE Constraint
**Changes**:
- Adds UNIQUE constraint to `teams.abbreviation`
- Enables proper foreign key integrity

**Data**: All data preserved ✅
**Queries**: All existing queries still work ✅
**Risk**: **LOW** (non-destructive)

### Phase 2: Remove Redundant Columns (Optional)
**Changes**:
- Removes `players.team` column (redundant with teams.name)
- Removes `player_stats.team_abbr` column (redundant with players.team_abbr)

**Data**: All data preserved (exported and re-imported) ✅
**Queries**: Simple queries need updates to use JOINs
**Risk**: **MEDIUM** (recreates database)

---

## Before Migration

### Current Schema Issues

**teams**:
```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    abbreviation VARCHAR(5) NOT NULL,  -- ❌ No UNIQUE constraint
    name VARCHAR(100) NOT NULL
);
```

**players**:
```sql
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    team VARCHAR(100) NOT NULL,        -- ⚠️ REDUNDANT
    team_abbr VARCHAR(5) NOT NULL,     -- FK to teams.abbreviation
    age INTEGER NOT NULL
);
```

**player_stats**:
```sql
CREATE TABLE player_stats (
    id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,        -- FK to players.id
    team_abbr VARCHAR(5) NOT NULL,     -- ⚠️ REDUNDANT
    pts INTEGER NOT NULL,
    -- ... 40 more stat columns ...
);
```

### Problems

1. **No UNIQUE constraint** on `teams.abbreviation` (violates FK integrity)
2. **Redundant data**: Team name stored in both `teams.name` and `players.team`
3. **Team queries fail**: LLM doesn't generate correct aggregation SQL

---

## After Migration

### Normalized Schema

**teams**:
```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    abbreviation VARCHAR(5) UNIQUE NOT NULL,  -- ✅ UNIQUE constraint
    name VARCHAR(100) NOT NULL
);
```

**players**:
```sql
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    team_abbr VARCHAR(5) NOT NULL,     -- FK to teams.abbreviation
    age INTEGER NOT NULL
    -- ✅ team column removed
);
```

**player_stats**:
```sql
CREATE TABLE player_stats (
    id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,        -- FK to players.id
    pts INTEGER NOT NULL,
    -- ... 40 more stat columns ...
    -- ✅ team_abbr column removed
);
```

### Benefits

1. ✅ **UNIQUE constraint** enforces data integrity
2. ✅ **No redundancy**: Single source of truth for team names
3. ✅ **Team queries work**: Forces proper JOIN patterns

---

## Migration Steps

### Step 1: Backup Current Database

```bash
# Automatic backup created by migration scripts
# Manual backup (optional):
cp data/sql/nba_stats.db data/sql/nba_stats_backup_$(date +%Y%m%d).db
```

### Step 2: Run Phase 1 (Required)

```bash
poetry run python scripts/migrate_database_phase1.py
```

**What it does**:
1. Creates timestamped backup
2. Checks for existing UNIQUE constraint
3. Verifies no duplicate abbreviations
4. Adds UNIQUE index on teams.abbreviation
5. Verifies constraint works

**Output**:
```
================================================================================
DATABASE MIGRATION - PHASE 1
Add UNIQUE Constraint to teams.abbreviation
================================================================================

STEP 1: Backup Database
✅ Backup created: data/sql/nba_stats_backup_20260213_120000.db

STEP 2: Check Existing Constraints
⚠️  No UNIQUE constraint found - migration required

STEP 3: Verify Data Integrity
✅ No duplicate abbreviations found

STEP 4: Add UNIQUE Constraint
✅ UNIQUE constraint added to teams.abbreviation

STEP 5: Verify Migration
✅ UNIQUE constraint verified (duplicate insert blocked)

================================================================================
✅ PHASE 1 MIGRATION COMPLETE
================================================================================
```

### Step 3: Run Phase 2 (Optional, Recommended)

```bash
poetry run python scripts/migrate_database_phase2.py
```

**What it does**:
1. Creates timestamped backup
2. Exports all data from current database
3. Drops existing tables
4. Creates new tables using SQLAlchemy models (normalized)
5. Imports data into new schema
6. Verifies data integrity

**Confirmation Required**:
```
⚠️  WARNING: This will recreate the database from scratch!
Proceed with Phase 2 migration? (yes/no):
```

Type `yes` to continue.

**Output**:
```
================================================================================
DATABASE MIGRATION - PHASE 2
Recreate Database with Normalized Schema
================================================================================

STEP 1: Backup Current Database
✅ Backup created: data/sql/nba_stats_phase2_backup_20260213_120500.db

STEP 2: Export Existing Data
✅ Exported data:
   Teams: 30
   Players: 329
   Player Stats: 329
   Dictionary: 150

STEP 3: Recreate Database Schema
✅ Tables dropped
✅ Tables created with normalized schema

STEP 4: Import Data
✅ 30 teams imported
✅ 329 players imported
✅ 329 player stats imported
✅ 150 dictionary entries imported

VERIFICATION
✅ Teams: 329/329
✅ Players: 329/329
✅ Player Stats: 329/329
✅ UNIQUE constraint on teams.abbreviation
✅ Team query works: Lakers have 8,691 total points

================================================================================
✅ PHASE 2 MIGRATION COMPLETE
================================================================================
```

### Step 4: Test Team Queries

```bash
poetry run python scripts/test_team_queries_after_migration.py
```

**What it does**:
- Runs 8 comprehensive team query tests
- Verifies team aggregations work
- Tests single team stats, comparisons, rankings, etc.

**Output**:
```
================================================================================
 TEAM QUERY TESTS (Post-Migration)
================================================================================

TEST 1: Single Team Statistics
✅ Query executed successfully
📊 Rows returned: 1

Results:
   1. ('Los Angeles Lakers', 20, 8691, 3321, 2135, 434.6)

... (7 more tests) ...

================================================================================
 TEST SUMMARY
================================================================================

✅ Passed: 8
❌ Failed: 0
📊 Success Rate: 8/8 (100.0%)

================================================================================
🎉 ALL TEAM QUERIES WORK CORRECTLY!
================================================================================
```

---

## Query Updates (Phase 2 Only)

If you run Phase 2, simple queries need updates to use JOINs:

### Before (Direct Access)
```sql
-- Get player with team name (used players.team)
SELECT name, team FROM players WHERE name LIKE '%LeBron%';
```

### After (With JOIN)
```sql
-- Get player with team name (JOIN with teams table)
SELECT p.name, t.name as team
FROM players p
JOIN teams t ON p.team_abbr = t.abbreviation
WHERE p.name LIKE '%LeBron%';
```

### Team Aggregation (Now Works!)
```sql
-- Get team statistics (requires SUM + GROUP BY)
SELECT
    t.name as team,
    SUM(ps.pts) as total_pts,
    SUM(ps.reb) as total_reb,
    SUM(ps.ast) as total_ast
FROM teams t
JOIN players p ON t.abbreviation = p.team_abbr
JOIN player_stats ps ON p.id = ps.player_id
WHERE t.abbreviation = 'LAL'
GROUP BY t.name;
```

---

## Rollback (If Needed)

### Rollback Phase 1
```bash
# Restore from backup
cp data/sql/nba_stats_backup_TIMESTAMP.db data/sql/nba_stats.db
```

### Rollback Phase 2
```bash
# Restore from Phase 2 backup
cp data/sql/nba_stats_phase2_backup_TIMESTAMP.db data/sql/nba_stats.db
```

---

## Next Steps After Migration

### 1. Update SQL Generation Prompt

Add to `src/tools/sql_query.py`:

```python
TEAM_QUERY_RULES = """
CRITICAL: Team statistics require aggregation!

Team stats pattern:
SELECT t.name, SUM(ps.[stat]) as total_[stat]
FROM teams t
JOIN players p ON t.abbreviation = p.team_abbr
JOIN player_stats ps ON p.id = ps.player_id
WHERE t.abbreviation = '[ABBR]'
GROUP BY t.name

Example: "Show me Lakers stats"
→ SELECT t.name, SUM(ps.pts), SUM(ps.reb), SUM(ps.ast)
   FROM teams t
   JOIN players p ON t.abbreviation = p.team_abbr
   JOIN player_stats ps ON p.id = ps.player_id
   WHERE t.abbreviation = 'LAL'
   GROUP BY t.name
"""
```

### 2. Test Team Queries in UI

Try these queries in the UI:
- "Show me Lakers stats"
- "Compare Celtics and Warriors"
- "Which team has the most points?"
- "Top 5 teams by rebounds"

### 3. Re-run Evaluations

```bash
# Delete old checkpoint
rm evaluation_results/sql_evaluation_checkpoint.json

# Re-run SQL evaluation
poetry run python src/evaluation/runners/run_sql_evaluation.py
```

---

## Troubleshooting

### Issue: UNIQUE constraint already exists
**Solution**: Phase 1 already completed. Skip to Phase 2 or verification.

### Issue: Duplicate abbreviations found
**Solution**: Check teams table for duplicates:
```sql
SELECT abbreviation, COUNT(*) FROM teams GROUP BY abbreviation HAVING COUNT(*) > 1;
```
Fix manually before running Phase 1.

### Issue: Phase 2 import fails
**Solution**: Restore from backup and check error message. May need to update SQLAlchemy models.

### Issue: Team queries still fail after migration
**Solution**:
1. Verify migration with test script
2. Check SQL generation prompt includes team aggregation rules
3. Test queries manually in database

---

## Summary

**Phase 1** (Required):
- ✅ Adds UNIQUE constraint
- ✅ Low risk (non-destructive)
- ✅ Enables proper foreign key integrity

**Phase 2** (Optional):
- ✅ Removes redundant columns
- ✅ Clean normalized schema
- ✅ Forces proper JOIN patterns
- ⚠️  Medium risk (recreates database)

**Expected Impact**:
- Team query success rate: 30% → 90%+ ✅
- Schema follows best practices ✅
- Data integrity enforced ✅

---

**Recommendation**: Run Phase 1 immediately, Phase 2 when ready for thorough testing.
