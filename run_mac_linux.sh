#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if { [ -e .venv ] || [ -L .venv ]; } && [ ! -x .venv/bin/python ]; then
  echo "Existing .venv is incomplete or broken; it was not replaced. See docs/LOCAL_INSTALLATION.md to rebuild only the environment." >&2
  exit 1
fi
if [ "${1:-}" = "--check" ]; then
  if [ -x .venv/bin/python ]; then
    exec .venv/bin/python -B scripts/check_installation.py
  fi
  exec python3 -B scripts/check_installation.py
fi
if [ "$#" -ne 0 ]; then
  echo "Usage: ./run_mac_linux.sh [--check]" >&2
  exit 2
fi
if [ ! -e .venv/bin/python ]; then
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Python 3.11+ is required; the environment was not created.")'
  python3 -m venv .venv
fi
.venv/bin/python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Existing .venv needs Python 3.11+; it was not replaced. See docs/LOCAL_INSTALLATION.md.")'
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B scripts/check_installation.py
exec .venv/bin/python studio.py serve
