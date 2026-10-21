"""Independent Part A. Explicit allowlist; never reads author code/outputs or 2027 plan prices."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, zipfile
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/pharma'
M=pd.read_csv(RAW/'ira/selected_drugs_mfp.csv', dtype={'NDC-11':str})
M['ndc']=M['NDC-11'].str.replace('-','',regex=False).str.zfill(11)
M['start']=pd.to_datetime(M['MFP Effective Date'])
M['end']=pd.to_datetime(M['MFP End Date'])
M=M[M.end.isna() | (M.end>=M.start)].copy()
M['drug']=M['Selected Drug Name'].str.split(';').str[0].str.strip()
M['mfp']=M['NDC-9 MFP per Unit Price']

def active(cohort, when):
    t=pd.Timestamp(when)
    d=M[(M.IPAY==cohort)&(M.start<=t)&(M.end.isna()|(M.end>=t))].copy()
    assert not d.ndc.duplicated().any()
    return d
m26=active(2026,'2026-12-31') # uses corrected Entresto Sprinkle
m27=active(2027,'2027-01-01')
cont=active(2026,'2027-01-01')
for name,d in [('mfp2026',m26),('mfp2027',m27),('continuing_mfp',cont)]:
    d.to_csv(OUT/f'{name}.csv',index=False)

pricing=[]
for year,label,mp in [(2026,'2025Q3',m26),(2027,'2026Q3',m27)]:
    assert label in ['2025Q3','2026Q3']
    pieces=[]; total=0
    path=RAW/'spuf'/label/f'pricing file PPUF_{label}.zip'
    with zipfile.ZipFile(path) as z:
        names=z.namelist(); assert len(names)==1
        with z.open(names[0]) as stream:
            for c in pd.read_csv(stream,sep='|',dtype={'NDC':str,'CONTRACT_ID':str,'PLAN_ID':str,'SEGMENT_ID':str},chunksize=800000):
                total+=len(c)
                c=c[(c.DAYS_SUPPLY==30)&c.NDC.isin(mp.ndc)].copy()
                if len(c): pieces.append(c)
    d=pd.concat(pieces,ignore_index=True).merge(mp[['ndc','drug','mfp']],left_on='NDC',right_on='ndc',validate='many_to_one')
    assert not d.duplicated(['CONTRACT_ID','PLAN_ID','SEGMENT_ID','NDC','DAYS_SUPPLY']).any()
    assert (d.UNIT_COST>0).all() and (d.mfp>0).all()
    d['ratio']=d.UNIT_COST/d.mfp
    s=d.groupby('drug').agg(r=('ratio','median'),rows=('ratio','size'),ndcs=('NDC','nunique')).reset_index()
    s['predicted']=1/s.r-1;s['cohort']=year
    pricing.append(s)
    d.groupby(['drug','NDC']).agg(rows=('ratio','size'),median_r=('ratio','median'),median_cost=('UNIT_COST','median')).to_csv(OUT/f'ndc_pricing_{year}.csv')
    print(label,'all rows',total,'matched',len(d),'drugs',len(s),flush=True)
pr=pd.concat(pricing,ignore_index=True)
P=pd.read_csv(RAW/'partd/partd_spending_quarterly.csv')
P=P[P.Mftr_Name.eq('Overall')].copy()
P['brand']=P.Brnd_Name.str.upper()
brandmap=[]; rows=[]
for cohort,mp in [(2026,m26),(2027,m27)]:
    for drug,g in mp.groupby('drug'):
        roots=[x.strip() for x in g['Selected Drug Name'].iloc[0].split(';')]
        mask=P.brand.apply(lambda b:any(b==r or b.startswith(r+' ') for r in roots))
        mask &= ~P.brand.str.startswith('NOVOLOG MIX')
        d=P[mask]
        assert len(d)>0
        for brand in sorted(d.Brnd_Name.unique()): brandmap.append({'cohort':cohort,'drug':drug,'brand':brand})
        vals={'cohort':cohort,'drug':drug}
        for year,label in [('2025 (Q1-Q4)','2025'),('2026 (Q1)','2026q1')]:
            t=d[d.Year==year]
            vals['claims_'+label]=t.Tot_Clms.sum(); vals['spend_'+label]=t.Tot_Spndng.sum()
            vals['pc_'+label]=vals['spend_'+label]/vals['claims_'+label]
        rows.append(vals)
pd.DataFrame(brandmap).to_csv(OUT/'brand_mapping.csv',index=False)
res=pr.merge(pd.DataFrame(rows),on=['cohort','drug'],validate='one_to_one')
res['realized']=res.pc_2026q1/res.pc_2025-1
res['error_pp']=(res.realized-res.predicted)*100
res['removed_q1']=res.spend_2026q1*(-res.predicted)
res.to_csv(OUT/'cohort_results.csv',index=False)
a=res[res.cohort==2026];b=res[res.cohort==2027]
summary={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
 'pred2026_fixed_claims':float((a.spend_2025*a.predicted).sum()/a.spend_2025.sum()),
 'real2026_fixed_claims':float((a.claims_2025*a.pc_2026q1).sum()/a.spend_2025.sum()-1),
 'pred2027_fixed_claims':float((b.spend_2026q1*b.predicted).sum()/b.spend_2026q1.sum()),
 'gross_removed_q1':float(b.removed_q1.sum()),'gross_q1_baseline':float(b.spend_2026q1.sum()),
 'gross_q1_projected':float((b.spend_2026q1*(1+b.predicted)).sum()),
 'calibration_mae_pp':float(a.error_pp.abs().mean()),'calibration_max_abs_pp':float(a.error_pp.abs().max())}
# NADAC: restrict to supplied MFP NDCs, then pick the maximum global snapshot date.
N=pd.read_csv(RAW/'nadac/nadac_2026.csv',dtype={'NDC':str})
N['ndc']=N.NDC.str.zfill(11);N['snapshot']=pd.to_datetime(N['As of Date'])
last=N.snapshot.max();N=N[(N.snapshot==last)&N['Classification for Rate Setting'].eq('B')].copy()
assert not N.ndc.duplicated().any()
summary['nadac_snapshot']=str(last.date())
ndata=[]
for year,mp in [(2026,m26),(2027,m27)]:
    d=N.merge(mp[['ndc','drug','mfp']],on='ndc',validate='one_to_one')
    d['ratio']=d['NADAC Per Unit']/d.mfp;d['cohort']=year
    ndata.append(d)
nd=pd.concat(ndata,ignore_index=True)
nd.to_csv(OUT/'nadac_ndcs.csv',index=False)
ns=nd.groupby(['cohort','drug']).agg(nadac_ratio=('ratio','median'),ndcs=('ndc','nunique')).reset_index()
ns.to_csv(OUT/'nadac_summary.csv',index=False)
# Historical changes on NDCs that are brand classified in the latest snapshot.
eligible=set(nd.ndc); cuts=[]
for c in pd.read_csv(RAW/'nadac/nadac_comparison.csv',dtype={'NDC':str},chunksize=200000):
    c['ndc']=c.NDC.str.zfill(11)
    c=c[c.ndc.isin(eligible)].copy()
    c['date']=pd.to_datetime(c['Effective Date'])
    c=c[(c.date>=pd.Timestamp('2024-01-01'))&(c.date<=last)&(c['Percent Change']<=-20)&c['Primary Reason'].str.contains('WAC',case=False,na=False)]
    if len(c):cuts.append(c)
cut=pd.concat(cuts,ignore_index=True).merge(nd[['cohort','drug','ndc']].drop_duplicates(),on='ndc',validate='many_to_one')
cut.to_csv(OUT/'wac_cuts.csv',index=False)
basecuts=cut[(cut.cohort==2026)&(cut.date>=pd.Timestamp('2025-12-20'))&(cut.date<=pd.Timestamp('2026-02-28'))]
summary['2026_cut_window_drugs']=sorted(basecuts.drug.unique().tolist())
summary['2026_cut_since2024_drugs']=sorted(cut[cut.cohort==2026].drug.unique().tolist())
cs=cont.groupby('drug')['Single MFP per 30 DES'].first().rename('mfp2027').to_frame().join(m26.groupby('drug')['Single MFP per 30 DES'].first().rename('mfp2026'))
cs['change']=cs.mfp2027/cs.mfp2026-1;cs.to_csv(OUT/'continuing.csv')
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

def table(headers, rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
lines=['# Independent Part A replication\n',f"Completed {summary['timestamp_utc']} before opening any author code or pharma outputs.\n",'No 2027 plan pricing data or new data were accessed. Inputs were limited to the seven named local raw sources (two pricing archives, MFP, spending, and two NADAC files).\n',
'## Methods\n','MFP rows with end before start are excluded. The 2026 lookup is active on 2026-12-31 to use the corrected Entresto Sprinkle values; the 2027 lookup is active on 2027-01-01. Pricing uses every matched plan x NDC x segment row at 30 days, with equal row weight. NDC strings retain leading zeros. The ratio median is inverted only after aggregation.\n',
'Part D uses Overall manufacturer rows, pools brand families using the selected names as prefixes with a word boundary, and excludes NovoLog Mix and InPen devices. This includes Enbrel Mini/SureClick, Fiasp Pumpcart and Austedo XR titration kits. Exact mappings are saved in brand_mapping.csv. Fixed claim mix means sum(baseline claims x new price per claim) / sum(baseline claims x old price per claim) minus 1, so baseline spending weights apply to percentage changes. Errors below are realized minus predicted, in percentage points. All dollars are gross.\n',
'## 2026 calibration\n',table(['Drug','r','Prediction %','Realized %','Error pp','2025 $/claim','2026Q1 $/claim','Matched rows'],[[x.drug,f'{x.r:.6f}',f'{100*x.predicted:.4f}',f'{100*x.realized:.4f}',f'{x.error_pp:.4f}',f'{x.pc_2025:.4f}',f'{x.pc_2026q1:.4f}',x.rows] for x in a.itertuples()]),
f"\nFixed 2025 claim mix: predicted {100*summary['pred2026_fixed_claims']:.6f}%; realized {100*summary['real2026_fixed_claims']:.6f}%. Mean absolute drug-level error {summary['calibration_mae_pp']:.4f} pp; maximum {summary['calibration_max_abs_pp']:.4f} pp.\n",
'## 2027 cohort\n',table(['Drug','r','Prediction %','2026Q1 $/claim','2026Q1 claims','Gross removed, $m','Matched rows'],[[x.drug,f'{x.r:.6f}',f'{100*x.predicted:.4f}',f'{x.pc_2026q1:.4f}',int(x.claims_2026q1),f'{x.removed_q1/1e6:.6f}',x.rows] for x in b.itertuples()]),
f"\nFixed 2026Q1 claim mix change: {100*summary['pred2027_fixed_claims']:.6f}%. Gross spending removed at Q1 volumes: ${summary['gross_removed_q1']:,.2f}, from ${summary['gross_q1_baseline']:,.2f} to ${summary['gross_q1_projected']:,.2f}.\n",
f"## NADAC snapshot {last.date()}\n",'Only brand-classified NDCs in the latest global snapshot are used. Each NDC has equal weight. WAC cuts use Effective Date, Percent Change <= -20, and Primary Reason containing WAC.\n',
table(['2027 drug','NADAC/MFP','NDCs','WAC cuts since 2024 (date: range %)'],[[x.drug,f'{x.nadac_ratio:.6f}',x.ndcs,'; '.join(f'{dt.date()}: {g["Percent Change"].min():.2f} to {g["Percent Change"].max():.2f}' for dt,g in cut[(cut.cohort==2027)&(cut.drug==x.drug)].groupby('date')) or 'None'] for x in ns[ns.cohort==2027].itertuples()]),
'\nDeselected 2026 drugs, NADAC / 2026 MFP:\n']
d=nd[(nd.cohort==2026)&nd.drug.isin(['ENTRESTO','STELARA','XARELTO','NOVOLOG'])].copy()
d.loc[d.drug=='NOVOLOG','drug']=d.loc[d.drug=='NOVOLOG','NDC Description'].str.extract(r'^(NOVOLOG|FIASP)',expand=False)
lines.append(table(['Drug','NADAC/MFP','NDCs'],[[k,f'{v.ratio.median():.6f}',v.ndc.nunique()] for k,v in d.groupby('drug')]))
lines+=['\n2026 cohort WAC-cut base rate: '+str(len(summary['2026_cut_window_drugs']))+'/10 in 2025-12-20 through 2026-02-28 ('+', '.join(summary['2026_cut_window_drugs'])+'); '+str(len(summary['2026_cut_since2024_drugs']))+'/10 since 2024 ('+', '.join(summary['2026_cut_since2024_drugs'])+').\n','## Six continuing 2026 drugs\n',table(['Drug','2026 MFP / 30 days','2027 MFP / 30 days','Change %'],[[k,f'{v.mfp2026:.2f}',f'{v.mfp2027:.2f}',f'{v.change*100:.6f}'] for k,v in cs.iterrows()]),'\nThese are descriptive gross price predictions, without a causal or net-savings interpretation.\n']
(OUT/'replication.md').write_text('\n'.join(lines))
print(json.dumps(summary,indent=2),flush=True)
