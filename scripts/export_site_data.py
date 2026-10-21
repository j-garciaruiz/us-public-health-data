"""Export the reviewed analysis outputs into compact files for the static site.

Inputs (all produced and reviewed earlier):
  outputs/atlas/atlas_county_long.csv          (scripts/build_atlas_data.py)
  outputs/covariate_test/*.csv                 (scripts/covariate_test.py)
  outputs/expected_vs_observed/places_vs_observed.csv
  site/data/us_counties_2023.topo.json         (Census 2023 cartographic boundaries, mapshaper)

Outputs (JavaScript, so the pages also open from disk without a server):
  site/data/geo.js               window.US_TOPO
  site/data/atlas_index.js       window.ATLAS_INDEX: outcomes and county order
  site/data/atlas_<id>.js        window.ATLAS_DATA[<id>]: arrays aligned to county order
  site/data/findings.js          window.FINDINGS: every number quoted on the project page

NCHS rule: mortality values exist only for counties with 10 or more deaths;
build_mortality_smr.py already removed the rest, and this script asserts it.
"""

import json
import os
import re

import numpy as np
import pandas as pd

SITE = "site/data"
os.makedirs(SITE, exist_ok=True)


def js(path, var, obj):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{var} = ")
        json.dump(obj, f, separators=(",", ":"), allow_nan=False)
        f.write(";\n")


def clean(values, nd):
    out = []
    for v in values:
        if v is None or (isinstance(v, float) and not np.isfinite(v)):
            out.append(None)
        else:
            out.append(round(float(v), nd))
    return out


# --- geometry and county order ------------------------------------------
topo = json.load(open(f"{SITE}/us_counties_2023.topo.json"))
js(f"{SITE}/geo.js", "window.US_TOPO", topo)
geoms = topo["objects"]["counties"]["geometries"]
counties = sorted(((g["id"], g["properties"]["name"], g["properties"]["st"]) for g in geoms))
order = {fips: i for i, (fips, _, _) in enumerate(counties)}

# --- atlas -------------------------------------------------------------
atlas = pd.read_csv("outputs/atlas/atlas_county_long.csv", dtype={"fips": str})
assert set(atlas["fips"]) <= set(order), "atlas county missing from geometry"
mort = atlas[atlas["layer"] == "mortality"]
assert mort["observed"].notna().all()

SOURCES = {
    "medicare_actual": ("Medicare claims", "Recorded diagnoses among Original Medicare beneficiaries, 2023",
                        "CMS Mapping Medicare Disparities"),
    "medicare_std": ("Medicare claims, age-standardized", "Recorded diagnoses among Original Medicare beneficiaries, 2023, age-standardized by CMS",
                     "CMS Mapping Medicare Disparities"),
    "acs": ("Census survey", "Reported difficulty among civilian noninstitutionalized adults 18+, 2019-2023",
            "Census American Community Survey, 5-year"),
    "mortality": ("Death certificates", "Deaths 2018-2024 as a standardized mortality ratio x 100 (100 = national rates for the same age mix)",
                  "CDC WONDER, Multiple Cause of Death"),
}
# Which PLACES measure is shown for context next to each observed outcome
PLACES_NAME = {
    "Diabetes deaths": "diabetes prevalence", "Heart disease deaths": "coronary heart disease prevalence",
    "Cerebrovascular deaths": "stroke prevalence", "Chronic lower respiratory deaths": "COPD prevalence",
    "Diabetes": "diabetes prevalence", "COPD": "COPD prevalence", "Depression": "depression prevalence",
    "Hypertension": "high blood pressure prevalence", "Ischemic heart disease": "coronary heart disease prevalence",
    "Stroke or TIA": "stroke prevalence", "Asthma": "current asthma prevalence", "Obesity (recorded)": "obesity prevalence",
    "Rheumatoid arthritis or osteoarthritis": "arthritis prevalence", "Hyperlipidemia (recorded)": "high cholesterol prevalence",
    "Cancer: breast, colorectal, prostate or lung": "cancer prevalence (non-skin)",
    "Hearing difficulty": "hearing disability", "Vision difficulty": "vision disability",
    "Cognitive difficulty": "cognitive disability", "Ambulatory difficulty": "mobility disability",
    "Self-care difficulty": "self-care disability", "Independent-living difficulty": "independent-living disability",
}

index = {"counties": [{"fips": f, "name": n, "st": s} for f, n, s in counties], "outcomes": []}
for (layer, outcome), g in atlas.groupby(["layer", "outcome"], sort=False):
    oid = re.sub(r"[^a-z0-9]+", "_", f"{layer}_{outcome}".lower()).strip("_")
    nat = g[g["mode"] == "national"].set_index("fips")
    ws = g[g["mode"] == "within_state"].set_index("fips")
    n = len(counties)

    def arr(frame, col, nd):
        a = [None] * n
        for fips, v in zip(frame.index, frame[col]):
            a[order[fips]] = v
        return clean(a, nd)

    nd = 1 if layer == "mortality" else 2
    data = {
        "obs": arr(nat, "observed", nd),
        "places": arr(nat, "places_context", 1),
        "note": [None] * n,
        "disc": [None] * n,
        "nat": {"exp": arr(nat, "expected", nd), "shr": arr(nat, "difference_shrunk", nd),
                "rel": arr(nat, "reliability", 2), "tier": arr(nat, "tier", 0)},
        "ws": {"exp": arr(ws, "expected", nd), "shr": arr(ws, "difference_shrunk", nd),
               "rel": arr(ws, "reliability", 2), "tier": arr(ws, "tier", 0),
               "peers": arr(ws, "state_peer_counties", 0)},
    }
    for fips, note, disc in zip(nat.index, nat["reliability_note"], nat["source_discrepancy"]):
        data["note"][order[fips]] = note if isinstance(note, str) else None
        data["disc"][order[fips]] = 1 if bool(disc) else None
    js(f"{SITE}/atlas_{oid}.js", f'window.ATLAS_DATA = window.ATLAS_DATA || {{}}; window.ATLAS_DATA["{oid}"]', data)
    short, long_, source = SOURCES[layer]
    index["outcomes"].append({
        "id": oid, "layer": layer, "label": outcome, "units": g["units"].iloc[0],
        "source_short": short, "measure": long_, "source": source,
        "places_label": (f"CDC PLACES {PLACES_NAME[outcome]}" if outcome in PLACES_NAME else None),
        "places_note": "model estimate, adults 18+" + ("" if layer == "acs" else ", age-adjusted"),
        "shrinkage": layer != "medicare_std", "counties": int(nat["observed"].notna().sum()),
    })
js(f"{SITE}/atlas_index.js", "window.ATLAS_INDEX", index)

# --- findings for the project page ---------------------------------------
r2c = pd.read_csv("outputs/covariate_test/r2_by_measure_crudeprev.csv")
r2a = pd.read_csv("outputs/covariate_test/r2_by_measure_adjprev.csv")
bench = pd.read_csv("outputs/covariate_test/benchmark_uninsurance.csv")
pairs = pd.read_csv("outputs/covariate_test/pairs_adjprev.csv")
pvo = pd.read_csv("outputs/expected_vs_observed/places_vs_observed.csv")
strong = pairs[pairs["raw_r"].abs() >= 0.7]
dfi = pairs.set_index(["a", "b"]).loc[("diabetes", "foodinsecu")]

findings = {
    "r2_crude_cv": r2c[["measure", "inputs_plus_state_cv", "n_counties"]].round(4).to_dict("records"),
    "r2_adj_cv_median": round(float(r2a["inputs_plus_state_cv"].median()), 4),
    "r2_adj_cv_min": round(float(r2a["inputs_plus_state_cv"].min()), 4),
    "r2_adj_inputs_only_median": round(float(r2a["inputs_only"].median()), 4),
    "n_measures": int(len(r2a)),
    "n_pairs": int(len(pairs)),
    "n_strong_pairs": int(len(strong)),
    "median_abs_raw_r": round(float(pairs["raw_r"].abs().median()), 3),
    "median_abs_partial_r": round(float(pairs["partial_r"].abs().median()), 3),
    "diab_food": {"raw_r": round(float(dfi["raw_r"]), 3), "partial_r": round(float(dfi["partial_r"]), 3),
                  "n": int(dfi["n"])},
    "benchmark": bench.round(4).to_dict("records"),
    "places_vs_observed": pvo.round(4).to_dict("records"),
    "pvo_max_gain": round(float(pvo["gain"].max()), 4),
    "pvo_n_pairs": int(pvo[pvo["sample"] == "all"].shape[0]),
    "pvo_demo_beats_places": int((pvo["cv_r2_demo"] > pvo["cv_r2_places"]).sum()),
    "pvo_rows": int(len(pvo)),
    "atlas_outcomes": len(index["outcomes"]),
    "atlas_counties": len(counties),
}
# Atlas examples quoted on the project page (national mode, smoothed difference)
EXAMPLES = [
    ("Diabetes deaths", "mortality", "22017"), ("Diabetes deaths", "mortality", "22045"),
    ("Diabetes deaths", "mortality", "22079"), ("Diabetes", "medicare_actual", "36085"),
    ("Diabetes", "medicare_actual", "36047"),
]
nat_all = atlas[atlas["mode"] == "national"].set_index(["outcome", "layer", "fips"])
names = {f: (n, s) for f, n, s in counties}
findings["examples"] = []
for outcome_, layer_, fips in EXAMPLES:
    r = nat_all.loc[(outcome_, layer_, fips)]
    findings["examples"].append({
        "outcome": outcome_, "layer": layer_, "fips": fips, "name": names[fips][0], "st": names[fips][1],
        "observed": round(float(r["observed"]), 1), "expected": round(float(r["expected"]), 1),
        "shrunk": round(float(r["difference_shrunk"]), 1), "tier": int(r["tier"]),
        "id": re.sub(r"[^a-z0-9]+", "_", f"{layer_}_{outcome_}".lower()).strip("_"),
    })
js(f"{SITE}/findings.js", "window.FINDINGS", findings)
print("examples:", [(e["name"], e["st"], e["observed"], e["expected"], e["shrunk"], e["tier"]) for e in findings["examples"]])

sizes = {f: os.path.getsize(f"{SITE}/{f}") for f in os.listdir(SITE)}
print(len(index["outcomes"]), "outcomes;", len(counties), "counties;",
      f"largest outcome file {max(v for k, v in sizes.items() if k.startswith('atlas_') and k != 'atlas_index.js') / 1e3:.0f} KB;",
      f"total {sum(sizes.values()) / 1e6:.1f} MB")
print({k: v for k, v in findings.items() if not isinstance(v, list)})
