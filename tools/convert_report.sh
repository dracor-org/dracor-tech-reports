#!/usr/bin/env bash
# Convert a Google-Docs-exported report (.docx) into MyST pages under book/reports/<id>/
# Usage: tools/convert_report.sh <id> <input.docx> [chapters to split at level 2...]
# Example: tools/convert_report.sh d7-4 "input/d7-4/....docx" 3
# Re-running overwrites the generated pages (not index.md); the recorded alignment
# with the Zenodo PDF (alignment/<id>_*.json) is re-applied automatically.
set -euo pipefail
cd "$(dirname "$0")/.."
id="$1"; src="$2"; shift 2
out="book/reports/$id"
tmp="$(mktemp -d)"
.venv/bin/python -I tools/docx_mark_code.py "$src" "$tmp/marked.docx"
mkdir -p "$out"
rm -rf "$out/media"
( cd "$out" && pandoc "$tmp/marked.docx" -t gfm --wrap=none \
    --lua-filter="$OLDPWD/tools/gdocs_cleanup.lua" -M rtfr_prefix="$id" \
    --extract-media=. -o "$tmp/full.md" )
pages=$(.venv/bin/python -I tools/split_report.py "$tmp/full.md" "$out" ${START:+--start "$START"} --split-sections "$@")
echo "$pages"
rm -rf "$tmp"
# re-apply the recorded manual alignment with the published PDF
for e in alignment/"$id"_*.json; do
  [ -e "$e" ] || continue
  echo "applying $e"
  .venv/bin/python -I tools/apply_edits.py "$e" "$out"
done
# keep DOI links as links (mystmd would turn doi.org links into citations)
.venv/bin/python -I tools/doi_links.py $(printf "$out/%s " $pages)
# renumber footnotes consecutively (MyST shows labels as numbers)
.venv/bin/python -I tools/renumber_footnotes.py "$out" $pages
