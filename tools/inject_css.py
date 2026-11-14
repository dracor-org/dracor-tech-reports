"""Inline book/_static/custom.css into the <head> of every exported HTML page.

The book theme accepts site.options.style but the static HTML export does not
link the stylesheet, so the rules (e.g. .mark for highlights) are inlined here
after the build. Usage: python tools/inject_css.py book/_build/html
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
css = Path("book/_static/custom.css").read_text(encoding="utf8")
tag = f'<style id="rtfr-custom-css">{css}</style>'
n = 0
for f in root.rglob("*.html"):
    t = f.read_text(encoding="utf8")
    if 'id="rtfr-custom-css"' in t or "</head>" not in t:
        continue
    f.write_text(t.replace("</head>", tag + "</head>", 1), encoding="utf8")
    n += 1
print(f"custom CSS inlined into {n} pages")
