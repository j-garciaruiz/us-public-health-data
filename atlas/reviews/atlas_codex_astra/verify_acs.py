"""Live Census spot checks. The authorized key is read in memory, never saved."""
import concurrent.futures
import json
import math
import re
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = "https://api.census.gov/data/2023/acs/acs5"
key = None
for line in (ROOT / ".env").read_text().splitlines():
    match = re.match(r"(?:export\s+)?CENSUS_API_KEY\s*=\s*(.*)", line)
    if match:
        key = match[1].strip().strip("'\"")
assert key
saved = pd.read_csv(ROOT / "data/raw/acs_disability_2023.csv", dtype={"fips": str}).set_index("fips")
counties = ["01001", "02158", "11001", "21111", "42101"]
tables = dict(zip(["B18102", "B18103", "B18104", "B18105", "B18106", "B18107"],
                  ["hearing", "vision", "cognition", "mobility", "selfcare", "indeplive"]))


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return json.load(response)
    except Exception as exc:
        # Exception messages and request URLs may contain the authorized key.
        raise RuntimeError("Census request failed: " + type(exc).__name__) from None


def task(table):
    meta = get(f"{BASE}/groups/{table}.json")
    (OUT / f"census_{table}_metadata.json").write_text(json.dumps(meta))
    adult = {"18 to 34 years:", "35 to 64 years:", "65 to 74 years:", "75 years and over:"}
    den, num = [], []
    for col, info in meta["variables"].items():
        if not re.fullmatch(table + r"_\d{3}E", col):
            continue
        bits = info["label"].split("!!")
        if len(bits) < 4 or bits[2] not in {"Male:", "Female:"} or bits[3] not in adult:
            continue
        if len(bits) == 4:
            den.append(col)
        elif len(bits) == 5 and bits[4].startswith("With a"):
            num.append(col)
    assert len(num) == len(den) == 8
    output, raw = [], []
    for fips in counties:
        rows = get(f"{BASE}?get=group({table})&for=county:{fips[2:]}&in=state:{fips[:2]}&key={key}")
        data = dict(zip(rows[0], rows[1]))
        raw.append(data)
        a = sum(float(data[c]) for c in num)
        b = sum(float(data[c]) for c in den)
        vm = sum(float(data[c[:-1] + "M"]) ** 2 for c in num)
        vd = sum(float(data[c[:-1] + "M"]) ** 2 for c in den)
        assert all(float(data[c[:-1] + "M"]) >= 0 for c in num + den)
        p = a / b
        rad = vm - p * p * vd
        ratio = rad < 0
        if ratio:
            rad = vm + p * p * vd
        moe = 100 * math.sqrt(rad) / b
        col = "acs_" + tables[table]
        output.append(dict(table=table, fips=fips, name=data["NAME"], numerator=a, denominator=b,
                           numerator_moe=math.sqrt(vm), denominator_moe=math.sqrt(vd),
                           rate=100*p, moe=moe, ratio_fallback=ratio,
                           saved_rate=saved.at[fips, col], saved_moe=saved.at[fips, col + "_moe"],
                           rate_error=abs(100*p - saved.at[fips, col]),
                           moe_error=abs(moe - saved.at[fips, col + "_moe"])))
    (OUT / f"census_{table}_selected_counties.json").write_text(json.dumps(raw))
    return output


rows = []
errors = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    futures = {pool.submit(task, table): table for table in tables}
    for f in concurrent.futures.as_completed(futures):
        try:
            rows.extend(f.result())
            print(futures[f] + " completed", flush=True)
        except Exception as exc:
            errors.append({"table": futures[f], "error_type": type(exc).__name__})
pd.DataFrame(rows).to_csv(OUT / "acs_live_spotchecks.csv", index=False)
(OUT / "acs_live_status.json").write_text(json.dumps({"completed": len(rows), "errors": errors}, indent=2))
if rows:
    print(pd.DataFrame(rows)[["rate_error", "moe_error"]].max().to_dict())
assert len(rows) == 30, "Not all 30 live checks completed"
