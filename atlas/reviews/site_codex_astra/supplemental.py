from pathlib import Path
import asyncio,json,hashlib,re,csv
import pandas as pd
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
async def main():
 a=pd.read_csv(ROOT/'outputs/atlas/atlas_county_long.csv',dtype={'fips':str}); result={}
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True)
  page=await browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  await page.goto((ROOT/'site/index.html').as_uri());await page.wait_for_function("document.querySelector('#examples article')")
  # Native d3 formatting of CSV precision vs actual serialized values, all county-mode rows.
  records=[]
  for r in a.itertuples():
   mortality=r.layer=='mortality'; nd=1 if mortality else 2
   records.append([r.fips,r.layer,r.outcome,r.mode,r.observed-r.expected,round(float(r.observed),nd)-round(float(r.expected),nd),mortality])
  diffs=await page.evaluate('''rows=>rows.filter(r=>d3.format(r[6]?'.0f':'.1f')(r[4])!==d3.format(r[6]?'.0f':'.1f')(r[5])).map(r=>[...r.slice(0,6),d3.format(r[6]?'.0f':'.1f')(r[4]),d3.format(r[6]?'.0f':'.1f')(r[5])])''',records)
  with (OUT/'d3_rounding_discrepancies.csv').open('w') as f:
   w=csv.writer(f);w.writerow(['fips','layer','outcome','mode','csv_difference','serialized_difference','csv_display','site_display']);w.writerows(diffs)
  result['native_d3_rounding_mismatches']=len(diffs);result['first_discrepancies']=diffs[:5]
  numeric=[]
  for r in a.itertuples():
   nd=1 if r.layer=='mortality' else 2
   for k in ['observed','expected','difference_shrunk']:
    v=float(getattr(r,k))
    if pd.notna(v):numeric.append([r.fips,r.layer,r.outcome,r.mode,k,v,round(v,nd),r.layer=='mortality'])
  field_diffs=await page.evaluate("rows=>rows.filter(r=>d3.format(r[7]?'.0f':'.1f')(r[5])!==d3.format(r[7]?'.0f':'.1f')(r[6])).map(r=>[...r.slice(0,7),d3.format(r[7]?'.0f':'.1f')(r[5]),d3.format(r[7]?'.0f':'.1f')(r[6])])",numeric)
  with (OUT/'d3_field_rounding_discrepancies.csv').open('w') as f:
   w=csv.writer(f);w.writerow(['fips','layer','outcome','mode','field','csv_value','serialized_value','csv_display','site_display']);w.writerows(field_diffs)
  result['field_rounding_mismatches']=len(field_diffs);result['field_rounding_examples']=field_diffs[:3]

  # Inspect actual chart-bound data and all project tables against source CSVs.
  chart=await page.evaluate('''()=>({r2:[...document.querySelectorAll('#chart-r2 circle')].map(x=>({measure:x.__data__.measure,value:x.__data__.inputs_plus_state_cv,n:x.__data__.n_counties})),pvo:[...document.querySelectorAll('#chart-pvo rect')].filter(x=>x.__data__).map(x=>x.__data__),heroPercent:document.querySelector('[data-bind=r2_median_pct]').textContent,maxGain:document.querySelector('[data-bind=max_gain_pts]').textContent})''')
  crude=pd.read_csv(ROOT/'outputs/covariate_test/r2_by_measure_crudeprev.csv').set_index('measure');pvo=pd.read_csv(ROOT/'outputs/expected_vs_observed/places_vs_observed.csv');pvo=pvo[pvo['sample']=='all'].set_index(['outcome','source'])
  ce=[]
  for r in chart['r2']:
   x=crude.loc[r['measure']]
   if r['value']!=round(float(x.inputs_plus_state_cv),4) or r['n']!=int(x.n_counties):ce.append(r)
  for r in chart['pvo']:
   x=pvo.loc[(r['outcome'],r['source'])]
   for k in ['cv_r2_demo','cv_r2_places','cv_r2_demo_places']:
    if r[k]!=round(float(x[k]),4):ce.append([r['outcome'],k])
  result['charts']={'r2_nodes':len(chart['r2']),'pvo_rows':len(chart['pvo']),'errors':ce,'headline':chart['heroPercent'],'gain':chart['maxGain']}
  result['layout']={}
  for width in [1440,390,320]:
   await page.set_viewport_size({'width':width,'height':900})
   for name in ['index','atlas']:
    await page.goto((ROOT/'site'/f'{name}.html').as_uri());await page.wait_for_timeout(250)
    result['layout'][f'{name}_{width}']=await page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll('body *')].filter(x=>{let r=x.getBoundingClientRect();return r.width&&r.right>innerWidth+1&&!(x.closest('.table-scroll')||x.closest('.tooltip'))}).slice(0,8).map(x=>x.tagName+'.'+x.className)})''')
  await page.set_viewport_size({'width':1440,'height':1000})
  await page.goto((ROOT/'site/atlas.html').as_uri()+'#o=medicare_actual_rheumatoid_arthritis_or_osteoarthritis&s=0&c=01031');await page.wait_for_function("document.querySelector('#status').hidden")
  result['rounding_example_details']=await page.locator('#details').inner_text()
  # Search/pin is a keyboard route to county details; sorting is tested by an actual Tab traversal.
  await page.locator('#search').focus();await page.keyboard.type('Iberia, LA');await page.keyboard.press('Tab');result['keyboard_search']=await page.locator('#details h3').inner_text()
  await page.locator('#table-details summary').focus();await page.keyboard.press('Enter');await page.wait_for_selector('#county-table th');await page.keyboard.press('Tab');result['focus_after_table_summary']=await page.evaluate('document.activeElement.outerHTML.slice(0,300)')
  # Missing data detail for geometry-only county and its notes.
  await page.goto((ROOT/'site/atlas.html').as_uri()+'#o=mortality_diabetes_deaths&c=48301');await page.wait_for_function("document.querySelector('#status').hidden");result['missing_details']=await page.locator('#details').inner_text()
  await browser.close()
 (OUT/'supplemental_results.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
asyncio.run(main())
