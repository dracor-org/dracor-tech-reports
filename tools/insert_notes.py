"""Insert editorial notes (admonitions) into the generated report pages.

The report text stays as published; notes are added as clearly marked boxes
(class "editorial"). They are recorded in alignment/<id>_notes.json:

  [{"file": "3-2.md", "after": "<label>" | "top", "kind": "outdated" | "update",
    "checked": "2026-11", "text": "Markdown text of the note"}, ...]

"after" names a MyST label (a heading or a paragraph label "<section>-pN"); the
note is inserted after that block, i.e. before the next label line, footnote
definition or end of the text. "top" inserts the note after the front matter.
Each note gets the label "<anchor>-note<N>". Run this as the last step of
convert_report.sh (after para_labels.py, so that notes are not counted as
report paragraphs).

Usage: python tools/insert_notes.py NOTES.json DIR
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

KINDS = {"outdated": ("warning", "Outdated"), "update": ("note", "Update")}
LABEL = re.compile(r"^\((clsinfra-[a-z0-9-]+)\)=$")

notes = json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
base = Path(sys.argv[2])
by_file = defaultdict(list)
for n in notes:
    by_file[n["file"]].append(n)

errors = 0
for fname, items in by_file.items():
    p = base / fname
    lines = p.read_text(encoding="utf8").split("\n")
    counter = defaultdict(int)
    # resolve insertion points on the original lines, insert from the bottom up
    inserts = []
    for n in items:
        directive, title = KINDS[n["kind"]]
        if n["after"] == "top":
            if lines[0] != "---":
                print(f"ERROR {fname}: no front matter"); errors += 1; continue
            pos = lines.index("---", 1) + 1
            m = re.search(r"^label: (\S+)$", "\n".join(lines[:pos]), re.M)
            anchor = m.group(1) if m else fname.removesuffix(".md")
        else:
            try:
                start = lines.index(f"({n['after']})=")
            except ValueError:
                print(f"ERROR {fname}: label not found: {n['after']}"); errors += 1; continue
            pos = len(lines)
            for i in range(start + 1, len(lines)):
                if LABEL.match(lines[i]) or lines[i].startswith("[^"):
                    pos = i
                    break
            while pos > start + 1 and not lines[pos - 1].strip():
                pos -= 1
            anchor = n["after"]
        counter[anchor] += 1
        block = ["", f"({anchor}-note{counter[anchor]})=",
                 f":::{{{directive}}} {title} (checked {n['checked']})",
                 ":class: editorial",
                 n["text"].strip(), ":::", ""]
        inserts.append((pos, block))
    for pos, block in sorted(inserts, key=lambda x: -x[0]):
        lines[pos:pos] = block
    p.write_text("\n".join(lines), encoding="utf8")
print(f"notes: {len(notes) - errors} inserted, {errors} failed")
sys.exit(1 if errors else 0)
