"""Apply exact string replacements to files, failing loudly on mismatch.

Edits file format (JSON): [{"file": "...", "old": "...", "new": "...", "count": 1}, ...]
"count" (default 1) is the exact number of expected occurrences.
Used to record the manual alignment of a converted draft with the published PDF
in a reviewable, re-applicable form.

Usage: python tools/apply_edits.py EDITS.json BASEDIR
"""
import json
import sys
from pathlib import Path

edits = json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
base = Path(sys.argv[2])
errors = 0
for e in edits:
    p = base / e["file"]
    t = p.read_text(encoding="utf8")
    n = t.count(e["old"])
    want = e.get("count", 1)
    if n != want:
        print(f"MISMATCH {e['file']}: expected {want}, found {n}: {e['old'][:80]!r}")
        errors += 1
        continue
    p.write_text(t.replace(e["old"], e["new"]), encoding="utf8")
print(f"{len(edits) - errors} applied, {errors} failed")
sys.exit(1 if errors else 0)
