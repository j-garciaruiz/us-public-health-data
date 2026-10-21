import json, math, hashlib
from pathlib import Path
import pandas as pd

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
D = json.loads((OUT/'embedded_data.json').read_text())
checks, failures = 0, []
def compare(group, file, keys, fields, filt=None, round_fields=None):
    global checks
    df = pd.read_csv(ROOT/'pharma/outputs'/file)
    if filt is not None:
        df = df.loc[filt(df)]
    assert len(D[group]) == len(df), (group, len(D[group]), len(df))
    for r in D[group]:
        match = df
        for dest, src in keys.items():
            match = match.loc[match[src].astype(str)==str(r[dest])]
        assert len(match)==1, (group, r)
        s = match.iloc[0]
        for dest, src in fields.items():
            a,b = r[dest], s[src]
            if round_fields and dest in round_fields:
                b = round(float(b), round_fields[dest])
            checks += 1
            good = a is None and pd.isna(b)
            if not good:
                if isinstance(a,(int,float)) and not isinstance(a,bool):
                    good = math.isclose(a, float(b), rel_tol=1e-12, abs_tol=1e-12)
                else:
                    good = a == b
            if not good:
                failures.append([group, {k:r[k] for k in keys}, dest, a, str(b)])

compare('f1','ira/partd_per_claim_by_drug.csv',{'drug':'drug','group':'group'},
        {'pc2025':'per_claim_2025','pc2026':'per_claim_2026Q1','chg':'chg_per_claim','claims2025':'Tot_Clms_2025'},
        lambda d:d.group.isin(['IPAY 2026','IPAY 2027']))
compare('groups','ira/partd_per_claim_by_group.csv',{'group':'group'},
        {'n':'drug_families','median':'median_pct_change','p25':'p25','p75':'p75','fixed':'fixed_weight_pct_change','share30':'share_falling_30pct_or_more'})
compare('f2','ira/wac_january_by_group.csv',{'january':'january','window':'window','group':'group'},
        {'n':'brand_ndcs','cut':'ndcs_with_wac_cut_ge_20pct','share':'share_cut','inc':'share_increase'})
compare('cuts','ira/wac_cut_events.csv',{'january':'january','group':'group','drug':'drug'},
        {k:k for k in D['cuts'][0]}, lambda d:d.group.str.startswith('IPAY'))
compare('f3','ira/nadac_to_mfp_weekly.csv',{'drug':'drug','date':'as_of'},
        {'ratio':'median_ratio','ndcs':'ndcs'},round_fields={'ratio':4})
compare('f4','spuf/ratio_by_drug.csv',{'drug':'drug','IPAY':'IPAY','snapshot':'snapshot'},
        {'ratio':'median_ratio','at':'share_at_mfp'})
compare('f4g','spuf/ratio_by_group.csv',{'snapshot':'snapshot'},
        {'rows':'plan_ndc_rows','median':'median_ratio','at':'share_at_mfp','below':'share_below_mfp','above':'share_above_mfp'}, lambda d:d.IPAY==2026)
compare('f4g','spuf/sensitivity_weights_panel.csv',{'snapshot':'snapshot'},{'weighted':'claims_2025'})
compare('cal','prereg_2027/calibration_2026.csv',{'drug':'drug'},
        {'r':'r_oct2025','pred':'predicted','real':'chg_per_claim','err':'error_pp','structural':'structural'})
compare('pred','prereg_2027/predictions_2027.csv',{'drug':'drug'},
        {'r':'r_oct2026','pred':'predicted','pc':'per_claim_2026Q1','nadac':'nadac_to_mfp2027','gab':'gabriel_off_net','cms':'cms_off_list_2024'})

c=pd.read_csv(ROOT/'pharma/outputs/prereg_2027/calibration_2026.csv')
p=pd.read_csv(ROOT/'pharma/outputs/prereg_2027/predictions_2027.csv')
stats={
 'cal_mae':c.error_pp.abs().mean(),
 'cal_spearman':c.predicted.rank().corr(c.chg_per_claim.rank()),
 'cal_fixed_pred':(c.Tot_Clms_2025*c.per_claim_2025*(1+c.predicted)).sum()/(c.Tot_Clms_2025*c.per_claim_2025).sum()-1,
 'cal_fixed_observed':(c.Tot_Clms_2025*c.per_claim_2026Q1).sum()/(c.Tot_Clms_2025*c.per_claim_2025).sum()-1,
 'pred_fixed':(p.Tot_Clms_2026Q1*p.per_claim_2026Q1*(1+p.predicted)).sum()/(p.Tot_Clms_2026Q1*p.per_claim_2026Q1).sum()-1,
 'pred_gross_removed':(-p.Tot_Spndng_2026Q1*p.predicted).sum(),
 'baseline_gross':p.Tot_Spndng_2026Q1.sum(),
 'sema_share':p.loc[p.drug=='OZEMPIC','Tot_Spndng_2026Q1'].sum()/p.Tot_Spndng_2026Q1.sum(),
 'all_spuf_rows':int(pd.read_csv(ROOT/'pharma/outputs/spuf/ratio_by_group.csv').plan_ndc_rows.sum()),
 'f2_max_share':max(r['share'] for r in D['f2']),
 'f3_min_ratio':min(r['ratio'] for r in D['f3']),
 'f3_max_ratio':max(r['ratio'] for r in D['f3']),
 'f3_dates':sorted({r['date'] for r in D['f3']})[::len({r['date'] for r in D['f3']})-1],
}
result={'numeric_or_categorical_checks':checks,'failures':failures,'statistics':stats,'array_lengths':{k:len(v) for k,v in D.items()},'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'pharma/report/index.html',ROOT/'pharma/report/template.html',ROOT/'pharma/report/prereg_note.html',ROOT/'pharma/prereg_2027.md']}}
(OUT/'numeric_audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
