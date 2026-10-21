"""Download a full dataset from data.cdc.gov (Socrata) as CSV.

Usage:
    python3 atlas/scripts/fetch_socrata.py <dataset_id> <output.csv> [--domain data.cdc.gov]

Examples:
    python3 atlas/scripts/fetch_socrata.py i46a-9kgh data/raw/places_county_2025.csv
    python3 atlas/scripts/fetch_socrata.py xkb8-kh2a data/raw/vsrr_overdose.csv

Standard library only, so it runs with plain Homebrew Python. Socrata caps
each request, so rows are fetched in pages of 50 000 until the dataset ends.
"""

# Paths in this script are relative to the repository root; anchor there so it
# runs from any working directory (atlas/scripts/<this file> -> repo root).
import os as _os
from pathlib import Path as _Path
_os.chdir(_Path(__file__).resolve().parents[2])

import argparse
import csv
import io
import json
import urllib.request

PAGE = 50_000


def fetch(domain: str, dataset_id: str, out_path: str) -> int:
    meta_url = f"https://{domain}/api/views/{dataset_id}.json"
    with urllib.request.urlopen(meta_url, timeout=60) as r:
        meta = json.load(r)
    print(f"{dataset_id}: {meta['name']}")

    rows_written = 0
    offset = 0
    writer = None
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        while True:
            url = (
                f"https://{domain}/resource/{dataset_id}.csv"
                f"?$limit={PAGE}&$offset={offset}&$order=:id"
            )
            with urllib.request.urlopen(url, timeout=120) as r:
                text = r.read().decode("utf-8")
            reader = csv.reader(io.StringIO(text))
            header = next(reader, None)
            page_rows = list(reader)
            if writer is None:
                writer = csv.writer(f)
                writer.writerow(header)
            writer.writerows(page_rows)
            rows_written += len(page_rows)
            if len(page_rows) < PAGE:
                break
            offset += PAGE
    print(f"wrote {rows_written} rows to {out_path}")
    return rows_written


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset_id")
    p.add_argument("out_path")
    p.add_argument("--domain", default="data.cdc.gov")
    a = p.parse_args()
    fetch(a.domain, a.dataset_id, a.out_path)
