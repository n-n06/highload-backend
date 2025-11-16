FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
ENV PYTHONPATH=/app

COPY pyproject.toml uv.lock ./
COPY README.md /app/

RUN uv sync --no-dev --frozen
ENV PATH="/app/.venv/bin:$PATH"  

COPY src/ /app/src
COPY .env .
COPY auth.env .
COPY alembic.ini .
COPY migrations/ ./migrations

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
