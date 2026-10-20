"""Independent follow-up replication. Only raw study inputs are read."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RAW = ROOT / "data/raw/pharma"
GROUPS = ["IPAY 2026", "IPAY 2027", "IPAY 2028", "Other brands"]


def export(df, name):
    df.to_csv(OUT / f"{name}.csv", index=False)
    return df


def table(df):
    def cell(v):
        if pd.isna(v):
            return "NA"
        return f"{v:.6f}" if isinstance(v, float) else str(v)
    return "\n".join(
        ["| " + " | ".join(df.columns) + " |",
         "| " + " | ".join(["---"] * len(df.columns)) + " |"]
        + ["| " + " | ".join(cell(v) for v in row) + " |"
           for row in df.itertuples(index=False, name=None)])


def ingredients(value):
    value = value.upper().replace(", HUMAN", "").replace("SACUBITRILAT", "SACUBITRIL")
    return frozenset(x.strip() for x in re.split(r"[/;]", value) if x.strip())


def main():
    selected = pd.read_csv(RAW / "ira/selected_drugs_mfp.csv", dtype=str)
    selected["IPAY"] = selected.IPAY.astype(int)
    selected["ndc"] = selected["NDC-11"].str.replace("-", "", regex=False)
    selected["family"] = selected["Selected Drug Name"].str.split(";").str[0].str.strip()
    ndc_group = selected.groupby("ndc").IPAY.min().map(lambda y: f"IPAY {y}")
    ndc_family = selected.sort_values("IPAY").drop_duplicates("ndc").set_index("ndc").family
    aliases = []
    for year, names, family in selected[["IPAY", "Selected Drug Name", "family"]].drop_duplicates().itertuples(index=False, name=None):
        aliases.extend((name.strip().upper(), year, family) for name in names.split(";"))
    aliases.sort(key=lambda x: (x[1], -len(x[0])))
    ingredient_sets = set(selected["Active Ingredient Name or Active Moiety Name"].map(ingredients))

    def match(brand):
        if brand.startswith("NOVOLOG MIX"):
            return None
        for alias, year, family in aliases:
            if brand == alias or brand.startswith(alias + " "):
                return f"IPAY {year}", family
        return None

    def other_reason(brand, generic):
        if brand == generic:
            return "brand equals generic"
        first = re.match(r"^[A-Z0-9]+", brand)
        if first and first.group() in re.split(r"[/,\- ]+", generic):
            return "brand first word in generic words"
        if re.search(r"NEEDL|SYRING|LANCET|TEST STRIP|DIAGNOSTIC|GLUCOSE|SENSOR|SUPPL|SWAB|ALCOHOL PREP", generic):
            return "supply or diagnostic"
        if ingredients(generic) in ingredient_sets:
            return "selected ingredient set"
        return None

    partd = pd.read_csv(RAW / "partd/partd_spending_quarterly.csv")
    partd = partd[partd.Mftr_Name.eq("Overall") & partd.Brnd_Name.notna()].copy()
    partd["brand"] = partd.Brnd_Name.str.upper().str.strip()
    partd["generic"] = partd.Gnrc_Name.fillna("").str.upper().str.strip()
    mapped, reasons = [], []
    for b, g in zip(partd.brand, partd.generic):
        selected_match = match(b)
        mapped.append(selected_match or ("Other brands", b))
        reasons.append(None if selected_match else other_reason(b, g))
    partd["group"] = [m[0] for m in mapped]
    partd["family"] = [m[1] for m in mapped]
    partd["exclusion_reason"] = reasons
    export(partd, "partd_row_audit")
    kept = partd[partd.exclusion_reason.isna()].copy()
    sums = kept.groupby(["group", "family", "Year"])[["Tot_Spndng", "Tot_Clms"]].sum().unstack("Year")
    f = pd.DataFrame(index=sums.index)
    for label, suffix in [("2025 (Q1-Q4)", "2025"), ("2026 (Q1)", "2026q1")]:
        f["spend_" + suffix] = sums["Tot_Spndng"][label]
        f["claims_" + suffix] = sums["Tot_Clms"][label]
        f["per_claim_" + suffix] = f["spend_" + suffix] / f["claims_" + suffix]
    f = f[(f.claims_2025 >= 4000) & (f.claims_2026q1 >= 1000)].copy().reset_index()
    f["change_pct"] = 100 * (f.per_claim_2026q1 / f.per_claim_2025 - 1)
    f["annualized_claim_change_pct"] = 100 * (4 * f.claims_2026q1 / f.claims_2025 - 1)
    export(f, "partd_families")
    rows = []
    for group in GROUPS:
        d = f[f.group.eq(group)]
        rows.append(dict(
            group=group, families=len(d), median_pct=d.change_pct.median(),
            p25_pct=d.change_pct.quantile(.25), p75_pct=d.change_pct.quantile(.75),
            pooled_pct=100 * ((d.spend_2026q1.sum() / d.claims_2026q1.sum()) /
                             (d.spend_2025.sum() / d.claims_2025.sum()) - 1),
            fixed_weight_pct=100 * ((d.claims_2025 * d.per_claim_2026q1).sum() /
                                   (d.claims_2025 * d.per_claim_2025).sum() - 1),
            share_falling_30_pct=100 * d.change_pct.le(-30).mean()))
    groups = export(pd.DataFrame(rows), "partd_groups")

    universes, snapshots, dates = {}, {}, {}
    cols = ["NDC", "NDC Description", "NADAC Per Unit", "As of Date",
            "Pricing Unit", "Classification for Rate Setting", "Effective Date"]
    for year in [2024, 2025, 2026]:
        universe, latest, pieces = set(), None, []
        for d in pd.read_csv(RAW / f"nadac/nadac_{year}.csv", usecols=cols, dtype=str, chunksize=200000):
            d["date"] = pd.to_datetime(d["As of Date"], format="%m/%d/%Y")
            jan = d.date.dt.year.eq(year) & d.date.dt.month.eq(1)
            universe.update(d.loc[jan & d["Classification for Rate Setting"].eq("B"), "NDC"])
            candidate = d.date.max()
            if latest is None or candidate > latest:
                latest, pieces = candidate, []
            if candidate == latest:
                pieces.append(d[d.date.eq(latest)].copy())
        universes[year] = universe
        snapshots[year] = pd.concat(pieces, ignore_index=True)
        assert not snapshots[year].NDC.duplicated().any()
        dates[year] = latest.strftime("%Y-%m-%d")

    pieces = []
    for d in pd.read_csv(RAW / "nadac/nadac_comparison.csv", dtype=str, chunksize=200000):
        d = d[d["Primary Reason"].str.contains("WAC", na=False)].copy()
        d["date"] = pd.to_datetime(d["Effective Date"], format="%m/%d/%Y")
        for year, universe in universes.items():
            for endpoint in ["01-31", "02-28"]:
                e = d[d.date.between(f"{year-1}-12-20", f"{year}-{endpoint}") & d.NDC.isin(universe)].copy()
                e["year"], e["window_end"] = year, endpoint
                pieces.append(e)
    events = pd.concat(pieces, ignore_index=True)
    events["Percent Change"] = pd.to_numeric(events["Percent Change"])
    events["group"] = events.NDC.map(ndc_group).fillna("Other brands")
    events["family"] = events.NDC.map(ndc_family)
    export(events, "wac_events")
    rows, cut_rows = [], []
    for (year, endpoint), e in events.groupby(["year", "window_end"]):
        for group in GROUPS:
            u = {n for n in universes[year] if ndc_group.get(n, "Other brands") == group}
            changes = e[e.NDC.isin(u)].groupby("NDC")["Percent Change"].agg(["min", "max"])
            cuts, increases = int(changes["min"].le(-20).sum()), int(changes["max"].gt(0).sum())
            rows.append(dict(year=year, window_end=endpoint, group=group, universe=len(u), cuts=cuts,
                             cuts_pct=100*cuts/len(u) if u else float("nan"),
                             increases=increases, increases_pct=100*increases/len(u) if u else float("nan")))
        lows = e.groupby(["group", "family", "NDC"])["Percent Change"].min().reset_index()
        lows = lows[lows["Percent Change"].le(-20)]
        for (group, family), x in lows.groupby(["group", "family"]):
            first = e[e.NDC.isin(x.NDC) & e["Percent Change"].le(-20)].date.min()
            cut_rows.append(dict(year=year, window_end=endpoint, group=group, family=family,
                                 ndcs=len(x), median_pct=x["Percent Change"].median(),
                                 earliest=first.strftime("%Y-%m-%d")))
    windows = export(pd.DataFrame(rows), "wac_groups")
    cuts = export(pd.DataFrame(cut_rows), "selected_cuts")

    mfp = selected[selected.IPAY.eq(2026)].copy()
    mfp["start"] = pd.to_datetime(mfp["MFP Effective Date"], format="%m/%d/%Y")
    mfp["end"] = pd.to_datetime(mfp["MFP End Date"], format="%m/%d/%Y")
    mfp["mfp_unit"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
    ratio_pieces, chosen_rows = [], []
    for year in [2025, 2026]:
        when = pd.Timestamp(dates[year])
        if year < 2026:
            m = mfp[mfp.start.dt.year.eq(2026)].copy()
            m = m[m.start.eq(m.groupby("ndc").start.transform("min"))]
        else:
            m = mfp[mfp.start.le(when) & (mfp.end.isna() | mfp.end.ge(when))].copy()
        assert m.groupby("ndc").mfp_unit.nunique().max() == 1
        m = m.drop_duplicates("ndc")
        m["snapshot_year"] = year
        chosen_rows.append(m)
        d = snapshots[year]
        d = d[d["Classification for Rate Setting"].str.startswith("B", na=False)]
        d = d.merge(m[["ndc", "family", "mfp_unit", "MFP Effective Date", "MFP End Date"]],
                    left_on="NDC", right_on="ndc", validate="one_to_one")
        insulin = d.family.eq("NOVOLOG")
        d.loc[insulin, "family"] = d.loc[insulin, "NDC Description"].str.upper().str.split().str[0]
        assert set(d.loc[insulin, "family"]) <= {"NOVOLOG", "FIASP"}
        d["ratio"] = pd.to_numeric(d["NADAC Per Unit"]) / d.mfp_unit
        d["year"] = year
        ratio_pieces.append(d)
    export(pd.concat(chosen_rows, ignore_index=True), "mfp_rows_used")
    ratios = export(pd.concat(ratio_pieces, ignore_index=True), "ratio_ndcs")
    rows = []
    for family in sorted(ratios.family.unique()):
        row = {"family": family}
        for year in [2025, 2026]:
            d = ratios[ratios.family.eq(family) & ratios.year.eq(year)]
            row.update({f"ratio_{year}": d.ratio.median(), f"ndcs_{year}": len(d),
                        f"units_{year}": ", ".join(sorted(d["Pricing Unit"].unique()))})
        rows.append(row)
    ratio_summary = export(pd.DataFrame(rows), "ratio_summary")
    hashes = {}
    files = [RAW / "ira/selected_drugs_mfp.csv", RAW / "ira/selected_drugs_mfp.zip",
             RAW / "partd/partd_spending_quarterly.csv", RAW / "nadac/nadac_comparison.csv",
             *[RAW / f"nadac/nadac_{year}.csv" for year in universes]]
    for p in files:
        with p.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        sidecar = p.with_suffix(".meta.json") if p.parent.name == "nadac" else Path(str(p)+".meta.json")
        if sidecar.exists():
            assert digest == json.loads(sidecar.read_text())["sha256"], p
        hashes[str(p.relative_to(ROOT))] = digest
    stamp = datetime.now(timezone.utc).isoformat()
    (OUT / "provenance.json").write_text(json.dumps(
        {"saved_utc": stamp, "snapshot_dates": dates, "sha256": hashes}, indent=2))
    details = f[f.group.eq("IPAY 2026") | f.family.eq("LINZESS")][
        ["family", "claims_2025", "claims_2026q1", "per_claim_2025", "per_claim_2026q1",
         "change_pct", "annualized_claim_change_pct"]]
    text = f"""# Independent revised replication

Saved {stamp} before opening the revised summary, findings, analysis script or Agy report.
Code: `replicate2.py`. Inputs: raw CMS/NADAC files only; available sidecar hashes verified.
The fixed volume filter applies before all group statistics. Ingredient sets are order-independent;
both names are uppercased, stripped, and normalized for ", HUMAN" and SACUBITRILAT.
NovoLog Mix is not mapped to a selected family and is evaluated against the Other brands filters.
WAC windows include both endpoints and share the original January B-only universe.
Ratios use B-prefix NADAC rows, effective MFP intervals in 2026, and the earliest 2026
MFP row per NDC for pre-2026 snapshots. They are independent cross-sections, not a constant panel.
Snapshot dates: {json.dumps(dates)}.

## Part D

{table(groups)}

{table(details)}

## WAC windows

{table(windows)}

{table(cuts)}

## Brand NADAC / date-appropriate MFP

{table(ratio_summary)}
"""
    (OUT / "replication2.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
