"""Keep links as published: same visible text, plain links.

1. DOI links

mystmd turns every link to doi.org into a citation (rendered as "Author (Year)"
and collected in a reference list), which changes the published text. There is
no setting to switch this off for doi.org links. DOIs are handles, so they also
resolve via hdl.handle.net, which mystmd leaves alone. This script rewrites the
link *targets* only; the visible text stays "https://doi.org/...".

  <https://doi.org/X>          -> [https://doi.org/X](https://hdl.handle.net/X)
  [text](https://doi.org/X)    -> [text](https://hdl.handle.net/X)
  bare https://doi.org/X       -> [https://doi.org/X](https://hdl.handle.net/X)

2. URLs written out in the text
mystmd replaces the text of a link whose text is the bare URL with a short
form for GitHub and Wikipedia ("report/github_utils.py",
"dracor-org/dracor-api#120", the article title) and shows percent-encoded
URLs decoded. Here the link text is written out as the full URL, pre-formatted with
the same invisible line-break hints (U+200B) mystmd adds to long URLs, so the
page looks as usual but shows the URL as printed in the report.

Code (fenced, indented, inline) is not touched. Idempotent.
Usage: python tools/links.py FILE.md ...
"""
import re
import sys
from pathlib import Path

DOI = r"https?://(?:dx\.|www\.)?doi\.org/(10\.[^\s<>()\[\]]+?)"
END = r"(?=[.,;:]?(?:[\s)\]]|$))"
AUTOLINK = re.compile(r"<" + DOI + r">")
TARGET = re.compile(r"\]\(" + DOI + r"\)")
BARE = re.compile(r"(?<![<\[/])(?<!\]\()\b" + DOI + END)
CODE = re.compile(r"(`[^`\n]*`)")
SHORTENED = r"https?://(?:[a-z]+\.)?(?:github\.com|wikipedia\.org)/[^\s<>()\[\]]+?"
ANY = r"https?://[^\s<>()\[\]]+?"
URL_AUTOLINK = re.compile(r"<(https?://[^\s<>]+)>")    # all written-out URLs
URL_SELF = re.compile(r"\[(" + ANY + r")\]\((\1)\)")
URL_BARE = re.compile(r"(?<![<\[/(\w])(" + SHORTENED + r")" + END)


def fmt(url):
    """mystmd's formatLinkText: zero-width spaces as line-break hints."""
    parts = url.split("//")
    parts = [re.sub(r"([=&])", "\u200b\\1\u200b", re.sub(r"([/~.,\-_?#%])", "\u200b\\1", p)) for p in parts]
    out = "//\u200b".join(parts)
    out = re.sub("\u200b(.{1,2})$", r"\1", out)
    return re.sub(r"([_*\[\]`<>])", r"\\\1", out)  # markdown escapes


def protect(seg):
    seg = URL_AUTOLINK.sub(lambda m: f"[{fmt(m.group(1))}](<{m.group(1)}>)", seg)
    seg = URL_SELF.sub(lambda m: f"[{fmt(m.group(1))}]({m.group(1)})", seg)
    parts = re.split(r"(\[[^\]]*\]\([^)]*\))", seg)
    for i in range(0, len(parts), 2):
        parts[i] = URL_BARE.sub(lambda m: f"[{fmt(m.group(1))}]({m.group(1)})", parts[i])
    return "".join(parts)


def fix_text(seg):
    seg = AUTOLINK.sub(lambda m: f"[{m.group(0)[1:-1]}](https://hdl.handle.net/{m.group(1)})", seg)
    seg = TARGET.sub(lambda m: f"](https://hdl.handle.net/{m.group(1)})", seg)
    # bare URLs: only outside existing link syntax
    parts = re.split(r"(\[[^\]]*\]\([^)]*\))", seg)
    for i in range(0, len(parts), 2):
        parts[i] = BARE.sub(lambda m: f"[{m.group(0)}](https://hdl.handle.net/{m.group(1)})", parts[i])
    return "".join(parts)


def fix(text):
    out, fence = [], False
    for ln in text.split("\n"):
        if ln.lstrip().startswith(("```", ":::{code")):
            fence = not fence
        if fence or ln.startswith("    ") or ln.lstrip().startswith("```"):
            out.append(ln)
            continue
        segs = CODE.split(ln)
        out.append("".join(s if i % 2 else protect(fix_text(s)) for i, s in enumerate(segs)))
    return "\n".join(out)


n = 0
for f in sys.argv[1:]:
    p = Path(f)
    t = p.read_text(encoding="utf8")
    new = fix(t)
    if new != t:
        n += 1
        p.write_text(new, encoding="utf8")
print(f"links: {n} files changed")
