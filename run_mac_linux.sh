#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -e .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
exec .venv/bin/python studio.py serve
