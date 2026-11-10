#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
export TK_SILENCE_DEPRECATION=1

PYTHON=""
for candidate in \
  "$SCRIPT_DIR/.venv/bin/python" \
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
  echo "Create the repository environment with:" >&2
  echo "  /opt/homebrew/bin/python3.14 -m venv .venv" >&2
  echo "  .venv/bin/python -m pip install pygame" >&2
  exit 1
fi

if [ "${ARCADE_HUB_DEBUG_SCROLL:-0}" = "1" ]; then
  {
    echo "launcher diagnostic session started"
    echo "launcher pid: $$"
    echo "selected python: $PYTHON"
    echo "script: $SCRIPT_DIR/arcade_hub.py"
    echo "working directory: $PWD"
  } >> "$SCRIPT_DIR/arcade_hub_scroll.log"
fi

exec "$PYTHON" "$SCRIPT_DIR/arcade_hub.py"
