import zipfile
import pandas as pd

with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/basic drugs formulary file  PPUF_2026Q3.zip") as z:
    with z.open(z.namelist()[0]) as f:
        form = pd.read_csv(f, sep="|", dtype=str)
form["NDC11"] = form["NDC"].str.zfill(11)

with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/plan information  PPUF_2026Q3.zip") as z:
    with z.open(z.namelist()[0]) as f:
        pinfo = pd.read_csv(f, sep="|", dtype=str, encoding="latin1")
pinfo["PLAN_KEY"] = pinfo["CONTRACT_ID"] + "|" + pinfo["PLAN_ID"] + "|" + pinfo["SEGMENT_ID"]
plans = pinfo.drop_duplicates("PLAN_KEY")

sel = form[form["SELECTED_DRUG_YN"] == "Y"].copy()
print("Unique NDCs with SELECTED_DRUG_YN == Y:", sel["NDC11"].nunique())
# Map NDC11 to drug family
mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
ndc_to_drug = mfp_df.drop_duplicates("NDC11").set_index("NDC11")["Selected Drug Name"].to_dict()
ndc_to_drug["00480352756"] = "FARXIGA (GENERIC PROXY)"
ndc_to_drug["00480352856"] = "FARXIGA (GENERIC PROXY)"
sel["DRUG"] = sel["NDC11"].map(ndc_to_drug)
print("Formulary count per drug in 2026Q3 (out of 328 formularies):")
print(sel.groupby("DRUG")["FORMULARY_ID"].nunique())

# Check what kind of plans use formularies that lack STELARA or JANUVIA
st_forms = set(sel[sel["DRUG"] == "STELARA"]["FORMULARY_ID"])
missing_st_plans = plans[~plans["FORMULARY_ID"].isin(st_forms)]
print("\nPlans missing STELARA in 2026Q3:", len(missing_st_plans))
print("By CONTRACT_ID prefix:", missing_st_plans["CONTRACT_ID"].str[0].value_counts().to_dict())
print("By SNP:", missing_st_plans["SNP"].value_counts().to_dict())
print("Top contract names missing STELARA:", missing_st_plans["CONTRACT_NAME"].value_counts().head(5).to_dict())
