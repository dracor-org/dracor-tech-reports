"""Split a converted report (GFM from pandoc) into MyST pages.

* everything before the first numbered level-1 heading ("# 0. ...") is front
  matter and is written to _frontmatter_raw.md for manual curation
* the Word table of contents ("# Index") is dropped
* each level-1 chapter becomes a page; chapters listed in --split-sections
  are additionally split at level-2 headings
* footnote definitions travel with the page that references them
* the page heading becomes the frontmatter title; deeper headings shift up

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
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-").split("-")[0]


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
        r'<img src="([^"]+)"[^>]*/>\s*\n\s*\n\*(Fig\.?\s*\d+[^\n]*?)\*[ \t]*\n',
        lambda m: f":::{{figure}} {m.group(1)}\n{m.group(2).strip()}\n:::\n",
        src,
    )
    src = re.sub(r'<img src="([^"]+)"[^>]*/>', r"![](\1)", src)
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
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "_frontmatter_raw.md").write_text("\n".join(body[:idx]) + "\n", encoding="utf8")

    # cut into pages
    pages, chap = [], None
    for ln in body[idx:]:
        m = H.match(ln)
        if m:
            lvl, title = len(m.group(1)), m.group(2)
            if lvl == 1:
                chap = slug(title)
                pages.append({"title": title, "level": 1, "lines": []})
                continue
            if lvl == 2 and chap in a.split_sections:
                pages.append({"title": title, "level": 2, "lines": []})
                continue
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
        title = p["title"].replace('"', '\\"')
        content = f'---\ntitle: "{title}"\n---\n\n' + "\n".join(text).rstrip() + "\n"
        if notes:
            content += "\n" + "\n".join(notes) + "\n"
        (out / fname).write_text(content, encoding="utf8")
        files.append(fname)
    if fns:
        print("WARNING unused footnotes:", sorted(fns)[:20])
    print("\n".join(files))


if __name__ == "__main__":
    main()
