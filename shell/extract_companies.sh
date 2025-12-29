#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-}"
if [[ -z "$INPUT" ]]; then
  echo "Usage: $0 <csv_url_or_path>" >&2
  exit 1
fi

# If URL, download to temp file (avoids curl pipe issues on Windows Git Bash)
TMP="constituents_tmp.csv"
CLEANUP=0

if [[ "$INPUT" =~ ^https?:// ]]; then
  curl -L -o "$TMP" "$INPUT"
  FILE="$TMP"
  CLEANUP=1
else
  FILE="$INPUT"
fi

python3 - << PY
import csv, re

file_path = r"$FILE"
out = []

with open(file_path, newline="", encoding="utf-8") as f:
    rows = csv.DictReader(f)
    for r in rows:
        name = (r.get("Security") or "").strip()
        loc  = (r.get("Headquarters Location") or "").strip()
        founded = (r.get("Founded") or "").strip()

        m = re.search(r"\b(1[6-9]\d{2}|20\d{2})\b", founded)
        if not m:
            continue
        year = int(m.group(1))
        out.append((year, name, loc))

out.sort(key=lambda x: x[0])

for year, name, loc in out:
    print(f"{name}\t{loc}\t{year}")
PY

if [[ "$CLEANUP" -eq 1 ]]; then
  rm -f "$TMP"
fi
