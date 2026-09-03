#!/bin/sh

set -e

echo "Running database migrations..."
alembic upgrade head

if psql "$DATABASE_URL" -tAc "SELECT EXISTS (SELECT 1 FROM categories WHERE id = '324d448d-50af-4dcc-aaf1-2c6c30281a47')" | grep -q 't'; then
    echo "Database already seeded. Skipping seeding."
else
    echo "Seeding database..."
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f scripts/seed_data.sql
fi

echo "Starting Business Pulse..."
exec streamlit run Home.py --server.port=8501 --server.address=0.0.0.0

