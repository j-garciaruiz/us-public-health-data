"""Part B comparisons; only run after replication.md has been saved."""
from pathlib import Path
import pandas as pd
import numpy as np
import json,hashlib
O=Path(__file__).resolve().parent
R=O.parent.parent
assert (O/'replication.md').exists()
A=R/'pharma/outputs/spuf'
labels={'2025 (Oct 2025 release)':'2025Q3','2026 (Jan 2026 release)':'2025Q4','2026 (Oct 2026 release)':'2026Q3'}
ren={'plan_ndc_rows':'rows','median_ratio':'median','share_at_mfp':'within_pct','share_below_mfp':'below_pct','share_above_mfp':'above_pct'}
checks=[]
for ours,theirs,keys in [('groups','ratio_by_group',['IPAY','release']),('drugs','ratio_by_drug',['IPAY','drug','release']),('plan_types','ratio_by_plan_type_ipay2026',['type','release'])]:
 x=pd.read_csv(O/(ours+'.csv'))
 y=pd.read_csv(A/(theirs+'.csv')).rename(columns=ren)
 y['release']=y.snapshot.map(labels)
 if 'drug' in x:x.drug=x.drug.str.split(';').str[0].str.strip()
 if 'plan_type' in y:y['type']=y.plan_type.map({'Medicare Advantage':'MA','Stand-alone PDP':'PDP'})
 for c in ['within_pct','below_pct','above_pct']:y[c]*=100
 j=x.merge(y,on=keys,how='outer',validate='one_to_one',suffixes=('_rep','_author'),indicator=True)
 assert (j._merge=='both').all()
 for c in ['rows','plans','ndcs','median','p05','p95','within_pct','below_pct','above_pct']:
  diff=np.abs(j[c+'_rep']-j[c+'_author'])
  checks.append(dict(table=ours,metric=c,cells=len(j),max_absolute_difference=float(diff.max()),disagreements_gt_1e_10=int((diff>1e-10).sum())))
checks=pd.DataFrame(checks)
checks.to_csv(O/'numeric_comparison.csv',index=False)
x=pd.read_csv(O/'matched_rows.csv.gz',dtype={'IPAY':str,'NDC':str,'PLAN_ID':str,'SEGMENT_ID':str})
y=pd.read_csv(A/'plan_prices_selected_ndcs.csv.gz',dtype={'IPAY':str,'NDC':str,'PLAN_ID':str,'SEGMENT_ID':str})
y['release']=y.snapshot.map(labels)
j=x.merge(y,on=['release','plan','NDC'],suffixes=('_rep','_author'),how='outer',indicator=True,validate='one_to_one')
rowcheck={'rows':len(j),'missing_from_either_side':int((j._merge!='both').sum()),'max_cost_difference':float(abs(j.UNIT_COST-j.unit_cost).max()),'max_mfp_difference':float(abs(j.mfp-j.mfp_ref).max()),'max_ratio_difference':float(abs(j.ratio_rep-j.ratio_author).max())}
assert rowcheck['missing_from_either_side']==0
assert rowcheck['max_ratio_difference']<1e-10
(O/'row_comparison.json').write_text(json.dumps(rowcheck,indent=2)+'\n')
# Verify every above-threshold row count and ratio, not just the largest NDC.
a=x[(x.IPAY=='2026')&(x.release!='2025Q3')&(x.ratio>1.005)].groupby(['release','NDC']).agg(rows=('ratio','size'),median_ratio=('ratio','median'),max_ratio=('ratio','max')).reset_index()
b=pd.read_csv(A/'above_mfp_2026.csv',dtype={'NDC':str});b['release']=b.snapshot.map(labels)
j=a.merge(b,on=['release','NDC'],suffixes=('_rep','_author'),validate='one_to_one',how='outer',indicator=True)
assert (j._merge=='both').all()
for c in ['rows','median_ratio','max_ratio']:assert np.allclose(j[c+'_rep'],j[c+'_author'],atol=1e-10,rtol=0)
# Frozen common-plan-NDC panel: descriptive robustness, not a causal design.
keys=x.groupby(['plan','NDC']).release.nunique();keys=keys[keys==3].reset_index()[['plan','NDC']]
panel=x.merge(keys,on=['plan','NDC'],validate='many_to_one')
ps=[]
for (label,ipay),g in panel.groupby(['release','IPAY']):
 ps.append(dict(release=label,IPAY=ipay,rows=len(g),plans=g.plan.nunique(),ndcs=g.NDC.nunique(),median=g.ratio.median(),within_pct=100*g.ratio.between(.995,1.005).mean(),above_pct=100*(g.ratio>1.005).mean()))
pd.DataFrame(ps).to_csv(O/'common_panel.csv',index=False)
# One plan gets equal weight after averaging its observed NDCs, plus equal drug weights.
s=[]
for label,g in x[x.IPAY=='2026'].groupby('release'):
 g=g.assign(at=g.ratio.between(.995,1.005).astype(float),above=(g.ratio>1.005).astype(float))
 s.append(dict(release=label,unweighted_rows_pct=100*g['at'].mean(),equal_plan_pct=100*g.groupby('plan')['at'].mean().mean(),equal_drug_pct=100*g.groupby('drug')['at'].mean().mean()))
pd.DataFrame(s).to_csv(O/'weight_sensitivity.csv',index=False)
# Same-NDC insulin and injectable spot checks.
u=x[x.drug.str.contains('NOVOLOG|ENBREL|STELARA|OZEMPIC')].groupby(['release','drug','NDC']).agg(rows=('ratio','size'),median_unit_cost=('UNIT_COST','median'),mfp=('mfp','first'),median_ratio=('ratio','median')).reset_index()
u.to_csv(O/'injectable_unit_checks.csv',index=False)
# Snapshot provenance for the reviewed version, without changing it.
manifest={}
for p in [R/'pharma/scripts/spuf_mfp_check.py',R/'pharma/ira_findings.md',*A.glob('*.csv'),A/'summary.md']:
 manifest[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest['replication_sha256']=hashlib.sha256((O/'replication.md').read_bytes()).hexdigest()
(O/'reviewed_files_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(checks.to_string(index=False));print(rowcheck);print(pd.DataFrame(ps).to_string(index=False));print(pd.DataFrame(s).to_string(index=False))
# Unit and longitudinal diagnostics supporting the review wording.
a=x[(x.IPAY=='2026')&(x.release=='2025Q4')&(x.ratio>1.005)]
b=x[x.release=='2026Q3']
j=a.merge(b,on=['plan','NDC'],how='left',suffixes=('_jan','_oct'),validate='one_to_one')
j.groupby('NDC').agg(jan_above=('ratio_jan','size'),seen_oct=('ratio_oct','count'),max_oct_ratio=('ratio_oct','max')).to_csv(O/'exception_followthrough.csv')
x[x.IPAY=='2026'].groupby(['release','drug','type']).ratio.median().reset_index().to_csv(O/'drug_plan_type_medians.csv',index=False)
k=x[(x.IPAY=='2026')&(x.release=='2025Q4')&(x.NDC.isin(['57894044001','57894044003']))].pivot(index='plan',columns='NDC',values='UNIT_COST').dropna()
r=k['57894044003']/k['57894044001']
(O/'vial_syringe_check.json').write_text(json.dumps({'paired_plans':len(r),'median_vial_to_syringe_ratio':float(r.median()),'within_0_01_of_three':int(((r-3).abs()<.01).sum()),'interpretation':'Diagnostic pattern only. Same 0.5 mL liquid presentation does not justify a threefold unit conversion.'},indent=2)+'\n')
import zipfile
contract=[]
for lab in labels.values():
 with zipfile.ZipFile(R/f'data/raw/pharma/spuf/{lab}/sample files PPUF_{lab}.zip') as z:
  n=next(n for n in z.namelist() if n.startswith('basic drugs formulary'))
  with z.open(n) as f:s=pd.read_csv(f,sep='|',dtype=str)
  contract.append({'folder':lab,'sample_contract_years':','.join(sorted(s.CONTRACT_YEAR.unique())),'sample_rows':len(s),'evidence':'Sample corroborates year only; full sample is not used for pricing estimates.'})
pd.DataFrame(contract).to_csv(O/'sample_contract_years.csv',index=False)
