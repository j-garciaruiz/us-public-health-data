import pandas as pd

kws_26 = ["ELIQUIS", "ENBREL", "ENTRESTO", "FARXIGA", "IMBRUVICA", "JANUVIA", "JARDIANCE", "NOVOLOG", "FIASP", "STELARA", "XARELTO",
          "APIXABAN", "ETANERCEPT", "SACUBITRIL", "DAPAGLIFLOZIN", "IBRUTINIB", "SITAGLIPTIN", "EMPAGLIFLOZIN", "INSULIN ASPART", "USTEKINUMAB", "RIVAROXABAN"]
kws_27 = ["AUSTEDO", "BREO", "CALQUENCE", "IBRANCE", "JANUMET", "LINZESS", "OFEV", "OTEZLA", "OZEMPIC", "RYBELSUS", "WEGOVY", "POMALYST", "TRADJENTA", "TRELEGY", "VRAYLAR", "XIFAXAN", "XTANDI",
          "DEUTETRABENAZINE", "VILANTEROL", "ACALABRUTINIB", "PALBOCICLIB", "LINACLOTIDE", "NINTEDANIB", "APREMILAST", "SEMAGLUTIDE", "POMALIDOMIDE", "LINAGLIPTIN", "CARIPRAZINE", "RIFAXIMIN", "ENZALUTAMIDE"]

pattern = "|".join(kws_26 + kws_27)
chunks = []
for chunk in pd.read_csv("data/raw/pharma/nadac/nadac_comparison.csv", dtype=str, chunksize=200000):
    sub = chunk[chunk["NDC Description"].str.upper().str.contains(pattern, na=False)].copy()
    if len(sub):
        chunks.append(sub)
df = pd.concat(chunks, ignore_index=True)
df["eff_dt"] = pd.to_datetime(df["Effective Date"])
df["pct_chg"] = pd.to_numeric(df["Percent Change"])
df24 = df[df["eff_dt"] >= "2024-01-01"].copy()

print("=== All WAC Adjustments or large cuts (<= -10%) since 2024 by NDC Description ===")
sub = df24[(df24["Primary Reason"] == "WAC Adjustment") | (df24["pct_chg"] <= -10.0)].copy()
for (desc, eff, reason, cls), grp in sub.groupby(["NDC Description", "Effective Date", "Primary Reason", "Classification for Rate Setting"]):
    if grp["pct_chg"].min() < 0:
        print(f"  {eff} | {desc:40s} | class={cls} | reason={reason:15s} | n={len(grp):2d} | min={grp['pct_chg'].min():+.2f}% | max={grp['pct_chg'].max():+.2f}% | NDCs={grp['NDC'].unique().tolist()}")
