TEST_DB="${TEST_DB:-test_greenhouse}"
DB_OWNER="${DB_OWNER:-postgres}"
INIT_SQL="${INIT_SQL:-database/init.sql}"

echo "Preparing test database!"
# Start postgres if needed
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl start postgresql >/dev/null 2>&1 || true
fi

# Check if DB exists
DB_EXISTS="$(sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_database WHERE datname='${TEST_DB}'")"

if [[ "$DB_EXISTS" != "1" ]]; then
  echo "creating database '${TEST_DB}'"
  sudo -u postgres createdb -O "${DB_OWNER}" "${TEST_DB}"
fi

# Check if schema is already initialized
SCHEMA_EXISTS="$(sudo -u postgres psql -tAc \
  "SELECT 1 FROM information_schema.tables \
   WHERE table_schema='public' AND table_name='species'" \
   "${TEST_DB}")"

if [[ "$SCHEMA_EXISTS" != "1" ]]; then
  echo "initializing schema"
  sudo -u postgres psql -v ON_ERROR_STOP=1 -d "${TEST_DB}" -f "${INIT_SQL}"
fi

sudo -u postgres psql -v ON_ERROR_STOP=1 <<'SQL'
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

sudo -u postgres psql -d test_greenhouse -c \
"GRANT ALL ON SCHEMA public TO greenhouse_test_user; Grant Select on species, plant, tag to greenhouse_test_user"

echo "✅ test database ready"