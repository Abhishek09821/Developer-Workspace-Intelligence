# Canary — Development Guide

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Docker | ≥ 24 | + Docker Compose v2 |
| Python | 3.12 | Match `requires-python` in pyproject.toml |
| Node.js | 20 LTS | Match web.Dockerfile |
| npm | ≥ 10 | |

---

## Quickstart (Docker Compose — full stack)

```bash
# Clone and enter
git clone <repo-url> canary
cd canary

# Start everything
docker compose up --build

# Services:
#   API  →  http://localhost:8000
#   Web  →  http://localhost:5173
#   Docs →  http://localhost:8000/docs  (Swagger UI)
```

The first run will:
1. Build the Python and Node images
2. Start PostgreSQL + Redis with health checks
3. Wait for healthy databases before starting the API
4. API container does NOT run migrations automatically — see below

---

## Running Migrations

```bash
# Option A: inside the running api container
docker compose exec api alembic upgrade head

# Option B: locally (requires local venv and postgres on 5433)
cd apps/api
alembic upgrade head
```

---

## Local Development (without Docker)

### Backend

```bash
cd apps/api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies (including dev extras)
pip install -e ".[dev]"

# Copy and edit environment variables
cp .env.example .env
# Edit CANARY_DATABASE_URL to point to your local postgres

# Start postgres + redis via docker (infra only)
docker compose up postgres redis -d

# Run migrations
alembic upgrade head

# Start the API with hot reload
uvicorn canary_api.main:app --reload

# API available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Frontend

```bash
cd apps/web

# Install dependencies
npm install

# Start dev server
npm run dev

# Frontend available at http://localhost:5173
```

---

## Environment Variables

All backend config is driven by environment variables with the `CANARY_` prefix.
See `apps/api/.env.example` for the full list.

Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CANARY_DATABASE_URL` | `postgresql+asyncpg://canary:canary@localhost:5433/canary` | Async SQLAlchemy URL |
| `CANARY_REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `CANARY_JWT_SECRET_KEY` | `dev-secret-change-me` | **Change in production** |
| `CANARY_AI_PROVIDER` | `none` | `openai`, `anthropic`, `bedrock`, or `none` |
| `CANARY_LOG_JSON` | `false` | Set to `true` for structured JSON logs |

Frontend config:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api/v1` | Backend API base URL |

---

## Running Tests

### Backend (pytest)

```bash
cd apps/api
source .venv/bin/activate

# All tests (SQLite in-memory, no live DB needed)
pytest

# With coverage
pytest --cov=canary_api --cov-report=term-missing

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Verbose
pytest -v
```

### Frontend (Vitest)

```bash
cd apps/web

# Single run
npm test

# Watch mode
npm run test:watch
```

---

## Code Quality

### Backend

```bash
cd apps/api
source .venv/bin/activate

# Lint + auto-fix
ruff check --fix src/ tests/

# Type checking
mypy src/

# Format
ruff format src/ tests/
```

### Frontend

```bash
cd apps/web

# Type check
npm run type-check

# Lint
npm run lint
```

---

## Project Structure Quick Reference

```
apps/api/src/canary_api/
├── api/           ← HTTP layer only (routes, schemas, deps)
├── application/   ← Business logic / use cases
├── domain/        ← Pure domain entities and repository interfaces
├── persistence/   ← SQLAlchemy models, repositories, migrations
├── analyzers/     ← Analysis modules (scanner, security, deps, arch, health)
├── background/    ← Celery worker configuration + tasks
├── integrations/  ← GitHub + AI provider clients
├── core/          ← Config, error hierarchy
└── logging/       ← structlog setup
```

---

## Adding a New API Endpoint

1. Add a Pydantic schema to `api/v1/schemas.py`
2. Create or update a service method in `application/<domain>/service.py`
3. Add a route handler in `api/v1/routes/<domain>.py`
4. Register the router in `api/v1/router.py` if it's a new file
5. Write an integration test in `tests/integration/test_<domain>.py`

---

## Running the Celery Worker

```bash
cd apps/api
source .venv/bin/activate

# Start a worker (requires Redis running)
celery -A canary_api.background.celery_app worker --loglevel=info
```

---

## API Documentation

When the API is running, interactive docs are available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Docker Compose Services

```bash
# Start all services
docker compose up --build

# Start only infrastructure (postgres + redis)
docker compose up postgres redis -d

# Rebuild a single service
docker compose up --build api

# View logs
docker compose logs -f api
docker compose logs -f web

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (wipes database)
docker compose down -v
```

---

## Troubleshooting

**API can't connect to PostgreSQL**
- Check Docker is running: `docker compose ps`
- Verify port 5433 is not in use: `lsof -i :5433`
- Check the `CANARY_DATABASE_URL` in `.env`

**`alembic upgrade head` fails with "table already exists"**
- This usually means the migration was already applied. Check: `alembic current`
- If the DB is fresh and the migration is wrong, run: `docker compose down -v` then start fresh

**Frontend 401 errors**
- The API is not returning a valid token or the token expired
- Clear `localStorage.canary_access_token` in browser devtools and log in again

**`pgvector` not available**
- The tests use SQLite which doesn't support pgvector — the `CodeEntity.embedding` column is patched to `None` in `tests/conftest.py`
- For live DB, ensure you're using the `pgvector/pgvector:pg16` Docker image
