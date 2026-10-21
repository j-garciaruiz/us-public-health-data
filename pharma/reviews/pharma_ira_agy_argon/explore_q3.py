import pandas as pd
import numpy as np

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv")
nadac25 = pd.read_csv("data/raw/pharma/nadac/nadac_2025.csv", dtype={"NDC": str})
nadac26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype={"NDC": str})

n25_last = nadac25[nadac25["As of Date"] == "12/31/2025"].copy()
n26_last = nadac26[nadac26["As of Date"] == "10/21/2026"].copy()

mfp26 = mfp[(mfp["IPAY"] == 2026) & (mfp["MFP Effective Date"] == "01/01/2026")].copy()

print("=== Check string-matching NDC Description vs NDC-11 join ===")
for d in sorted(mfp26["Selected Drug Name"].unique()):
    parts = [p.strip() for p in d.split(";")]
    first_word = parts[0].split()[0]
    
    # Match in n25_last by starting with first_word or any part
    m25_fw = n25_last[n25_last["NDC Description"].str.upper().str.startswith(first_word.upper(), na=False)]
    m26_fw = n26_last[n26_last["NDC Description"].str.upper().str.startswith(first_word.upper(), na=False)]
    
    m25_any = n25_last[n25_last["NDC Description"].str.upper().str.startswith(tuple(p.upper() for p in parts), na=False)]
    m26_any = n26_last[n26_last["NDC Description"].str.upper().str.startswith(tuple(p.upper() for p in parts), na=False)]
    
    d_mfp = mfp26[mfp26["Selected Drug Name"] == d]
    med_mfp = d_mfp["NDC-9 MFP per Unit Price"].median()
    
    r25_fw = m25_fw["NADAC Per Unit"].median() / med_mfp if len(m25_fw) else np.nan
    r26_fw = m26_fw["NADAC Per Unit"].median() / med_mfp if len(m26_fw) else np.nan
    r25_any = m25_any["NADAC Per Unit"].median() / med_mfp if len(m25_any) else np.nan
    r26_any = m26_any["NADAC Per Unit"].median() / med_mfp if len(m26_any) else np.nan
    
    print(f"{first_word:10s} | med_mfp={med_mfp:10.4f} | fw_n=({len(m25_fw):2d},{len(m26_fw):2d}) med_nadac=({m25_fw['NADAC Per Unit'].median() if len(m25_fw) else np.nan:10.4f},{m26_fw['NADAC Per Unit'].median() if len(m26_fw) else np.nan:10.4f}) ratio=({r25_fw:.4f},{r26_fw:.4f}) | any_n=({len(m25_any):2d},{len(m26_any):2d}) ratio=({r25_any:.4f},{r26_any:.4f})")
