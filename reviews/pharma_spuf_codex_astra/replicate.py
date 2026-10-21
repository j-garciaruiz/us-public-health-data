"""Independent Part A; authored before reading the analysis under review."""
from pathlib import Path
from datetime import datetime, timezone
import json, zipfile, hashlib
import pandas as pd
import numpy as np
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
LABELS={'2025Q3':('2025','2026-10-01','SPUF_2025_20251009'),'2025Q4':('2026','2026-01-01','SPUF_2026_20260107'),'2026Q3':('2026','2026-09-01','SPUF_2026_20261007')}
raw=pd.read_csv(ROOT/'data/raw/pharma/ira/selected_drugs_mfp.csv',dtype=str)
raw=raw[raw.IPAY.isin(['2026','2027'])].copy()
raw['NDC']=raw['NDC-11'].str.replace('-','',regex=False)
raw['start']=pd.to_datetime(raw['MFP Effective Date'])
raw['end']=pd.to_datetime(raw['MFP End Date']).fillna(pd.Timestamp('2099-12-31'))
raw['mfp']=pd.to_numeric(raw['NDC-9 MFP per Unit Price'])
raw['drug']=raw['Selected Drug Name']
invalid=raw[raw.end<raw.start]
invalid.to_csv(OUT/'invalid_mfp_intervals.csv',index=False)
valid=raw[raw.end>=raw.start].copy()

def select_mfp(date):
    out=[]
    for ipay in ['2026','2027']:
        t=pd.Timestamp(date if ipay=='2026' else '2027-01-01')
        a=valid[(valid.IPAY==ipay)&(valid.start<=t)&(valid.end>=t)].copy()
        assert not a.NDC.duplicated().any()
        assert a.mfp.notna().all() and (a.mfp>0).all()
        out.append(a[['IPAY','NDC','drug','mfp']])
    return pd.concat(out,ignore_index=True)

def summary(d):
    r=d.ratio
    return dict(rows=len(d),plans=d.plan.nunique(),ndcs=d.NDC.nunique(),median=r.median(),p05=r.quantile(.05),p95=r.quantile(.95),within_pct=100*r.between(.995,1.005).mean(),below_pct=100*(r<.995).mean(),above_pct=100*(r>1.005).mean())

def md(d):
    cols=list(d.columns)
    def fmt(x):
        if isinstance(x,(float,np.floating)):return f'{x:.6f}'
        return str(x)
    return '| '+' | '.join(cols)+' |\n| '+' | '.join(['---']*len(cols))+' |\n'+'\n'.join('| '+' | '.join(fmt(x) for x in row)+' |' for row in d.itertuples(index=False,name=None))

groups=[];drugs=[];splits=[];above=[];probes=[];quality=[];sens=[];all_rows=[]
for label,(year,date,release) in LABELS.items():
    print('Scanning',label,flush=True)
    path=ROOT/f'data/raw/pharma/spuf/{label}/pricing file PPUF_{label}.zip'
    chunks=[];n=0;all30=0
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as f:
            for c in pd.read_csv(f,sep='|',dtype={'CONTRACT_ID':str,'PLAN_ID':str,'SEGMENT_ID':str,'NDC':str,'DAYS_SUPPLY':'int16','UNIT_COST':'float64'},chunksize=700000):
                n+=len(c);all30+=int((c.DAYS_SUPPLY==30).sum())
                a=c[(c.DAYS_SUPPLY==30)&c.NDC.isin(raw.NDC)].copy()
                if len(a):chunks.append(a)
    candidates=pd.concat(chunks,ignore_index=True)
    candidates.to_csv(OUT/f'{label}_selected_raw.csv.gz',index=False)
    m=select_mfp(date)
    m.to_csv(OUT/f'{label}_mfp_lookup.csv',index=False)
    d=candidates.merge(m,on='NDC',how='inner',validate='many_to_one')
    d['plan']=d.CONTRACT_ID+'-'+d.PLAN_ID+'-'+d.SEGMENT_ID
    d['ratio']=d.UNIT_COST/d.mfp
    d['type']=np.where(d.CONTRACT_ID.str.startswith('S'),'PDP','MA')
    assert set(d.CONTRACT_ID.str[0])<=set('HRS')
    assert d.UNIT_COST.notna().all() and (d.UNIT_COST>=0).all()
    duplicates=int(d.duplicated(['plan','NDC']).sum())
    assert duplicates==0
    d['release']=label
    all_rows.append(d)
    quality.append(dict(release=label,total_rows=n,all_30day_rows=all30,selected_candidates=len(candidates),matched_rows=len(d),unmatched_rows=len(candidates)-len(d),duplicate_plan_ndc=duplicates,zero_cost=int((d.UNIT_COST==0).sum()),mfp_ndcs=len(m),observed_ndcs=d.NDC.nunique()))
    unmatched=candidates[~candidates.NDC.isin(m.NDC)].groupby('NDC').size().rename('rows').reset_index()
    unmatched.to_csv(OUT/f'{label}_no_valid_mfp.csv',index=False)
    for ipay,a in d.groupby('IPAY'):
        groups.append(dict(release=label,plan_year=year,IPAY=ipay,**summary(a)))
        for tol in [.0001,.001,.005,.01]:
            sens.append(dict(release=label,IPAY=ipay,tolerance_pct=100*tol,within_pct=100*a.ratio.between(1-tol,1+tol).mean()))
    for (ipay,drug),a in d.groupby(['IPAY','drug']):drugs.append(dict(release=label,IPAY=ipay,drug=drug,**summary(a)))
    for kind,a in d[d.IPAY=='2026'].groupby('type'):splits.append(dict(release=label,type=kind,**summary(a)))
    for ndc,a in d[(d.IPAY=='2026')&(d.ratio>1.005)&(year=='2026')].groupby('NDC'):
        above.append(dict(release=label,drug=a.drug.iloc[0],NDC=ndc,above_rows=len(a),all_rows_for_ndc=int((d.NDC==ndc).sum()),mfp=a.mfp.iloc[0],min_unit_cost=a.UNIT_COST.min(),max_unit_cost=a.UNIT_COST.max(),median_ratio=a.ratio.median()))
    a=d[d.NDC=='00003089421']
    probes.append(dict(release=label,plan_year=year,rows=len(a),min_cost=a.UNIT_COST.min(),median_cost=a.UNIT_COST.median(),max_cost=a.UNIT_COST.max(),mfp=a.mfp.iloc[0],median_ratio=a.ratio.median()))
    print(label,quality[-1],flush=True)
frames={k:pd.DataFrame(v) for k,v in dict(groups=groups,drugs=drugs,plan_types=splits,above_mfp=above,year_probe=probes,quality=quality,tolerance=sens).items()}
for k,d in frames.items():d.to_csv(OUT/f'{k}.csv',index=False)
pd.concat(all_rows,ignore_index=True).to_csv(OUT/'matched_rows.csv.gz',index=False)
manifest={}
for p in [ROOT/'data/raw/pharma/ira/selected_drugs_mfp.csv',*[ROOT/f'data/raw/pharma/spuf/{l}/pricing file PPUF_{l}.zip' for l in LABELS]]:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    manifest[str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'sha256':h.hexdigest()}
manifest['part_a_completed_utc']=datetime.now(timezone.utc).isoformat()
(OUT/'part_a_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
intro='''# Independent Part A replication

Completed before opening the author script, outputs, or finding 4. Code: `replicate.py`. Raw inputs and SHA-256 hashes: `part_a_manifest.json`.

## Release year and MFP selection

CMS says the first year in SPUF.YYYY.YYYYMMDD denotes the contract year, and the final date is the website posting date. Thus SPUF_2025_20251009 (folder 2025Q3) is 2025; SPUF_2026_20260107 (folder 2025Q4) and SPUF_2026_20261007 (folder 2026Q3) are 2026. The January posting is the early 2026 contract-year price schedule, not a 2025 baseline. Source: https://data.cms.gov/sites/default/files/2025-10/cf6b8476-ca42-48c6-9fc4-281b08c6ea87/Methodology-SPUF-2026.pdf . The Eliquis 5 mg check below independently corroborates the distinction.

For 2025 prices use the corrected late-2026 MFP benchmark. For the January 2026 publication use the initial 2026 MFP; for the October 2026 publication use the post-June MFP. IPAY 2027 always uses 2027-01-01 MFP. Exclude 70 impossible effective/end intervals (11 starting 2026 and 59 starting 2027); do not treat them as active prices. Preserve unmatched observed NDCs in the no_valid_mfp CSVs. Coverage counts are observed valid-price NDCs, not every nominal historical list entry.

Only DAYS_SUPPLY=30. One observation is a unique contract-plan-segment-NDC; plans count the full contract-plan-segment key. Percentiles use pandas linear interpolation. Within = ratio in [0.995,1.005]; below <0.995; above >1.005, so categories partition the rows. Counts are unweighted. Ratios use UNIT_COST / NDC-9 MFP per Unit Price without any package-size conversion at this stage; unit validity is a separate Part B check.

'''
parts=[intro]
for key,title in [('year_probe','Eliquis plan-year check'),('groups','Group results'),('plan_types','IPAY 2026 by plan type'),('above_mfp','IPAY 2026 NDCs above MFP in the two 2026 releases'),('drugs','Every drug and release'),('quality','Input coverage and integrity'),('tolerance','Tolerance sensitivity')]:
    parts.extend(['## '+title+'\n',md(frames[key]),'\n'])
(OUT/'replication.md').write_text('\n'.join(parts))
print('PART A SAVED',manifest['part_a_completed_utc'],flush=True)
