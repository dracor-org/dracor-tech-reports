"""Highlights and table cell colours as in the published PDFs.

1. Highlights: gdocs_cleanup.lua writes every highlight of the source as
   <span class="mark">…</span>. Most of them are leftover review marks that
   are not visible in the PDF. Only the texts listed in
   alignment/<id>.highlights.json (checked against the yellow areas in the
   PDF) are kept; the others are unwrapped. Kept highlights stay as HTML in
   HTML tables and become the MyST role {span .mark}`…` elsewhere (styled in
   book/_static/custom.css).

2. Cell shading: docx_mark_code.py puts "⁤RRGGBB⁤" at the start of
   shaded table cells. In HTML tables this becomes a background colour on the
   <td>/<th> (with white or black text for contrast); elsewhere it is removed.

Usage: python tools/highlights.py ID FILE.md ...
"""
import json
import re
import sys
from pathlib import Path

SHADE = "⁤"
MARK = re.compile(r'<span class="mark">(.*?)</span>', re.S)
CELL = re.compile(r"<(td|th)([^>]*)>((?:<[^>]+>)*)" + SHADE + r"([0-9A-F]{6})" + SHADE)
ANY_SHADE = re.compile(SHADE + r"[0-9A-F]{6}" + SHADE)

rid, files = sys.argv[1], sys.argv[2:]
wl_file = Path(f"alignment/{rid}.highlights.json")
keep = set(json.loads(wl_file.read_text(encoding="utf8"))) if wl_file.exists() else set()


def unescape(t):
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!|<>])", r"\1", t)


def cell_style(m):
    tag, attrs, inner, fill = m.groups()
    r, g, b = (int(fill[i:i + 2], 16) for i in (0, 2, 4))
    fg = "#ffffff" if (0.299 * r + 0.587 * g + 0.114 * b) < 128 else "#000000"
    style = f"background-color: #{fill}; color: {fg}"
    old = re.search(r'\sstyle="([^"]*)"', attrs)  # merge with an existing style attribute
    if old:
        style = old.group(1).rstrip("; ") + "; " + style
        attrs = attrs.replace(old.group(0), "")
    return f'<{tag}{attrs} style="{style}">{inner}'


def process(text):
    out, in_html = [], False
    for ln in text.split("\n"):
        s = ln.lstrip()
        if s.startswith("<table"):
            in_html = True
        if in_html:
            ln = CELL.sub(cell_style, ln)
            ln = MARK.sub(lambda m: m.group(0) if unescape(m.group(1)) in keep else m.group(1), ln)
        else:
            ln = MARK.sub(lambda m: ("{span .mark}`" + unescape(m.group(1)) + "`")
                          if unescape(m.group(1)) in keep else m.group(1), ln)
        ln = ANY_SHADE.sub("", ln)
        if s.startswith("</table>"):
            in_html = False
        out.append(ln)
    return "\n".join(out)


n = 0
for f in files:
    p = Path(f)
    t = p.read_text(encoding="utf8")
    new = process(t)
    if new != t:
        n += 1
        p.write_text(new, encoding="utf8")
print(f"highlights/shading: {n} files changed ({len(keep)} highlight texts whitelisted)")
