#!/usr/bin/env bash
set -euo pipefail

# make all outputs including Notice but not errors

TEST_DB="${TEST_DB:-test_greenhouse}"
DB_OWNER="${DB_OWNER:-postgres}"
INIT_SQL="${INIT_SQL:-database/init.sql}"

echo "🔄 Resetting test database: ${TEST_DB}"

# Start postgres if available (useful on some Linux setups / CI images)
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl start postgresql >/dev/null 2>&1 || true
fi

# 1) Drop DB if it exists (must terminate connections first)
sudo -u postgres psql -X -q -v ON_ERROR_STOP=1 <<SQL
-- prevent new connections
UPDATE pg_database SET datallowconn = false WHERE datname = '${TEST_DB}';

-- kill existing sessions
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${TEST_DB}' AND pid <> pg_backend_pid();
SQL

sudo -u postgres dropdb --if-exists "${TEST_DB}"

# 2) Recreate DB
sudo -u postgres createdb -O "${DB_OWNER}" "${TEST_DB}"

# 3) Run schema + seed silence notices
sudo -u postgres psql -X -q -v client_min_messages=warning -d "${TEST_DB}" -f "${INIT_SQL}"

# 4) Ensure role exists
sudo -u postgres psql -X -q -v client_min_messages=warning <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT FROM pg_roles WHERE rolname = 'greenhouse_test_user'
  ) THEN
    CREATE ROLE greenhouse_test_user
      LOGIN
      PASSWORD 'greenhouse_test_pass';
  END IF;
END
$$;
SQL

# 5) Grants (schema + tables)
sudo -u postgres psql -X -q -v ON_ERROR_STOP=1 -d "${TEST_DB}" <<SQL
GRANT USAGE, CREATE ON SCHEMA public TO greenhouse_test_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO greenhouse_test_user;

-- If you might add tables later and still want them selectable:
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO greenhouse_test_user;
SQL

sudo -u postgres psql -X -q -d "${TEST_DB}" -c \
"GRANT ALL ON SCHEMA public TO greenhouse_test_user;
 GRANT SELECT ON species, plant, view, tag, camera, height_view, width_view TO greenhouse_test_user;"

echo "✅ Fresh test database ready: ${TEST_DB}"
