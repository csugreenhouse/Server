TEST_DB="${TEST_DB:-test_greenhouse}"
DB_OWNER="${DB_OWNER:-postgres}"
INIT_SQL="${INIT_SQL:-database/init.sql}"

echo "Preparing test database!"

if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl start postgresql >/dev/null 2>&1 || true
fi

DB_EXISTS="$(sudo -u postgres psql -X -q -tAc \
  "SELECT 1 FROM pg_database WHERE datname='${TEST_DB}'")"

if [[ "$DB_EXISTS" != "1" ]]; then
  sudo -u postgres createdb -O "${DB_OWNER}" "${TEST_DB}"
fi

SCHEMA_EXISTS="$(sudo -u postgres psql -X -q -tAc \
  "SELECT 1 FROM information_schema.tables \
   WHERE table_schema='public' AND table_name='species'" \
   "${TEST_DB}")"

if [[ "$SCHEMA_EXISTS" != "1" ]]; then
  sudo -u postgres psql -X -q -v ON_ERROR_STOP=1 -d "${TEST_DB}" -f "${INIT_SQL}"
fi

sudo -u postgres psql -X -q -v ON_ERROR_STOP=1 <<'SQL'
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

sudo -u postgres psql -X -q -d "${TEST_DB}" -c \
"GRANT ALL ON SCHEMA public TO greenhouse_test_user;
 GRANT SELECT,INSERT,UPDATE,DELETE ON species, height_log, width_log, plant, camera, view, tag, height_view, width_view TO greenhouse_test_user;"

echo "✅ test database ready"
