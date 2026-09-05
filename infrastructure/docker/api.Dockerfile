# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency manifest first so Docker can cache the install layer
COPY apps/api/pyproject.toml ./apps/api/pyproject.toml

# Create a minimal src stub so pip -e doesn't fail on missing package
RUN mkdir -p ./apps/api/src/canary_api && \
    touch ./apps/api/src/canary_api/__init__.py

WORKDIR /app/apps/api
RUN pip install --upgrade pip && pip install -e ".[dev]"

# Now copy full source (invalidates cache only when source changes)
WORKDIR /app
COPY apps/api/src ./apps/api/src
COPY apps/api/alembic.ini ./apps/api/alembic.ini
# Copy tests so pytest can run inside the container
COPY apps/api/tests ./apps/api/tests

WORKDIR /app/apps/api

EXPOSE 8000

CMD ["uvicorn", "canary_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
