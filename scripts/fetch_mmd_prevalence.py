"""County prevalence of chronic conditions among Original Medicare beneficiaries, from claims.

Source: CMS Mapping Medicare Disparities (MMD) Population tool, data year 2023.
CMS retired its downloadable chronic-conditions files; the MMD tool now carries
these data and loads them from a public data.cms.gov endpoint, used here.
Prevalence is the share of fee-for-service beneficiaries with the condition
identified by the CMS Chronic Conditions Warehouse claims algorithms.

fltr=1 unsmoothed actual, fltr=2 unsmoothed age-standardized.
Output: data/raw/mmd_prevalence_2023.csv (long: fips, condition, fltr, rate).
"""

import json
import time
import urllib.parse
import urllib.request

import pandas as pd

BASE = "https://data.cms.gov/data-api/v1/mmd-tool/"
SOURCE = "prev_final_long_fltr12_racecat_all_sexcat_all_23_p"

# MMD condition code -> matching PLACES measure
CONDITIONS = {
    15: ("diabetes", "diabetes"), 13: ("copd", "copd"), 14: ("depression", "depression"),
    17: ("hypertension", "bphigh"), 19: ("ischemic_heart_disease", "chd"),
    23: ("stroke_tia", "stroke"), 4: ("asthma", "casthma"), 20: ("obesity", "obesity"),
    3: ("arthritis", "arthritis"), 18: ("hyperlipidemia", "highchol"),
    5: ("cancer_4_sites", "cancer"), 12: ("chronic_kidney_disease", None),
}


def fetch(cond, fltr):
    q = (
        f"_source={SOURCE}&population=f&year=23&geography=c&measure=v&condition={cond}"
        "&sexcat=.|IS%20NULL&agecat=.|IS%20NULL&dual=.|IS%20NULL&eligcat=.|IS%20NULL"
        f"&racecat=.|IS%20NULL&fltr={fltr}&_size=500000"
    )
    with urllib.request.urlopen(BASE + "?" + q, timeout=180) as r:
        return json.load(r)


rows = []
for cond, (name, places) in CONDITIONS.items():
    for fltr in (1, 2):
        data = fetch(cond, fltr)
        for d in data:
            rows.append({
                "fips": d["fips"], "condition_code": cond, "condition": name,
                "places_measure": places, "fltr": fltr, "rate_raw": d.get("rate"),
            })
        print(name, fltr, len(data))
        time.sleep(0.5)

df = pd.DataFrame(rows)
df["rate"] = pd.to_numeric(df["rate_raw"], errors="coerce")
df.to_csv("data/raw/mmd_prevalence_2023.csv", index=False)
print(df.groupby(["condition", "fltr"]).rate.describe().round(2))
print("non-numeric rate values:", df.loc[df.rate.isna(), "rate_raw"].value_counts().head())
