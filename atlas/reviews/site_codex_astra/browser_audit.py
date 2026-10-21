import asyncio, json, threading, http.server, functools, re
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'site')))
threading.Thread(target=server.serve_forever,daemon=True).start(); BASE=f'http://127.0.0.1:{server.server_port}'
errors=[]; console=[]; results={'states':[],'interactions':{},'errors':errors,'console':console}
# Verification is separate from app closures; calculate rows, ranks and scales independently.
CHECK=r'''({id,mode,smooth,view})=>{
 const I=ATLAS_INDEX,D=ATLAS_DATA[id],O=I.outcomes.find(x=>x.id===id),M=D[mode];
 const fmt=(v,s=false)=>v===null?'n/a':(s&&v>0?'+':'')+d3.format(O.units==='SMR x 100'?'.0f':'.1f')(v)+(O.units==='SMR x 100'?'':s?' pts':'%');
 const rows=I.counties.map((c,i)=>({...c,i,obs:D.obs[i],exp:M.exp[i],diff:smooth&&O.shrinkage?M.shr[i]:D.obs[i]===null||M.exp[i]===null?null:D.obs[i]-M.exp[i],tier:M.tier[i]}));
 const available=rows.filter(x=>x.obs!==null).sort((a,b)=>b.diff-a.diff);
 const T={0:'Not estimated',1:'High',2:'Moderate',3:'Low'};
 const want=available.map(x=>[x.name,x.st,fmt(x.obs),fmt(x.exp),fmt(x.diff,true),x.tier===null?'n/a':T[x.tier]]);
 const got=Array.from(document.querySelectorAll('#county-table tbody tr'),tr=>Array.from(tr.cells,x=>x.textContent));
 const eligible=rows.filter(x=>x.diff!==null&&(!O.shrinkage||[1,2].includes(x.tier))).sort((a,b)=>b.diff-a.diff);
 const ranked=el=>Array.from(document.querySelectorAll(el+' button'),x=>[x.dataset.fips,x.querySelector('.v').textContent]);
 const rank=(xs)=>xs.map(x=>[x.fips,fmt(x.diff,true)]);
 let mismatches=[];if(JSON.stringify(got)!==JSON.stringify(want))mismatches.push('table');
 if(JSON.stringify(ranked('#top-high'))!==JSON.stringify(rank(eligible.slice(0,8))))mismatches.push('top-high');
 if(JSON.stringify(ranked('#top-low'))!==JSON.stringify(rank(eligible.slice(-8).reverse())))mismatches.push('top-low');
 const vals=rows.map(x=>x[view==='obs'?'obs':view==='exp'?'exp':'diff']);
 const q=(xs,p)=>{xs=xs.filter(x=>x!==null).sort((a,b)=>a-b);let i=(xs.length-1)*p;return xs[Math.floor(i)]+(xs[Math.ceil(i)]-xs[Math.floor(i)])*(i%1)};
 const hi=view==='diff'?Math.max(q(vals.map(x=>x===null?null:Math.abs(x)),.98),1e-6):q(D.obs,.98);
 const lo=view==='diff'?-hi:q(D.obs,.02);
 const ticks=Array.from(document.querySelectorAll('#legend .ticks span'),x=>x.innerText);
 const expectedTicks=view==='diff'?[fmt(lo,true)+'\nlower','0',fmt(hi,true)+'\nhigher']:[fmt(lo),fmt(hi)];
 if(JSON.stringify(ticks)!==JSON.stringify(expectedTicks))mismatches.push('legend');
 const pos=Object.fromEntries(I.counties.map((x,i)=>[x.fips,i]));
 let hatch=0,wrongHatch=0,wrongOpacity=0;
 document.querySelectorAll('#map path.county').forEach(p=>{let i=pos[p.dataset.fips],missing=vals[i]===null;let hatched=p.getAttribute('fill')==='url(#hatch)';hatch+=hatched;if(missing!==hatched)wrongHatch++;let opacity=view==='diff'&&O.shrinkage&&M.tier[i]===3?.28:1;if(+p.getAttribute('fill-opacity')!==opacity)wrongOpacity++});
 if(wrongHatch)mismatches.push('hatching');if(wrongOpacity)mismatches.push('opacity');
 return {id,mode,smooth,view,rows:got.length,mismatches,hatch,lo,hi,ticks};
}'''
async def ready(p):
    await p.wait_for_function("document.querySelector('#status').hidden && document.querySelectorAll('#map path.county').length===3144")
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True)
  results['browser']=browser.version
  ctx=await browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  p=await ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:console.append({'type':m.type,'text':m.text}) if m.type in ['error','warning'] else None)
  await p.goto(BASE+'/index.html');await p.wait_for_function("document.querySelector('#examples article') && document.querySelectorAll('#hero-map .county').length===3144")
  results['index']={'text':await p.locator('main').inner_text(),'r2_rows':await p.locator('#table-r2 tbody tr').all_inner_texts(),'pvo_rows':await p.locator('#table-pvo tbody tr').all_inner_texts()}
  await p.screenshot(path=str(OUT/'index_desktop.png'),full_page=True)
  await p.goto(BASE+'/atlas.html#o=mortality_diabetes_deaths&v=diff&m=nat&s=1&f=1&c=22017');await ready(p)
  results['interactions']['hash_pin']=await p.locator('#details').inner_text()
  await p.locator('#table-details summary').click();await p.wait_for_selector('#county-table tbody tr')
  ids=await p.locator('#outcome option').evaluate_all('(xs)=>xs.map(x=>x.value)')
  for id in ids:
   await p.select_option('#outcome',id);await ready(p)
   for mode in ['nat','ws']:
    await p.locator(f'#mode button[data-m="{mode}"]').click()
    for smooth in [True,False]:
     if await p.locator('#smooth').is_enabled():await p.locator('#smooth').set_checked(smooth)
     elif not smooth:continue
     for view in ['diff','obs','exp']:
      await p.locator(f'#view button[data-v="{view}"]').click()
      result=await p.evaluate(CHECK,{'id':id,'mode':mode,'smooth':smooth,'view':view});results['states'].append(result)
     await p.locator('#view button[data-v="diff"]').click()
   (OUT/'browser_results.json').write_text(json.dumps(results,indent=2));print('checked',id,flush=True)
  await p.goto(BASE+'/atlas.html#o=mortality_diabetes_deaths&v=diff&m=nat&s=1&f=1&c=22017');await ready(p)
  await p.locator('#search').fill('Iberia, LA');await p.locator('#search').press('Tab');results['interactions']['search']=await p.locator('#details').inner_text()
  await p.keyboard.press('Escape');results['interactions']['escape']=await p.locator('#details').inner_text()
  await p.locator('#top-high button').first.click();results['interactions']['extreme_pin']=await p.locator('#details').inner_text()
  await p.locator('#map [data-fips="22017"]').dispatch_event('mousemove',{'clientX':800,'clientY':400});results['interactions']['tooltip']=await p.locator('#tooltip').inner_text()
  await p.locator('#fade').uncheck();results['interactions']['fade_off_opacities']=await p.locator('#map .county').evaluate_all('(xs)=>[...new Set(xs.map(x=>x.getAttribute("fill-opacity")))]')
  
  if not await p.locator('#table-details').evaluate('(e)=>e.open'):await p.locator('#table-details summary').click()
  await p.wait_for_selector('#county-table th');await p.locator('#county-table th[data-k="name"]').click()
  results['interactions']['sort_county']=await p.locator('#county-table tbody tr').first.inner_text()
  results['interactions']['sort_keyboard']=await p.locator('#county-table th').evaluate_all('(xs)=>xs.map(x=>({tag:x.tagName,tabIndex:x.tabIndex,buttons:x.querySelectorAll("button").length}))')
  await p.goto(BASE+'/atlas.html#o=medicare_std_diabetes&v=diff&m=ws&s=1&f=1&c=11001');await ready(p)
  results['interactions']['standardized']={'details':await p.locator('#details').inner_text(),'extremes_heading':await p.locator('.extremes h3').inner_text(),'smooth_disabled':await p.locator('#smooth').is_disabled(),'fade_disabled':await p.locator('#fade').is_disabled()}
  await p.screenshot(path=str(OUT/'atlas_standardized.png'),full_page=True)
  # Browser-native contrast calculation for every visible text node, effective ancestor background.
  contrast_js=r'''()=>{const rgb=s=>(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);const lum=a=>a.map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((s,x,i)=>s+x*[.2126,.7152,.0722][i],0);let out=[];for(const e of document.querySelectorAll('body *')){if(![...e.childNodes].some(x=>x.nodeType===3&&x.textContent.trim())||!e.getClientRects().length)continue;let cs=getComputedStyle(e),a=e,bg;while(a){let c=getComputedStyle(a).backgroundColor;if(c!=='rgba(0, 0, 0, 0)'&&c!=='transparent'){bg=c;break}a=a.parentElement}if(!bg)continue;let l=lum(rgb(cs.color)),b=lum(rgb(bg)),ratio=(Math.max(l,b)+.05)/(Math.min(l,b)+.05),large=parseFloat(cs.fontSize)>=24||(parseFloat(cs.fontSize)>=18.66&&+cs.fontWeight>=700);if(ratio<(large?3:4.5))out.push({selector:e.tagName+'.'+e.className,text:e.textContent.slice(0,100),foreground:cs.color,background:bg,ratio,fontSize:cs.fontSize})}return out}'''
  results['contrast']={}
  for theme in ['light','dark']:
   await p.emulate_media(color_scheme=theme)
   for name in ['index','atlas']:
    await p.goto(BASE+'/'+name+'.html');await p.wait_for_timeout(400)
    results['contrast'][name+'_'+theme]=await p.evaluate(contrast_js)
  for name in ['index','atlas']:
   await p.goto((ROOT/'site'/f'{name}.html').as_uri());await p.wait_for_timeout(500)
   results['interactions']['file_'+name]={'text':await p.locator('main').inner_text(),'county_paths':await p.locator('path.county').count()}
   if name=='atlas':await p.select_option('#outcome','acs_hearing_difficulty');await ready(p);results['interactions']['file_switch']=await p.locator('#map-title').inner_text()
  # Reproduce overlapping loads: slow first request, faster last choice.
  async def delay(route):
   if 'atlas_acs_vision_difficulty.js' in route.request.url:await asyncio.sleep(1)
   await route.continue_()
  race=await ctx.new_page();await race.route('**/data/atlas_*.js',delay)
  await race.goto(BASE+'/atlas.html#o=mortality_diabetes_deaths&c=22017');await ready(race)
  await race.select_option('#outcome','acs_vision_difficulty');await race.select_option('#outcome','medicare_actual_diabetes');await asyncio.sleep(1.5)
  results['race']={'chosen':await race.locator('#outcome').input_value(),'heading':await race.locator('#map-title').inner_text(),'details':await race.locator('#details').inner_text()}
  await race.close()
  await ctx.close();await browser.close()
 (OUT/'browser_results.json').write_text(json.dumps(results,indent=2))
 print('states',len(results['states']),'failures',sum(bool(x['mismatches']) for x in results['states']),'errors',errors,flush=True)
try:asyncio.run(main())
finally:server.shutdown();server.server_close()
