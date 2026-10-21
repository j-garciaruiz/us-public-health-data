"""Post-freeze robustness checks. Exploratory, not model selection."""
import json
import numpy as np
import pandas as pd
from replicate import HERE, FEATURES, load, panels, evaluate
from compare import selected

def main():
    base,m=load()
    den=pd.read_csv(HERE/"cms_denominator_categories.csv",dtype={"fips":str})
    results=[]
    for key,d,features in panels(base,m):
        if not selected(key):
            continue
        for seed in range(20261021,20261026):
            r,_=evaluate(d,features,seed)
            results.append({**key,"test":"repeat_partition","seed":seed,**r})
        # Prespecified modest nonlinearity, no feature search.
        flex=d.copy()
        extras=[]
        for col in FEATURES:
            name=col+"_square"
            flex[name]=flex[col]**2
            extras.append(name)
            if col!="poverty150_adult":
                name=col+"_x_poverty"
                flex[name]=flex[col]*flex.poverty150_adult
                extras.append(name)
        r,_=evaluate(flex,features+extras)
        results.append({**key,"test":"squares_poverty_interactions","seed":20261020,**r})
        if key["source"]=="Medicare":
            r,_=evaluate(d,FEATURES)
            results.append({**key,"test":"no_ma_same_counties","seed":20261020,**r})
            if key["sample"]=="large":
                cats=den[(den.condition_name==key["condition"])&(den.fltr==key["fltr"])]
                sub=d.merge(cats[["fips","dencat"]],on="fips",validate="one_to_one")
                sub=sub[sub.dencat>=4].reset_index(drop=True)
                r,_=evaluate(sub,features)
                results.append({**key,"test":"mmd_denominator_ge5000","seed":20261020,**r})
        # Drop a documented source discrepancy from both data types consistently.
        if key["source"]=="Medicare" and (d.fips=="02122").any():
            r,_=evaluate(d[d.fips!="02122"].reset_index(drop=True),features)
            results.append({**key,"test":"exclude_kenai","seed":20261020,**r})
    pd.DataFrame(results).to_csv(HERE/"sensitivity_results.csv",index=False)
    print(pd.DataFrame(results).groupby(["test","source","sample"]).gain.agg(["min","median","max"]).to_string())

if __name__=="__main__":
    main()
