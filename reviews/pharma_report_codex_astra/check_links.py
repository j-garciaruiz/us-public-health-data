"""HEAD requests for cited URLs; metadata only for DOI and dataset identity."""
import concurrent.futures, json, urllib.request, urllib.error
from pathlib import Path

OUT=Path(__file__).resolve().parent
def get(url, method='GET'):
    req=urllib.request.Request(url,method=method,headers={'User-Agent':'Mozilla/5.0 (source verification)'})
    with urllib.request.urlopen(req,timeout=35) as r:
        return r.status,r.url,r.read() if method=='GET' else b''
def check(link):
    result=dict(link)
    try:
        status,url,_=get(link['url'],'HEAD')
        result.update(status=status,final_url=url)
    except urllib.error.HTTPError as e:
        result.update(status=e.code,final_url=e.url)
    except Exception as e:
        result['error']=str(e)
    if 'doi.org/' in link['url']:
        doi=link['url'].split('doi.org/')[1]
        try:
            _,_,raw=get('https://api.crossref.org/works/'+doi)
            m=json.loads(raw)['message']
            result['crossref']={k:m.get(k) for k in ['title','container-title','published','author','URL']}
        except Exception as e:
            result['metadata_error']=str(e)
    return result
links=[l for l in json.loads((OUT/'links.json').read_text()) if l['url'].startswith('https:')]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(check,links))
(OUT/'link_audit.json').write_text(json.dumps(results,indent=2))
for r in results:
    print(r['text'],r.get('status',r.get('error')),r.get('crossref',{}).get('title',''))

# Catalog metadata only. Do not retrieve any distribution or data rows.
catalog_urls={
 'medicaid':'https://data.medicaid.gov/api/1/metastore/schemas/dataset/items?show-reference-ids=false',
 'cms':'https://data.cms.gov/data.json',
}
metadata={}
for kind,url in catalog_urls.items():
    try:
        _,_,raw=get(url)
        cat=json.loads(raw)
        rows=cat if isinstance(cat,list) else cat['dataset']
        wanted=[]
        for d in rows:
            title=d.get('title','')
            if kind=='medicaid':
                use=title in ['NADAC (National Average Drug Acquisition Cost) 2026','NADAC Comparison'] or d.get('identifier')=='fbb83258-11c7-47f5-8b18-5f8e79f7e704'
            else:
                use=title in ['Medicare Quarterly Part D Spending by Drug','Quarterly Prescription Drug Plan Formulary, Pharmacy Network, and Pricing Information']
            if use:
                wanted.append({k:d.get(k) for k in ['title','identifier','landingPage','description']})
        metadata[kind]=wanted
    except Exception as e:
        metadata[kind]={'error':str(e)}
(OUT/'catalog_metadata.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata,indent=2))
