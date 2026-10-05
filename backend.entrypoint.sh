#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

python - <<'PY'
import os
import time

import psycopg2

host = os.getenv("POSTGRES_HOST", "db")
port = os.getenv("POSTGRES_PORT", "5432")
database = os.getenv("POSTGRES_DB", "videoflix")
user = os.getenv("POSTGRES_USER", "videoflix")
password = os.getenv("POSTGRES_PASSWORD", "videoflix")

while True:
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
        )
        connection.close()
        break
    except psycopg2.OperationalError:
        print("PostgreSQL is not ready yet. Waiting...")
        time.sleep(1)

print("PostgreSQL is ready.")
PY

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Videoflix backend..."
exec "$@"
