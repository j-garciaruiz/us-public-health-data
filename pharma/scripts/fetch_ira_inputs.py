"""Download the inputs for the IRA negotiation study (pharma idea 2).

- CMS Medicare Drug Price Negotiation selected drug list and Maximum Fair Prices (ZIP, cms.gov)
- Medicare Part D Spending by Drug (annual, latest file) and Quarterly Part D Spending by Drug,
  located through the data.cms.gov catalog by title so new releases are picked up

NADAC files come from fetch_nadac.py (run it with 2024 2025 2026 --comparison).

Standard library only. Each file gets a .meta.json sidecar (source URL, retrieval time, bytes, SHA-256).
Output: data/raw/pharma/ira/ and data/raw/pharma/partd/

Usage:
    python pharma/scripts/fetch_ira_inputs.py
"""
import datetime as dt
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "pharma"
UA = {"User-Agent": "Mozilla/5.0 (us-data-lab; public data research)"}

IRA_ZIP = ("https://www.cms.gov/files/zip/"
           "selected-drug-list-negotiated-prices-also-known-maximum-fair-prices-statutezip.zip")
CMS_CATALOG = "https://data.cms.gov/data.json"
PARTD_TITLES = {
    "Medicare Part D Spending by Drug": "partd_spending_annual.csv",
    "Medicare Quarterly Part D Spending by Drug": "partd_spending_quarterly.csv",
}


def download(url, dest, extra=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    sha = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
            sha.update(chunk)
            size += len(chunk)
    if size == 0:
        raise SystemExit(f"Empty download: {url}")
    meta = {"source_url": url, "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "bytes": size, "sha256": sha.hexdigest(), **(extra or {})}
    dest.with_name(dest.name + ".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  -> {dest.relative_to(ROOT)} ({size / 1e6:.1f} MB)")


def latest_csv(catalog, title):
    """Most recent version of a data.cms.gov dataset: the CSV distribution with the latest temporal end."""
    best = None
    for ds in catalog["dataset"]:
        if ds["title"].split(" : ")[0] != title:
            continue
        for dist in ds.get("distribution", []):
            url = dist.get("downloadURL") or ""
            if url.lower().endswith(".csv"):
                key = (ds.get("temporal", ""), ds.get("modified", ""))
                if best is None or key > best[0]:
                    best = (key, url, ds)
    if best is None:
        raise SystemExit(f"No CSV found on data.cms.gov for {title!r}")
    return best[1], best[2]


def main():
    print("CMS negotiation: selected drugs and MFPs")
    z = RAW / "ira" / "selected_drugs_mfp.zip"
    download(IRA_ZIP, z)
    with zipfile.ZipFile(z) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".csv"):
                (RAW / "ira" / "selected_drugs_mfp.csv").write_bytes(zf.read(name))
                print(f"  extracted {name} -> data/raw/pharma/ira/selected_drugs_mfp.csv")

    req = urllib.request.Request(CMS_CATALOG, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r:
        catalog = json.load(r)
    for title, fname in PARTD_TITLES.items():
        url, ds = latest_csv(catalog, title)
        print(title)
        download(url, RAW / "partd" / fname,
                 {"title": title, "catalog_modified": ds.get("modified"), "temporal": ds.get("temporal")})


if __name__ == "__main__":
    main()
