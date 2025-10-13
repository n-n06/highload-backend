#!/bin/bash
set -e

# Run migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start the app
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
