"""Independent blind recomputation; reads raw data and saved live API response only."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
RAW = ROOT / "data/raw/pharma/nadac"
lines = ["# Independent NADAC recomputation", "",
         f"Computed UTC: {datetime.now(timezone.utc).isoformat()}", "",
         "Written before opening the author's outputs, analysis scripts or README sections.",
         "NDCs are strings. Dates are parsed; weekly comparisons join adjacent snapshots by NDC.",
         "Quantiles use pandas linear interpolation. Prices are dollars per listed pricing unit.",
         "A change greater than 1% means absolute relative change > 0.01. Increases are also reported separately.",
         ""]

def table(frame):
    lines.append("| " + " | ".join(map(str, frame.columns)) + " |")
    lines.append("| " + " | ".join("---" for _ in frame.columns) + " |")
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    lines.append("")

frames = {}
for year in (2025, 2026):
    path = RAW / f"nadac_{year}.csv"
    meta = json.loads(path.with_suffix(".meta.json").read_text())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == meta["sha256"], (year, digest)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for col in ("As of Date", "Effective Date"):
        df[col] = pd.to_datetime(df[col], format="%m/%d/%Y", errors="raise")
    df["price"] = pd.to_numeric(df["NADAC Per Unit"], errors="coerce")
    frames[year] = df
    lines += [f"- {year}: SHA-256 matches sidecar `{digest}`; {len(df):,} parsed rows.",
              f"  Source recorded in sidecar: {meta['source_url']}"]
live = json.loads((OUT / "live_nadac_count.json").read_text())
d = frames[2026]
assert len(d) == live["count"]
lines += [f"- Live 2026 API count: {live['count']:,}, matches parsed rows.",
          "- Hashes establish agreement with saved provenance, not an independent re-download of source bytes.", ""]
snaps = sorted(d["As of Date"].unique())
counts = d.groupby("As of Date")["NDC"].nunique()
lines += ["## 1. Coverage", "",
          f"Rows: {len(d):,}; snapshots: {len(snaps)}; first: {pd.Timestamp(snaps[0]).date()}; latest: {pd.Timestamp(snaps[-1]).date()}.",
          f"NDCs per snapshot min/median/max: {counts.min():,} / {counts.median():,.1f} / {counts.max():,}.",
          f"Distinct annual NDCs: {d.NDC.nunique():,}.", "",
          "## 2. Integrity", "",
          f"Not exactly 11 ASCII digits: {(~d.NDC.str.fullmatch('[0-9]{11}')).sum():,}.",
          f"Duplicate (snapshot,NDC) rows beyond first: {d.duplicated(['As of Date','NDC']).sum():,}.",
          f"Missing/non-numeric price: {d.price.isna().sum():,}; non-positive: {d.price.le(0).sum():,}.", ""]
assert not d.duplicated(["As of Date", "NDC"]).any()
transitions = []
for before, after in zip(snaps[:-1], snaps[1:]):
    a = d[d["As of Date"].eq(before)].set_index("NDC")
    b = d[d["As of Date"].eq(after)].set_index("NDC")
    joined = a[["Effective Date","price"]].join(b[["Effective Date","price"]], how="inner", lsuffix="_old", rsuffix="_new")
    eff = joined["Effective Date_old"].ne(joined["Effective Date_new"])
    delta = joined.price_new / joined.price_old - 1
    changed = joined.price_new.ne(joined.price_old)
    transitions.append({
        "snapshot": str(pd.Timestamp(after).date()), "shared": len(joined),
        "effective_changed": int(eff.sum()), "effective_pct": round(100*eff.mean(), 6),
        "price_changed": int(changed.sum()), "abs_change_gt1pct": int(delta.abs().gt(.01).sum()),
        "increased_any": int(delta.gt(0).sum()), "increased_gt1pct": int(delta.gt(.01).sum()),
        "added": len(b.index.difference(a.index)), "dropped": len(a.index.difference(b.index))
    })
t = pd.DataFrame(transitions)
t.to_csv(OUT / "snapshot_transitions.csv", index=False)
lines += ["## 3. Effective-date changes exceeding half of shared NDCs", ""]
table(t[t.effective_pct.gt(50)][["snapshot","shared","effective_changed","effective_pct"]])
latest = d[d["As of Date"].eq(snaps[-1])]
old = frames[2025]
oldlatest = old[old["As of Date"].eq(old["As of Date"].max())]
lines += ["## 4. Annual overlap", "",
          f"Latest 2025 ({old['As of Date'].max().date()}) and latest 2026 shared NDCs: {len(set(latest.NDC) & set(oldlatest.NDC)):,}.", "",
          "## 5. Latest-snapshot strata", ""]
groups = latest.groupby(["Classification for Rate Setting","Pricing Unit"], dropna=False)
stats = groups.agg(NDCs=("NDC","nunique"), p10=("price",lambda s:s.quantile(.1)),
                   median=("price","median"), p90=("price",lambda s:s.quantile(.9))).reset_index()
table(stats)
table(latest.groupby("OTC",dropna=False).agg(NDCs=("NDC","nunique")).reset_index())
lines += ["## 6. Last-two-snapshot transition", "",
          f"From {pd.Timestamp(snaps[-2]).date()} to {pd.Timestamp(snaps[-1]).date()}.", ""]
table(t.tail(1))
tracers = [
    "ATORVASTATIN 20 MG TABLET", "METFORMIN HCL 500 MG TABLET", "LISINOPRIL 10 MG TABLET",
    "AMLODIPINE BESYLATE 5 MG TAB", "LEVOTHYROXINE 50 MCG TABLET", "ALBUTEROL HFA 90 MCG INHALER",
    "SITAGLIPTIN PHOSPHATE 100 MG TABLET", "JANUVIA 100 MG TABLET", "ELIQUIS 5 MG TABLET",
    "XARELTO 20 MG TABLET", "JARDIANCE 10 MG TABLET", "OZEMPIC 1 MG/DOSE (4 MG/3 ML) PEN",
    "LANTUS SOLOSTAR 100 UNIT/ML"]
rows = []
dates = [old["As of Date"].min(), pd.Timestamp(snaps[0]), pd.Timestamp(snaps[-1])]
for desc in tracers:
    prices = [f.loc[f["As of Date"].eq(date)&f["NDC Description"].eq(desc),"price"].median()
              for f,date in zip([old,d,d], dates)]
    rows.append([desc,*prices,(prices[2]/prices[0]-1)*100])
tr = pd.DataFrame(rows, columns=["description",*(str(x.date()) for x in dates),"change_pct"])
tr.to_csv(OUT / "independent_tracers.csv",index=False)
lines += ["## 7. Exact-description tracer medians", "", "Missing descriptions remain NaN; no substitution.", ""]
table(tr)
lines += ["## 8. Timing of tracer drops", "",
          "Drops compare consecutive snapshot medians over all available 2025 and 2026 snapshots.", ""]
both = pd.concat([old,d],ignore_index=True)
for desc in ["ELIQUIS 5 MG TABLET","JARDIANCE 10 MG TABLET","JANUVIA 100 MG TABLET","XARELTO 20 MG TABLET"]:
    series = both[both["NDC Description"].eq(desc)].groupby("As of Date").price.median().sort_index()
    changes = series.pct_change(fill_method=None)*100
    if desc.startswith(("ELIQUIS","JARDIANCE")):
        drops = changes[changes.lt(0)]
        lines += [f"### {desc}", ""]
        table(pd.DataFrame({"snapshot":drops.index.strftime("%Y-%m-%d"),"median":series.loc[drops.index].values,"drop_pct":drops.values}))
    else:
        selected = series.reindex(snaps[:4])
        lines += [f"### {desc}: first four 2026 snapshots", ""]
        table(pd.DataFrame({"snapshot":selected.index.strftime("%Y-%m-%d"),"median":selected.values,
                            "change_from_previous_snapshot_pct":changes.reindex(selected.index).values}))
(OUT / "nadac_recompute.md").write_text("\n".join(lines)+"\n")
print("\n".join(lines))
