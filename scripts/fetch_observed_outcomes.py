"""Directly measured county outcomes to set against PLACES model estimates.

1. ACS 2019-2023 5-year disability by type, adults 18+ (tables B18102-B18107),
   via the Census API (key in .env as CENSUS_API_KEY). Survey-measured, not modeled.
2. Medicare Geographic Variation PUF 2023, county level (data.cms.gov):
   Original Medicare and Medicare Advantage counts, and Prevention Quality
   Indicator admission rates (preventable hospitalizations, from claims).

Outputs: data/raw/acs_disability_2023.csv, data/raw/medicare_gv_county_2023.csv
"""

import json
import os
import re
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd

KEY = os.environ["CENSUS_API_KEY"]
BASE = "https://api.census.gov/data/2023/acs/acs5"


def get(url):
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.load(r)


# --- 1. ACS disability, adults 18+ --------------------------------------
TABLES = {
    "B18102": "hearing", "B18103": "vision", "B18104": "cognition",
    "B18105": "mobility", "B18106": "selfcare", "B18107": "indeplive",
}
out = None
for table, name in TABLES.items():
    labels = {
        k: v["label"]
        for k, v in get(f"{BASE}/groups/{table}.json")["variables"].items()
        if re.fullmatch(rf"{table}_\d+E", k)
    }
    rows = get(f"{BASE}?get=group({table})&for=county:*&key={KEY}")
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df.index = df["state"] + df["county"]
    num = df[list(labels)].apply(pd.to_numeric, errors="coerce")
    tot_cols, yes_cols = [], []
    for var, lb in labels.items():
        parts = lb.split("!!")
        # Estimate!!Total:!!Male:!!18 to 34 years:[!!With a hearing difficulty]
        if len(parts) < 4:
            continue
        age = parts[3]
        m = re.match(r"(\d+)", age)
        if not m or int(m.group(1)) < 18:
            continue
        if len(parts) == 4:
            tot_cols.append(var)
        elif parts[4].startswith("With a"):
            yes_cols.append(var)
    yes, den = num[yes_cols].sum(axis=1), num[tot_cols].sum(axis=1)
    rate = 100 * yes / den
    # 90% margin of error of the proportion (Census ACS handbook): sum MOEs in
    # quadrature, then the proportion formula; fall back to the ratio formula
    # when the term under the root is negative.
    moe = df[[c[:-1] + "M" for c in yes_cols + tot_cols]].apply(pd.to_numeric, errors="coerce").abs()
    moe_yes = np.sqrt((moe[[c[:-1] + "M" for c in yes_cols]] ** 2).sum(axis=1))
    moe_den = np.sqrt((moe[[c[:-1] + "M" for c in tot_cols]] ** 2).sum(axis=1))
    p = yes / den
    rad = moe_yes**2 - p**2 * moe_den**2
    rad = rad.where(rad >= 0, moe_yes**2 + p**2 * moe_den**2)
    rate_moe = 100 * np.sqrt(rad) / den
    print(table, name, "age groups used:", len(tot_cols), "with-difficulty cells:", len(yes_cols))
    block = pd.DataFrame({f"acs_{name}": rate, f"acs_{name}_moe": rate_moe})
    out = block if out is None else out.join(block)

# any disability is not in these tables by age 18+ without double counting; skip
out.index.name = "fips"
out.to_csv("data/raw/acs_disability_2023.csv")
print(out.describe().round(2))

# --- 2. Medicare Geographic Variation, county 2023 ------------------------
GV = "https://data.cms.gov/data-api/v1/dataset/6219697b-8f6c-4164-bed4-cd9317c58ebc/data"
recs, offset = [], 0
while True:
    q = urllib.parse.urlencode({
        "filter[BENE_GEO_LVL]": "County", "filter[YEAR]": "2023",
        "filter[BENE_AGE_LVL]": "All", "size": 5000, "offset": offset,
    })
    page = get(f"{GV}?{q}")
    recs += page
    if len(page) < 5000:
        break
    offset += 5000
gv = pd.DataFrame(recs)
keep = ["BENE_GEO_CD", "BENE_GEO_DESC", "BENES_TOTAL_CNT", "BENES_OM_CNT", "BENES_MA_CNT",
        "BENE_AVG_AGE", "BENE_DUAL_PCT", "BENE_RACE_HSPNC_PCT", "BENE_RACE_BLACK_PCT"]
keep += [c for c in gv.columns if c.startswith("PQI")]
gv = gv[keep].rename(columns={"BENE_GEO_CD": "fips"})
gv.to_csv("data/raw/medicare_gv_county_2023.csv", index=False)
print("GV county rows:", len(gv))
print(gv.head(3).T)
