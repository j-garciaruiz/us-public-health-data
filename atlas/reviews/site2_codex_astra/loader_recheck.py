import asyncio,functools,hashlib,http.server,json,threading
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
initial=json.loads((OUT/'hashes_start.json').read_text())
common=(ROOT/'site/assets/common.js').read_text()
removed=common.replace('    // Single-file builds embed every outcome up front; use it when present.\n    if (window.ATLAS_DATA && window.ATLAS_DATA[id]) return window.ATLAS_DATA[id];\n','')
result={'common_change_exactly_two_added_lines':hashlib.sha256(removed.encode()).hexdigest()==initial['site/assets/common.js'],'current_common_sha256':hashlib.sha256(common.encode()).hexdigest()}
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'site')));threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}'
async def ready(p):await p.wait_for_function("document.querySelector('#status').hidden")
async def main():
 async with async_playwright() as pw:
  b=await pw.chromium.launch(headless=True)
  for case in ['reverse_success','stale_failure','table_pending','file_index','file_atlas']:
   p=await b.new_page();errors=[];messages=[]
   p.on('pageerror',lambda e:errors.append(str(e)))
   p.on('console',lambda m:messages.append(m.text) if m.type in ['error','warning'] else None)
   if case.startswith('file'):
    name=case[5:];await p.goto((ROOT/'site'/f'{name}.html').as_uri())
    if name=='atlas':
     await ready(p)
     for o in ['acs_hearing_difficulty','mortality_diabetes_deaths','acs_hearing_difficulty']:
      await p.select_option('#outcome',o);await ready(p)
    else:await p.wait_for_function("document.querySelector('#hero-map .county')")
    result[case]={'errors':errors,'console':messages,'paths':await p.locator('path.county').count()}
   else:
    async def delayed(route):
     await asyncio.sleep(1)
     if case=='stale_failure':await route.abort()
     else:await route.continue_()
    await p.route('**/atlas_acs_vision_difficulty.js',delayed)
    await p.goto(BASE+'/atlas.html#c=22017');await ready(p)
    await p.select_option('#outcome','acs_vision_difficulty')
    if case=='table_pending':await p.locator('#table-details summary').click()
    else:await p.select_option('#outcome','medicare_actual_diabetes')
    await p.wait_for_timeout(1500)
    result[case]={'errors':errors,'title':await p.locator('#map-title').inner_text(),'details':await p.locator('#details').inner_text(),'status_hidden':await p.locator('#status').evaluate('e=>e.hidden')}
   await p.close()
  await b.close()
try:asyncio.run(main())
finally:server.shutdown();server.server_close()
result['changed_since_initial']=[f for f,h in initial.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h]
(OUT/'loader_recheck_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
