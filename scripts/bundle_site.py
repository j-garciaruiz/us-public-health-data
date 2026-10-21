"""Bundle the site into self-contained single HTML files for sharing.

site/index.html -> dist/expected_vs_observed.html        (project page)
site/atlas.html -> dist/expected_vs_observed_atlas.html  (atlas, all 34 layers inlined)

Stylesheets, scripts, data files and the Geist fonts (as base64) are inlined,
so each file opens on its own (double-click, email attachment, phone preview).
The two files link to each other by their new names when kept side by side.
"""

import base64
import os
import re

SITE, DIST = "site", "dist"
os.makedirs(DIST, exist_ok=True)
NAMES = {"index.html": "expected_vs_observed.html", "atlas.html": "expected_vs_observed_atlas.html"}


def read(path):
    with open(os.path.join(SITE, path), encoding="utf-8") as f:
        return f.read()


def inline_css(html):
    def repl(m):
        css = read(m.group(1))
        def font(fm):
            data = base64.b64encode(open(os.path.join(SITE, "assets", fm.group(1)), "rb").read()).decode()
            return f'url("data:font/woff2;base64,{data}")'
        css = re.sub(r'url\("(\.\./fonts/[^"]+)"\)', font, css)
        return f"<style>\n{css}\n</style>"
    return re.sub(r'<link rel="stylesheet" href="([^"]+)">', repl, html)


def inline_js(html, extra=""):
    def repl(m):
        src = m.group(1)
        js = read(src).replace("</script>", "<\\/script>")
        return f"<script>/* {src} */\n{js}\n</script>"
    html = re.sub(r'<script src="([^"]+)"></script>', repl, html)
    if extra:
        html = html.replace("<script>/* assets/common.js */", extra + "\n<script>/* assets/common.js */", 1)
    return html


def relink(html):
    for old, new in NAMES.items():
        html = re.sub(rf'href="{re.escape(old)}([#"])', rf'href="{new}\1', html)
    # links built in JavaScript
    html = html.replace('`atlas.html#', f'`{NAMES["atlas.html"]}#').replace('href="atlas.html"', f'href="{NAMES["atlas.html"]}"')
    return html


def all_outcomes():
    parts = []
    for f in sorted(os.listdir(os.path.join(SITE, "data"))):
        if f.startswith("atlas_") and f != "atlas_index.js":
            parts.append(read(f"data/{f}"))
    return "<script>/* all atlas layers */\n" + "\n".join(parts) + "\n</script>"


def hero_outcome():
    return "<script>/* hero layer */\n" + read("data/atlas_mortality_diabetes_deaths.js") + "\n</script>"


for src, extra in [("index.html", hero_outcome()), ("atlas.html", all_outcomes())]:
    html = read(src)
    html = inline_css(html)
    html = inline_js(html, extra)
    html = relink(html)
    assert "<link rel=\"stylesheet\"" not in html and 'src="' not in html.replace('src="data:', "")
    out = os.path.join(DIST, NAMES[src])
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(out, f"{os.path.getsize(out) / 1e6:.1f} MB")
