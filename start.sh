#!/bin/sh

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Business Pulse..."
exec streamlit run Home.py --server.port=8501 --server.address=0.0.0.0