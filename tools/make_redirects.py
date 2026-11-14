"""Write redirect pages for URLs that were published before the report ids
were renamed (2026-11-14): /reports/d7-N/<page>/ -> /clsinfra-d7N/<page>/.

Anchors of the old scheme (#d7-N-5-3, #d71-5-3) are mapped to the new labels
(#clsinfra-d7N-5-3). Run after the build:

    python tools/make_redirects.py book/_build/html [BASE_URL]
"""
import sys
from pathlib import Path

html = Path(sys.argv[1])
base = sys.argv[2].rstrip("/") if len(sys.argv) > 2 else ""
TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Moved</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>
  var h = location.hash.replace(/^#d7-(\\d)-/, "#clsinfra-d7$1-").replace(/^#d7(\\d)-/, "#clsinfra-d7$1-");
  location.replace("{target}" + h);
</script>
</head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>
"""
n = 0
for rep in sorted(p for p in html.glob("clsinfra-d7*") if p.is_dir()):
    num = rep.name[-1]
    for page in [rep] + sorted(p for p in rep.iterdir() if (p / "index.html").exists()):
        rel = page.relative_to(rep)
        old = html / "reports" / f"d7-{num}" / rel
        target = f"{base}/{rep.name}/" + (f"{rel}/" if str(rel) != "." else "")
        old.mkdir(parents=True, exist_ok=True)
        (old / "index.html").write_text(TEMPLATE.format(target=target), encoding="utf8")
        n += 1
print(f"{n} redirect pages written")
