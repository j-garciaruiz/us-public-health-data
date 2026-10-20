import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NADAC_DIR = ROOT / "data" / "raw" / "pharma" / "nadac"


def verify_sha256(csv_path: Path, meta_path: Path) -> dict:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    h = hashlib.sha256()
    total_bytes = 0
    with csv_path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
            total_bytes += len(chunk)
    actual_sha = h.hexdigest()
    return {
        "file": csv_path.name,
        "expected_sha256": meta["sha256"],
        "actual_sha256": actual_sha,
        "sha256_match": actual_sha == meta["sha256"],
        "expected_bytes": meta["bytes"],
        "actual_bytes": total_bytes,
        "bytes_match": total_bytes == meta["bytes"],
        "expected_data_rows": meta["data_rows"],
    }


def load_nadac(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        csv_path,
        dtype=str,
        keep_default_na=False,
    )
    df["nadac_per_unit_num"] = pd.to_numeric(df["NADAC Per Unit"], errors="raise")
    df["as_of_dt"] = pd.to_datetime(df["As of Date"], format="%m/%d/%Y")
    df["eff_dt"] = pd.to_datetime(df["Effective Date"], format="%m/%d/%Y")
    return df


def main():
    print("=== 1. SHA-256 VERIFICATION ===")
    for year in ["2025", "2026"]:
        res = verify_sha256(
            NADAC_DIR / f"nadac_{year}.csv",
            NADAC_DIR / f"nadac_{year}.meta.json",
        )
        print(json.dumps(res, indent=2))

    print("\nLoading 2025 and 2026 datasets...")
    df25 = load_nadac(NADAC_DIR / "nadac_2025.csv")
    df26 = load_nadac(NADAC_DIR / "nadac_2026.csv")
    print(f"2025 loaded rows: {len(df25):,}")
    print(f"2026 loaded rows: {len(df26):,}")

    print("\n=== 2. 2026 SUMMARY METRICS ===")
    total_rows_26 = len(df26)
    snapshots_26 = sorted(df26["as_of_dt"].unique())
    n_snapshots_26 = len(snapshots_26)
    first_snap_26 = pd.Timestamp(snapshots_26[0]).strftime("%Y-%m-%d")
    latest_snap_26 = pd.Timestamp(snapshots_26[-1]).strftime("%Y-%m-%d")
    first_snap_26_raw = df26.loc[df26["as_of_dt"] == snapshots_26[0], "As of Date"].iloc[0]
    latest_snap_26_raw = df26.loc[df26["as_of_dt"] == snapshots_26[-1], "As of Date"].iloc[0]

    distinct_ndcs_26 = df26["NDC"].nunique()
    ndcs_per_snap = df26.groupby("as_of_dt")["NDC"].nunique().sort_index()
    rows_per_snap = df26.groupby("as_of_dt").size().sort_index()

    not_11_mask = (df26["NDC"].str.len() != 11) | (~df26["NDC"].str.isdigit())
    n_not_11_rows = int(not_11_mask.sum())
    n_not_11_ndcs = df26.loc[not_11_mask, "NDC"].nunique()
    leading_zero_ndcs = df26["NDC"].str.startswith("0").sum()

    dup_mask = df26.duplicated(subset=["As of Date", "NDC"], keep=False)
    n_dup_rows = int(dup_mask.sum())
    n_dup_pairs = int(df26.duplicated(subset=["As of Date", "NDC"], keep="first").sum())

    print(f"Rows (2026): {total_rows_26:,}")
    print(f"Number of snapshots (2026): {n_snapshots_26}")
    print(f"First snapshot (2026): {first_snap_26} ({first_snap_26_raw})")
    print(f"Latest snapshot (2026): {latest_snap_26} ({latest_snap_26_raw})")
    print(f"Distinct NDCs (2026): {distinct_ndcs_26:,}")
    print(
        f"NDCs per snapshot (min / median / max): "
        f"{ndcs_per_snap.min():,} / {ndcs_per_snap.median():,.1f} / {ndcs_per_snap.max():,}"
    )
    print(
        f"Rows per snapshot (min / median / max): "
        f"{rows_per_snap.min():,} / {rows_per_snap.median():,.1f} / {rows_per_snap.max():,}"
    )
    print(f"NDCs not 11 digits (rows / distinct): {n_not_11_rows} / {n_not_11_ndcs}")
    print(f"Rows with leading-zero NDCs (would be <11 digits if parsed as int): {leading_zero_ndcs:,}")
    print(f"Duplicate (snapshot, NDC) rows (extra / all involved): {n_dup_pairs} / {n_dup_rows}")

    print("\n=== 3. LATEST 2026 SNAPSHOT: MEDIAN NADAC PER UNIT (PRICING UNIT = EA) ===")
    df26_latest = df26[df26["as_of_dt"] == snapshots_26[-1]]
    print("All classifications & pricing units in latest snapshot:")
    print(
        df26_latest.groupby(["Classification for Rate Setting", "Pricing Unit"])["nadac_per_unit_num"]
        .agg(["count", "median", "mean"])
    )
    df26_latest_ea = df26_latest[df26_latest["Pricing Unit"] == "EA"]
    for cls in ["G", "B"]:
        sub = df26_latest_ea[df26_latest_ea["Classification for Rate Setting"] == cls]["nadac_per_unit_num"]
        print(f"Class {cls}, Pricing Unit EA: count={len(sub):,}, median={sub.median():.6f} (raw={sub.median()})")

    print("\n=== 4. 2026 MONTHLY SURVEY REFRESHES ===")
    # Also check first 2026 vs last 2025 just in case
    snapshots_25 = sorted(df25["as_of_dt"].unique())
    prev_df = df25[df25["as_of_dt"] == snapshots_25[-1]][["NDC", "Effective Date"]].rename(
        columns={"Effective Date": "prev_eff"}
    )
    first_26_df = df26[df26["as_of_dt"] == snapshots_26[0]][["NDC", "Effective Date"]]
    m0 = first_26_df.merge(prev_df, on="NDC", how="inner")
    changed0 = (m0["Effective Date"] != m0["prev_eff"]).sum()
    print(
        f"Cross-year check {pd.Timestamp(snapshots_25[-1]).strftime('%Y-%m-%d')} -> {first_snap_26}: "
        f"common={len(m0):,}, changed={changed0:,} ({changed0/len(m0)*100:.2f}%)"
    )

    refresh_rows = []
    for i in range(1, len(snapshots_26)):
        prev_dt = snapshots_26[i - 1]
        curr_dt = snapshots_26[i]
        p_sub = df26[df26["as_of_dt"] == prev_dt][["NDC", "Effective Date"]].rename(
            columns={"Effective Date": "prev_eff"}
        )
        c_sub = df26[df26["as_of_dt"] == curr_dt][["NDC", "Effective Date", "As of Date"]]
        merged = c_sub.merge(p_sub, on="NDC", how="inner")
        n_common = len(merged)
        n_changed = int((merged["Effective Date"] != merged["prev_eff"]).sum())
        frac = n_changed / n_common if n_common else 0.0
        modal_eff = c_sub.loc[
            c_sub["NDC"].isin(merged.loc[merged["Effective Date"] != merged["prev_eff"], "NDC"]),
            "Effective Date",
        ].mode()
        modal_eff_str = modal_eff.iloc[0] if len(modal_eff) > 0 else ""
        refresh_rows.append(
            {
                "snapshot_iso": pd.Timestamp(curr_dt).strftime("%Y-%m-%d"),
                "snapshot_raw": c_sub["As of Date"].iloc[0],
                "prev_iso": pd.Timestamp(prev_dt).strftime("%Y-%m-%d"),
                "common_ndcs": n_common,
                "changed_eff": n_changed,
                "pct_changed": frac * 100,
                "is_refresh": frac > 0.5,
                "modal_new_eff_date": modal_eff_str,
            }
        )
    ref_df = pd.DataFrame(refresh_rows)
    print("All 2026 snapshots with >5% changed Effective Date:")
    print(ref_df[ref_df["pct_changed"] > 5.0].to_string(index=False))
    print("\nSnapshots where >50% of common NDCs have a new Effective Date:")
    refreshes_only = ref_df[ref_df["is_refresh"]]
    print(refreshes_only.to_string(index=False))
    print(f"Total monthly survey refreshes in 2026: {len(refreshes_only)}")

    print("\n=== 5. TRACER DESCRIPTIONS: FIRST 2025 vs LATEST 2026 ===")
    tracers = [
        "ATORVASTATIN 20 MG TABLET",
        "METFORMIN HCL 500 MG TABLET",
        "ELIQUIS 5 MG TABLET",
        "JARDIANCE 10 MG TABLET",
        "JANUVIA 100 MG TABLET",
        "XARELTO 20 MG TABLET",
    ]
    first_25_dt = snapshots_25[0]
    latest_26_dt = snapshots_26[-1]
    print(f"First 2025 snapshot: {pd.Timestamp(first_25_dt).strftime('%Y-%m-%d')} ({df25[df25['as_of_dt']==first_25_dt]['As of Date'].iloc[0]})")
    print(f"Latest 2026 snapshot: {pd.Timestamp(latest_26_dt).strftime('%Y-%m-%d')} ({df26[df26['as_of_dt']==latest_26_dt]['As of Date'].iloc[0]})")

    df25_first = df25[df25["as_of_dt"] == first_25_dt]
    for desc in tracers:
        s25 = df25_first[df25_first["NDC Description"] == desc]
        s26 = df26_latest[df26_latest["NDC Description"] == desc]
        med25 = s25["nadac_per_unit_num"].median()
        med26 = s26["nadac_per_unit_num"].median()
        diff = med26 - med25
        pct = (med26 / med25 - 1.0) * 100
        print(
            f"{desc:30s} | 2025-01-01: n={len(s25):3d}, med={med25:.5f} | "
            f"2026-10-21: n={len(s26):3d}, med={med26:.5f} | "
            f"diff={diff:+.5f} ({pct:+.2f}%)"
        )

    print("\n=== 6. ELIQUIS 5 MG TABLET & JARDIANCE 10 MG TABLET DROP ANALYSIS ===")
    df_all = pd.concat([df25, df26], ignore_index=True)
    for desc in tracers:
        sub = df_all[df_all["NDC Description"] == desc].copy()
        by_snap = (
            sub.groupby(["as_of_dt", "As of Date"])
            .agg(
                n_ndcs=("NDC", "nunique"),
                median_nadac=("nadac_per_unit_num", "median"),
                min_nadac=("nadac_per_unit_num", "min"),
                max_nadac=("nadac_per_unit_num", "max"),
            )
            .reset_index()
            .sort_values("as_of_dt")
        )
        by_snap["prev_median"] = by_snap["median_nadac"].shift(1)
        by_snap["delta"] = by_snap["median_nadac"] - by_snap["prev_median"]
        by_snap["pct_delta"] = (by_snap["median_nadac"] / by_snap["prev_median"] - 1.0) * 100
        changes = by_snap[by_snap["delta"].abs() > 1e-9]
        print(f"\n--- {desc}: snapshots where median changed ---")
        if len(changes) == 0:
            print("No changes.")
        else:
            for _, row in changes.iterrows():
                print(
                    f"  {row['as_of_dt'].strftime('%Y-%m-%d')} ({row['As of Date']}): "
                    f"n={row['n_ndcs']}, prev={row['prev_median']:.5f} -> new={row['median_nadac']:.5f}, "
                    f"delta={row['delta']:+.5f} ({row['pct_delta']:+.2f}%), "
                    f"range=[{row['min_nadac']:.5f}, {row['max_nadac']:.5f}]"
                )

    for desc in ["ELIQUIS 5 MG TABLET", "JARDIANCE 10 MG TABLET", "JANUVIA 100 MG TABLET", "XARELTO 20 MG TABLET"]:
        print(f"\nDetailed NDC-level history around changes for {desc}:")
        sub = df_all[df_all["NDC Description"] == desc].copy()
        piv = sub.pivot_table(
            index="as_of_dt",
            columns="NDC",
            values="nadac_per_unit_num",
            aggfunc="first",
        )
        # Print rows where any column or median changed compared to previous row
        med_series = sub.groupby("as_of_dt")["nadac_per_unit_num"].median()
        piv["MEDIAN"] = med_series
        changed_idx = piv.index[piv.ne(piv.shift(1)).any(axis=1)]
        print(piv.loc[changed_idx].to_string())
        # Also print metadata for each distinct NDC of this description in latest 2026 and around drop
        print(f"Distinct NDCs for {desc} across 2025-2026:")
        ndc_summary = (
            sub.groupby(["NDC", "Classification for Rate Setting", "OTC", "Pricing Unit", "Explanation Code"])
            .agg(
                first_seen=("as_of_dt", "min"),
                last_seen=("as_of_dt", "max"),
                n_snaps=("as_of_dt", "nunique"),
                min_rate=("nadac_per_unit_num", "min"),
                max_rate=("nadac_per_unit_num", "max"),
                eff_dates=("Effective Date", lambda x: ",".join(sorted(set(x)))),
            )
            .reset_index()
        )
        print(ndc_summary.to_string(index=False))


if __name__ == "__main__":
    main()
