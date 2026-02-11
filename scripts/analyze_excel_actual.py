"""
FILE: analyze_excel_actual.py
STATUS: Active
RESPONSIBILITY: Analyze actual NBA Excel file content
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Script to read and analyze all sheets in the NBA Excel file.
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Fix Windows encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')

def analyze_excel():
    excel_path = Path(__file__).parent.parent / "data" / "inputs" / "regular NBA.xlsx"

    print(f"Analyzing: {excel_path}")
    print("=" * 80)

    # Read all sheets
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names

    print(f"\nFound {len(sheet_names)} sheets: {sheet_names}\n")

    results = {}

    for sheet_name in sheet_names:
        print(f"\n{'=' * 80}")
        print(f"SHEET: {sheet_name}")
        print("=" * 80)

        # Read with header row (first row contains column names)
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)

        # Basic info
        print(f"\nRows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"\nColumn names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")

        # Check if sheet is empty
        is_empty = df.empty or df.dropna(how='all').empty
        print(f"\nIs empty? {is_empty}")

        if not is_empty:
            # Data types
            print(f"\nColumn types:")
            for col, dtype in df.dtypes.items():
                non_null = df[col].notna().sum()
                print(f"  {col}: {dtype} ({non_null}/{len(df)} non-null)")

            # Sample data
            print(f"\nFirst 5 rows:")
            print(df.head(5).to_string())

            # For small sheets, show all
            if len(df) <= 10:
                print(f"\nALL {len(df)} rows:")
                print(df.to_string())

        # Store results
        results[sheet_name] = {
            'rows': len(df),
            'columns': list(df.columns),
            'is_empty': is_empty,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'non_null_counts': {col: int(df[col].notna().sum()) for col in df.columns}
        }

    # Save analysis to JSON
    output_path = Path(__file__).parent.parent / "docs" / "excel_analysis.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\nAnalysis saved to: {output_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for sheet_name, info in results.items():
        print(f"\n{sheet_name}:")
        print(f"  Rows: {info['rows']}")
        print(f"  Columns: {len(info['columns'])}")
        print(f"  Empty: {info['is_empty']}")

if __name__ == "__main__":
    analyze_excel()
