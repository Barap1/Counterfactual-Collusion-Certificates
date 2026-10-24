#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$ROOT"
python3 paper/build/markdown_to_html.py paper/draft.md
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
if [ -x "$CHROME" ]; then
  "$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf="$ROOT/paper/build/draft.pdf" "file://$ROOT/paper/build/draft.html"
  if [ ! -s "$ROOT/paper/build/draft.pdf" ]; then
    echo "Chrome exited without producing paper/build/draft.pdf" >&2
    exit 3
  fi
else
  echo 'Google Chrome not found; no supported PDF renderer available.' >&2
  exit 2
fi
