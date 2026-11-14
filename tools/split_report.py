"""Split a converted report (GFM from pandoc) into MyST pages.

* everything before the first numbered level-1 heading ("# 0. ...") is front
  matter and is written to _frontmatter_raw.md for manual curation
* the Word table of contents ("# Index") is dropped
* each level-1 chapter becomes a page; chapters listed in --split-sections
  are additionally split at level-2 headings
* footnote definitions travel with the page that references them
* the page heading becomes the frontmatter title; deeper headings shift up
* a MyST label line "(label)=" before a page heading becomes the page's
  frontmatter label; footnote references in a page heading (not allowed in
  titles) move to the first sentence of the page's first paragraph

Usage:
  python tools/split_report.py IN.md OUTDIR --prefix d7-4 --split-sections 3
Prints the generated file list (for myst.yml toc).
"""
import argparse
import re
from pathlib import Path

H = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FN_DEF = re.compile(r"^\[\^([^\]]+)\]:")
FN_REF = re.compile(r"\[\^([^\]]+)\]")


PROTECT = re.compile(r"(`[^`\n]*`|<https?://[^>\s]*>|\]\([^)\s]*\)|https?://\S+)")


def escape_prose(line):
    """Escape '@' outside code/URLs so MyST does not read it as a citation."""
    parts = PROTECT.split(line)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"(?<![\w\\])@(?=\w)", r"\\@", parts[i])
    return "".join(parts)


def escape_md(lines):
    out, fence = [], False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            fence = not fence
        out.append(ln if fence or ln.startswith("    ") else escape_prose(ln))
    return out


def slug(title):
    m = re.match(r"^(\d+(?:\.\d+)*)\.?\s", title)
    if m:
        return m.group(1).replace(".", "-")
    # unnumbered chapters (e.g. "Excursus: ...", "References"): first word
    words = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-").split("-")
    return "-".join(words[:2]) if words[0] in ("code", "list") else words[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("outdir")
    ap.add_argument("--split-sections", nargs="*", default=[])
    ap.add_argument("--start", default=r"^0\.\s", help="regex for first chapter heading")
    a = ap.parse_args()

    src = Path(a.src).read_text(encoding="utf8")
    # <img> + italic "Fig..." caption paragraph -> MyST figure; other <img> -> markdown image
    src = re.sub(
        r'<img src="([^"]+)"[^>]*/>\s*\n\s*\n\*?(Fig\.?\s*\d+[^\n]*?)\*?[ \t]*\n',
        lambda m: f":::{{figure}} {m.group(1)}\n{m.group(2).strip()}\n:::\n",
        src,
    )
    src = re.sub(r'<img src="([^"]+)"[^>]*/>', r"![](\1)", src)
    # Word layout tables holding two figures side by side -> two figures
    src = re.sub(
        r"\|\s*\|\s*\|\n\|[-:| ]+\|\n"
        r"\| !\[\]\(([^)]+)\) \| !\[\]\(([^)]+)\) \|\n"
        r"\| (Fig\.[^|\n]*?) \| (Fig\.[^|\n]*?) \|\n",
        lambda m: f":::{{figure}} {m.group(1)}\n{m.group(3).strip()}\n:::\n\n"
                  f":::{{figure}} {m.group(2)}\n{m.group(4).strip()}\n:::\n",
        src,
    )
    # pipe tables with an empty header and a bold first row: use that row as header
    def promote(m):
        cells = [c.strip() for c in m.group(2).strip().strip("|").split("|")]
        if not all(re.fullmatch(r"\*\*.+\*\*", c) for c in cells):
            return m.group(0)
        return "| " + " | ".join(c[2:-2] for c in cells) + " |\n" + m.group(1)
    src = re.sub(r"^\|(?:\s*\|)+\n(\|[-:| ]+\|\n)(\|.*\|)\n", promote, src, flags=re.M)
    lines = escape_md(src.splitlines())

    # collect footnote definitions (possibly multi-line, indented continuation)
    body, fns, cur = [], {}, None
    for i, ln in enumerate(lines):
        m = FN_DEF.match(ln)
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if m:
            cur = m.group(1)
            fns[cur] = [ln]
        elif cur and (ln.startswith("    ") or (ln == "" and nxt.startswith("    "))):
            fns[cur].append(ln)
        else:
            cur = None
            body.append(ln)

    # drop empty headings (Google Docs page breaks)
    body = [ln for ln in body if not re.fullmatch(r"#{1,6}\s*", ln)]

    start = re.compile(a.start)
    idx = next(i for i, ln in enumerate(body)
               if (m := H.match(ln)) and len(m.group(1)) == 1 and start.match(m.group(2)))
    # keep the label line of the first chapter heading with the chapter
    j = idx - 1
    while j >= 0 and not body[j].strip():
        j -= 1
    if j >= 0 and re.fullmatch(r"\([^)\s]+\)=", body[j]):
        idx = j
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "_frontmatter_raw.md").write_text("\n".join(body[:idx]) + "\n", encoding="utf8")

    # cut into pages
    pages, chap, label = [], None, None
    LABEL = re.compile(r"^\(([^)\s]+)\)=$")
    for ln in body[idx:]:
        m = H.match(ln)
        if m:
            lvl, title = len(m.group(1)), m.group(2)
            if lvl == 1 or (lvl == 2 and chap in a.split_sections):
                if lvl == 1:
                    chap = slug(title)
                pages.append({"title": title, "level": lvl, "lines": [], "label": label})
                label = None
                continue
        if label and not ln.strip():
            continue  # blank line between label and heading
        if label:
            pages[-1]["lines"].append(f"({label})=")
            label = None
        if (lm := LABEL.match(ln)):
            label = lm.group(1)
            continue
        if pages:
            pages[-1]["lines"].append(ln)

    files = []
    for p in pages:
        base = p["level"]
        text = []
        for ln in p["lines"]:
            m = H.match(ln)
            if m:
                lvl = max(2, len(m.group(1)) - base + 1)
                ln = "#" * lvl + " " + m.group(2)
            text.append(ln)
        while text and not text[0].strip():
            text.pop(0)
        # footnote refs are not allowed in titles: move them to the first paragraph
        title_refs = FN_REF.findall(p["title"])
        if title_refs:
            p["title"] = FN_REF.sub("", p["title"]).strip()
            for i, ln in enumerate(text):
                if ln.strip() and not ln.startswith(("#", "(", "    ", "```", ":::", "<", "|", "!")):
                    # insert at the end of the first sentence, but before the
                    # paragraph's first own footnote ref (keeps PDF numbering)
                    marks = "".join(f"[^{r}]" for r in title_refs)
                    sent = re.search(r"[.!?:](?=\s)", ln)
                    ref = FN_REF.search(ln)
                    cut = min([x for x in (sent and sent.end(), ref and ref.start()) if x] or [len(ln.rstrip())])
                    text[i] = ln[:cut] + marks + ln[cut:]
                    break
        refs = []
        for ln in text:
            for r in FN_REF.findall(ln):
                if r not in refs:
                    refs.append(r)
        notes = []
        for r in refs:
            if r in fns:
                notes.extend(fns.pop(r))
        fname = f"{slug(p['title'])}.md"
        title = p["title"].strip().replace('"', '\\"')
        fm = f'title: "{title}"\n' + (f'label: {p["label"]}\n' if p.get("label") else "")
        content = f'---\n{fm}---\n\n' + "\n".join(text).rstrip() + "\n"
        if notes:
            content += "\n" + "\n".join(notes) + "\n"
        (out / fname).write_text(content, encoding="utf8")
        files.append(fname)
    if fns:
        print("WARNING unused footnotes:", sorted(fns)[:20])
    print("\n".join(files))


if __name__ == "__main__":
    main()
