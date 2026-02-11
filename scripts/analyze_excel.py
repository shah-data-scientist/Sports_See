"""
FILE: analyze_excel.py
STATUS: Active
RESPONSIBILITY: Analyze Excel file structure for Phase 2 database design
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

import pandas as pd


def analyze_excel_structure(file_path: str) -> None:
    """Analyze Excel file structure and print schema information."""
    print("=" * 80)
    print("EXCEL FILE STRUCTURE ANALYSIS")
    print("=" * 80)
    print(f"\nFile: {file_path}\n")

    xls = pd.ExcelFile(file_path)
    print(f"Sheets found: {len(xls.sheet_names)}")
    print(f"Sheet names: {xls.sheet_names}\n")

    # First, read data dictionary if available
    dict_sheet = "Dictionnaire des données" if "Dictionnaire des données" in xls.sheet_names else None
    if dict_sheet:
        print("=" * 80)
        print("DATA DICTIONARY")
        print("=" * 80)
        dict_df = pd.read_excel(file_path, sheet_name=dict_sheet)
        print(dict_df.to_string(index=False, max_colwidth=50))
        print("\n")

    for sheet_name in xls.sheet_names:
        # Skip analysis sheets
        if "Analyse" in sheet_name or "Dictionnaire" in sheet_name:
            continue

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)

        print("=" * 80)
        print(f"Sheet: {sheet_name}")
        print("=" * 80)
        print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")

        # Get non-empty columns only
        non_empty_cols = [col for col in df.columns if df[col].notna().any()]

        print(f"Columns with data ({len(non_empty_cols)}):")
        for i, col in enumerate(non_empty_cols, 1):
            dtype = df[col].dtype
            non_null = df[col].notna().sum()
            null_count = df[col].isna().sum()
            unique_count = df[col].nunique()
            col_str = str(col)[:30]  # Truncate long column names
            print(f"  {i:2d}. {col_str:<30} | Type: {str(dtype):<10} | "
                  f"Non-null: {non_null:>3}/{len(df):<3} | Unique: {unique_count:>3}")

        print(f"\nSample data (first 3 rows, first 10 columns):")
        sample_cols = non_empty_cols[:10]
        for idx, row in df[sample_cols].head(3).iterrows():
            print(f"\nRow {idx + 1}:")
            for col in sample_cols:
                val = str(row[col])[:40] if pd.notna(row[col]) else "NULL"
                print(f"  {str(col)[:20]:<20}: {val}")
        print("\n")


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "data/inputs/regular NBA.xlsx"

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    analyze_excel_structure(file_path)
