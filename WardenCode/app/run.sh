#!/usr/bin/env bash
# Warden GUI launcher — double-click (or `./run.sh`) to start.
# Installs Flask on first run if it's missing, then starts the local server.

set -e
cd "$(dirname "$0")"

PYTHON=python3
command -v python3 >/dev/null 2>&1 || PYTHON=python

if ! $PYTHON -c "import flask" >/dev/null 2>&1; then
  echo "First run: installing Flask..."
  $PYTHON -m pip install -r requirements.txt
fi

echo "Starting Warden — opening http://127.0.0.1:5057 in your browser..."
$PYTHON app.py
