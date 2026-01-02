#!/usr/bin/env bash
set -euo pipefail

echo "Running tests"

#activate the virtual environment
source ../.venv/bin/activate

# Move to the directory containing this script (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

pytest

echo "All tests passed"