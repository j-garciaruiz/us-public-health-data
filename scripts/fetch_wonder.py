"""Pull county mortality from CDC WONDER (Multiple Cause of Death, 2018-2024, single race).

WONDER blocks scripted HTTP clients and its API refuses sub-national queries,
so this drives the public web form with a headless browser (Playwright,
chromium-headless-shell). It clicks "I Agree" on the NCHS data use agreement:
Johnattan accepted those terms on 2026-10-20. Terms that bind every use of
these data: health statistical analysis only; never publish counts of 9 or
fewer (or rates based on them); no attempt to identify anyone.

Queries (all years 2018-2024 pooled, underlying cause, ICD-10 113 list):
  county_cause:  deaths and population by county x cause (diabetes, heart
                 disease, cerebrovascular, chronic lower respiratory)
  national_age:  deaths and population by 10-year age group x cause, US total
WONDER does not give age-adjusted rates at county level, so the analysis uses
indirect standardization (national age-specific rates applied to each
county's age structure).

Outputs: data/raw/wonder/*.txt (WONDER export format, tab-delimited + notes).
"""

import os
import re
import sys

from playwright.sync_api import sync_playwright

OUT = "data/raw/wonder"
os.makedirs(OUT, exist_ok=True)
URL = "https://wonder.cdc.gov/mcd-icd10-expanded.html"
CAUSES = ["GR113-046", "GR113-054", "GR113-070", "GR113-082"]

QUERIES = {
    "county_cause": {"B_1": "D157.V9-level2", "B_2": "D157.V4"},
    "national_age": {"B_1": "D157.V5", "B_2": "D157.V4"},
}

JS = """
async ([overrides, causes]) => {
  const form = document.forms['form'];
  const fd = new FormData(form);
  fd.set('O_change_action-Send-Export Results', 'Export Results');
  fd.set('action-Send', 'Send');
  fd.set('O_aar', 'aar_none'); fd.delete('O_aar_enable');
  fd.set('O_show_suppressed', 'true'); fd.set('O_show_zeros', 'true'); fd.delete('O_show_totals');
  fd.set('O_ucd', 'D157.V4');
  fd.delete('V_D157.V4'); causes.forEach(c => fd.append('V_D157.V4', c));
  for (const [k, v] of Object.entries(overrides)) fd.set(k, v);
  const r = await fetch(form.action, {method: 'POST', body: new URLSearchParams(fd), credentials: 'include'});
  return await r.text();
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()  # chromium-headless-shell
    page = browser.new_page(user_agent=(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/145.0 Safari/537.36"))
    page.goto(URL, wait_until="domcontentloaded")
    page.locator("input[type=submit][value*='Agree'], button:has-text('I Agree')").last.click()
    page.wait_for_selector("form[name=form]", timeout=60000)
    for name, overrides in QUERIES.items():
        for attempt in range(3):  # WONDER occasionally returns an error page; retry
            txt = page.evaluate(JS, [overrides, CAUSES])
            if not txt.lstrip().startswith("<"):
                break
            page.wait_for_timeout(5000)
        if txt.lstrip().startswith("<"):
            msgs = re.findall(r'class="[^"]*rror[^"]*"[^>]*>(.*?)</', txt, flags=re.S)
            print(name, "FAILED:", [re.sub(r"\s+", " ", m).strip()[:300] for m in msgs][:4], file=sys.stderr)
            continue
        path = f"{OUT}/{name}_2018_2024.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        print(name, "rows:", txt.count("\n"), "->", path)
    browser.close()
