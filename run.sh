#!/usr/bin/env bash
set -euo pipefail

# Move to the directory containing this script (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# initialize test database
bash "$SCRIPT_DIR/run/initialize_test_db.sh"

if pytest -s
then
  echo "All tests passed"
  exit 0
fi

# reset test database
bash "$SCRIPT_DIR/run/reset_test_db.sh"

echo "✅ test database reset after tests"

pytest -s 