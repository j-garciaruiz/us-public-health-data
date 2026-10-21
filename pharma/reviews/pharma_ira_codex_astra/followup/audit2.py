"""Post-freeze comparison and independent checks of supplementary write-up claims."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from replicate2 import OUT, ROOT, RAW, table, export

assert (OUT / "replication2.md").exists()
TARGET = ROOT / "pharma/outputs/ira"
checks = []


def compare(name, independent, published, key, mappings):
    a, b = independent.set_index(key).sort_index(), published.set_index(key).sort_index()
    assert a.index.equals(b.index), name
    maximum = 0
    cells = 0
    for left, right, scale in mappings:
        av, bv = a[left].astype(float), b[right].astype(float) * scale
        assert np.allclose(av, bv, atol=1e-9, rtol=1e-10, equal_nan=True), (name, left, (av-bv).abs().max())
        maximum = max(maximum, float((av-bv).abs().max()))
        cells += len(av)
    checks.append(dict(table=name, rows=len(a), numeric_cells=cells, max_absolute_difference=maximum))


groups = pd.read_csv(OUT / "partd_groups.csv")
compare("Part D groups", groups, pd.read_csv(TARGET / "partd_per_claim_by_group.csv"), ["group"], [
    ("families", "drug_families", 1), ("median_pct", "median_pct_change", 100),
    ("p25_pct", "p25", 100), ("p75_pct", "p75", 100), ("pooled_pct", "pooled_pct_change", 100),
    ("fixed_weight_pct", "fixed_weight_pct_change", 100),
    ("share_falling_30_pct", "share_falling_30pct_or_more", 100)])
f = pd.read_csv(OUT / "partd_families.csv").rename(columns={"family": "drug"})
pub = pd.read_csv(TARGET / "partd_per_claim_by_drug.csv")
pub["drug"] = pub.drug.str.upper()
compare("Part D families", f, pub, ["group", "drug"], [
    ("claims_2025", "Tot_Clms_2025", 1), ("claims_2026q1", "Tot_Clms_2026Q1", 1),
    ("spend_2025", "Tot_Spndng_2025", 1), ("spend_2026q1", "Tot_Spndng_2026Q1", 1),
    ("per_claim_2025", "per_claim_2025", 1), ("per_claim_2026q1", "per_claim_2026Q1", 1),
    ("change_pct", "chg_per_claim", 100),
    ("annualized_claim_change_pct", "claims_2026Q1_x4_vs_2025", 100)])
w = pd.read_csv(OUT / "wac_groups.csv").rename(columns={"year": "january"})
w["window"] = w.window_end.map({"01-31": "Dec 20-Jan 31", "02-28": "Dec 20-Feb 28"})
compare("WAC groups", w, pd.read_csv(TARGET / "wac_january_by_group.csv"), ["january", "window", "group"], [
    ("universe", "brand_ndcs", 1), ("cuts", "ndcs_with_wac_cut_ge_20pct", 1),
    ("cuts_pct", "share_cut", 100), ("increases", "ndcs_with_wac_increase", 1),
    ("increases_pct", "share_increase", 100)])
r = pd.read_csv(OUT / "ratio_summary.csv").rename(columns={"family": "drug"})
published_ratios = pd.read_csv(TARGET / "nadac_to_mfp_by_drug.csv")
compare("Brand snapshot ratios", r, published_ratios, ["drug"], [
    ("ratio_2025", "ratio_dec2025", 1), ("ndcs_2025", "ndcs_dec2025", 1),
    ("ratio_2026", "ratio_latest", 1), ("ndcs_2026", "ndcs_latest", 1)])
assert r.units_2026.str.replace(", ", "/", regex=False).tolist() == published_ratios.unit.tolist()

events = pd.read_csv(OUT / "wac_events.csv", dtype={"NDC": str})
cut = events[events.window_end.eq("02-28")].sort_values("Percent Change").drop_duplicates(["year", "NDC"])
cut = cut[cut["Percent Change"].le(-20)].copy()
cut["product"] = cut["NDC Description"].str.split().str[0]
cut["drug"] = cut.family.fillna(cut["NDC Description"])
ce = cut.groupby(["year", "group", "drug"]).agg(
    ndcs=("NDC", "nunique"), median_pct=("Percent Change", "median"),
    effective=("date", "min"), products=("product", lambda s: "/".join(sorted(set(s))))).reset_index()
ce = ce.rename(columns={"year": "january"})
pe = pd.read_csv(TARGET / "wac_cut_events.csv")
compare("WAC cut details", ce, pe, ["january", "group", "drug"], [
    ("ndcs", "ndcs", 1), ("median_pct", "median_pct", 1)])
for col in ["effective", "products"]:
    assert ce.set_index(["january", "group", "drug"])[col].sort_index().equals(
        pe.set_index(["january", "group", "drug"])[col].sort_index())
export(ce, "wac_cut_details")
product_cuts = cut[cut.year.eq(2026)].groupby(["group", "product"]).agg(
    ndcs=("NDC", "nunique"), median_pct=("Percent Change", "median"),
    first=("date", "min")).reset_index()
export(product_cuts, "wac_product_cuts_2026")
increases = events[events.year.eq(2026) & events.window_end.eq("02-28") &
                   events.group.eq("IPAY 2026") & events["Percent Change"].gt(0)]
inc = increases.groupby("family").agg(ndcs=("NDC", "nunique"), first=("date", "min"),
                                     median_pct=("Percent Change", "median")).reset_index()
export(inc, "selected_increases_2026")

# Read all selected NDC observations independently, to verify all-NDC and constant-panel sensitivities.
s = pd.read_csv(RAW / "ira/selected_drugs_mfp.csv", dtype=str)
s["ndc"] = s["NDC-11"].str.replace("-", "", regex=False)
s = s[s.IPAY.eq("2026")].copy()
s["family"] = s["Selected Drug Name"].str.split(";").str[0].str.strip()
raw_pieces = []
for year in [2024, 2025, 2026]:
    for d in pd.read_csv(RAW / f"nadac/nadac_{year}.csv", dtype=str, chunksize=200000):
        d = d[d.NDC.isin(s.ndc)].copy()
        if len(d):
            raw_pieces.append(d)
n = pd.concat(raw_pieces, ignore_index=True)
n["date"] = pd.to_datetime(n["As of Date"], format="%m/%d/%Y")
assert not set(n.NDC) & set(s[s.family.eq("IMBRUVICA")].ndc)
m = pd.read_csv(OUT / "mfp_rows_used.csv", dtype={"ndc": str})
all_ratios = []
for year in [2025, 2026]:
    d = n[n.date.eq(n[n.date.dt.year.eq(year)].date.max())].merge(
        m[m.snapshot_year.eq(year)][["ndc", "family", "mfp_unit"]], left_on="NDC", right_on="ndc",
        validate="one_to_one")
    product = d["NDC Description"].str.split().str[0]
    d.loc[d.family.eq("NOVOLOG") & product.isin(["FIASP", "NOVOLOG"]), "family"] = product
    d["ratio"] = pd.to_numeric(d["NADAC Per Unit"]) / d.mfp_unit
    d["year"] = year
    all_ratios.append(d)
a = export(pd.concat(all_ratios, ignore_index=True), "all_ndc_ratios")
br = pd.read_csv(OUT / "ratio_ndcs.csv", dtype={"NDC": str})
constant = br[br.NDC.isin(set(br[br.year.eq(2025)].NDC) & set(br[br.year.eq(2026)].NDC))]
cs = constant.groupby(["family", "year"]).ratio.median().unstack().rename(
    columns={2025: "constant_2025", 2026: "constant_2026"}).reset_index()
export(cs, "constant_panel")
extras = a.groupby(["family", "year"]).ratio.median().unstack().rename(
    columns={2025: "all_2025", 2026: "all_2026"}).reset_index()
extras = extras.merge(cs, on="family").rename(columns={"family": "drug"})
compare("Supplementary ratios", extras, published_ratios, ["drug"], [
    ("all_2025", "ratio_dec2025_all_ndcs", 1), ("all_2026", "ratio_latest_all_ndcs", 1),
    ("constant_2026", "ratio_latest_same_ndcs", 1)])
# Verify historical distinct matched NDC counts using applicable intervals.
sm = s.copy()
sm["start"] = pd.to_datetime(sm["MFP Effective Date"], format="%m/%d/%Y")
sm["end"] = pd.to_datetime(sm["MFP End Date"], format="%m/%d/%Y")
z = n[n.date.dt.year.ge(2025)].merge(sm, left_on="NDC", right_on="ndc")
reference = z.date.clip(lower=pd.Timestamp("2026-01-01"))
z = z[z.start.le(reference) & (z.end.isna() | z.end.ge(reference))].copy()
product = z["NDC Description"].str.split().str[0]
z.loc[z.family.eq("NOVOLOG") & product.isin(["NOVOLOG", "FIASP"]), "family"] = product
counts = z.groupby("family").NDC.nunique()
assert counts.sort_index().tolist() == published_ratios.set_index("drug").sort_index().mfp_ndcs_in_nadac.tolist()
z["ratio"] = pd.to_numeric(z["NADAC Per Unit"]) / pd.to_numeric(z["NDC-9 MFP per Unit Price"])
weekly = z[z["Classification for Rate Setting"].str.startswith("B", na=False)].groupby(
    ["family", "date"]).agg(ndcs=("NDC", "nunique"), ratio=("ratio", "median")).reset_index()
weekly = weekly.rename(columns={"family": "drug", "date": "as_of"})
weekly["as_of"] = weekly.as_of.dt.strftime("%Y-%m-%d")
compare("Weekly chart series", weekly, pd.read_csv(TARGET / "nadac_to_mfp_weekly.csv"), ["drug", "as_of"], [
    ("ndcs", "ndcs", 1), ("ratio", "median_ratio", 1)])
export(weekly, "weekly_ratios")
# NovoLog/Fiasp pooled result versus separate named products.
pdrows = pd.read_csv(OUT / "partd_row_audit.csv")
insulin = pdrows[pdrows.family.eq("NOVOLOG") & pdrows.exclusion_reason.isna()].copy()
insulin["product"] = insulin.brand.str.split().str[0]
ip = insulin.groupby(["product", "Year"])[["Tot_Spndng", "Tot_Clms"]].sum().unstack()
ir = pd.DataFrame(index=ip.index)
ir["change_pct"] = 100 * ((ip.Tot_Spndng["2026 (Q1)"] / ip.Tot_Clms["2026 (Q1)"]) /
                         (ip.Tot_Spndng["2025 (Q1-Q4)"] / ip.Tot_Clms["2025 (Q1-Q4)"]) - 1)
export(ir.reset_index(), "insulin_split_partd")
other = f[f.group.eq("Other brands") & f.change_pct.le(-30)].sort_values("change_pct")
export(other, "other_large_partd_declines")
# Exact decomposition: pooled difference is sum((s1-s0)*p1), on the eligible product panel.
o = f[f.group.eq("Other brands")].copy()
o["mix_contribution_pp"] = 100 * (
    (o.claims_2026q1 / o.claims_2026q1.sum() - o.claims_2025 / o.claims_2025.sum()) *
    o.per_claim_2026q1 / (o.spend_2025.sum() / o.claims_2025.sum()))
export(o.sort_values("mix_contribution_pp", ascending=False), "mix_decomposition")
# Confirm actual coverage of NovoLog Mix and deselection remarks, without importing study code.
mix = pdrows[pdrows.brand.str.startswith("NOVOLOG MIX")]
export(mix, "novolog_mix_disposition")
des = s[s.Remarks.fillna("").str.contains("deselect", case=False)][
    ["family", "MFP Effective Date", "MFP End Date", "Remarks"]].drop_duplicates()
export(des, "deselection_rows")
checks.append({"table": "Ancillary checks", "matched_brand_ndcs_2025": int(r.ndcs_2025.sum()),
               "matched_brand_ndcs_2026": int(r.ndcs_2026.sum()),
               "other_large_declines": len(other), "mix_contribution_pp": float(o.mix_contribution_pp.sum()),
               "imbruvica_matches_all_years": 0})
(OUT / "comparison_checks.json").write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
print(table(ir.reset_index()))
print(table(mix[["brand", "generic", "Year", "group", "exclusion_reason"]]))
print(table(des))
