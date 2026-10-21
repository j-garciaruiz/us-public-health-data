"""Local-only rendering of the report. Never follows external links."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("https://**/*", lambda route: route.abort())
    page.route("http://**/*", lambda route: route.abort())
    page.goto((ROOT / "pharma/report/index.html").as_uri())
    page.locator("details").evaluate_all("es => es.forEach(e => e.open=true)")
    (OUT / "rendered_text.txt").write_text(page.locator("body").inner_text())
    links = page.locator("a").evaluate_all("es => es.map(e=>({text:e.textContent,url:e.getAttribute('href')}))")
    (OUT / "links.json").write_text(json.dumps(links, indent=2))
    (OUT / "embedded_data.json").write_text(json.dumps(page.evaluate("D"), indent=2))
    checks = {"page_errors": errors, "charts": {}, "tooltips": {}, "controls": []}
    for name in ["chartF1", "chartF2", "chartF3", "chartF4", "chartCal", "chartPred"]:
        chart = page.locator("#"+name)
        chart.screenshot(path=str(OUT / (name+".png")))
        checks["charts"][name] = chart.locator("svg").count()
        hits = chart.locator('[fill="transparent"]')
        checks["tooltips"][name] = []
        for i in range(hits.count()):
            hits.nth(i).dispatch_event("mousemove", {"clientX": 500, "clientY": 100, "pageX": 500, "pageY": 100})
            checks["tooltips"][name].append(page.locator("#tip").inner_text())
    for selector in ["#f2win button", "#f3pick button"]:
        for i in range(page.locator(selector).count()):
            b = page.locator(selector).nth(i)
            label = b.inner_text()
            b.click()
            checks["controls"].append({"label": label, "pressed": page.locator(selector).nth(i).get_attribute("aria-pressed")})
    page.locator('#f2win button').nth(1).click()
    page.locator('#chartF2').screenshot(path=str(OUT / 'chartF2_feb.png'))
    for name in ['tblPred','tblCuts']:
        for i in range(page.locator(f'#{name} th.sortable').count()):
            page.locator(f'#{name} th.sortable').nth(i).click()
    page.locator('#themeBtn').click()
    page.locator('#chartCal').screenshot(path=str(OUT / 'chartCal_dark.png'))
    checks['desktop_overflow'] = page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.set_viewport_size({'width':390, 'height':844})
    checks['phone_overflow'] = page.evaluate('document.documentElement.scrollWidth > innerWidth')
    (OUT / 'render_checks.json').write_text(json.dumps(checks, indent=2))
    browser.close()
print(json.dumps({k:v for k,v in checks.items() if k != 'tooltips'}, indent=2))
