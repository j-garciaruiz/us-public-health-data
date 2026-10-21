"""Coverage and reliability audit of supplied files; no source mutations."""
import json
import pandas as pd
from replicate import HERE, ROOT, FEATURES, load

base,m=load()
rows=[]
for row in m.dropna(subset=["places_measure"])[["condition","places_measure"]].drop_duplicates().itertuples(index=False):
    obs=m[(m.condition==row.condition)&(m.fltr==2)][["fips","rate"]]
    d=base.merge(obs,on="fips",how="left",validate="one_to_one")
    xok=d[FEATURES+["ma_share"]].notna().all(axis=1)
    usable=xok & d.rate.gt(0)
    pair=usable & d[f"{row.places_measure}_adjprev"].notna()
    omitted=d[usable&~pair]
    rows.append(dict(condition=row.condition,source="Medicare",
        atlas_possible_on_places_geographies=int(usable.sum()),pair_n=int(pair.sum()),
        lost_solely_places=int((usable&~pair).sum()),
        omitted_states=",".join(sorted(omitted.stateabbr.unique())),
        unavailable_mmd=int(d.rate.isna().sum()),ambiguous_zero=int(d.rate.eq(0).sum()),
        missing_ma_share=int(d.ma_share.isna().sum())))
for measure in ["hearing","vision","cognition","mobility","selfcare","indeplive"]:
    usable=base[FEATURES+[f"acs_{measure}"]].notna().all(axis=1)
    pair=usable&base[f"{measure}_crudeprev"].notna()
    rows.append(dict(condition=measure,source="ACS",
        atlas_possible_on_places_geographies=int(usable.sum()),pair_n=int(pair.sum()),
        lost_solely_places=int((usable&~pair).sum()),
        omitted_states=",".join(sorted(base.loc[usable&~pair,"stateabbr"].unique()))))
pd.DataFrame(rows).to_csv(HERE/"coverage_audit.csv",index=False)
cat=pd.read_csv(HERE/"cms_denominator_categories.csv",dtype={"fips":str})
check=cat[(cat.fltr==2)&(cat.condition_name=="hypertension")].merge(base[["fips","BENES_OM_CNT","ma_share","bphigh_adjprev"]],on="fips")
small=check[(check.BENES_OM_CNT>=5000)&(check.dencat<4)&check.ma_share.notna()&check.bphigh_adjprev.notna()&check.rate.gt(0)]
small.to_csv(HERE/"large_panel_denominator_flags.csv",index=False)
print(pd.DataFrame(rows).to_string(index=False))
print("Larger hypertension panel with MMD denominator below5000",len(small))
print("CMS missing in PLACES",len(set(base.fips)-set(m.fips)))
print(base.loc[~base.fips.isin(m.fips),["fips","stateabbr","countyname"]].to_string(index=False))

gv=pd.read_csv(ROOT/"data/raw/medicare_gv_county_2023.csv",dtype={"fips":str})
gvl=pd.read_csv(HERE/"gv_county_counts_live.csv",dtype=str)
gvc=gv[["fips","BENES_OM_CNT","BENES_MA_CNT"]].merge(gvl,left_on="fips",right_on="BENE_GEO_CD",validate="one_to_one",suffixes=("_file","_live"))
counts={c:int((gvc[c+"_file"].astype(str)!=gvc[c+"_live"].astype(str)).sum()) for c in ["BENES_OM_CNT","BENES_MA_CNT"]}
assert all(n==0 for n in counts.values())
(HERE/"gv_verification.json").write_text(json.dumps(dict(rows=len(gvc),mismatches=counts),indent=2))
