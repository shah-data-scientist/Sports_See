"""
Show the complete schema of the NBA stats database.
"""
import sqlite3
from pathlib import Path

db_path = Path("data/sql/nba_stats.db")

print("="*80)
print(f"DATABASE SCHEMA: {db_path}")
print("="*80)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n📊 TABLES FOUND: {len(tables)}")
for table in tables:
    print(f"   - {table[0]}")

print("\n" + "="*80)

# Show schema for each table
for table_name in [t[0] for t in tables]:
    print(f"\n{'─'*80}")
    print(f"TABLE: {table_name}")
    print('─'*80)

    # Get CREATE TABLE statement
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    create_stmt = cursor.fetchone()[0]
    print(f"\n{create_stmt}\n")

    # Get sample data (first 3 rows)
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()

    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]

    print(f"COLUMNS ({len(col_names)}):")
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        pk_marker = " [PRIMARY KEY]" if pk else ""
        notnull_marker = " NOT NULL" if notnull else ""
        print(f"   {name}: {type_}{notnull_marker}{pk_marker}")

    print(f"\nSAMPLE DATA (first 3 rows):")
    for i, row in enumerate(rows, 1):
        print(f"\n   Row {i}:")
        for col_name, value in zip(col_names, row):
            print(f"      {col_name}: {value}")

print("\n" + "="*80)
print("RELATIONSHIPS AND FOREIGN KEYS")
print("="*80)

for table_name in [t[0] for t in tables]:
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    fks = cursor.fetchall()
    if fks:
        print(f"\n{table_name}:")
        for fk in fks:
            print(f"   → {fk[2]}.{fk[4]} (references {fk[3]})")
    else:
        print(f"\n{table_name}: No foreign keys defined")

conn.close()
print("\n" + "="*80)
