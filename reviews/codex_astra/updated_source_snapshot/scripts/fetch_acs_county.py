"""Build county covariates from ACS 2019-2023 5-year that mirror the PLACES model inputs.

PLACES (2025 release) models each measure from individual age, sex,
race/ethnicity and education, plus the county share of adults below 150% of
the federal poverty level, with state and county random effects. This script
builds the county-level versions of those inputs, plus a direct ACS
uninsurance rate (ages 19-64) used as an outside benchmark.

Output: data/raw/acs_county_2023.csv (one row per county, 5-digit FIPS string).
"""

import json
import re
import urllib.request

import pandas as pd

BASE = "https://api.census.gov/data/2023/acs/acs5"


def get_json(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


def labels(group):
    v = get_json(f"{BASE}/groups/{group}.json")["variables"]
    return {k: v[k]["label"] for k in v if re.fullmatch(rf"{group}_\d+E", k)}


SF_URL = (
    "https://www2.census.gov/programs-surveys/acs/summary_file/2023/"
    "table-based-SF/data/5YRData/acsdt5y2023-{t}.dat"
)
SF_DIR = "data/raw/acs_sf"


def pull(group):
    """Read county rows of one ACS table from the bulk summary file.

    The data API now requires a key for county-wide requests, so estimates
    come from the table-based summary file (download it first with curl to
    data/raw/acs_sf/; see SF_URL). Variable labels still come from the API
    metadata endpoint, which needs no key.
    """
    path = f"{SF_DIR}/acsdt5y2023-{group.lower()}.dat"
    df = pd.read_csv(path, sep="|", dtype=str)
    df = df[df["GEO_ID"].str.startswith("0500000US")]
    df["fips"] = df["GEO_ID"].str[-5:]
    est = [c for c in df.columns if re.fullmatch(rf"{group}_E\d+", c)]
    out = df[["fips"] + est].set_index("fips").apply(pd.to_numeric, errors="coerce")
    out.columns = [f"{group}_{c.split('_E')[1]}E" for c in est]
    return out


def main():
    feats = pd.DataFrame()

    # Age and sex among adults (B01001)
    lab = labels("B01001")
    age = pull("B01001")
    adult_bands = {
        "18_24": ["18 and 19", "20 years", "21 years", "22 to 24"],
        "25_34": ["25 to 29", "30 to 34"],
        "35_44": ["35 to 39", "40 to 44"],
        "45_54": ["45 to 49", "50 to 54"],
        "55_64": ["55 to 59", "60 and 61", "62 to 64"],
        "65_74": ["65 and 66", "67 to 69", "70 to 74"],
        "75p": ["75 to 79", "80 to 84", "85 years"],
    }
    band_cols = {b: [] for b in adult_bands}
    male_adult = []
    for var, lb in lab.items():
        for b, keys in adult_bands.items():
            if any(k in lb for k in keys):
                band_cols[b].append(var)
                if "!!Male:" in lb:
                    male_adult.append(var)
    adults = age[[c for cols in band_cols.values() for c in cols]].sum(axis=1)
    for b, cols in band_cols.items():
        feats[f"age_{b}"] = age[cols].sum(axis=1) / adults
    feats["male"] = age[male_adult].sum(axis=1) / adults
    feats["adults"] = adults

    # Race/ethnicity, all ages (B03002); no adult-only table at county level
    r = pull("B03002")
    tot = r["B03002_001E"]
    for name, var in {
        "nh_white": "B03002_003E", "nh_black": "B03002_004E",
        "nh_aian": "B03002_005E", "nh_asian": "B03002_006E",
        "nh_nhpi": "B03002_007E", "nh_other_multi": None, "hispanic": "B03002_012E",
    }.items():
        if var:
            feats[name] = r[var] / tot
    feats["nh_other_multi"] = (r["B03002_008E"] + r["B03002_009E"]) / tot

    # Education, adults 25+ (B15003)
    e = pull("B15003")
    et = e["B15003_001E"]
    col = lambda a, b: [f"B15003_{i:03d}E" for i in range(a, b + 1)]
    feats["edu_lt_hs"] = e[col(2, 16)].sum(axis=1) / et
    feats["edu_hs"] = e[col(17, 18)].sum(axis=1) / et
    feats["edu_some_college"] = e[col(19, 21)].sum(axis=1) / et
    feats["edu_ba_plus"] = e[col(22, 25)].sum(axis=1) / et

    # Adults below 150% of poverty (B17024): 18+ age groups, ratio < 1.50
    lab = labels("B17024")
    p = pull("B17024")
    adult_tot, below = [], []
    for var, lb in lab.items():
        parts = lb.split("!!")
        if len(parts) < 3 or parts[2].startswith(("Under 6", "6 to 11", "12 to 17")):
            continue
        if len(parts) == 3:
            adult_tot.append(var)
        elif parts[3] in ("Under .50", ".50 to .74", ".75 to .99", "1.00 to 1.24", "1.25 to 1.49"):
            below.append(var)
    feats["pov150_adults"] = p[below].sum(axis=1) / p[adult_tot].sum(axis=1)

    # Benchmark: direct ACS uninsurance, ages 19-64 (B27010)
    u = pull("B27010")
    feats["acs_uninsured_19_64"] = (u["B27010_033E"] + u["B27010_050E"]) / (
        u["B27010_018E"] + u["B27010_034E"]
    )

    feats.index.name = "fips"
    feats.to_csv("data/raw/acs_county_2023.csv")
    print(feats.shape)
    print(feats.describe().T[["mean", "min", "max"]].round(3))


if __name__ == "__main__":
    main()
