"""Source audit, credentials never logged or persisted in review artifacts."""
from pathlib import Path
import concurrent.futures
import urllib.request
import json
import re
import pandas as pd
from replicate import HERE, ROOT

def fetch(url):
    try:
        with urllib.request.urlopen(url,timeout=180) as response:
            return json.load(response)
    except Exception:
        # urllib exceptions can contain the credential-bearing URL.
        raise RuntimeError("Source request failed; URL and credential omitted") from None

def cms():
    m=pd.read_csv(ROOT/"data/raw/mmd_prevalence_2023.csv",dtype={"fips":str})
    jobs=m.dropna(subset=["places_measure"])[["condition_code","condition","fltr"]].drop_duplicates()
    def one(row):
        q=("https://data.cms.gov/data-api/v1/mmd-tool/?_source=prev_final_long_fltr12_racecat_all_sexcat_all_23_p"
           f"&population=f&year=23&geography=c&measure=v&condition={row.condition_code}"
           "&sexcat=.|IS%20NULL&agecat=.|IS%20NULL&dual=.|IS%20NULL&eligcat=.|IS%20NULL"
           f"&racecat=.|IS%20NULL&fltr={row.fltr}&_size=500000")
        data=fetch(q)
        (HERE/f"cms_{row.condition}_fltr{row.fltr}_live.json").write_text(json.dumps(data))
        d=pd.DataFrame(data)
        d["condition_name"]=row.condition
        return d
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        frames=list(pool.map(one,jobs.itertuples(index=False)))
    d=pd.concat(frames,ignore_index=True)
    for col in ["condition","fltr","rate","dencat"]:
        d[col]=pd.to_numeric(d[col])
    x=d.merge(m,on=["fips","fltr"],how="inner",suffixes=("_live","_file"))
    x=x[x.condition_live.eq(x.condition_code)]
    assert len(x)==len(d)
    assert (x.rate_live==x.rate_file).all()
    d[["fips","condition_name","fltr","rate","dencat"]].to_csv(HERE/"cms_denominator_categories.csv",index=False)
    g=pd.read_csv(ROOT/"data/raw/medicare_gv_county_2023.csv",dtype={"fips":str})
    for col in ["BENES_OM_CNT","BENES_MA_CNT"]:
        g[col]=pd.to_numeric(g[col],errors="coerce")
    z=d.merge(g[["fips","BENES_OM_CNT","BENES_MA_CNT"]],on="fips",how="left")
    z[(z.BENES_OM_CNT>=5000)&(z.dencat<4)].to_csv(HERE/"large_county_small_mmd_denominator.csv",index=False)
    print("All requested CMS series exact:",len(d),flush=True)

def census():
    # User-authorized existing Census API key, used only in memory for requests.
    content=(ROOT/".env").read_text()
    match=re.search(r"(?m)^CENSUS_API_KEY\s*=\s*(.+)$",content)
    if not match:
        raise RuntimeError("Census key not found")
    key=match.group(1).strip().strip("'\"")
    checks, mapping, counts=[],[],[]
    original=pd.read_csv(ROOT/"data/raw/acs_disability_2023.csv",dtype={"fips":str}).set_index("fips")
    for table, measure in zip(range(18102,18108),["hearing","vision","cognition","mobility","selfcare","indeplive"]):
        t=f"B{table}"
        meta=fetch(f"https://api.census.gov/data/2023/acs/acs5/groups/{t}.json")
        (HERE/f"{t}_metadata.json").write_text(json.dumps(meta))
        # Select adult age-band totals by exact known age labels, not positions.
        bands={"18 to 34 years:","35 to 64 years:","65 to 74 years:","75 years and over:"}
        nums,dens=[],[]
        for var, val in meta["variables"].items():
            if not re.fullmatch(t+r"_\d{3}E",var):
                continue
            parts=val["label"].split("!!")
            if len(parts)>=4 and parts[3] in bands:
                if len(parts)==4: dens.append(var)
                elif len(parts)==5 and parts[4].startswith(("With a ", "With an ")): nums.append(var)
        assert len(nums)==len(dens)==8, "Expected four adult bands by two sexes"
        data=fetch(f"https://api.census.gov/data/2023/acs/acs5?get=group({t})&for=county:*&key={key}")
        d=pd.DataFrame(data[1:],columns=data[0])
        d["fips"]=d.state+d.county
        v=d.set_index("fips")[nums+dens].apply(pd.to_numeric,errors="coerce")
        assert not v.index.duplicated().any()
        assert (v>=0).all().all()
        n=v[nums].sum(axis=1,min_count=len(nums))
        den=v[dens].sum(axis=1,min_count=len(dens))
        rate=100*n/den
        diff=rate-original[f"acs_{measure}"]
        assert diff.notna().all() and diff.abs().max()<1e-10
        checks.append(dict(measure=measure,n=len(rate),numerator_cells=len(nums),
                           denominator_cells=len(dens),max_abs_error=diff.abs().max()))
        counts.append(pd.DataFrame(dict(fips=rate.index,measure=measure,numerator=n,denominator=den,rate=rate)))
        for kind, cols in [("numerator",nums),("denominator",dens)]:
            for col in cols: mapping.append(dict(table=t,kind=kind,variable=col,label=meta["variables"][col]["label"]))
    pd.DataFrame(checks).to_csv(HERE/"acs_live_checks.csv",index=False)
    pd.DataFrame(mapping).to_csv(HERE/"acs_disability_mapping.csv",index=False)
    pd.concat(counts,ignore_index=True).to_csv(HERE/"acs_disability_counts_live.csv",index=False)
    print(pd.DataFrame(checks).to_string(index=False),flush=True)

if __name__=="__main__":
    cms()
    census()
