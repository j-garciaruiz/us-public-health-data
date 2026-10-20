"""Download CMS quarterly Part D plan files (SPUF) and keep only the small tables we use.

Each release is a ~2.5 GB ZIP (mostly pharmacy-network tables). This script downloads one release
at a time, extracts the pricing, plan-information and sample tables into
data/raw/pharma/spuf/<internal label>/ (e.g. 2026Q3), writes a .meta.json, and deletes the big ZIP.

Usage:
    python pharma/scripts/fetch_spuf.py            # the three releases used in spuf_mfp_check.py
"""
import datetime as dt
import hashlib
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "pharma" / "spuf"
RELEASES = [
    "https://data.cms.gov/sites/default/files/2025-10/6b0620f5-9259-4f1f-929c-70feb8857887/SPUF_2025_20251009.zip",
    "https://data.cms.gov/sites/default/files/2026-01/5942aa7e-a0c4-4e65-bd56-32608c33649f/SPUF_2026_20260107.zip",
    "https://data.cms.gov/sites/default/files/2026-10/062e9434-ed9d-4e83-abbd-4d64eb375949/SPUF_2026_20261007.zip",
]
KEEP = ("pricing file", "plan information", "sample files")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for url in RELEASES:
        name = url.rsplit("/", 1)[1]
        tmp = OUT / name
        sha = hashlib.sha256()
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                                    timeout=1800) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 22):
                f.write(chunk)
                sha.update(chunk)
        with zipfile.ZipFile(tmp) as zf:
            label = re.search(r"PPUF_(\d{4}Q\d)", " ".join(zf.namelist())).group(1)
            dest = OUT / label
            dest.mkdir(exist_ok=True)
            members = [m for m in zf.namelist() if m.startswith(KEEP)]
            for m in members:
                zf.extract(m, dest)
        meta = {"source_url": url, "release_file": name, "internal_label": label,
                "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "zip_bytes": tmp.stat().st_size, "zip_sha256": sha.hexdigest(), "kept": members}
        (dest / "release.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        tmp.unlink()
        print(f"{name} -> {dest.relative_to(ROOT)} ({len(members)} tables)")


if __name__ == "__main__":
    main()
