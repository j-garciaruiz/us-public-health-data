"""Post-freeze sensitivity tests and independent matched-specification checks."""
import ast
import json
import numpy as np
import pandas as pd
from replicate import HERE, ROOT, FEATURES, design, fold_ids, r2

d = pd.read_csv(HERE / "analysis_data.csv", dtype={"countyfips": str}).copy()
age = pd.read_csv(HERE / "B01001_county_estimates.csv", dtype={"countyfips": str}).set_index("countyfips")
d["age_75p"] = d.countyfips.map(age[[f"B01001_E{i:03}" for i in [23,24,25,47,48,49]]].sum(axis=1)) / d.adult_population
d["race_other_multi"] = d.race_other + d.race_multi
claude_features = [c for c in FEATURES if c not in ["race_other","race_multi"]] + ["race_other_multi","age_75p"]
expanded_features = FEATURES + ["age_75p"]
joint_features = [c for c in FEATURES if not c.startswith("age_") and c != "female_adult"] + [
    f"{sex}_age_{band}" for sex in ["male","female"] for band in ["18_24","25_34","35_44","45_54","55_64","65_plus"]
    if (sex,band) != ("female","65_plus")]
detailed_names = [f"sex_age_cell_{i:03}" for i in list(range(7,26))+list(range(31,50))]
detailed = {
    name: d.countyfips.map(age[f"B01001_E{int(name[-3:]):03}"]) / d.adult_population
    for name in detailed_names
}
d = pd.concat([d,pd.DataFrame(detailed)],axis=1).copy()
detailed_features = [c for c in FEATURES if not c.startswith("age_") and c != "female_adult"] + detailed_names[:-1]
for c in FEATURES:
    d[c+"_sq"] = d[c]**2
# Align the flexible comparison to Claude's educational reference category:
# unlike linear OLS, dropping a different compositional category before squaring
# changes the nonlinear function space.
flex_base = [c for c in FEATURES if c != "edu_hs"] + ["edu_ba_plus"]
for c in flex_base:
    d[c+"_sq"] = d[c]**2
products = []
for c in ["edu_less_hs","edu_ba_plus","race_black","race_hispanic","race_aian"]:
    name=c+"_x_poverty"
    d[name] = d[c]*d.poverty150_adult
    products.append(name)
flex_features = flex_base + [c+"_sq" for c in flex_base] + products
models = {
    "state_only": ([],True,False),
    "inputs_only": (FEATURES,False,False),
    "primary": (FEATURES,True,False),
    "claude_spec_independent": (claude_features,True,False),
    "expanded_age_and_race": (expanded_features,True,False),
    "age_sex_joint": (joint_features,True,False),
    "detailed_age_sex": (detailed_features,True,False),
    "flexible": (flex_features,True,False),
    "logit_outcome": (FEATURES,True,True),
}


def fit_predict(x,y,ns,logit=False,seed=20261020):
    target = np.log(np.clip(y/100,1e-6,1-1e-6)/(1-np.clip(y/100,1e-6,1-1e-6))) if logit else y
    inverse = (lambda z: 100/(1+np.exp(-np.clip(z,-40,40)))) if logit else (lambda z:z)
    b, _, rank, _ = np.linalg.lstsq(x,target,rcond=None)
    fitted = inverse(x@b)
    oof = np.empty_like(y)
    for k in range(10):
        tr = fold_ids(len(y),seed) != k
        b = np.linalg.lstsq(x[tr],target[tr],rcond=None)[0]
        pred = x[~tr]@b
        bad = x[~tr,:ns][:,x[tr,:ns].sum(0)==0].sum(1)>0
        if np.any(bad):
            pred[bad] += np.average(b[:ns],axis=0,weights=x[tr,:ns].sum(0))
        oof[~tr] = inverse(pred)
    return r2(y,fitted),r2(y,oof),int(rank),fitted,oof


ms = sorted(c for c in d if c.endswith(("_adjprev","_crudeprev")))
patterns = {}
for m in ms:
    mask=d[m].notna()
    patterns.setdefault(mask.to_numpy().tobytes(),(mask,[]))[1].append(m)
out,matched = [],[]
for name,(features,state,logit) in models.items():
    for mask,cols in patterns.values():
        sub=d.loc[mask].reset_index(drop=True)
        x,ns=design(sub,features,state)
        ins,cv,rank,fit,oof=fit_predict(x,sub[cols].to_numpy(float),ns,logit)
        for j,m in enumerate(cols):
            out.append(dict(model=name,measure=m,n=len(sub),rank=rank,r2_in_sample=ins[j],r2_cv=cv[j]))
            if name=="claude_spec_independent":
                kind="adjprev" if m.endswith("_adjprev") else "crudeprev"
                orig=pd.read_csv(HERE/f"claude_reproduced_r2_{kind}.csv").set_index("measure")
                value=orig.loc[m.removesuffix("_"+kind),"inputs_plus_state"]
                matched.append(dict(measure=m,difference=ins[j]-value))
pd.DataFrame(out).to_csv(HERE/"sensitivity_r2.csv",index=False)
pd.DataFrame(matched).to_csv(HERE/"matched_spec_independent_checks.csv",index=False)
assert max(abs(r["difference"]) for r in matched)<1e-10

# Benchmark on richer composition and logit scale, always common samples.
br=[]
for threshold in [0,20000]:
    sub=d[(d.adult_population>=threshold)&d.access2_crudeprev.notna()].reset_index(drop=True)
    for name in ["primary","expanded_age_and_race","age_sex_joint","detailed_age_sex","flexible","logit_outcome"]:
        features,state,logit=models[name]; x,ns=design(sub,features,state)
        cols=["access2_crudeprev","acs_uninsured_19_64"]
        ins,cv,rank,fit,oof=fit_predict(x,sub[cols].to_numpy(float),ns,logit)
        for j,m in enumerate(cols):
            br.append(dict(threshold=threshold,model=name,measure=m,r2_in_sample=ins[j],r2_cv=cv[j]))
pd.DataFrame(br).to_csv(HERE/"sensitivity_benchmark.csv",index=False)

# Isolate the singleton-state CV issue using the original column coding, order,
# seed and covariates, changing only the held-out DC prediction.
source=ast.parse((ROOT/"scripts/covariate_test.py").read_text())
nodes=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=="design"
       or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="COMPOSITION" for t in n.targets)]
p=pd.read_csv(ROOT/"data/raw/places_county_2025.csv",dtype={"countyfips":str})
p["fips"]=p.countyfips.str.zfill(5)
a=pd.read_csv(ROOT/"data/raw/acs_county_2023.csv",dtype={"fips":str})
cd=p.merge(a,on="fips",how="inner")
env=dict(pd=pd,np=np,df=cd,states=pd.get_dummies(cd.stateabbr,prefix="st",drop_first=True,dtype=float))
exec(compile(ast.Module(body=nodes,type_ignores=[]),"claude_design_readonly","exec"),env)
dcrows=[]
for m in ms:
    sub=cd[cd[m].notna()]
    xx=env["design"](sub.index)
    x=xx.to_numpy(float); y=sub[m].to_numpy(float)
    pred=np.empty_like(y); pred_fixed=np.empty_like(y)
    ids=fold_ids(len(y),0)
    for k in range(10):
        tr=ids!=k; te=~tr
        b=np.linalg.lstsq(x[tr],y[tr],rcond=None)[0]
        v=x[te]@b
        pred[te]=v
        bad=sub.loc[te,"stateabbr"].to_numpy()=="DC"
        if bad.any():
            statecols=xx.columns.str.startswith("st_")
            # DC column has no nonzero training values; its coefficient is zero.
            mean_state_effect=np.mean(x[tr][:,statecols]@b[statecols])
            v[bad]+=mean_state_effect
        pred_fixed[te]=v
    dc=sub.stateabbr.to_numpy()=="DC"
    dcrows.append(dict(measure=m,original_cv=r2(y,pred),fallback_cv=r2(y,pred_fixed),
                       cv_scored_without_dc=r2(y[~dc],pred[~dc]),
                       dc_observed=float(y[dc][0]),dc_original_prediction=float(pred[dc][0]),
                       dc_fallback_prediction=float(pred_fixed[dc][0]),
                       fallback_cv_change=float(r2(y,pred_fixed)-r2(y,pred))))
pd.DataFrame(dcrows).to_csv(HERE/"singleton_state_cv_audit.csv",index=False)

# Record supplemental differences for the other original R2 specifications.
extra=[]
ss=pd.DataFrame(out)
for kind in ["adjprev","crudeprev"]:
    orig=pd.read_csv(ROOT/f"outputs/covariate_test/r2_by_measure_{kind}.csv").set_index("measure")
    for name,col in [("state_only","state_only"),("inputs_only","inputs_only"),("flexible","flexible_plus_state")]:
        for _,r in ss[(ss.model==name)&ss.measure.str.endswith("_"+kind)].iterrows():
            m=r.measure.removesuffix("_"+kind)
            delta=r.r2_in_sample-orig.loc[m,col]
            if abs(delta)>.0005000001:
                extra.append(dict(file=f"r2_by_measure_{kind}.csv",key=m,metric=col,
                                  independent=r.r2_in_sample,claude=orig.loc[m,col],delta=delta,
                                  cause="Age/race grouping and nonlinear feature space" if name=="flexible" else "Age/race grouping"))
pd.DataFrame(extra).to_csv(HERE/"supplemental_numeric_disagreements.csv",index=False)
print(ss.groupby(["model",ss.measure.str.endswith("_adjprev")])[["r2_in_sample","r2_cv"]].median().to_string())
print("Supplemental differences:",len(extra))
print(pd.DataFrame(dcrows).sort_values("fallback_cv_change",ascending=False).head(5).to_string(index=False))
