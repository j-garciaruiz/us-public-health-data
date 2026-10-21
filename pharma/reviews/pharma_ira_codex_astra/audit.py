"""Part B comparisons and bounded sensitivity analyses, after Part A was saved."""
from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ORIG = ROOT / "pharma/outputs/ira"
RAW = ROOT / "data/raw/pharma"
checks = []


def compare(a, b, keys, cols, name):
    a = a.set_index(keys).sort_index()
    b = b.set_index(keys).sort_index()
    assert a.index.equals(b.index), (name, "keys differ")
    for c in cols:
        av, bv = a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float)
        assert np.allclose(av, bv, rtol=1e-11, atol=1e-8, equal_nan=True), (name, c)
    checks.append({"table": name, "rows": len(a), "numeric_columns": len(cols), "result": "MATCH"})


f = pd.read_csv(OUT / "partd_families.csv").rename(columns={
    "family": "drug", "claims_2025": "Tot_Clms_2025", "claims_2026q1": "Tot_Clms_2026Q1",
    "spend_2025": "Tot_Spndng_2025", "spend_2026q1": "Tot_Spndng_2026Q1",
    "per_claim_2026q1": "per_claim_2026Q1", "change_pct": "chg_per_claim",
    "annualized_claim_change_pct": "claims_2026Q1_x4_vs_2025"})
f[["chg_per_claim", "claims_2026Q1_x4_vs_2025"]] /= 100
o = pd.read_csv(ORIG / "partd_per_claim_by_drug.csv")
o["drug"] = o.drug.str.upper()
compare(f, o, ["group", "drug"], list(o.columns[2:]), "partd_per_claim_by_drug")
g = pd.read_csv(OUT / "partd_groups.csv").rename(columns={
    "families": "drug_families", "median_pct": "median_pct_change", "p25_pct": "p25",
    "p75_pct": "p75", "pooled_pct": "pooled_pct_change", "share_falling_30_pct": "share_falling_30pct_or_more"})
g.iloc[:, 2:] /= 100
compare(g, pd.read_csv(ORIG / "partd_per_claim_by_group.csv"), ["group"], list(g.columns[1:]), "partd_per_claim_by_group")
j = pd.read_csv(OUT / "january_groups.csv").rename(columns={
    "year": "january", "universe": "brand_ndcs", "cuts": "ndcs_with_wac_cut_ge_20pct",
    "cuts_pct": "share_cut", "increases": "ndcs_with_wac_increase", "increases_pct": "share_increase"})
j[["share_cut", "share_increase"]] /= 100
compare(j, pd.read_csv(ORIG / "wac_january_by_group.csv"), ["january", "group"], list(j.columns[2:]), "wac_january_by_group")

e = pd.read_csv(OUT / "wac_events.csv", dtype={"NDC": str})
e = e[e["Percent Change"].le(-20)].copy()
e["family"] = e.family.fillna(e["NDC Description"])
dedup = e.sort_values("Percent Change").drop_duplicates(["year", "NDC"])
events = dedup.groupby(["year", "group", "family"]).agg(ndcs=("NDC", "nunique"), median_pct=("Percent Change", "median")).reset_index()
dates = e.groupby(["year", "group", "family"])["Effective Date"].agg(lambda s: pd.to_datetime(s, format="%m/%d/%Y").min().strftime("%Y-%m-%d")).reset_index(name="effective")
events = events.merge(dates).rename(columns={"year": "january", "family": "drug"})
oe = pd.read_csv(ORIG / "wac_cut_events.csv")
compare(events, oe, ["january", "group", "drug"], ["ndcs", "median_pct"], "wac_cut_events")
assert events.set_index(["january", "group", "drug"]).effective.sort_index().equals(oe.set_index(["january", "group", "drug"]).effective.sort_index())

s = pd.read_csv(RAW / "ira/selected_drugs_mfp.csv", dtype=str)
s["NDC"] = s["NDC-11"].str.replace("-", "", regex=False)
s["drug"] = s["Selected Drug Name"].str.split(";").str[0]
m = s[s.IPAY.eq("2026") & s["MFP Effective Date"].eq("01/01/2026")].drop_duplicates("NDC").copy()
m["mfp_unit"] = pd.to_numeric(m["NDC-9 MFP per Unit Price"])
parts = []
for year in [2025, 2026]:
    for d in pd.read_csv(RAW / f"nadac/nadac_{year}.csv", dtype=str, chunksize=200000,
                         usecols=["NDC", "NADAC Per Unit", "As of Date"]):
        x = d.merge(m[["NDC", "drug", "mfp_unit"]], on="NDC", validate="many_to_one")
        x["ratio"] = pd.to_numeric(x["NADAC Per Unit"]) / x.mfp_unit
        parts.append(x)
x = pd.concat(parts, ignore_index=True)
w = x.groupby(["drug", "As of Date"]).agg(ndcs=("NDC", "nunique"), median_ratio=("ratio", "median")).reset_index()
w["as_of"] = pd.to_datetime(w["As of Date"], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
compare(w, pd.read_csv(ORIG / "nadac_to_mfp_weekly.csv"), ["drug", "as_of"], ["ndcs", "median_ratio"], "nadac_to_mfp_weekly")
r = pd.read_csv(OUT / "ratio_summary.csv").rename(columns={
    "family": "drug", "ratio_2025": "ratio_dec2025", "ratio_2026": "ratio_latest",
    "ndcs_2025": "ndcs_dec2025", "ndcs_2026": "ndcs_latest"})
r["mfp_ndcs"] = r.drug.map(m.groupby("drug").NDC.nunique())
orr = pd.read_csv(ORIG / "nadac_to_mfp_by_drug.csv")
orr[["ndcs_dec2025", "ndcs_latest"]] = orr[["ndcs_dec2025", "ndcs_latest"]].fillna(0)
compare(r, orr, ["drug"], ["ratio_dec2025", "ratio_latest", "ndcs_dec2025", "ndcs_latest", "mfp_ndcs"], "nadac_to_mfp_by_drug")
assert r.set_index("drug").units_2026.fillna("").str.replace(", ", "/", regex=False).sort_index().equals(orr.set_index("drug").unit.fillna("").sort_index())

mapped = pd.read_csv(OUT / "partd_mapping.csv")
selected_like = mapped[mapped.family.eq("NOVOLOG")].copy()
sens = []
for label, d in [("fixed brief", selected_like), ("exclude NovoLog Mix", selected_like[~selected_like.brand.str.startswith("NOVOLOG MIX")])]:
    a = d.groupby("Year")[["Tot_Spndng", "Tot_Clms"]].sum()
    pc = a.Tot_Spndng/a.Tot_Clms
    sens.append({"mapping": label, "claims_2025": a.loc["2025 (Q1-Q4)", "Tot_Clms"],
                 "claims_2026q1": a.loc["2026 (Q1)", "Tot_Clms"],
                 "per_claim_2025": pc["2025 (Q1-Q4)"], "per_claim_2026q1": pc["2026 (Q1)"],
                 "change_pct": 100*(pc["2026 (Q1)"]/pc["2025 (Q1-Q4)"]-1)})
pd.DataFrame(sens).to_csv(OUT / "novolog_sensitivity.csv", index=False)
q = pd.read_csv(RAW / "partd/partd_spending_quarterly.csv")
q = q[q.Mftr_Name.eq("Overall")]
q[q.Brnd_Name.str.contains("aspart|dapagliflozin|sacubitril", case=False, na=False)].to_csv(OUT / "generic_selected_candidates.csv", index=False)
extras = {
    "ndcs_with_multiple_ipays": int(s.groupby("NDC").IPAY.nunique().gt(1).sum()),
    "duplicate_qualifying_cut_rows_per_ndc_window": int(e.duplicated(["year", "NDC"]).sum()),
    "novolog_sensitivity": sens,
    "generic_or_supply_examples": mapped[mapped.brand.isin(["ABACAVIR", "ALBUTEROL SULFATE HFA", "ALPRAZOLAM ER", "INSULIN ASPART FLEXPEN", "INSULIN ASPART PENFILL", "ADVOCATE PEN NEEDLES"])][["brand", "generic", "group"]].drop_duplicates().to_dict("records"),
}
result = json.dumps({"checks": checks, "audit": extras}, indent=2, default=lambda v: v.item())
(OUT / "comparison_checks.json").write_text(result)
print(result)
