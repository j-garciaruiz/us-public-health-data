import pandas as pd

partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
ov = partd[partd["Mftr_Name"] == "Overall"].copy()
for b in ["Ozempic", "Rybelsus", "Wegovy"]:
    s25 = ov[(ov["Brnd_Name"] == b) & (ov["Year"] == "2025 (Q1-Q4)")]
    s26 = ov[(ov["Brnd_Name"] == b) & (ov["Year"] == "2026 (Q1)")]
    c25, sp25 = s25["Tot_Clms"].sum(), s25["Tot_Spndng"].sum()
    c26, sp26 = s26["Tot_Clms"].sum(), s26["Tot_Spndng"].sum()
    print(f"{b:10s}: 2025 clms={c25:10,.0f}, spc=${sp25/c25:8,.2f} | 2026Q1 clms={c26:10,.0f} ({c26/3358770*100:5.2f}%), spnd=${sp26:13,.0f} ({sp26/4761090328*100:5.2f}%), spc=${sp26/c26:8,.2f}")
