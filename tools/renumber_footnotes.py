"""Renumber footnotes consecutively across the pages of one report.

MyST displays the footnote label, so after alignment edits that remove or add
footnotes the numbers would no longer match the published PDF. Pages are
processed in the given order; labels are renumbered by first reference.

Usage: python tools/renumber_footnotes.py DIR page1.md page2.md ...
"""
import re
import sys
from pathlib import Path

REF = re.compile(r"\[\^([^\]]+)\]")

d = Path(sys.argv[1])
pages = sys.argv[2:]
mapping, n = {}, 0
texts = {}
for p in pages:
    t = (d / p).read_text(encoding="utf8")
    texts[p] = t
    for m in REF.finditer(t):
        lab = m.group(1)
        # count only references, not definitions at line start
        if t[max(0, m.start() - 1):m.start()] in ("", "\n") and t[m.end():m.end() + 1] == ":":
            continue
        if lab not in mapping:
            n += 1
            mapping[lab] = f"x{n}"
for p, t in texts.items():
    t = REF.sub(lambda m: f"[^{mapping.get(m.group(1), m.group(1))}]", t)
    t = re.sub(r"\[\^x(\d+)\]", r"[^\1]", t)
    (d / p).write_text(t, encoding="utf8")
print(f"{n} footnotes renumbered")
