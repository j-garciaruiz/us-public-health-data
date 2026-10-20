import pandas as pd
import numpy as np

# Load ira_analysis outputs
wac_grp = pd.read_csv("pharma/outputs/ira/wac_january_by_group.csv")
wac_ev = pd.read_csv("pharma/outputs/ira/wac_cut_events.csv")
nadac_mfp = pd.read_csv("pharma/outputs/ira/nadac_to_mfp_by_drug.csv")
partd_grp = pd.read_csv("pharma/outputs/ira/partd_per_claim_by_group.csv")
partd_drug = pd.read_csv("pharma/outputs/ira/partd_per_claim_by_drug.csv")

print("=== partd_per_claim_by_group.csv ===")
print(partd_grp.to_string(index=False))

print("\n=== partd_per_claim_by_drug.csv (IPAY 2026, 2027, 2028) ===")
print(partd_drug[partd_drug["group"] != "Other brands"].to_string(index=False))

# Check Other brands in partd_per_claim_by_drug.csv
oth = partd_drug[partd_drug["group"] == "Other brands"]
print(f"\nOther brands count in partd_drug: {len(oth)}")
print("Top 15 largest drops in Other brands:")
print(oth.sort_values("chg_per_claim").head(15).to_string(index=False))

# Check what was excluded from Other brands by `first_in_generic`, `SUPPLY`, and `selected_ingredient`
q = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv", dtype=str)
q = q[q.Mftr_Name == "Overall"].copy()
for c in ("Tot_Clms", "Tot_Spndng"):
    q[c] = pd.to_numeric(q[c], errors="coerce")
q["period"] = q.Year.map({"2025 (Q1-Q4)": "2025", "2026 (Q1)": "2026Q1"})
q["B"] = q.Brnd_Name.str.upper().str.strip()
q["G"] = q.Gnrc_Name.str.upper().str.strip()

# Pivot all rows with Clms_2025 >= 4000 and Clms_2026Q1 >= 1000
piv = q.pivot(index=["Brnd_Name", "Gnrc_Name", "B", "G"], columns="period", values=["Tot_Clms", "Tot_Spndng"])
piv.columns = [f"{a}_{b}" for a, b in piv.columns]
piv = piv.reset_index()
piv = piv[(piv.Tot_Clms_2025 >= 4000) & (piv.Tot_Clms_2026Q1 >= 1000)].copy()
piv["chg"] = (piv.Tot_Spndng_2026Q1 / piv.Tot_Clms_2026Q1) / (piv.Tot_Spndng_2025 / piv.Tot_Clms_2025) - 1

in_ira_other = set(oth["drug"])
in_ira_sel = set(partd_drug[partd_drug["group"] != "Other brands"]["drug"])

piv_b_ne_g = piv[piv.B != piv.G].copy()
print(f"\nTotal rows with B != G and >=4000/1000 claims: {len(piv_b_ne_g)}")
dropped = piv_b_ne_g[~piv_b_ne_g["Brnd_Name"].isin(in_ira_other)]
print(f"Rows with B != G not in ira_analysis 'Other brands': {len(dropped)}")
print(dropped[["Brnd_Name", "Gnrc_Name", "Tot_Clms_2025", "Tot_Clms_2026Q1", "chg"]].head(60).to_string(index=False))
