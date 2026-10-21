import pandas as pd
import numpy as np

partd_a = pd.read_csv("data/raw/pharma/partd/partd_spending_annual.csv")
ov_a = partd_a[partd_a["Mftr_Name"] == "Overall"].copy()

for kw in ["Eliquis", "Enbrel", "Entresto", "Farxiga", "Imbruvica", "Januvia", "Jardiance", "Novolog", "Fiasp", "Stelara", "Xarelto"]:
    m = ov_a[ov_a["Brnd_Name"].str.contains(kw, case=False, na=False)]
    print(m[["Brnd_Name", "Gnrc_Name", "Tot_Spndng_2024", "Tot_Dsg_Unts_2024", "Tot_Clms_2024", "Avg_Spnd_Per_Dsg_Unt_Wghtd_2024", "Avg_Spnd_Per_Clm_2024"]].to_string())
