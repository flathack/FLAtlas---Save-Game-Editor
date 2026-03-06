#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt

MODE="${1:-onedir}" # onedir|onefile
python build.py --clean --mode "$MODE"

echo
echo "Build artifacts:"
find "$ROOT_DIR/dist" -maxdepth 2 -type f | sort
