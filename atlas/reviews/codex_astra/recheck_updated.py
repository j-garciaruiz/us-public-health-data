"""Verify the concurrent Claude corrections, preserving the original review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd
from replicate import HERE, ROOT, FEATURES, design, fold_ids, r2

SNAP=HERE/"updated_source_snapshot"
paths=[ROOT/f"scripts/{s}" for s in ["fetch_acs_county.py","covariate_test.py","covariate_charts.py"]]
paths+=sorted((ROOT/"outputs/covariate_test").glob("*"))
hashes={}
for path in paths:
    if not path.is_file():
        continue
    rel=path.relative_to(ROOT)
    target=SNAP/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    b=path.read_bytes()
    target.write_bytes(b)
    hashes[str(rel)]=hashlib.sha256(b).hexdigest()
(HERE/"updated_source_hashes.json").write_text(json.dumps(
    dict(snapshot_utc=datetime.now(timezone.utc).isoformat(),files_sha256=hashes),indent=2))

d=pd.read_csv(HERE/"analysis_data.csv",dtype={"countyfips":str})
age=pd.read_csv(HERE/"B01001_county_estimates.csv",dtype={"countyfips":str}).set_index("countyfips")
d=d.assign(
    age_75p=d.countyfips.map(age[[f"B01001_E{i:03}" for i in [23,24,25,47,48,49]]].sum(axis=1))/d.adult_population,
    race_other_multi=d.race_other+d.race_multi,
)
features=[c for c in FEATURES if c not in ["race_other","race_multi"]]+["race_other_multi","age_75p"]


def calculate(sub,cols):
    x,ns=design(sub,features)
    y=sub[cols].to_numpy(float)
    q,_=np.linalg.qr(x,mode="reduced")
    fit=q@(q.T@y)
    pred=np.empty_like(y)
    ids=fold_ids(len(y),0)
    for k in range(10):
        tr=ids!=k
        b=np.linalg.lstsq(x[tr],y[tr],rcond=None)[0]
        out=x[~tr]@b
        bad=x[~tr,:ns][:,x[tr,:ns].sum(0)==0].sum(1)>0
        if bad.any():
            out[bad]+=np.average(b[:ns],axis=0,weights=x[tr,:ns].sum(0))
        pred[~tr]=out
    return r2(y,fit),r2(y,pred),y-fit


checks, differences, headline = [], [], []
own=pd.read_csv(HERE/"measure_r2.csv").set_index("measure")
ownp=pd.read_csv(HERE/"pair_correlations.csv")
att=pd.read_csv(HERE/"pair_disagreement_attribution.csv")
def check(file,key,metric,expected,actual):
    delta=expected-actual
    checks.append(dict(file=file,key=key,metric=metric,expected=expected,saved=actual,delta=delta))
    assert abs(delta)<=.0005000001,(file,key,metric,expected,actual)
def diff(file,key,metric,independent,current,cause):
    if abs(independent-current)>.0005000001:
        differences.append(dict(file=file,key=key,metric=metric,independent=independent,
                                claude_updated=current,delta=independent-current,cause=cause))
for kind in ["adjprev","crudeprev"]:
    oldr=pd.read_csv(HERE/f"claude_reproduced_r2_{kind}.csv").set_index("measure")
    curr=pd.read_csv(SNAP/f"outputs/covariate_test/r2_by_measure_{kind}.csv").set_index("measure")
    results={}
    for n in oldr.n_counties.unique():
        ms=oldr.index[oldr.n_counties==n].tolist()
        cols=[m+"_"+kind for m in ms]
        sub=d[d[cols[0]].notna()]
        ins,cv,e=calculate(sub,cols)
        for j,m in enumerate(ms):
            results[m]=cv[j]
            for metric in curr.columns:
                expect=cv[j] if metric=="inputs_plus_state_cv" else (
                    ins[j] if metric=="inputs_plus_state" else oldr.loc[m,metric])
                check(f"r2_by_measure_{kind}.csv",m,metric,expect,curr.loc[m,metric])
            for om,cm in [("r2_in_sample","inputs_plus_state"),("r2_cv_pooled","inputs_plus_state_cv")]:
                diff(f"r2_by_measure_{kind}.csv",m,cm,own.loc[m+"_"+kind,om],curr.loc[m,cm],
                     "Age/race grouping"+("; CV seed" if om=="r2_cv_pooled" else ""))
    cp=pd.read_csv(SNAP/f"outputs/covariate_test/pairs_{kind}.csv")
    cp["key"]=cp.apply(lambda r:"|".join(sorted([r.a,r.b])),axis=1)
    cp=cp.set_index("key")
    a=att[att.kind==kind].set_index("pair")
    for key,r in cp.iterrows():
        ours=ownp[(ownp.kind==kind)&ownp.apply(lambda q:"|".join(sorted([q.measure_a,q.measure_b]))==key,axis=1)].iloc[0]
        for metric,matched in [("raw_r","raw_r"),("partial_r","common_sample_partial"),
                               ("cov_share_remaining","common_sample_share"),("n","n")]:
            check(f"pairs_{kind}.csv",key,metric,a.loc[key,matched],r[metric])
            ourmetric="covariance_share_remaining" if metric=="cov_share_remaining" else metric
            diff(f"pairs_{kind}.csv",key,metric,ours[ourmetric],r[metric],"Age/race grouping")
    strong=a[a.raw_r.abs()>=.7]
    headline.append(dict(kind=kind,updated_cv_median=float(np.median(list(results.values()))),
                          updated_strong_covariance_share_median=strong.common_sample_share.median(),
                          updated_strong_partial_count=int((strong.common_sample_partial.abs()>=.7).sum()),
                          updated_partial_abs_median=a.common_sample_partial.abs().median()))

cb=pd.read_csv(SNAP/"outputs/covariate_test/benchmark_uninsurance.csv").set_index("sample")
ownb=pd.read_csv(HERE/"benchmark.csv")
newb=[]
for threshold,label in [(0,"all counties"),(20000,">=20k adults")]:
    sub=d[(d.adult_population>=threshold)&d.access2_crudeprev.notna()]
    cols=["access2_crudeprev","acs_uninsured_19_64"]
    ins,cv,e=calculate(sub,cols)
    vals=dict(n=len(sub),raw_r=np.corrcoef(sub[cols].to_numpy().T)[0,1],
              partial_r=np.corrcoef(e.T)[0,1],r2_places_on_inputs=ins[0],
              r2_acs_direct_on_inputs=ins[1],cv_r2_places=cv[0],cv_r2_acs_direct=cv[1])
    newb.append(dict(sample=label,**vals))
    mapping={"n":"n","raw_r":"raw_r","partial_r":"partial_r",
             "r2_places_on_inputs":"access2_crudeprev_r2_in_sample",
             "r2_acs_direct_on_inputs":"acs_uninsured_19_64_r2_in_sample",
             "cv_r2_places":"access2_crudeprev_r2_cv_pooled",
             "cv_r2_acs_direct":"acs_uninsured_19_64_r2_cv_pooled"}
    oo=ownb[ownb.adult_threshold==threshold].iloc[0]
    for metric,val in vals.items():
        check("benchmark_uninsurance.csv",label,metric,val,cb.loc[label,metric])
        diff("benchmark_uninsurance.csv",label,metric,oo[mapping[metric]],cb.loc[label,metric],
             "Age/race grouping"+("; CV seed" if metric.startswith("cv_") else ""))

# Add alternative-model, highlighted and summary-view discrepancies so this
# current-version ledger is complete in the same sense as the original ledger.
supp=pd.read_csv(HERE/"supplemental_numeric_disagreements.csv")
for _,r in supp.iterrows():
    differences.append(dict(file=r.file,key=r.key,metric=r.metric,independent=r.independent,
                            claude_updated=r.claude,delta=r.delta,cause=r.cause))
hl=pd.read_csv(SNAP/"outputs/covariate_test/highlight_pairs_adjprev.csv")
for _,r in hl.iterrows():
    a,b=r["pair"].split(" ~ ")
    op=ownp[(ownp.kind=="adjprev")&
            ownp.apply(lambda q:{q.measure_a,q.measure_b}=={a,b},axis=1)].iloc[0]
    for metric,om in [("n","n"),("raw_r","raw_r"),("partial_r","partial_r"),
                      ("cov_share_remaining","covariance_share_remaining")]:
        diff("highlight_pairs_adjprev.csv",r["pair"],metric,op[om],r[metric],
             "Duplicate of corresponding age/race grouping difference")
for kind in ["adjprev","crudeprev"]:
    op=ownp[ownp.kind==kind]
    cr=pd.read_csv(SNAP/f"outputs/covariate_test/r2_by_measure_{kind}.csv")
    cp=pd.read_csv(SNAP/f"outputs/covariate_test/pairs_{kind}.csv")
    # For summary thresholds and medians, use full-precision corrected values.
    aa=att[att.kind==kind]
    hh=next(h for h in headline if h["kind"]==kind)
    vals={
        "sign_flips":(int((op.raw_r*op.partial_r<0).sum()),
                      int((aa.raw_r*aa.common_sample_partial<0).sum()),0),
        "strong_remaining_count":(int(((op.raw_r.abs()>=.7)&(op.partial_r.abs()>=.7)).sum()),
                                  hh["updated_strong_partial_count"],0),
        "strong_share_median":(op.loc[op.raw_r.abs()>=.7,"covariance_share_remaining"].median(),
                               round(hh["updated_strong_covariance_share_median"],3),3),
        "strong_share_max":(op.loc[op.raw_r.abs()>=.7,"covariance_share_remaining"].max(),
                            round(aa.loc[aa.raw_r.abs()>=.7,"common_sample_share"].max(),3),3),
        "cv_min":(own.loc[own.index.str.endswith("_"+kind),"r2_cv_pooled"].min(),
                   cr.inputs_plus_state_cv.min(),3)
    }
    for metric,(ours,current,decimals) in vals.items():
        if abs(ours-current)>(0 if decimals==0 else .0005000001):
            differences.append(dict(file="summary.txt",key=kind,metric=metric,independent=ours,
                                    claude_updated=current,delta=ours-current,
                                    cause="Aggregate of age/race grouping and CV seed differences"))
pd.DataFrame(checks).to_csv(HERE/"updated_output_checks.csv",index=False)
pd.DataFrame(differences).to_csv(HERE/"updated_numeric_disagreements.csv",index=False)
pd.DataFrame(headline).to_csv(HERE/"updated_headline_comparison.csv",index=False)
pd.DataFrame(newb).to_csv(HERE/"updated_benchmark.csv",index=False)
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in hashes.items())
print("Updated source checked:",len(checks),"numeric cells; max rounding error",
      max(abs(r["delta"]) for r in checks))
print(pd.DataFrame(headline).to_string(index=False))
print(pd.DataFrame(newb).to_string(index=False))
print("Updated numerical differences:",len(differences))
