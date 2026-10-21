import zipfile
import pandas as pd

with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/plan information  PPUF_2026Q3.zip") as z:
    with z.open(z.namelist()[0]) as f:
        pinfo = pd.read_csv(f, sep="|", dtype=str, encoding="latin1")
pinfo["PLAN_KEY"] = pinfo["CONTRACT_ID"] + "|" + pinfo["PLAN_ID"] + "|" + pinfo["SEGMENT_ID"]
plans_26q3 = pinfo[["PLAN_KEY", "CONTRACT_ID", "PLAN_ID", "SEGMENT_ID", "FORMULARY_ID", "PLAN_NAME", "SNP"]].drop_duplicates("PLAN_KEY")
print("Unique plans in plan info 2026Q3:", len(plans_26q3))

with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/basic drugs formulary file  PPUF_2026Q3.zip") as z:
    with z.open(z.namelist()[0]) as f:
        form = pd.read_csv(f, sep="|", dtype=str, encoding="latin1")
form["NDC11"] = form["NDC"].str.zfill(11)
print("Unique formularies in basic drugs formulary file 2026Q3:", form["FORMULARY_ID"].nunique())

df30 = pd.read_pickle("/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch/spuf_matched_30d.pkl")
p26q3 = df30[df30["RELEASE"] == "2026Q3"].copy()
p26q3["PLAN_KEY"] = p26q3["CONTRACT_ID"] + "|" + p26q3["PLAN_ID"] + "|" + p26q3["SEGMENT_ID"]

for name, ndc_prefix in [("FARXIGA", "0031062"), ("JANUVIA", "000060277"), ("STELARA", "57894006"), ("STELARA_UNB", "57894044"), ("ELIQUIS", "000030894"), ("POMALYST", "59572050"), ("OFEV", "00597014")]:
    f_ndcs = form[form["NDC11"].str.startswith(ndc_prefix)]
    f_ids = set(f_ndcs["FORMULARY_ID"].unique())
    plans_with_form = plans_26q3[plans_26q3["FORMULARY_ID"].isin(f_ids)]
    plans_in_pricing = p26q3[p26q3["NDC"].str.startswith(ndc_prefix)]["PLAN_KEY"].nunique()
    print(f"{name} ({ndc_prefix}*): in {len(f_ids)}/{form['FORMULARY_ID'].nunique()} formularies -> {len(plans_with_form)} plans in plan_info, {plans_in_pricing} plans in pricing_file (30d)")
