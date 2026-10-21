import asyncio,json,re
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
r=json.loads((OUT/'results.json').read_text());out={}
def lum(rgb):
    v=[x/255 for x in rgb];return sum((x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)*w for x,w in zip(v,[.2126,.7152,.0722]))
out['dark_button_contrast']=1.05/(lum([134,182,239])+.05)
out['proposed_button_contrast']=1.05/(lum([28,92,171])+.05)
v=pd.read_csv(ROOT/'outputs/expected_vs_observed/places_vs_observed.csv');c=pd.read_csv(ROOT/'outputs/covariate_test/r2_by_measure_crudeprev.csv')
out['statistics']={'crude_median':float(c.inputs_plus_state_cv.median()),'crude_county_min':int(c.n_counties.min()),'crude_county_max':int(c.n_counties.max()),'baseline_wins':int((v.cv_r2_demo>v.cv_r2_places).sum()),'comparison_count':len(v),'gains':{s:float((d.cv_r2_demo_places-d.cv_r2_demo).max()*100) for s,d in v.groupby('sample')}}
out['em_dashes']=[str(p.relative_to(ROOT)) for p in [ROOT/'site/index.html',ROOT/'site/atlas.html',*list((ROOT/'site/assets').glob('*.js')),*list((ROOT/'site/assets').glob('*.css'))] if '\u2014' in p.read_text() or '&mdash;' in p.read_text() or '&#8212;' in p.read_text()]
linejs=r'''e=>{let lines={};let w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);while(w.nextNode()){let n=w.currentNode;for(let m of n.textContent.matchAll(/\S+/g)){let r=document.createRange();r.setStart(n,m.index);r.setEnd(n,m.index+m[0].length);let box=r.getBoundingClientRect();(lines[Math.round(box.top)]??=[]).push(m[0]);}}return Object.values(lines).map(x=>x.join(' '))}'''
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(headless=True);p=await b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  await p.goto((ROOT/'site/index.html').as_uri());await p.wait_for_function("document.querySelector('#examples article')");await p.evaluate('document.fonts.ready')
  out['replacement_heading_checks']={}
  for width in [1440,1024,768,390,320]:
   await p.set_viewport_size({'width':width,'height':1000})
   await p.locator('#f1-title').evaluate("e=>e.innerHTML='Demographics + state<br>explain most<br>PLACES variation'")
   await p.locator('#examples h3').first.evaluate("e=>e.innerHTML='Diabetes deaths:<br>Caddo&nbsp;Parish, Louisiana'")
   out['replacement_heading_checks'][str(width)]={'f1':await p.locator('#f1-title').evaluate(linejs),'caddo':await p.locator('#examples h3').first.evaluate(linejs),'overflow':await p.evaluate('document.documentElement.scrollWidth>innerWidth')}
  await p.set_viewport_size({'width':1440,'height':1000})
  await p.goto((ROOT/'site/atlas.html').as_uri()+'#o=medicare_actual_diabetes&s=0');await p.wait_for_function("document.querySelector('#status').hidden")
  await p.locator('#table-details summary').focus();await p.keyboard.press('Enter');await p.wait_for_selector('#county-table th button');await p.keyboard.press('Tab')
  out['all_sort_keys']=[]
  for k in ['name','st','obs','exp','diff','tier']:
   assert await p.evaluate('document.activeElement.dataset.k')==k
   await p.keyboard.press('Enter')
   expected='ascending' if k in ['name','st'] else 'descending'
   assert await p.locator(f'#county-table th:has(button[data-k="{k}"])').get_attribute('aria-sort')==expected
   for _ in range(2):
    rows=await p.locator('#county-table tbody tr').evaluate_all('(xs)=>xs.map(x=>[...x.cells].map(c=>c.textContent))')
    col=['name','st','obs','exp','diff','tier'].index(k)
    def val(row):
     if col<2:return row[col]
     if col==5:return {'Not estimated':0,'High':1,'Moderate':2,'Low':3}[row[col]]
     return float(re.sub(r'[^0-9.\-]','',row[col].replace('−','-')))
    vals=[val(x) for x in rows]
    good=vals==sorted(vals,reverse=expected=='descending')
    out['all_sort_keys'].append({'key':k,'direction':expected,'rows':len(rows),'ordered':good,'focus_preserved':await p.evaluate('document.activeElement.dataset.k')==k})
    if _==0:
     await p.keyboard.press('Space');expected='descending' if expected=='ascending' else 'ascending'
   await p.keyboard.press('Tab')
  await b.close()
asyncio.run(main());(OUT/'followup_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
