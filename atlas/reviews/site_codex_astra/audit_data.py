from pathlib import Path
import json, re, hashlib, math
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent

def readjs(name):
    text=(ROOT/'site/data'/name).read_text()
    return json.loads(text[text.index('= {')+2:].strip().rstrip(';')) if name!='geo.js' else json.loads(text.split(' = ',1)[1].rstrip(';\n'))
def readout(oid):
    return json.loads((ROOT/'site/data'/('atlas_'+oid+'.js')).read_text().rsplit(' = ',1)[1].rstrip(';\n'))
def digest():
    files=list((ROOT/'site').rglob('*'))+[ROOT/'scripts/export_site_data.py']+list((ROOT/'outputs').rglob('*.csv'))+list((ROOT/'outputs').rglob('REVIEW_SUMMARY.md'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}

if not (OUT/'source_hashes_start.json').exists(): (OUT/'source_hashes_start.json').write_text(json.dumps(digest(),indent=2))
idx=readjs('atlas_index.js'); findings=readjs('findings.js'); geo=readjs('geo.js')
a=pd.read_csv(ROOT/'outputs/atlas/atlas_county_long.csv',dtype={'fips':str})
counties=[c['fips'] for c in idx['counties']]
errors=[]; checked=0; display_errors=[]
def eq(got,want,where):
    global checked
    checked+=1
    if got!=want: errors.append({'where':where,'got':got,'want':want})
geometry={g['id']:g['properties'] for g in geo['objects']['counties']['geometries']}
eq(len(counties),len(set(counties)),'unique counties');eq(set(counties),set(geometry),'geometry IDs')
for c in idx['counties']:
    eq((c['name'],c['st']),(geometry[c['fips']]['name'],geometry[c['fips']]['st']),c['fips']+' geometry')
metadata=[]
for o in idx['outcomes']:
    d=readout(o['id']); g=a[(a.layer==o['layer'])&(a.outcome==o['label'])]; nd=1 if o['layer']=='mortality' else 2
    eq(o['shrinkage'],o['layer']!='medicare_std',o['id']+' shrinkage')
    eq(o['counties'],len(g[g['mode']=='national']),o['id']+' count')
    for mode,source_mode in [('nat','national'),('ws','within_state')]:
        f=g[g['mode']==source_mode].set_index('fips').reindex(counties)
        eq(len(g[g['mode']==source_mode]),g[g['mode']==source_mode].fips.nunique(),o['id']+mode+' duplicates')
        fields=[('exp','expected',nd),('shr','difference_shrunk',nd),('rel','reliability',2),('tier','tier',0)]
        if mode=='ws': fields+=[('peers','state_peer_counties',0)]
        if mode=='nat': fields+=[('obs','observed',nd),('places','places_context',1)]
        for key,col,precision in fields:
            values=d[key] if key in ['obs','places'] else d[mode][key]
            eq(len(values),len(counties),o['id']+mode+key+' length')
            for i,(actual,expected) in enumerate(zip(values,f[col])):
                want=None if pd.isna(expected) else round(float(expected),precision)
                eq(actual,want,f"{o['id']} {mode} {counties[i]} {key}")
        for i,r in enumerate(f.itertuples()):
            if pd.isna(r.observed): continue
            raw_export=d['obs'][i]-d[mode]['exp'][i]
            raw_csv=r.observed-r.expected
            # D3 .0f/.1f uses positive magnitude rounding (avoid ties in this diagnostic).
            places=0 if o['layer']=='mortality' else 1
            rnd=lambda v: math.floor(abs(v)*10**places+0.5)/10**places * (-1 if v<0 else 1)
            if rnd(raw_export)!=rnd(raw_csv): display_errors.append({'id':o['id'],'mode':mode,'fips':counties[i],'csv_diff':raw_csv,'export_diff':raw_export,'display_csv':rnd(raw_csv),'display_export':rnd(raw_export)})
            if mode=='nat':
                eq(d['note'][i],None if pd.isna(r.reliability_note) else r.reliability_note,o['id']+counties[i]+' note')
                eq(d['disc'][i],1 if r.source_discrepancy==True else None,o['id']+counties[i]+' discrepancy')
    metadata.append({'id':o['id'],'counties':o['counties'],'tier_counts':g.tier.value_counts().to_dict()})
# Independently recompute findings from their CSVs.
c=pd.read_csv(ROOT/'outputs/covariate_test/r2_by_measure_crudeprev.csv'); adj=pd.read_csv(ROOT/'outputs/covariate_test/r2_by_measure_adjprev.csv'); p=pd.read_csv(ROOT/'outputs/covariate_test/pairs_adjprev.csv'); b=pd.read_csv(ROOT/'outputs/covariate_test/benchmark_uninsurance.csv'); v=pd.read_csv(ROOT/'outputs/expected_vs_observed/places_vs_observed.csv')
for key,frame in [('r2_crude_cv',c[['measure','inputs_plus_state_cv','n_counties']]),('benchmark',b),('places_vs_observed',v)]: eq(findings[key],frame.round(4).to_dict('records'),key)
stats={'r2_adj_cv_median':round(adj.inputs_plus_state_cv.median(),4),'r2_adj_cv_min':round(adj.inputs_plus_state_cv.min(),4),'r2_adj_inputs_only_median':round(adj.inputs_only.median(),4),'n_measures':len(adj),'n_pairs':len(p),'n_strong_pairs':int((p.raw_r.abs()>=.7).sum()),'median_abs_raw_r':round(p.raw_r.abs().median(),3),'median_abs_partial_r':round(float(p.partial_r.abs().median()),3),'pvo_max_gain':round(v.gain.max(),4),'pvo_n_pairs':int((v['sample']=='all').sum()),'pvo_demo_beats_places':int((v.cv_r2_demo>v.cv_r2_places).sum()),'pvo_rows':len(v),'atlas_outcomes':len(a[['layer','outcome']].drop_duplicates()),'atlas_counties':len(counties)}
for k,x in stats.items():eq(findings[k],x,k)
dfi=p[(p.a=='diabetes')&(p.b=='foodinsecu')].iloc[0];eq(findings['diab_food'],{'raw_r':round(dfi.raw_r,3),'partial_r':round(dfi.partial_r,3),'n':int(dfi.n)},'diab_food')
for e in findings['examples']:
    r=a[(a['mode']=='national')&(a.fips==e['fips'])&(a.layer==e['layer'])&(a.outcome==e['outcome'])].iloc[0]
    for key,col in [('observed','observed'),('expected','expected'),('shrunk','difference_shrunk')]:eq(e[key],round(r[col],1),e['fips']+key)
# Independently join source death counts and require every exported mortality slot to be eligible.
w=pd.read_csv(ROOT/'data/raw/wonder_county_smr.csv',dtype={'fips':str})
raw=pd.read_csv(ROOT/'data/raw/wonder/county_cause_2018_2024.txt',sep='\t',dtype=str)
raw=raw[raw['County Code'].str.fullmatch(r'\d{5}',na=False)].copy(); raw['fips']=raw['County Code'].replace({'02270':'02158','46113':'46102'})
causemap={'Diabetes deaths':('diabetes','GR113-046'),'Heart disease deaths':('heart','GR113-054'),'Cerebrovascular deaths':('stroke','GR113-070'),'Chronic lower respiratory deaths':('clrd','GR113-082')}
mortality=[]
for o in idx['outcomes']:
    if o['layer']!='mortality':continue
    cause,code=causemap[o['label']]; d=readout(o['id']); counts=raw[raw['UCD - ICD-10 113 Cause List Code']==code].set_index('fips')['Deaths']; ww=w[w.cause==cause].set_index('fips')
    unsafe=0; displayed=0
    for i,fips in enumerate(counties):
        n=pd.to_numeric(counts.get(fips),errors='coerce'); eligible=pd.notna(n) and n>=10
        if d['obs'][i] is not None:
            displayed+=1
            if not eligible:unsafe+=1
        if not eligible:
            eq(d['note'][i],None,f'{o["id"]} suppressed {fips} note')
            eq(d['disc'][i],None,f'{o["id"]} suppressed {fips} discrepancy')
            for mode in ['nat','ws']:
                for key in ['exp','shr','rel','tier']:
                    eq(d[mode][key][i],None,f'{o["id"]} suppressed {fips} {mode} {key}')
            eq(d['obs'][i],None,f'{o["id"]} suppressed {fips} observed')
    mortality.append({'id':o['id'],'published':displayed,'unsafe':unsafe,'raw_min_published':float(pd.to_numeric(counts.reindex([f for i,f in enumerate(counties) if d['obs'][i] is not None]),errors='coerce').min())})
# Geographic adjacency claimed in the example.
geoms={g['id']:g for g in geo['objects']['counties']['geometries']}
def arcs(x):
    if isinstance(x,int):return {x if x>=0 else ~x}
    return set().union(*(arcs(y) for y in x))
summary={'checks':checked,'errors':errors,'atlas_rows':len(a),'atlas_counties_unique':a.fips.nunique(),'geometry_counties':len(counties),'crude_median':c.inputs_plus_state_cv.median(),'adjusted_median':adj.inputs_plus_state_cv.median(),'gain_max':v.gain.max(),'gain_recomputed_max':(v.cv_r2_demo_places-v.cv_r2_demo).max(),'gain_max_row':v.loc[v.gain.idxmax()].to_dict(),'metadata':metadata,'examples':findings['examples'],'mortality':mortality,'raw_difference_display_mismatches':len(display_errors),'caddo_iberia_shared_arcs':len(arcs(geoms['22017']['arcs'])&arcs(geoms['22045']['arcs']))}
(OUT/'data_results.json').write_text(json.dumps(summary,indent=2,default=lambda x: int(x) if isinstance(x,np.integer) else str(x)))
pd.DataFrame(display_errors).to_csv(OUT/'rounding_discrepancies.csv',index=False)
print(json.dumps({k:v for k,v in summary.items() if k!='metadata'},indent=2))
