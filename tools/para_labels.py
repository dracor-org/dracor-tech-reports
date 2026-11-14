"""Give every paragraph of the report pages a stable, linkable label.

Labels are "<section label>-p<n>", numbered per section: the 4th paragraph of
section clsinfra-d71-5-3-3-2 gets clsinfra-d71-5-3-3-2-p4.
The section is the page's frontmatter label or the last heading label
("(label)=" line) above the paragraph.

Labelled: text paragraphs, block quotes and lists (a list counts as one unit,
also when its items are separated by blank lines). Not labelled: headings,
code, tables, figures/directives, HTML blocks, footnote definitions.

Run after the alignment edits (they match text across paragraph boundaries).
Idempotent: existing paragraph labels are removed and recomputed, so the
numbering always reflects the current text.

Usage: python tools/para_labels.py FILE.md ...
"""
import re
import sys
from pathlib import Path

LABEL = re.compile(r"^\(([^)\s]+)\)=$")
PARA_LABEL = re.compile(r"^\([^)\s]+-p\d+\)=$")
LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s")
SKIP = ("#", "```", ":::", "<", "|", "[^", "!", "$$", "+++")


def kind(block):
    first = block[0]
    if first.startswith("    ") and not LIST.match(first):
        return "code"
    if first.startswith(SKIP) or LABEL.match(first):
        return "skip"
    if LIST.match(first):
        return "list"
    return "para"


def process(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return text
    head, body = text[: m.end()], text[m.end():]
    fm = re.search(r"^label:\s*(\S+)", m.group(1), re.M)
    section = fm.group(1) if fm else None
    lines = [ln for ln in body.split("\n") if not PARA_LABEL.match(ln)]

    # group into blocks separated by blank lines; keep fenced code / directives intact
    blocks, cur, fence = [], [], None
    for ln in lines:
        s = ln.lstrip()
        if fence:
            cur.append(ln)
            if s.startswith(fence):
                fence = None
            continue
        if s.startswith("```") or s.startswith(":::"):
            fence = "```" if s.startswith("```") else ":::"
            if s.strip() in ("```", ":::") and cur:  # closing marker on its own
                pass
            cur.append(ln)
            continue
        if ln.strip() == "":
            if cur:
                blocks.append(cur)
                cur = []
            blocks.append(None)  # blank line
        else:
            cur.append(ln)
    if cur:
        blocks.append(cur)

    out, counter, in_list = [], {}, False
    for b in blocks:
        if b is None:
            out.append("")
            continue
        lab = LABEL.match(b[0])
        if lab and (len(b) == 1 or b[1].startswith("#")):
            section = lab.group(1)
            in_list = False
            out.extend(b)
            continue
        k = kind(b)
        continuation = in_list and (k == "list" or b[0].startswith(("  ", "\t")))
        if k in ("para", "list") and section and not continuation:
            counter[section] = counter.get(section, 0) + 1
            out.append(f"({section}-p{counter[section]})=")
        in_list = k == "list" or continuation
        out.extend(b)
    return head + "\n".join(out)


n = 0
for f in sys.argv[1:]:
    p = Path(f)
    t = p.read_text(encoding="utf8")
    new = process(t)
    if new != t:
        n += 1
        p.write_text(new, encoding="utf8")
print(f"paragraph labels: {n} files changed")
