import zipfile
import pandas as pd

print("=== 1. selected_drugs_mfp.csv ===")
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
print(mfp.columns.tolist())
print(mfp.groupby(["IPAY", "Selected Drug Name", "MFP Effective Date", "MFP End Date", "Type of Update"], dropna=False).size())

print("\n=== 2. SPUF zip contents ===")
for label in ["2025Q3", "2026Q3"]:
    zpath = f"data/raw/pharma/spuf/{label}/pricing file PPUF_{label}.zip"
    with zipfile.ZipFile(zpath) as zf:
        print(label, zf.namelist())
        for name in zf.namelist():
            if name.endswith(".txt") or name.endswith(".csv"):
                with zf.open(name) as f:
                    for _ in range(5):
                        print("  ", f.readline().decode("utf-8", errors="replace").strip())

print("\n=== 3. partd_spending_quarterly.csv ===")
partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv", dtype=str)
print("Years:", partd["Year"].unique())
overall = partd[partd["Mftr_Name"] == "Overall"]
print("Sample brands matching selected drugs:")
for kw in ["ELIQUIS", "ENBREL", "ENTRESTO", "FARXIGA", "IMBRUVICA", "JANUVIA", "JARDIANCE", "NOVOLOG", "FIASP", "STELARA", "XARELTO",
           "AUSTEDO", "BREO", "CALQUENCE", "IBRANCE", "JANUMET", "LINZESS", "OFEV", "OTEZLA", "OZEMPIC", "RYBELSUS", "WEGOVY", "POMALYST", "TRADJENTA", "TRELEGY", "VRAYLAR", "XIFAXAN", "XTANDI"]:
    matches = overall[overall["Brnd_Name"].str.upper().str.contains(kw, na=False)]["Brnd_Name"].unique()
    print(f"  {kw}: {matches}")

print("\n=== 4. nadac_2026.csv & nadac_comparison.csv headers ===")
nadac_head = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", nrows=5, dtype=str)
print("nadac_2026 columns:", nadac_head.columns.tolist())
print(nadac_head)

comp_head = pd.read_csv("data/raw/pharma/nadac/nadac_comparison.csv", nrows=5, dtype=str)
print("nadac_comparison columns:", comp_head.columns.tolist())
print(comp_head)
