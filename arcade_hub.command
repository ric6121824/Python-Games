#!/bin/bash
cd "$(dirname "$0")"
export TK_SILENCE_DEPRECATION=1

PYTHON=""
for candidate in \
  "/opt/homebrew/bin/python3" \
  "/usr/local/bin/python3" \
  "/Applications/Xcode.app/Contents/Developer/usr/bin/python3"; do
  if [ -x "$candidate" ] && "$candidate" - <<'PY' >/dev/null 2>&1
import tkinter
import pygame
print('ok')
PY
  then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "No working GUI runtime found." >&2
  echo "Install Tk/Pygame with:" >&2
  echo "  /Applications/Xcode.app/Contents/Developer/usr/bin/python3 -m pip install pygame" >&2
  exit 1
fi

exec "$PYTHON" "$(dirname "$0")/arcade_hub.py"
