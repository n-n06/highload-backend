FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

ADD . .

RUN chmod +x /app/entrypoint.sh