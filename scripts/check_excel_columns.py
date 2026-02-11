"""
FILE: check_excel_columns.py
STATUS: Active
RESPONSIBILITY: Check Excel columns for database schema validation
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import sys
import io

# Force UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd

# Read Excel
df = pd.read_excel("data/inputs/regular NBA.xlsx", sheet_name="Données NBA")
headers = df.iloc[0].tolist()
df.columns = headers
df = df.drop(0).reset_index(drop=True)

# Check TS%
print("=" * 80)
print("TS% ANALYSIS")
print("=" * 80)
print("\nSample values:")
print(df["TS%"].head(20).tolist())
print("\nStatistics:")
print(df["TS%"].describe())
print(f"\nMax value: {df['TS%'].max()}")
print(f"Min value: {df['TS%'].min()}")

# Check TOV
print("\n" + "=" * 80)
print("TOV (TURNOVERS) ANALYSIS")
print("=" * 80)
if "TOV" in df.columns:
    print("\nTOV column EXISTS")
    print("\nSample values:")
    print(df[["Player", "TOV"]].head(10))
    print("\nStatistics:")
    print(df["TOV"].describe())
else:
    print("\nTOV column DOES NOT EXIST")
    print("\nAvailable columns:")
    print([col for col in df.columns if isinstance(col, str)])

# Check Team column
print("\n" + "=" * 80)
print("TEAM COLUMN ANALYSIS")
print("=" * 80)
print("\nSample values:")
print(df[["Player", "Team"]].head(10))
print("\nUnique teams:")
print(df["Team"].unique()[:10])
