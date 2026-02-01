#!/usr/bin/env bash
set -euo pipefail

#initialize test database
bash "$(dirname"$0")run/initialize_test_db.sh"


# Move to the directory containing this script (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

pytest

echo "All tests passed"