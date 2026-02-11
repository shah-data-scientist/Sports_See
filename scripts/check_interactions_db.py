"""
FILE: check_interactions_db.py
STATUS: Active
RESPONSIBILITY: Check interactions database schema and tables
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Quick diagnostic script to inspect interactions.db schema.
"""
import sqlite3

conn = sqlite3.connect('data/sql/interactions.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:")
for (t,) in cursor.fetchall():
    print(f"  - {t}")

cursor.execute("PRAGMA table_info(chat_interactions)")
print("\nchat_interactions columns:")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

conn.close()
