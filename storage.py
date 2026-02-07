import csv
import json
import os
from typing import List, Dict

import pandas as pd


def append_rows_to_csv(rows: List[Dict], csv_path: str) -> None:
    """Append rows to a CSV file, creating it with header if it doesn't exist."""
    if not rows:
        return

    file_exists = os.path.exists(csv_path)
    fieldnames = list(rows[0].keys())

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for row in rows:
            writer.writerow(row)


def load_progress(progress_path: str) -> Dict:
    """Load scraping progress (page_index, next_job_id)."""
    if not os.path.exists(progress_path):
        return {"page_index": 1, "next_job_id": 1}

    with open(progress_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress_path: str, state: Dict) -> None:
    """Save scraping progress."""
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def csv_to_excel(csv_path: str, xlsx_path: str) -> None:
    """Convert CSV checkpoint file to Excel."""
    if not os.path.exists(csv_path):
        print(f"[csv_to_excel] No CSV found at {csv_path}, skipping Excel export.")
        return

    df = pd.read_csv(csv_path)
    df.to_excel(xlsx_path, index=False)
    print(f"[csv_to_excel] Wrote Excel file to {xlsx_path}")
