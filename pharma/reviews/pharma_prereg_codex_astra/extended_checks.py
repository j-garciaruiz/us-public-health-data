"""Part B additional local checks of historical claims. No 2027 plan prices."""
from pathlib import Path
import zipfile, json, hashlib
import pandas as pd
O=Path(__file__).resolve().parent; R=O.parents[1];RAW=R/'data/raw/pharma'
assert (O/'replication.md').exists()
m=pd.read_csv(RAW/'ira/selected_drugs_mfp.csv',dtype={'NDC-11':str})
m['ndc']=m['NDC-11'].str.replace('-','',regex=False);m['start']=pd.to_datetime(m['MFP Effective Date']);m['end']=pd.to_datetime(m['MFP End Date'])
m=m[m.end.isna()|(m.end>=m.start)].copy();m['drug']=m['Selected Drug Name'].str.split(';').str[0].str.strip();m['mfp']=m['NDC-9 MFP per Unit Price']
allres=[]
for label,which in [('2025Q3','2026-12-31'),('2025Q4','2026-01-01'),('2026Q3','2026-12-31')]:
 m26=m[(m.IPAY==2026)&(m.start<=which)&(m.end.isna()|(m.end>=which))]
 m27=m[(m.IPAY==2027)&(m.start=='2027-01-01')]
 mp=pd.concat([m26,m27]);assert not mp.ndc.duplicated().any()
 pieces=[]
 with zipfile.ZipFile(RAW/'spuf'/label/f'pricing file PPUF_{label}.zip') as z:
  with z.open(z.namelist()[0]) as stream:
   for c in pd.read_csv(stream,sep='|',dtype={'NDC':str},chunksize=800000):
    c=c[(c.DAYS_SUPPLY==30)&c.NDC.isin(mp.ndc)]
    if len(c):pieces.append(c[['NDC','UNIT_COST']])
 d=pd.concat(pieces).merge(mp[['ndc','drug','mfp','IPAY']],left_on='NDC',right_on='ndc',validate='many_to_one')
 d['ratio']=d.UNIT_COST/d.mfp;d['within']=abs(d.ratio-1)<=.005;d['above']=d.ratio>1.005
 s=d.groupby(['IPAY','drug']).agg(r=('ratio','median'),rows=('ratio','size'),within=('within','mean'),above=('above','mean')).reset_index();s['label']=label
 allres.append(s)
 print(label,'finished',flush=True)
s=pd.concat(allres);s.to_csv(O/'historical_plan_checks.csv',index=False)
a=pd.read_csv(R/'pharma/outputs/spuf/ratio_by_drug.csv')
print('author ratio columns',list(a.columns),flush=True)
labels={'2025Q3':'2025 (Oct 2025 release)','2025Q4':'2026 (Jan 2026 release)','2026Q3':'2026 (Oct 2026 release)'}
s['snapshot']=s.label.map(labels);z=s.merge(a,on=['IPAY','drug','snapshot']);z['difference']=z.r-z.median_ratio
print('all historical ratio max difference',z.difference.abs().max(),flush=True)
print('Jan2026 above 5%',s[(s.label=='2025Q4')&(s.IPAY==2026)&(s.above>.05)][['drug','above']].to_dict('records'),flush=True)
# December NADAC checks use each NDC's first valid 2026 MFP, matching historical effective-date logic.
mp=m[m.IPAY==2026].sort_values('start').drop_duplicates('ndc')
n=pd.read_csv(RAW/'nadac/nadac_2025.csv',dtype={'NDC':str});n['dt']=pd.to_datetime(n['As of Date'])
n=n[(n.dt==n.dt.max())&(n['Classification for Rate Setting']=='B')]
x=n.merge(mp[['ndc','drug','mfp']],left_on='NDC',right_on='ndc',validate='one_to_one');x['ratio']=x['NADAC Per Unit']/x.mfp
x.loc[x.drug=='NOVOLOG','drug']=x.loc[x.drug=='NOVOLOG','NDC Description'].str.extract(r'^(NOVOLOG|FIASP)',expand=False)
s=x.groupby('drug').ratio.median().rename('replicated').reset_index();s=s.merge(pd.read_csv(R/'pharma/outputs/ira/nadac_to_mfp_by_drug.csv')[['drug','ratio_dec2025']],on='drug');s['difference']=s.replicated-s.ratio_dec2025;s.to_csv(O/'dec2025_nadac_check.csv',index=False)
print('dec2025 NADAC max difference',s.difference.abs().max(),flush=True)
# Hash the six Part A raw inputs and three reviewed author files, for a review manifest.
paths=[RAW/'spuf'/q/f'pricing file PPUF_{q}.zip' for q in ['2025Q3','2026Q3']]+[RAW/'ira/selected_drugs_mfp.csv',RAW/'partd/partd_spending_quarterly.csv',RAW/'nadac/nadac_2026.csv',RAW/'nadac/nadac_comparison.csv']+[R/p for p in ['pharma/prereg_2027.md','pharma/scripts/prereg_2027.py','pharma/outputs/prereg_2027/baseline.md']]
manifest=[]
for p in paths:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 manifest.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
(O/'review_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
