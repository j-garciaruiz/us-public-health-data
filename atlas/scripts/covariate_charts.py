"""Charts for the shared-covariate test (run atlas/scripts/covariate_test.py first)."""

# Paths in this script are relative to the repository root; anchor there so it
# runs from any working directory (atlas/scripts/<this file> -> repo root).
import os as _os
from pathlib import Path as _Path
_os.chdir(_Path(__file__).resolve().parents[2])

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUT = "atlas/outputs/covariate_test"
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE = "#2a78d6", "#eb6834"

LABELS = {
    "access2": "No health insurance (18-64)", "arthritis": "Arthritis", "binge": "Binge drinking",
    "bphigh": "High blood pressure", "bpmed": "Taking BP medication", "cancer": "Cancer (non-skin)",
    "casthma": "Current asthma", "chd": "Coronary heart disease", "checkup": "Routine checkup",
    "cholscreen": "Cholesterol screening", "colon_screen": "Colorectal screening", "copd": "COPD",
    "csmoking": "Current smoking", "dental": "Dental visit", "depression": "Depression",
    "diabetes": "Diabetes", "ghlth": "Fair or poor health", "highchol": "High cholesterol",
    "lpa": "Physical inactivity", "mammouse": "Mammography", "mhlth": "Frequent mental distress",
    "obesity": "Obesity", "phlth": "Frequent physical distress", "sleep": "Short sleep",
    "stroke": "Stroke", "teethlost": "All teeth lost (65+)", "hearing": "Hearing disability",
    "vision": "Vision disability", "cognition": "Cognitive disability", "mobility": "Mobility disability",
    "selfcare": "Self-care disability", "indeplive": "Independent-living disability",
    "disability": "Any disability", "loneliness": "Loneliness", "foodstamp": "Received SNAP",
    "foodinsecu": "Food insecurity", "housinsecu": "Housing insecurity",
    "shututility": "Utility shut-off threat", "lacktrpt": "Lack of transportation",
    "emotionspt": "Lack of emotional support",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK, "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

# Chart 1: share of county-to-county variation reproduced by the model's inputs
r2 = pd.read_csv(f"{OUT}/r2_by_measure_crudeprev.csv")
bench = pd.read_csv(f"{OUT}/benchmark_uninsurance.csv").set_index("sample")
r2 = r2.sort_values("inputs_plus_state_cv")
names = [LABELS[m] for m in r2.measure]
vals = r2.inputs_plus_state_cv.values * 100
acs = bench.loc["all counties", "cv_r2_acs_direct"] * 100
places_unins = r2.set_index("measure").loc["access2", "inputs_plus_state_cv"] * 100

fig, ax = plt.subplots(figsize=(8.2, 11))
y = np.arange(len(names)) + 2
ax.hlines(y, 60, vals, color=GRID, lw=1, zorder=1)
ax.scatter(vals, y, s=46, color=BLUE, zorder=3, edgecolor=SURFACE, linewidth=1.5)
ax.hlines(0, 60, acs, color=GRID, lw=1, zorder=1)
ax.scatter([acs], [0], s=60, color=ORANGE, zorder=3, edgecolor=SURFACE, linewidth=1.5)
ax.set_yticks(list(y) + [0])
ax.set_yticklabels(names + ["Uninsured 19-64, measured\ndirectly (Census ACS)"])
ax.get_yticklabels()[-1].set_color(ORANGE)
ax.annotate(f"{acs:.0f}%", (acs, 0), xytext=(8, 0), textcoords="offset points", va="center", color=INK)
iu = list(r2.measure).index("access2")
ax.annotate(f"{places_unins:.0f}%", (places_unins, y[iu]), xytext=(8, 0), textcoords="offset points",
            va="center", color=INK)
ax.annotate(f"{vals[0]:.0f}%", (vals[0], y[0]), xytext=(8, 0), textcoords="offset points", va="center", color=INK)
ax.axhline(1, color=GRID, lw=0.8, ls=(0, (3, 3)))
ax.set_xlim(60, 101)
ax.set_ylim(-1, len(names) + 2.5)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax.grid(axis="x", color=GRID, lw=0.6)
ax.set_axisbelow(True)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.set_xlabel("Share of county-to-county variation reproduced by the inputs\n(10-fold cross-validated R²)")
fig.text(0.02, 0.985, "Almost every PLACES county map can be reconstructed from demographics and state", fontsize=14,
         weight="bold", color=INK, va="top")
fig.text(0.02, 0.962, "Each PLACES measure (blue) regressed on county age, sex, race/ethnicity, education, "
         "poverty and state.\nThe same inputs explain much less of a directly measured rate (orange).",
         fontsize=10, color=INK2, va="top")
fig.text(0.02, 0.012, "Sources: CDC PLACES 2025 county release (crude prevalence); Census ACS 2019-2023 5-year.\n"
         "2,299-3,143 counties per measure (Kentucky and Pennsylvania missing for most measures).", fontsize=8, color=INK2)
fig.subplots_adjust(left=0.36, right=0.95, top=0.915, bottom=0.095)
fig.savefig(f"{OUT}/chart1_r2_by_measure.png", dpi=180)

# Chart 2: diabetes vs food insecurity, before and after removing the inputs
import sys
sys.path.insert(0, "atlas/scripts")
places = pd.read_csv("data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places.countyfips.str.zfill(5)
acs_df = pd.read_csv("data/raw/acs_county_2023.csv", dtype={"fips": str})
df = places.merge(acs_df, on="fips").dropna(subset=["diabetes_adjprev", "foodinsecu_adjprev"]).reset_index(drop=True)
COMP = ["age_25_34", "age_35_44", "age_45_54", "age_55_64", "age_65_74", "age_75p", "male",
        "nh_black", "nh_aian", "nh_asian", "nh_nhpi", "nh_other_multi", "hispanic",
        "edu_lt_hs", "edu_some_college", "edu_ba_plus", "pov150_adults"]
X = pd.concat([pd.Series(1.0, index=df.index), df[COMP],
               pd.get_dummies(df.stateabbr, drop_first=True, dtype=float)], axis=1).values


def resid(col):
    yv = df[col].values
    b, *_ = np.linalg.lstsq(X, yv, rcond=None)
    return yv - X @ b


x_raw, y_raw = df.foodinsecu_adjprev.values, df.diabetes_adjprev.values
x_res, y_res = x_raw.mean() + resid("foodinsecu_adjprev"), y_raw.mean() + resid("diabetes_adjprev")
r_raw, r_res = np.corrcoef(x_raw, y_raw)[0, 1], np.corrcoef(x_res, y_res)[0, 1]
share = np.cov(x_res, y_res)[0, 1] / np.cov(x_raw, y_raw)[0, 1]

fig, axes = plt.subplots(1, 2, figsize=(10, 5.2), sharex=True, sharey=True)
for ax, xv, yv, title in [
    (axes[0], x_raw, y_raw, f"As published: r = {r_raw:.2f}"),
    (axes[1], x_res, y_res, "After removing county demographics and state\n(what is left, around the averages)"),
]:
    ax.scatter(xv, yv, s=9, color=BLUE, alpha=0.45, linewidth=0)
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.set_xlabel("Food insecurity, % of adults (age-adjusted)")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
axes[0].set_ylabel("Diabetes, % of adults (age-adjusted)")
axes[1].annotate(f"Left-over spread: SD {np.std(y_res):.1f} pts (diabetes),\n{np.std(x_res):.1f} pts (food insecurity); residual r = {r_res:.2f}",
                 (x_raw.mean(), y_raw.mean()), xytext=(x_raw.mean() + 4, y_raw.mean() + 6),
                 color=INK, fontsize=9.5, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
fig.text(0.02, 0.985, "Demographics and state reproduce almost all of the diabetes and food insecurity pattern",
         fontsize=13, weight="bold", color=INK, va="top")
fig.text(0.02, 0.012, f"CDC PLACES 2025, {len(df):,} counties in states that fielded the social-needs questions. Same axes in both panels.\n"
         "Inputs removed: county age, sex, race/ethnicity, education, adults below 150% of poverty, and state.",
         fontsize=8, color=INK2)
fig.subplots_adjust(left=0.08, right=0.98, top=0.83, bottom=0.17, wspace=0.08)
fig.savefig(f"{OUT}/chart2_diabetes_foodinsecurity.png", dpi=180)
print("r_raw", round(r_raw, 3), "r_res", round(r_res, 3), "share", round(share, 4), "n", len(df))
