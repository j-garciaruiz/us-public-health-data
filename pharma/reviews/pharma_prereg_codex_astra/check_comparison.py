"""Part B numerical reconciliation. Run only after independent replication.md exists."""
from pathlib import Path
import pandas as pd
import numpy as np
import json
O=Path(__file__).resolve().parent
R=O.parents[1]
assert (O/'replication.md').exists()
ours=pd.read_csv(O/'cohort_results.csv')
checks=[]
def compare(a,b,label,cols):
 a=a.set_index('drug');b=b.set_index('drug')
 assert set(a.index)<=set(b.index)
 for left,right in cols.items():
  for drug in a.index:
   x=a.loc[drug,left];y=b.loc[drug,right]
   checks.append(dict(table=label,drug=drug,field=right,replication=x,author=y,difference=x-y))
compare(ours[ours.cohort==2026],pd.read_csv(R/'pharma/outputs/prereg_2027/calibration_2026.csv'),'calibration',{'r':'r_oct2025','predicted':'predicted','realized':'chg_per_claim','error_pp':'error_pp','pc_2025':'per_claim_2025','pc_2026q1':'per_claim_2026Q1','claims_2025':'Tot_Clms_2025'})
x=ours[ours.cohort==2027].copy();x['pred_pc']=x.pc_2026q1*(1+x.predicted)
a=pd.read_csv(R/'pharma/outputs/prereg_2027/predictions_2027.csv')
compare(x,a,'predictions',{'r':'r_oct2026','predicted':'predicted','pc_2026q1':'per_claim_2026Q1','pred_pc':'pc_2027Q1_pred','claims_2026q1':'Tot_Clms_2026Q1','spend_2026q1':'Tot_Spndng_2026Q1','realized':'chg_per_claim'})
n=pd.read_csv(O/'nadac_summary.csv');compare(n[n.cohort==2027],a,'nadac2027',{'nadac_ratio':'nadac_to_mfp2027','ndcs':'nadac_ndcs'})
a=pd.read_csv(R/'pharma/outputs/prereg_2027/ipay2026_in_2027.csv')
compare(pd.read_csv(O/'continuing.csv'),a,'continuing',{'mfp2026':'mfp30_2026','mfp2027':'mfp30_2027','change':'mfp30_change'})
# Split NovoLog/Fiasp to agree with the author's separate NADAC series.
n=pd.read_csv(O/'nadac_ndcs.csv');n=n[n.cohort==2026].copy()
n.loc[n.drug=='NOVOLOG','drug']=n.loc[n.drug=='NOVOLOG','NDC Description'].str.extract(r'^(NOVOLOG|FIASP)',expand=False)
n=n.groupby('drug').ratio.median().rename('nadac_ratio').reset_index()
compare(n,pd.read_csv(R/'pharma/outputs/ira/nadac_to_mfp_by_drug.csv'),'nadac2026',{'nadac_ratio':'ratio_latest'})
c=pd.DataFrame(checks);c.to_csv(O/'numeric_comparison.csv',index=False)
print('Comparisons',len(c),'max absolute difference',c.difference.abs().max())
print(c[c.difference.abs()>1e-8].to_string(index=False))
print('Semaglutide spend share',float(x.loc[x.drug=='OZEMPIC','spend_2026q1'].iloc[0]/x.spend_2026q1.sum()))
print('Semaglutide removed share',float(x.loc[x.drug=='OZEMPIC','removed_q1'].iloc[0]/x.removed_q1.sum()))
# Current NADAC cut detection without latest-snapshot survivor filtering, for all active MFP NDCs.
m=pd.read_csv(O/'mfp2026.csv',dtype={'ndc':str})
frames=[]
for c in pd.read_csv(R/'data/raw/pharma/nadac/nadac_comparison.csv',dtype=str,chunksize=250000):
 d=c[c.NDC.isin(m.ndc)].copy();d['pct']=pd.to_numeric(d['Percent Change']);d['date']=pd.to_datetime(d['Effective Date'])
 d=d[(d.pct<=-20)&d['Primary Reason'].str.contains('WAC',na=False)&(d.date>='2024-01-01')&(d.date<='2026-10-21')]
 frames.append(d)
d=pd.concat(frames).merge(m[['ndc','drug']],left_on='NDC',right_on='ndc')
d.to_csv(O/'all_selected_wac_cuts.csv',index=False)
print('NADAC only cuts since2024',sorted(d.drug.unique()))
print('NADAC only cuts window',sorted(d[d.date.between('2025-12-20','2026-02-28')].drug.unique()))
