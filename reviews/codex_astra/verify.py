"""Final verification, using QR projections independently of the SVD fit."""
import hashlib
import itertools
import json
import platform
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from replicate import HERE, ROOT, FEATURES, design, pair_stats, r2

frozen = json.loads((HERE/"PART_A_FROZEN.json").read_text())
for file,digest in frozen["files_sha256"].items():
    assert hashlib.sha256((HERE/file).read_bytes()).hexdigest() == digest, file
source_hashes = json.loads((HERE/"reviewed_source_hashes.json").read_text())
for file,digest in source_hashes.items():
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest() == digest, file
source_hashes["scripts/covariate_charts.py"] = hashlib.sha256(
    (ROOT/"scripts/covariate_charts.py").read_bytes()).hexdigest()
(HERE/"reviewed_source_hashes.json").write_text(json.dumps(source_hashes,indent=2))

d=pd.read_csv(HERE/"analysis_data.csv",dtype={"countyfips":str})
scores=pd.read_csv(HERE/"measure_r2.csv").set_index("measure")
pred=pd.read_csv(HERE/"predictions.csv",dtype={"countyfips":str})
pairs=pd.read_csv(HERE/"pair_correlations.csv")
assert len(scores)==80 and len(pairs)==1560
assert scores.n.sum()==len(pred)
assert pred.groupby(["measure","countyfips"]).size().max()==1
max_score_error=0.
for m,g in pred.groupby("measure"):
    s=scores.loc[m]
    assert len(g)==s.n
    for ycol,rcol in [("fitted","r2_in_sample"),("oof_prediction","r2_cv_pooled")]:
        err=abs(float(r2(g.observed.to_numpy(),g[ycol].to_numpy()))-s[rcol])
        max_score_error=max(max_score_error,err)
assert max_score_error<1e-12

cache={}
errors=[]
for _,r in pairs.iterrows():
    cols=[f"{m}_{r.kind}" for m in [r.measure_a,r.measure_b]]
    mask=d[cols].notna().all(axis=1).to_numpy()
    key=mask.tobytes()
    if key not in cache:
        sub=d.loc[mask]
        available=[m for m in scores.index if sub[m].notna().all()]
        x,ns=design(sub)
        q,_=np.linalg.qr(x,mode="reduced")
        y=sub[available].to_numpy(float)
        fit=q@(q.T@y)
        cache[key]=(available,y,y-fit,fit)
    available,y,e,fit=cache[key]
    idx=[available.index(c) for c in cols]
    checked=pair_stats(y[:,idx],e[:,idx],fit[:,idx])
    for metric,value in checked.items():
        errors.append(abs(value-r[metric]))
assert max(errors)<1e-9
assert (pairs.residual_df == pairs.n-pairs["rank"]).all()
assert (scores.residual_df == scores.n-scores["rank"]).all()
bench=pd.read_csv(HERE/"benchmark.csv")
assert bench.n.tolist()==[2956,1485]
ledger=pd.read_csv(HERE/"all_numeric_disagreements.csv")
assert ledger.cause.notna().all() and ledger.key.notna().all()
assert (abs(ledger.independent-ledger.claude-ledger.delta)<1e-12).all()
assert not ledger.duplicated(["file","key","metric"]).any()
report=(HERE/"REPORT.md").read_text()
assert "\u2014" not in report
assert f"{len(ledger):,} differing reported cells" in report
assert "2026-10-20 12:05:31 UTC" in report
# A Markdown table cell must not contain an unescaped absolute-value bar.
assert "| Pairs with |" not in report
raw_paths=[ROOT/"data/raw/places_county_2025.csv"]+sorted((ROOT/"data/raw/acs_sf").glob("*.dat"))
raw_hashes={}
for path in raw_paths:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    raw_hashes[str(path.relative_to(ROOT))]=h.hexdigest()
checks=dict(
    verified_utc=datetime.now(timezone.utc).isoformat(),
    python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
    frozen_artifacts_unchanged=True,reviewed_sources_unchanged=True,
    outcomes=80,pairs=1560,selected_pairs=6,benchmark_samples=2,
    numeric_disagreement_cells=len(ledger),prediction_rows=len(pred),
    max_recalculated_r2_error=max_score_error,max_qr_pair_metric_error=max(errors),
    raw_source_sha256=raw_hashes,
    final_report_sha256=hashlib.sha256((HERE/"REPORT.md").read_bytes()).hexdigest(),
)
(HERE/"final_verification.json").write_text(json.dumps(checks,indent=2))
print(json.dumps({k:v for k,v in checks.items() if k!="raw_source_sha256"},indent=2))
