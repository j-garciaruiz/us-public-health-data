"""County standardized mortality ratios (SMR) from CDC WONDER, 2018-2024 pooled.

Indirect age standardization (WONDER gives no county age-adjusted rates):
  expected_c = sum over age bands of national death rate(age, cause)
               x county person-years(age)
  county person-years(age) = WONDER county population (person-years, all
  ages, 2018-2024) x the county's age distribution from ACS 2019-2023 (B01001)
  SMR = observed deaths / expected deaths

Data use rule (NCHS agreement accepted 2026-10-20): counts of 9 or fewer are
"Suppressed" by WONDER and must never be published; those counties get no SMR.

Output: data/raw/wonder_county_smr.csv
"""

import re

import numpy as np
import pandas as pd

CAUSE = {"GR113-046": "diabetes", "GR113-054": "heart", "GR113-070": "stroke", "GR113-082": "clrd"}


def read_wonder(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        header = [h.strip('"') for h in f.readline().rstrip("\n").split("\t")]
        for line in f:
            if line.startswith('"---"'):
                break
            rows.append([c.strip('"') for c in line.rstrip("\n").split("\t")])
    return pd.DataFrame(rows, columns=header)


# --- national age-specific rates, bands matched to ACS -------------------
nat = read_wonder("data/raw/wonder/national_age_2018_2024.txt")
nat["deaths"] = pd.to_numeric(nat["Deaths"], errors="coerce").fillna(0)  # suppressed national cells (infant diabetes) ~ 0
nat["pop"] = pd.to_numeric(nat["Population"], errors="coerce")
nat["cause"] = nat["UCD - ICD-10 113 Cause List Code"].map(CAUSE)
BAND = {"1": "0_4", "1-4": "0_4", "5-14": "5_14", "15-24": "15_24", "25-34": "25_34",
        "35-44": "35_44", "45-54": "45_54", "55-64": "55_64", "65-74": "65_74",
        "75-84": "75_84", "85+": "85p"}
nat["band"] = nat["Ten-Year Age Groups Code"].map(BAND)
nat = nat.dropna(subset=["band", "pop"])
nat_rates = nat.groupby(["cause", "band"]).agg(deaths=("deaths", "sum"), pop=("pop", "sum"))
nat_rates["rate"] = nat_rates["deaths"] / nat_rates["pop"]
rates = nat_rates["rate"].unstack("band")

# --- county age structure from ACS B01001 (all ages, both sexes) ---------
sf = pd.read_csv("data/raw/acs_sf/acsdt5y2023-b01001.dat", sep="|", dtype=str)
sf = sf[sf["GEO_ID"].str.startswith("0500000US")]
sf = sf.set_index(sf["GEO_ID"].str[-5:])
est = sf[[c for c in sf.columns if re.fullmatch(r"B01001_E\d+", c)]].apply(pd.to_numeric)
# B01001 cells: male 003-025, female 027-049, same age order within sex
ACS_BANDS = {
    "0_4": [3], "5_14": [4, 5], "15_24": [6, 7, 8, 9, 10], "25_34": [11, 12],
    "35_44": [13, 14], "45_54": [15, 16], "55_64": [17, 18, 19], "65_74": [20, 21, 22],
    "75_84": [23, 24], "85p": [25],
}
age = pd.DataFrame({
    b: est[[f"B01001_E{i:03d}" for i in cells] + [f"B01001_E{i + 24:03d}" for i in cells]].sum(axis=1)
    for b, cells in ACS_BANDS.items()
})
assert (age.sum(axis=1) == est["B01001_E001"]).all(), "age bands must sum to total population"
age_share = age.div(age.sum(axis=1), axis=0)

# --- county observed deaths and SMR --------------------------------------
cty = read_wonder("data/raw/wonder/county_cause_2018_2024.txt")
# WONDER keeps some pre-change county codes. Oglala Lakota County, SD was
# Shannon County (46113) until 2015; its current code is 46102. Connecticut's
# old counties (09001-09015) cannot be mapped to the 2022+ planning regions
# used by ACS and PLACES, and Valdez-Cordova (02261) split in 2019 into 02063
# and 02066; those stay unmatched. Kusilvak Census Area, AK was Wade Hampton
# (02270) until 2015, a rename with identical boundaries (Agy review, bug 2).
cty["fips"] = cty["County Code"].replace({"46113": "46102", "02270": "02158"})
cty["cause"] = cty["UCD - ICD-10 113 Cause List Code"].map(CAUSE)
cty["observed"] = pd.to_numeric(cty["Deaths"], errors="coerce")  # "Suppressed" -> NaN
# WONDER prints 1-9 as "Suppressed" but shows zero deaths as 0. Zero is also a
# count of 9 or fewer, so it is suppressed here too (NCHS rule; Agy review, bug 1).
cty.loc[cty["observed"] <= 9, "observed"] = np.nan
cty["person_years"] = pd.to_numeric(cty["Population"], errors="coerce")
cty = cty.dropna(subset=["cause"])

out = []
for _, r in cty.iterrows():
    if r["fips"] not in age_share.index or pd.isna(r["person_years"]):
        continue
    py_age = age_share.loc[r["fips"]] * r["person_years"]
    expected = float((py_age * rates.loc[r["cause"], py_age.index]).sum())
    out.append({"fips": r["fips"], "cause": r["cause"], "observed": r["observed"],
                "expected": expected, "person_years": r["person_years"]})
smr = pd.DataFrame(out)
# The ACS 2019-2023 age structure is slightly younger at 75-84 than WONDER's
# 2018-2024 person-years, so raw expected deaths run about 1% low nationally
# (Agy review, section 2.2). Rescale each cause so expected deaths over all
# matched counties (suppressed ones included) equal observed national deaths
# of known age; SMRs are then centered on the national rate.
known_age = nat.groupby("cause")["deaths"].sum()
# Remove deaths in counties that cannot be matched (Connecticut's old
# counties, Valdez-Cordova), so the target covers the same counties as the sum.
unmatched = cty[~cty["fips"].isin(age_share.index)].groupby("cause")["observed"].sum()
target = known_age - unmatched.reindex(known_age.index).fillna(0)
scale = target / smr.groupby("cause")["expected"].sum()
smr["expected"] = smr["expected"] * smr["cause"].map(scale)
print("expected-death rescaling factors:", scale.round(4).to_dict())
smr["smr"] = smr["observed"] / smr["expected"]
smr["suppressed"] = smr["observed"].isna()
smr.to_csv("data/raw/wonder_county_smr.csv", index=False)

print("WONDER county rows:", cty["fips"].nunique(), "| with ACS age structure:", smr["fips"].nunique())
print("missing from ACS:", sorted(set(cty["fips"]) - set(age_share.index))[:12])
print(smr.groupby("cause").agg(counties=("fips", "size"), suppressed=("suppressed", "sum"),
                               median_smr=("smr", "median"), obs=("observed", "sum"),
                               exp=("expected", "sum")).round(3))
