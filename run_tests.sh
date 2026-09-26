#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]; then
  PYTHON=".venv/Scripts/python.exe"
else
  echo "Python interpreter not found in .venv"
  exit 1
fi

"$PYTHON" -m pytest -q
