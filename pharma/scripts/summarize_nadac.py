"""Sanity summary of the NADAC files pulled by fetch_nadac.py.

Reads data/raw/pharma/nadac/nadac_<year>.csv for the latest year and the year
before, checks structure (11-digit NDCs, one row per NDC per weekly snapshot),
describes the latest weekly snapshot, and tracks a fixed set of tracer drugs.

Writes:
    pharma/outputs/nadac_sanity.md          human-readable summary
    pharma/outputs/nadac_tracers.csv        tracer drugs: median NADAC per unit by snapshot

Usage:
    python pharma/scripts/summarize_nadac.py [year]
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "pharma" / "nadac"
OUT = ROOT / "pharma" / "outputs"

# Exact NDC Description strings as NADAC spells them (checked in the 2026-10-21 snapshot).
TRACERS = [
    "ATORVASTATIN 20 MG TABLET",
    "METFORMIN HCL 500 MG TABLET",
    "LISINOPRIL 10 MG TABLET",
    "AMLODIPINE BESYLATE 5 MG TAB",
    "LEVOTHYROXINE 50 MCG TABLET",
    "ALBUTEROL HFA 90 MCG INHALER",
    "SITAGLIPTIN PHOSPHATE 100 MG TABLET",
    "JANUVIA 100 MG TABLET",
    "ELIQUIS 5 MG TABLET",
    "XARELTO 20 MG TABLET",
    "JARDIANCE 10 MG TABLET",
    "OZEMPIC 1 MG/DOSE (4 MG/3 ML) PEN",
    "LANTUS SOLOSTAR 100 UNIT/ML",
]


def load(year):
    f = RAW / f"nadac_{year}.csv"
    d = pd.read_csv(f, dtype=str)
    d["as_of"] = pd.to_datetime(d["As of Date"], format="%m/%d/%Y")
    d["nadac"] = pd.to_numeric(d["NADAC Per Unit"])
    return d


def md_table(df, floatfmt="{:,.5g}"):
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for v in r:
            if isinstance(v, float):
                cells.append("" if pd.isna(v) else floatfmt.format(v))
            elif isinstance(v, int):
                cells.append(f"{v:,}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    year = int(sys.argv[1]) if len(sys.argv) > 1 else max(int(p.stem.split("_")[1]) for p in RAW.glob("nadac_20*.csv"))
    cur = load(year)
    prev_path = RAW / f"nadac_{year - 1}.csv"
    prev = load(year - 1) if prev_path.exists() else None

    weeks = cur.groupby("as_of").size()
    last_wk = weeks.index.max()
    last = cur[cur.as_of == last_wk]
    prev_wk = weeks.index[-2]
    prior = cur[cur.as_of == prev_wk]

    checks = {
        "rows": len(cur),
        "weekly snapshots": cur.as_of.nunique(),
        "first snapshot": weeks.index.min().date().isoformat(),
        "latest snapshot": last_wk.date().isoformat(),
        "NDCs per snapshot (min / median / max)": f"{weeks.min():,} / {int(weeks.median()):,} / {weeks.max():,}",
        "distinct NDCs in the year": cur.NDC.nunique(),
        "NDCs that are not 11 digits": int((~cur.NDC.str.fullmatch(r"\d{11}")).sum()),
        "duplicate NDC rows within a snapshot": int(cur.duplicated(["as_of", "NDC"]).sum()),
        "rows with missing or non-positive NADAC": int((cur.nadac.isna() | (cur.nadac <= 0)).sum()),
        "pharmacy type values": ", ".join(sorted(cur["Pharmacy Type Indicator"].dropna().unique())),
    }
    s = cur.sort_values(["NDC", "as_of"])
    s = s[s.NDC.eq(s.NDC.shift())]  # rows that have a previous snapshot for the same NDC
    new_eff = s["Effective Date"].ne(cur.sort_values(["NDC", "as_of"])["Effective Date"].shift().loc[s.index])
    share = new_eff.groupby(s.as_of).mean()
    checks["snapshots where most NDCs got a new Effective Date (monthly survey refresh)"] = ", ".join(
        d.strftime("%m-%d") for d in share[share > 0.5].index)
    if prev is not None:
        p_last = prev[prev.as_of == prev.as_of.max()]
        checks[f"latest {year - 1} snapshot"] = prev.as_of.max().date().isoformat()
        checks[f"NDCs in latest {year} snapshot also in latest {year - 1} snapshot"] = int(last.NDC.isin(p_last.NDC).sum())

    # Composition of the latest snapshot.
    comp = (
        last.groupby(["Classification for Rate Setting", "Pricing Unit"])
        .nadac.agg(NDCs="size", p10=lambda s: s.quantile(0.1), median="median", p90=lambda s: s.quantile(0.9))
        .reset_index()
        .rename(columns={"Classification for Rate Setting": "class", "Pricing Unit": "unit"})
    )
    otc = last.OTC.value_counts().to_dict()

    # Week-over-week movement between the last two snapshots.
    # A monthly survey refresh moves the Effective Date for most NDCs at once; ordinary weeks touch few.
    m = last[["NDC", "nadac", "Effective Date"]].merge(
        prior[["NDC", "nadac", "Effective Date"]], on="NDC", suffixes=("", "_prev"))
    changed = m[m.nadac != m.nadac_prev]
    rel = (changed.nadac / changed.nadac_prev - 1).abs()
    wow = {
        "NDCs in both of the last two snapshots": len(m),
        "NDCs with a new Effective Date": int((m["Effective Date"] != m["Effective Date_prev"]).sum()),
        "NDCs whose NADAC changed": len(changed),
        "of which by more than 1%": int((rel > 0.01).sum()),
        "of which increased": int((changed.nadac > changed.nadac_prev).sum()),
        "added (in latest only)": int((~last.NDC.isin(prior.NDC)).sum()),
        "dropped (in prior only)": int((~prior.NDC.isin(last.NDC)).sum()),
    }

    # Tracers: median NADAC per unit across NDCs sharing the description, per snapshot.
    both = pd.concat([d for d in (prev, cur) if d is not None])
    t = both[both["NDC Description"].isin(TRACERS)]
    tr = (
        t.groupby(["NDC Description", "as_of"])
        .agg(ndcs=("NDC", "nunique"), median_nadac=("nadac", "median"), unit=("Pricing Unit", "first"),
             cls=("Classification for Rate Setting", lambda s: "/".join(sorted(s.unique()))))
        .reset_index()
    )
    OUT.mkdir(parents=True, exist_ok=True)
    tr.assign(as_of=tr.as_of.dt.date).to_csv(OUT / "nadac_tracers.csv", index=False)

    snaps = [cur.as_of.min(), last_wk]
    labels = [f"{cur.as_of.min().date()}", f"{last_wk.date()}"]
    if prev is not None:
        snaps.insert(0, prev.as_of.min())
        labels.insert(0, f"{prev.as_of.min().date()}")
    wide = tr[tr.as_of.isin(snaps)].pivot(index="NDC Description", columns="as_of", values="median_nadac")
    wide.columns = labels[: len(wide.columns)] if len(wide.columns) == len(labels) else [c.date().isoformat() for c in wide.columns]
    lastinfo = tr[tr.as_of == last_wk].set_index("NDC Description")[["unit", "cls", "ndcs"]]
    wide = lastinfo.join(wide).reindex(TRACERS).reset_index()
    first_col, last_col = wide.columns[4], wide.columns[-1]
    wide[f"change {first_col} to {last_col}"] = (wide[last_col] / wide[first_col] - 1).map(
        lambda x: "" if pd.isna(x) else f"{x:+.1%}")
    wide = wide.rename(columns={"NDC Description": "drug", "cls": "class", "ndcs": "NDCs (latest)"})

    lines = [
        f"# NADAC {year}: sanity summary",
        "",
        f"Generated by `pharma/scripts/summarize_nadac.py` from `data/raw/pharma/nadac/nadac_{year}.csv`"
        + (f" and `nadac_{year - 1}.csv`" if prev is not None else "") + ".",
        "NADAC is the CMS survey estimate of the average invoice price retail community pharmacies pay, per pricing unit"
        " (EA = tablet/capsule/each, ML, GM). It excludes rebates paid to payers and off-invoice discounts.",
        "",
        "## Structure checks",
        "",
        md_table(pd.DataFrame({"check": list(checks), "value": [f"{v:,}" if isinstance(v, int) else v for v in checks.values()]})),
        "",
        f"## Latest snapshot ({last_wk.date()}): price per unit by class",
        "",
        "Class: G = generic, B = brand, B-ANDA = brand-name product approved on an ANDA, B-BIO = biosimilar or"
        " interchangeable biologic. OTC flag in this snapshot: " + ", ".join(f"{k} = {v:,}" for k, v in otc.items()) + ".",
        "",
        md_table(comp),
        "",
        f"## Week-over-week ({prev_wk.date()} to {last_wk.date()})",
        "",
        md_table(pd.DataFrame({"measure": list(wow), "NDCs": list(wow.values())})),
        "",
        "## Tracer drugs: median NADAC per unit across NDCs with the same description",
        "",
        "Medians across all NDCs (labelers, package sizes) carrying the exact description. Full weekly series in"
        " `pharma/outputs/nadac_tracers.csv`.",
        "",
        md_table(wide),
        "",
    ]
    (OUT / "nadac_sanity.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
