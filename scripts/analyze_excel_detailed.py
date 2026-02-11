"""
FILE: analyze_excel_detailed.py
STATUS: Active
RESPONSIBILITY: Deep analysis of NBA Excel file with proper headers
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Detailed analysis of all sheets with proper column handling.
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Fix Windows encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')

def analyze_sheet_detailed(df, sheet_name):
    """Analyze a single sheet in detail."""
    print(f"\n{'=' * 80}")
    print(f"SHEET: {sheet_name}")
    print("=" * 80)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # Check if truly empty
    non_empty_rows = df.dropna(how='all')
    print(f"Non-empty rows: {len(non_empty_rows)}")

    print(f"\nColumn names:")
    for i, col in enumerate(df.columns, 1):
        non_null = df[col].notna().sum()
        dtype = df[col].dtype
        print(f"  {i:2d}. {col} ({dtype}, {non_null}/{len(df)} non-null)")

    # Show first 10 rows
    print(f"\nFirst 10 rows:")
    print(df.head(10).to_string())

    # For very small sheets, show all
    if len(non_empty_rows) <= 15 and len(non_empty_rows) > 0:
        print(f"\n\nALL NON-EMPTY DATA ({len(non_empty_rows)} rows):")
        print(non_empty_rows.to_string())

    return {
        'rows': len(df),
        'non_empty_rows': len(non_empty_rows),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'non_null_counts': {col: int(df[col].notna().sum()) for col in df.columns}
    }

def analyze_excel():
    excel_path = Path(__file__).parent.parent / "data" / "inputs" / "regular NBA.xlsx"

    print(f"Analyzing: {excel_path}")
    print("=" * 80)

    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names

    print(f"\nFound {len(sheet_names)} sheets: {sheet_names}\n")

    results = {}

    # Sheet 1: Données NBA - player stats
    sheet_name = "Données NBA"
    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {sheet_name} (Player Statistics)")
    print("=" * 80)

    # Read first row as header
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"\nColumn names:")
    for i, col in enumerate(df.columns, 1):
        non_null = df[col].notna().sum()
        print(f"  {i:2d}. {col} ({non_null}/{len(df)} non-null)")

    print(f"\nFirst 5 players:")
    print(df[['Player', 'Team', 'Age', 'GP', 'PTS', 'REB', 'AST']].head(5).to_string())

    print(f"\nLast 5 players:")
    print(df[['Player', 'Team', 'Age', 'GP', 'PTS', 'REB', 'AST']].tail(5).to_string())

    results[sheet_name] = {
        'rows': len(df),
        'columns': list(df.columns),
        'type': 'structured_stats',
        'recommendation': 'SQL_DATABASE'
    }

    # Sheet 2 & 3: Analyse sheets
    for analysis_sheet in ["Analyse", "Analyse Vide"]:
        print(f"\n{'=' * 80}")
        print(f"ANALYZING: {analysis_sheet}")
        print("=" * 80)

        df = pd.read_excel(excel_file, sheet_name=analysis_sheet, header=None)
        non_empty = df.dropna(how='all')

        print(f"\nTotal rows: {len(df)}")
        print(f"Non-empty rows: {len(non_empty)}")

        if len(non_empty) > 0:
            print(f"\nFirst 20 non-empty rows:")
            print(non_empty.head(20).to_string())

        results[analysis_sheet] = {
            'rows': len(df),
            'non_empty_rows': len(non_empty),
            'columns': list(df.columns),
            'type': 'analysis_template',
            'recommendation': 'TBD'
        }

    # Sheet 4: Equipe (Teams)
    sheet_name = "Equipe"
    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {sheet_name} (Teams)")
    print("=" * 80)

    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
    print(f"\nRows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    print(f"\nAll teams:")
    print(df.to_string())

    results[sheet_name] = {
        'rows': len(df),
        'columns': list(df.columns),
        'type': 'reference_data',
        'recommendation': 'SQL_DATABASE'
    }

    # Sheet 5: Dictionnaire (Dictionary)
    sheet_name = "Dictionnaire des données"
    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {sheet_name} (Data Dictionary)")
    print("=" * 80)

    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
    print(f"\nRows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Rename for clarity
    df.columns = ['Column_Name', 'Description']

    print(f"\nAll dictionary entries:")
    print(df.to_string())

    results[sheet_name] = {
        'rows': len(df),
        'columns': list(df.columns),
        'entries': df.to_dict('records'),
        'type': 'metadata',
        'recommendation': 'BOTH_VECTOR_AND_SQL'
    }

    # Save to JSON
    output_path = Path(__file__).parent.parent / "docs" / "excel_detailed_analysis.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'=' * 80}")
    print(f"Analysis saved to: {output_path}")
    print("=" * 80)

if __name__ == "__main__":
    analyze_excel()
