"""Download NADAC (National Average Drug Acquisition Cost) files from data.medicaid.gov.

NADAC is CMS's weekly survey-based estimate of what retail community pharmacies
pay to acquire a drug (invoice price), per pricing unit, by 11-digit NDC.
data.medicaid.gov publishes one dataset per calendar year; each year's file holds
every weekly snapshot ("as_of_date") released during that year.

Standard library only. Looks the dataset up in the data.medicaid.gov metastore by
title, downloads the CSV it points to, and writes a small JSON sidecar with the
source URL, catalog modified date, retrieval time, size, row count and SHA-256.

Usage:
    python pharma/scripts/fetch_nadac.py                 # current year
    python pharma/scripts/fetch_nadac.py 2024 2025 2026  # several years
    python pharma/scripts/fetch_nadac.py --comparison    # also the week-over-week NADAC Comparison file

Output: data/raw/pharma/nadac/nadac_<year>.csv (+ .meta.json)
"""
import argparse
import datetime as dt
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

CATALOG = "https://data.medicaid.gov/api/1/metastore/schemas/dataset/items?show-reference-ids=false"
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "raw" / "pharma" / "nadac"
UA = {"User-Agent": "us-data-lab/0.1 (public data research)"}


def get(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout)


def load_catalog():
    with get(CATALOG) as r:
        return json.load(r)


def find_dataset(catalog, title):
    for ds in catalog:
        if ds.get("title", "").strip() == title:
            return ds
    raise SystemExit(f"Dataset not found in data.medicaid.gov catalog: {title!r}")


def csv_url(ds):
    for dist in ds.get("distribution", []):
        data = dist.get("data", dist)
        url = data.get("downloadURL")
        if url and url.lower().endswith(".csv"):
            return url
    raise SystemExit(f"No CSV distribution for {ds.get('title')}")


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    sha = hashlib.sha256()
    size = 0
    rows = 0
    with get(url, timeout=600) as r, open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            sha.update(chunk)
            size += len(chunk)
            rows += chunk.count(b"\n")
    if size == 0:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"Empty download from {url}")
    tmp.replace(dest)
    return size, sha.hexdigest(), rows


def fetch(catalog, title, dest):
    ds = find_dataset(catalog, title)
    url = csv_url(ds)
    print(f"{title}\n  {url}", flush=True)
    size, digest, lines = download(url, dest)
    meta = {
        "title": title,
        "dataset_id": ds.get("identifier"),
        "catalog_modified": ds.get("modified"),
        "source_url": url,
        "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "bytes": size,
        "data_rows": lines - 1,  # minus header; assumes no embedded newlines (true for NADAC)
        "sha256": digest,
    }
    dest.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  -> {dest.relative_to(ROOT)} ({size / 1e6:.1f} MB, {lines - 1:,} rows)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("years", nargs="*", type=int, help="calendar years (default: current year)")
    p.add_argument("--comparison", action="store_true", help="also fetch the NADAC Comparison file")
    a = p.parse_args()
    years = a.years or [dt.date.today().year]
    catalog = load_catalog()
    for y in years:
        fetch(catalog, f"NADAC (National Average Drug Acquisition Cost) {y}", OUT_DIR / f"nadac_{y}.csv")
    if a.comparison:
        fetch(catalog, "NADAC Comparison", OUT_DIR / "nadac_comparison.csv")


if __name__ == "__main__":
    sys.exit(main())
