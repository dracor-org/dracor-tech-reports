#!/usr/bin/env bash
# Convert a Google-Docs-exported report (.docx) into MyST pages under book/reports/<id>/
# Usage: tools/convert_report.sh <id> <input.docx> [chapters to split at level 2...]
# Example: tools/convert_report.sh d7-4 "input/d7-4/....docx" 3
# Re-running overwrites the generated pages; manual alignment with the Zenodo PDF
# is done afterwards in separate commits (see CLAUDE.md).
set -euo pipefail
cd "$(dirname "$0")/.."
id="$1"; src="$2"; shift 2
out="book/reports/$id"
tmp="$(mktemp -d)"
.venv/bin/python -I tools/docx_mark_code.py "$src" "$tmp/marked.docx"
mkdir -p "$out"
rm -rf "$out/media"
( cd "$out" && pandoc "$tmp/marked.docx" -t gfm --wrap=none \
    --lua-filter="$OLDPWD/tools/gdocs_cleanup.lua" \
    --extract-media=. -o "$tmp/full.md" )
.venv/bin/python -I tools/split_report.py "$tmp/full.md" "$out" --split-sections "$@"
rm -rf "$tmp"
# re-apply the recorded manual alignment with the published PDF
for e in alignment/"$id"_*.json; do
  [ -e "$e" ] || continue
  echo "applying $e"
  .venv/bin/python -I tools/apply_edits.py "$e" "$out"
done
