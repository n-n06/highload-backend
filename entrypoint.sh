#!/bin/bash
set -e

# Run migrations
echo "Running Alembic migrations..."
uv run alembic upgrade head
uv run python -m src.presentation.app
