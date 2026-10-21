import asyncio, ast, functools, hashlib, http.server, json, threading
from pathlib import Path
import numpy as np
import pandas as pd
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent

def readout(name):
    s=(ROOT/'site/data'/name).read_text(); return json.loads(s[s.index('= {')+2:].rstrip(';\n'))
def hashes():
    paths=[*list((ROOT/'site').rglob('*')),ROOT/'scripts/export_site_data.py',ROOT/'outputs/atlas/atlas_county_long.csv']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
start=hashes(); (OUT/'hashes_start.json').write_text(json.dumps(start,indent=2))
I=readout('atlas_index.js'); F=readout('findings.js'); counties=[c['fips'] for c in I['counties']]
a=pd.read_csv(ROOT/'outputs/atlas/atlas_county_long.csv',dtype={'fips':str})
results={'numeric':{'checked':0,'mismatches':[]},'rounding':{'checked':0,'mismatches':[]},'guard':[], 'errors':[]}
# Execute only the actual guard AST, never the exporter or its writes.
tree=ast.parse((ROOT/'scripts/export_site_data.py').read_text())
guard=ast.Module(body=[n for n in tree.body if 62<=n.lineno<=68],type_ignores=[])
code=compile(guard,'export_site_data.py:guard','exec')
for label,count,flag,obs,matched in [('zero',0,False,0,True),*[(f'count_{n}',n,False,1,True) for n in range(1,10)],('ten',10,False,100,True),('suppressed',20,True,100,True),('missing_count',np.nan,False,100,True),('missing_flag',20,np.nan,100,True),('missing_match',20,False,100,False),('missing_observation',20,False,np.nan,True),('infinite_count',np.inf,False,100,True)]:
    ns={'atlas':pd.DataFrame([{'fips':'99999','layer':'mortality','outcome':'Diabetes deaths','observed':obs}]),'smr_src':pd.DataFrame([{'fips':'99999' if matched else '99998','cause':'diabetes','observed':count,'suppressed':flag}])}
    try: exec(code,ns); passed=True
    except AssertionError: passed=False
    results['guard'].append({'synthetic_case':label,'accepted':passed,'expected_accept':label=='ten'})
# Current public mortality checked against raw count eligibility, without exporting small cells.
raw=pd.read_csv(ROOT/'data/raw/wonder/county_cause_2018_2024.txt',sep='\t',dtype=str)
raw=raw[raw['County Code'].str.fullmatch(r'\d{5}',na=False)].copy();raw['fips']=raw['County Code'].replace({'02270':'02158','46113':'46102'})
causes={'Diabetes deaths':'GR113-046','Heart disease deaths':'GR113-054','Cerebrovascular deaths':'GR113-070','Chronic lower respiratory deaths':'GR113-082'}
results['mortality']=[]
for o in I['outcomes']:
    d=readout('atlas_'+o['id']+'.js')
    g=a[(a.layer==o['layer'])&(a.outcome==o['label'])]
    for mode,src in [('nat','national'),('ws','within_state')]:
        frame=g[g['mode']==src].set_index('fips').reindex(counties)
        for key,col in [('obs','observed'),('exp','expected'),('raw','difference'),('shr','difference_shrunk')]:
            vals=d[key] if key=='obs' else d[mode][key]
            want=[None if pd.isna(v) else float(v) for v in frame[col]]
            results['numeric']['checked']+=len(want)
            results['numeric']['mismatches'] += [[o['id'],mode,key,counties[i],x,y] for i,(x,y) in enumerate(zip(vals,want)) if x!=y]
    if o['layer']=='mortality':
        counts=pd.to_numeric(raw[raw['UCD - ICD-10 113 Cause List Code']==causes[o['label']]].set_index('fips')['Deaths'],errors='coerce')
        unsafe=0; hidden_leaks=0; published=[]
        for i,f in enumerate(counties):
            n=counts.get(f,np.nan); eligible=pd.notna(n) and n>=10
            if d['obs'][i] is not None:
                unsafe+=int(not eligible)
                if eligible: published.append(float(n))
            if not eligible:
                hidden_leaks+=sum(d[k][i] is not None for k in ['obs','note','disc'])
                hidden_leaks+=sum(d[m][k][i] is not None for m in ['nat','ws'] for k in ['exp','raw','shr','rel','tier'])
        results['mortality'].append({'id':o['id'],'published':len(published),'minimum_published_count':min(published),'unsafe_observations':unsafe,'ineligible_derived_values':hidden_leaks})
results['coverage']={'min':min(o['counties'] for o in I['outcomes']),'max':max(o['counties'] for o in I['outcomes']),'layers':len(I['outcomes']),'unique_outcomes':a.outcome.nunique()}
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'site')))
threading.Thread(target=server.serve_forever,daemon=True).start(); BASE=f'http://127.0.0.1:{server.server_port}'
async def ready(p):
    await p.wait_for_function("document.querySelector('#status').hidden && document.querySelectorAll('#map path.county').length===3144")
linejs=r'''()=>[...document.querySelectorAll('h1,h2,h3,.ex-num')].filter(e=>e.getClientRects().length).map(e=>{let lines={};let w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);while(w.nextNode()){let n=w.currentNode;for(let m of n.textContent.matchAll(/\S+/g)){let r=document.createRange();r.setStart(n,m.index);r.setEnd(n,m.index+m[0].length);let box=r.getBoundingClientRect();let y=Math.round(box.top);(lines[y]??=[]).push(m[0]);}}return {text:e.textContent,lines:Object.values(lines).map(x=>x.join(' '))}})'''
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(headless=True)
  results['browser']={'version':b.version,'playwright':'1.58.0','headless_shell':True}
  ctx=await b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  p=await ctx.new_page();p.on('pageerror',lambda e:results['errors'].append(str(e)))
  await p.goto(BASE+'/index.html');await p.wait_for_function("document.querySelector('#examples article') && document.querySelector('#hero-map .county')")
  await p.locator('details').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
  (OUT/'index_visible_text.txt').write_text(await p.locator('body').inner_text())
  results['index_tooltips']=[]
  for node in await p.locator('#chart-r2 circle, #chart-r2 path:not(.domain), #chart-pvo rect').all():
   await node.dispatch_event('mousemove',{'clientX':600,'clientY':300})
   if await p.locator('#tooltip').evaluate("e=>e.classList.contains('on')"):results['index_tooltips'].append(await p.locator('#tooltip').inner_text())
   await node.dispatch_event('mouseleave')
  # Browser-native formatting of source CSV versus actual new exported arrays, all rows.
  for o in I['outcomes']:
   d=readout('atlas_'+o['id']+'.js'); g=a[(a.layer==o['layer'])&(a.outcome==o['label'])]
   records=[]
   for m,sm in [('nat','national'),('ws','within_state')]:
    frame=g[g['mode']==sm].set_index('fips').reindex(counties)
    for key,col in [('obs','observed'),('exp','expected'),('raw','difference'),('shr','difference_shrunk')]:
     vals=d[key] if key=='obs' else d[m][key]
     records.extend([[counties[i],m,key,float(v),vals[i]] for i,v in enumerate(frame[col]) if pd.notna(v)])
   fmt='.0f' if o['layer']=='mortality' else '.1f'
   bad=await p.evaluate("({rows,fmt})=>rows.filter(r=>d3.format(fmt)(r[3])!==d3.format(fmt)(r[4]))",{'rows':records,'fmt':fmt})
   results['rounding']['checked']+=len(records);results['rounding']['mismatches'] += [[o['id'],*x] for x in bad]
  # Rounded project-page findings: separately compare all displayed PVO series.
  v=pd.read_csv(ROOT/'outputs/expected_vs_observed/places_vs_observed.csv')
  rr=[]
  for row in F['places_vs_observed']:
   src=v[(v.outcome==row['outcome'])&(v.source==row['source'])&(v['sample']==row['sample'])].iloc[0]
   for k in ['cv_r2_places','cv_r2_demo','cv_r2_demo_places']:rr.append([row['outcome'],row['sample'],k,float(src[k]),row[k]])
  results['pvo_rounding']=await p.evaluate("rows=>rows.filter(r=>d3.format('.1%')(r[3])!==d3.format('.1%')(r[4])).map(r=>[...r,d3.format('.1%')(r[3]),d3.format('.1%')(r[4])])",rr)
  results['layout']={};results['heading_lines']={}
  for width in [1440,1024,768,390,320]:
   await p.set_viewport_size({'width':width,'height':1000})
   for name in ['index','atlas']:
    await p.goto(BASE+'/'+name+'.html'); await p.wait_for_timeout(150)
    await p.evaluate('document.fonts.ready')
    if name=='index':await p.wait_for_function("document.querySelector('#examples article')")
    else:await ready(p)
    results['layout'][f'{name}_{width}']=await p.evaluate("()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})")
    results['heading_lines'][f'{name}_{width}']=await p.evaluate(linejs)
    if width in [1440,320]:await p.screenshot(path=str(OUT/f'{name}_{width}.png'),full_page=True)
  await p.set_viewport_size({'width':1440,'height':1000})
  await p.emulate_media(color_scheme='dark');await p.goto(BASE+'/index.html');await p.wait_for_function("document.querySelector('#examples article')")
  results['button_colors']=await p.locator('.btn-primary').evaluate("e=>{let s=getComputedStyle(e);return {foreground:s.color,background:s.backgroundColor,size:s.fontSize}}")
  await p.screenshot(path=str(OUT/'index_dark.png'),full_page=True)
  await p.emulate_media(color_scheme='light')
  await p.goto(BASE+'/atlas.html#o=medicare_actual_rheumatoid_arthritis_or_osteoarthritis&s=0&c=01031');await ready(p)
  results['coffee_details']=await p.locator('#details').inner_text()
  await p.locator('#map [data-fips="01031"]').dispatch_event('mousemove',{'clientX':800,'clientY':400});results['coffee_tooltip']=await p.locator('#tooltip').inner_text()
  await p.locator('#table-details summary').focus();await p.keyboard.press('Enter');await p.wait_for_selector('#county-table th button');await p.keyboard.press('Tab')
  results['keyboard']={'first_focus':await p.evaluate('document.activeElement.outerHTML')}
  await p.keyboard.press('Enter');results['keyboard']['after_enter']={'first_row':await p.locator('#county-table tbody tr').first.inner_text(),'aria_sort':await p.locator('#county-table th').first.get_attribute('aria-sort'),'focus':await p.evaluate('document.activeElement.outerHTML')}
  await p.keyboard.press('Space');results['keyboard']['after_space']={'first_row':await p.locator('#county-table tbody tr').first.inner_text(),'aria_sort':await p.locator('#county-table th').first.get_attribute('aria-sort')}
  results['coffee_table']=await p.locator('#county-table tbody tr').filter(has_text='Coffee').all_inner_texts()
  # Read every generated about panel plus both expectation descriptions.
  results['atlas_text']=[]
  for o in I['outcomes']:
   await p.select_option('#outcome',o['id']);await ready(p)
   for mode in ['nat','ws']:
    await p.locator(f'#mode button[data-m="{mode}"]').click()
    results['atlas_text'].append({'id':o['id'],'mode':mode,'about':await p.locator('#about').inner_text(),'subtitle':await p.locator('#map-sub').inner_text(),'extremes':await p.locator('#ext-title').inner_text()})
  results['file']={}
  for name in ['index','atlas']:
   q=await ctx.new_page();messages=[];errs=[]
   q.on('console',lambda m:messages.append({'type':m.type,'text':m.text}) if m.type in ['error','warning'] else None)
   q.on('pageerror',lambda e:errs.append(str(e)))
   await q.goto((ROOT/'site'/f'{name}.html').as_uri())
   if name=='atlas':
    await ready(q);await q.select_option('#outcome','acs_hearing_difficulty');await ready(q)
   else:await q.wait_for_function("document.querySelector('#hero-map .county')")
   await q.wait_for_timeout(600)
   results['file'][name]={'console':messages.copy(),'errors':errs.copy(),'county_paths':await q.locator('path.county').count()}
   await q.close()
  async def race_test(fail=False,toggle=False):
   q=await ctx.new_page();errs=[];q.on('pageerror',lambda e:errs.append(str(e)))
   async def delay(route):
    await asyncio.sleep(1)
    if fail: await route.abort()
    else: await route.continue_()
   await q.route('**/atlas_acs_vision_difficulty.js',delay)
   await q.goto(BASE+'/atlas.html#o=mortality_diabetes_deaths&c=22017');await ready(q)
   await q.select_option('#outcome','acs_vision_difficulty')
   if toggle:
    await q.locator('#table-details summary').click();await q.wait_for_timeout(100)
   else:await q.select_option('#outcome','medicare_actual_diabetes')
   await q.wait_for_timeout(1500)
   r={'selected':await q.locator('#outcome').input_value(),'title':await q.locator('#map-title').inner_text(),'details':await q.locator('#details').inner_text(),'status_hidden':await q.locator('#status').evaluate('e=>e.hidden'),'errors':errs}
   await q.close();return r
  results['race']=await race_test();results['race_stale_failure']=await race_test(fail=True);results['pending_table']=await race_test(toggle=True)
  await ctx.close();await b.close()
try:asyncio.run(main())
finally:server.shutdown();server.server_close()
results['unchanged_inputs']=start==hashes()
(OUT/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False))
print(json.dumps({k:v for k,v in results.items() if k not in ['atlas_text','index_tooltips','heading_lines']},indent=2))
