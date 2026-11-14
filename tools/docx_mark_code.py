"""Mark monospace-formatted text in a Google-Docs-exported .docx as code.

Google Docs exports code as direct font formatting (Courier New, Roboto Mono,
Consolas) instead of styles, so pandoc loses it. This script rewrites
word/document.xml:

* paragraphs whose text runs are all monospace get the paragraph style
  "SourceCode" (pandoc -> code block)
* monospace runs inside normal paragraphs get the character style
  "VerbatimChar" (pandoc -> inline code)

Usage: python tools/docx_mark_code.py IN.docx OUT.docx
"""
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
MONO = {"Courier New", "Roboto Mono", "Consolas", "Source Code Pro", "Courier"}


def q(tag):
    return f"{{{W}}}{tag}"


def run_font(r):
    f = r.find("w:rPr/w:rFonts", NS)
    return f.get(q("ascii")) if f is not None else None


def run_text(r):
    return "".join(t.text or "" for t in r.findall("w:t", NS))


def set_pstyle(p, style):
    ppr = p.find("w:pPr", NS)
    if ppr is None:
        ppr = etree.SubElement(p, q("pPr"))
        p.remove(ppr)
        p.insert(0, ppr)
    ps = ppr.find("w:pStyle", NS)
    if ps is None:
        ps = etree.Element(q("pStyle"))
        ppr.insert(0, ps)
    ps.set(q("val"), style)


def set_rstyle(r):
    rpr = r.find("w:rPr", NS)
    if rpr is None:
        rpr = etree.Element(q("rPr"))
        r.insert(0, rpr)
    rs = rpr.find("w:rStyle", NS)
    if rs is None:
        rs = etree.Element(q("rStyle"))
        rpr.insert(0, rs)
    rs.set(q("val"), "VerbatimChar")


STYLES = f"""
<w:style xmlns:w="{W}" w:type="paragraph" w:customStyle="1" w:styleId="SourceCode">
  <w:name w:val="Source Code"/></w:style>
<w:style xmlns:w="{W}" w:type="character" w:customStyle="1" w:styleId="VerbatimChar">
  <w:name w:val="Verbatim Char"/></w:style>
"""


def main(src, dst):
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(src) as z:
        z.extractall(tmp)
    doc = tmp / "word/document.xml"
    tree = etree.parse(str(doc))
    n_para = n_inline = 0
    for p in tree.iter(q("p")):
        ppr_style = p.find("w:pPr/w:pStyle", NS)
        if ppr_style is not None and ppr_style.get(q("val"), "").startswith(("Heading", "Title", "berschrift", "Titel", "Verzeichnis", "Abbildungsverzeichnis", "Caption")):
            continue
        runs = [r for r in p.iter(q("r")) if run_text(r).strip()]
        if not runs:
            continue
        mono = [run_font(r) in MONO for r in runs]
        if all(mono):
            set_pstyle(p, "SourceCode")
            n_para += 1
        else:
            for r, m in zip(runs, mono):
                if m:
                    set_rstyle(r)
                    n_inline += 1
    tree.write(str(doc), xml_declaration=True, encoding="UTF-8", standalone=True)
    st = tmp / "word/styles.xml"
    sty = etree.parse(str(st))
    root = sty.getroot()
    for el in etree.fromstring(f"<x>{STYLES}</x>"):
        root.append(el)
    sty.write(str(st), xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(tmp.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(tmp).as_posix())
    shutil.rmtree(tmp)
    print(f"code paragraphs: {n_para}, inline code runs: {n_inline}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
