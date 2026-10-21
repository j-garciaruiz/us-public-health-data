"""Independent Part A implementation. Reads raw inputs only."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/pharma"
GROUPS = ["IPAY 2026", "IPAY 2027", "IPAY 2028", "Other brands"]


def table(df):
    def cell(v):
        if pd.isna(v):
            return "NA"
        return f"{v:.4f}" if isinstance(v, float) else str(v)
    rows = ["| " + " | ".join(map(str, df.columns)) + " |",
            "| " + " | ".join(["---"] * len(df.columns)) + " |"]
    rows += ["| " + " | ".join(cell(v) for v in r) + " |"
             for r in df.itertuples(index=False, name=None)]
    return "\n".join(rows)


def export(df, name):
    df.to_csv(OUT / f"{name}.csv", index=False)
    return df


def main():
    selected = pd.read_csv(RAW / "ira/selected_drugs_mfp.csv", dtype=str)
    selected["IPAY"] = selected["IPAY"].astype(int)
    selected["ndc"] = selected["NDC-11"].str.replace("-", "", regex=False)
    selected["family"] = selected["Selected Drug Name"].str.split(";").str[0].str.strip()
    assert selected.ndc.str.fullmatch(r"\d{11}").all()
    ndc_group = selected.groupby("ndc").IPAY.min().map(lambda n: f"IPAY {n}")
    ndc_family = selected.sort_values("IPAY").drop_duplicates("ndc").set_index("ndc").family
    aliases = []
    for row in selected[["IPAY", "Selected Drug Name", "family"]].drop_duplicates().itertuples(index=False, name=None):
        for alias in row[1].split(";"):
            aliases.append((alias.strip().upper(), row[0], row[2]))
    aliases.sort(key=lambda x: (x[1], -len(x[0])))

    def match(name):
        if pd.isna(name):
            return None
        for alias, year, family in aliases:
            if name == alias or name.startswith(alias + " "):
                return family, f"IPAY {year}"
        return None

    partd = pd.read_csv(RAW / "partd/partd_spending_quarterly.csv")
    partd = partd[partd.Mftr_Name.eq("Overall")].copy()
    partd["brand"] = partd.Brnd_Name.str.upper().str.strip()
    partd["generic"] = partd.Gnrc_Name.str.upper().str.strip()
    matches = partd.brand.map(match)
    partd["family"] = [m[0] if m else b for m, b in zip(matches, partd.brand)]
    partd["group"] = [m[1] if m else "Other brands" for m in matches]
    partd = partd[partd.brand.notna() & (matches.notna() | partd.brand.ne(partd.generic))].copy()
    export(partd, "partd_mapping")
    totals = partd.groupby(["group", "family", "Year"])[["Tot_Spndng", "Tot_Clms"]].sum().unstack("Year")
    f = pd.DataFrame(index=totals.index)
    for period, year in [("2025 (Q1-Q4)", "2025"), ("2026 (Q1)", "2026q1")]:
        f["spend_" + year] = totals["Tot_Spndng"][period]
        f["claims_" + year] = totals["Tot_Clms"][period]
        f["per_claim_" + year] = f["spend_" + year] / f["claims_" + year]
    f = f[(f.claims_2025 >= 4000) & (f.claims_2026q1 >= 1000)].copy()
    f["change_pct"] = 100 * (f.per_claim_2026q1 / f.per_claim_2025 - 1)
    f["annualized_claim_change_pct"] = 100 * (4 * f.claims_2026q1 / f.claims_2025 - 1)
    f = export(f.reset_index(), "partd_families")
    group_rows = []
    for group in GROUPS:
        d = f[f.group.eq(group)]
        group_rows.append(dict(group=group, families=len(d), median_pct=d.change_pct.median(),
                               p25_pct=d.change_pct.quantile(.25), p75_pct=d.change_pct.quantile(.75),
                               pooled_pct=100*((d.spend_2026q1.sum()/d.claims_2026q1.sum()) /
                                               (d.spend_2025.sum()/d.claims_2025.sum())-1),
                               share_falling_30_pct=100*d.change_pct.le(-30).mean()))
    groups = export(pd.DataFrame(group_rows), "partd_groups")

    universes, snapshots, dates = {}, {}, {}
    nadac_cols = ["NDC", "NDC Description", "NADAC Per Unit", "As of Date",
                  "Pricing Unit", "Classification for Rate Setting", "Effective Date"]
    for year in [2024, 2025, 2026]:
        universe = set()
        latest = None
        last_chunks = []
        for d in pd.read_csv(RAW / f"nadac/nadac_{year}.csv", usecols=nadac_cols, dtype=str, chunksize=200000):
            d["date"] = pd.to_datetime(d["As of Date"], format="%m/%d/%Y")
            jan = d.date.dt.year.eq(year) & d.date.dt.month.eq(1)
            universe.update(d.loc[jan & d["Classification for Rate Setting"].eq("B"), "NDC"])
            candidate = d.date.max()
            if latest is None or candidate > latest:
                latest, last_chunks = candidate, []
            if candidate == latest:
                last_chunks.append(d[d.date.eq(latest)].copy())
        universes[year] = universe
        dates[year] = latest.strftime("%Y-%m-%d")
        snapshots[year] = pd.concat(last_chunks, ignore_index=True)
        assert not snapshots[year].NDC.duplicated().any()

    event_parts = []
    for d in pd.read_csv(RAW / "nadac/nadac_comparison.csv", dtype=str, chunksize=200000):
        d = d[d["Primary Reason"].str.contains("WAC", na=False)].copy()
        d["date"] = pd.to_datetime(d["Effective Date"], format="%m/%d/%Y")
        for year in universes:
            e = d[d.date.between(f"{year-1}-12-20", f"{year}-01-31") & d.NDC.isin(universes[year])].copy()
            e["year"] = year
            event_parts.append(e)
    events = pd.concat(event_parts, ignore_index=True)
    events["Percent Change"] = pd.to_numeric(events["Percent Change"])
    events["group"] = events.NDC.map(ndc_group).fillna("Other brands")
    events["family"] = events.NDC.map(ndc_family)
    export(events.drop(columns="date"), "wac_events")
    window_rows, cut_rows = [], []
    for year, universe in universes.items():
        e = events[events.year.eq(year)]
        for group in GROUPS:
            u = {ndc for ndc in universe if ndc_group.get(ndc, "Other brands") == group}
            x = e[e.NDC.isin(u)].groupby("NDC")["Percent Change"].agg(["min", "max"])
            cuts, raises = int(x["min"].le(-20).sum()), int(x["max"].gt(0).sum())
            window_rows.append(dict(year=year, group=group, universe=len(u), cuts=cuts,
                                    cuts_pct=100*cuts/len(u) if u else float("nan"),
                                    increases=raises, increases_pct=100*raises/len(u) if u else float("nan")))
        lows = e.groupby(["group", "family", "NDC"])["Percent Change"].min().reset_index()
        lows = lows[lows["Percent Change"].le(-20)]
        for (group, family), x in lows.groupby(["group", "family"]):
            first = e[e.NDC.isin(x.NDC) & e["Percent Change"].le(-20)].date.min()
            cut_rows.append(dict(year=year, group=group, family=family, ndcs=len(x),
                                 median_pct=x["Percent Change"].median(), earliest=first.strftime("%Y-%m-%d")))
    windows = export(pd.DataFrame(window_rows), "january_groups")
    cuts = export(pd.DataFrame(cut_rows), "selected_cuts")

    mfp = selected[selected.IPAY.eq(2026) & selected["MFP Effective Date"].eq("01/01/2026")].copy()
    mfp["mfp_unit"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
    assert mfp.groupby("ndc").mfp_unit.nunique().max() == 1
    mfp = mfp.drop_duplicates("ndc")
    ratios = []
    for year in [2025, 2026]:
        d = snapshots[year].merge(mfp[["ndc", "family", "mfp_unit"]], left_on="NDC", right_on="ndc", validate="one_to_one")
        d["ratio"] = pd.to_numeric(d["NADAC Per Unit"]) / d.mfp_unit
        d["year"] = year
        ratios.append(d)
    ratios = export(pd.concat(ratios, ignore_index=True), "ratio_ndcs")
    ratio_rows = []
    for family in sorted(mfp.family.unique()):
        row = {"family": family}
        for year in [2025, 2026]:
            d = ratios[ratios.family.eq(family) & ratios.year.eq(year)]
            row[f"ratio_{year}"] = d.ratio.median()
            row[f"ndcs_{year}"] = len(d)
            row[f"units_{year}"] = ", ".join(sorted(d["Pricing Unit"].unique()))
        ratio_rows.append(row)
    ratio_summary = export(pd.DataFrame(ratio_rows), "ratio_summary")
    hashes = {}
    for p in [RAW / "ira/selected_drugs_mfp.csv", RAW / "ira/selected_drugs_mfp.zip",
              RAW / "partd/partd_spending_quarterly.csv",
              *[RAW / f"nadac/nadac_{y}.csv" for y in universes], RAW / "nadac/nadac_comparison.csv"]:
        digest = hashlib.file_digest(p.open("rb"), "sha256").hexdigest()
        sidecar = p.with_suffix(".meta.json") if p.parent.name == "nadac" else Path(str(p)+".meta.json")
        if sidecar.exists():
            assert digest == json.loads(sidecar.read_text())["sha256"], p
        hashes[str(p.relative_to(ROOT))] = digest
    stamp = datetime.now(timezone.utc).isoformat()
    (OUT / "provenance.json").write_text(json.dumps({"saved_utc": stamp, "snapshot_dates": dates, "sha256": hashes}, indent=2))
    details = f[f.group.eq("IPAY 2026") | f.family.eq("LINZESS")][
        ["family", "claims_2025", "claims_2026q1", "per_claim_2025", "per_claim_2026q1", "change_pct", "annualized_claim_change_pct"]]
    text = f"""# Independent Part A replication

Saved {stamp}, before opening the original IRA script, outputs or findings.
Implemented from raw inputs in `replicate.py`. All available sidecar SHA-256 checks passed.
Percentiles use linear interpolation. Pooled changes use the same volume-eligible families.
Other-brand families are uppercase brand names. Missing brand names are excluded.
WAC windows include both endpoints; event counts are distinct January-universe NDCs.
Selected cut medians use each NDC's most negative event; earliest date is among qualifying cut events.
NDC identifiers preserve leading zeroes. No cross-IPAY NDC is counted twice.
Ratio summaries use all matched NDCs independently at each snapshot, without a constant-panel restriction.
The MFP CSV has no explicit pricing-unit column, so these are arithmetic joins pending unit validation in Part B.
Last snapshot dates: {json.dumps(dates)}. The 2026 snapshot is labeled one day after retrieval.

## A1. Part D spending per claim

{table(groups)}

{table(details)}

## A2. January WAC-related cuts

{table(windows)}

### Selected families with qualifying cuts

{table(cuts)}

## A3. NADAC / MFP per unit

2025 and 2026 column labels refer to the last available snapshot listed above.

{table(ratio_summary)}
"""
    (OUT / "replication.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
