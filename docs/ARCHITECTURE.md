# Canary — Architecture

> Developer Workspace Intelligence Platform

---

## Overview

Canary is built as a clean, modular monorepo with a hard separation between the frontend application, the backend API, and shared infrastructure. The backend follows a layered architecture with strict dependency direction: outer layers depend on inner layers, never the reverse.

```
┌─────────────────────────────────────────────────┐
│                  Frontend (React)               │
│                   apps/web/                     │
└─────────────────────┬───────────────────────────┘
                      │ HTTP / REST
┌─────────────────────▼───────────────────────────┐
│                   API Layer                     │
│              apps/api/ → FastAPI                │
│  ┌───────────────────────────────────────────┐  │
│  │          Route Handlers (thin)            │  │
│  ├───────────────────────────────────────────┤  │
│  │       Application Services / Use Cases    │  │
│  ├───────────────────────────────────────────┤  │
│  │            Domain Entities / Enums        │  │
│  ├───────────────────────────────────────────┤  │
│  │   Repository Ports (abstract interfaces)  │  │
│  ├───────────────────────────────────────────┤  │
│  │    Persistence (SQLAlchemy, PostgreSQL)   │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │     Background Workers (Celery + Redis)   │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Repository Structure

```
canary/
├── apps/
│   ├── api/                    Python / FastAPI backend
│   │   ├── src/canary_api/
│   │   │   ├── api/            HTTP layer: routes, schemas, deps, exception handlers
│   │   │   ├── application/    Use cases / application services / DTOs
│   │   │   ├── domain/         Domain entities, enums, repository interfaces (ports)
│   │   │   ├── persistence/    SQLAlchemy models, migrations, repository impls
│   │   │   ├── analyzers/      Codebase analysis modules (scanner, AST, security, etc.)
│   │   │   ├── background/     Celery app factory + task definitions
│   │   │   ├── integrations/   External service clients (GitHub, AI providers)
│   │   │   ├── core/           Config (Settings), error hierarchy
│   │   │   └── logging/        structlog setup
│   │   ├── tests/              pytest test suite
│   │   └── alembic.ini
│   │
│   └── web/                    React / TypeScript frontend
│       ├── src/
│       │   ├── components/     Reusable UI components (layout, ui, domain-specific)
│       │   ├── contexts/       React context providers (auth)
│       │   ├── hooks/          React Query data-fetching hooks
│       │   ├── lib/            Axios client, utility functions
│       │   ├── pages/          Route-level page components
│       │   ├── types/          TypeScript types mirroring API schemas
│       │   └── test/           Vitest tests + setup
│       └── ...
│
├── packages/
│   └── shared/                 Shared TypeScript types (future)
│
├── infrastructure/
│   └── docker/
│       ├── api.Dockerfile
│       └── web.Dockerfile
│
├── docs/
├── scripts/
├── tests/
│   └── e2e/                    Playwright E2E tests (future)
└── docker-compose.yml
```

---

## Backend Layer Details

### API Layer (`api/`)
Thin HTTP adapters only. Route handlers:
- Validate input via Pydantic schemas
- Extract authenticated user via dependency injection
- Delegate all business logic to application services
- Map application errors to HTTP responses via a single exception handler

No SQL, no business logic, no direct model access.

### Application Layer (`application/`)
Use cases / application services. Each module owns one bounded context:
- `auth/` — registration, login, token issuance
- `projects/` — create, list, retrieve projects
- `scans/` — orchestrate scan lifecycle (future)
- `imports/` — workspace / ZIP / GitHub import (future)

Services depend on **repository interfaces** from the domain layer, never on concrete implementations.

### Domain Layer (`domain/`)
Pure Python. Contains:
- **Entities** — dataclasses with business state and factory methods
- **Enums** — project status, source type, scan status
- **Repository ports** — abstract base classes defining persistence contracts

Zero framework imports. Fully unit-testable without a database.

### Persistence Layer (`persistence/`)
Concrete implementations:
- SQLAlchemy ORM models (mapped independently from domain entities)
- Repository implementations that map entity ↔ ORM model
- Alembic migration environment

The mapping pattern (entity-to-model and model-to-entity functions) ensures the domain layer never sees SQLAlchemy internals.

### Analyzers (`analyzers/`)
Independent, composable analysis modules. Each analyzer is responsible for one concern:

| Module               | Responsibility |
|----------------------|----------------|
| `scanner/`           | Walk filesystem, collect file metadata |
| `indexing/`          | Build the codebase index |
| `code_analysis/`     | AST parsing, code entity extraction |
| `dependency_analysis/` | Parse package manifests |
| `security_analysis/` | Detect vulnerabilities, secrets, risky patterns |
| `architecture_analysis/` | Build module/component dependency graph |
| `health/`            | Compute composite health scores |
| `recommendations/`   | Generate actionable recommendations |

Each module is independently testable and never depends on another analyzer.

### Background Jobs (`background/`)
Celery workers powered by Redis. Long-running scans and analysis pipelines run asynchronously to keep the API responsive. The Celery app is configured in `background/celery_app/` and task definitions live in `background/tasks/`.

---

## Authentication

- JWT (HS256) bearer tokens
- Issued on register/login, validated on every protected request
- `get_current_user` dependency: decodes token → fetches User row → raises 401 if invalid
- Token lifetime configurable via `CANARY_JWT_ACCESS_TOKEN_EXPIRE_MINUTES`

---

## Data Flow: Creating a Project

```
POST /api/v1/projects
  │
  ▼
routes/projects.py:create_project()
  → CurrentUserDep resolves JWT → User
  → ProjectServiceDep creates ProjectService(SqlAlchemyProjectRepository(session))
  │
  ▼
ProjectService.create_project(CreateProjectInput)
  → validates name
  → Project.create() → domain entity
  → repository.add(entity)
  │
  ▼
SqlAlchemyProjectRepository.add()
  → _to_model(entity) → ORM model
  → session.flush()
  → _to_entity(model) → domain entity
  │
  ▼
session committed by get_db_session dependency
  │
  ▼
ProjectResponse serialized → 201 Created
```

---

## Security Design

- Imported project code is **never executed**
- ZIP archives validated for path traversal, symlink attacks, and size limits before extraction
- Local workspace scanner reads only within the explicitly selected root path
- No project `npm install`, `pip install`, `make`, or shell execution
- All user input passed through typed Pydantic models with validation constraints

---

## Frontend Architecture

React SPA built on:
- **Vite** for fast dev builds
- **React Router v6** for client-side routing with protected routes
- **TanStack Query (React Query)** for server state, caching, and background refetch
- **Axios** for HTTP with automatic JWT attachment and 401 redirect
- **Tailwind CSS** for utility-first styling with a dark developer-tool design system

Component organization:
- `components/layout/` — AppShell, Sidebar, Topbar
- `components/ui/` — design system primitives (Modal, Toast, EmptyState, Badge, StatCard, etc.)
- `components/auth/` — ProtectedRoute
- `components/projects/` — domain-specific project components
- `pages/` — route-level page components (one per route)
- `contexts/` — AuthContext (JWT state, login/logout/register)
- `hooks/` — React Query hooks wrapping API calls

---

## Infrastructure

All services run in Docker containers orchestrated by Docker Compose:

| Service    | Image                        | Port  | Purpose |
|------------|------------------------------|-------|---------|
| `postgres` | `pgvector/pgvector:pg16`     | 5433  | Primary database + pgvector |
| `redis`    | `redis:7-alpine`             | 6379  | Celery broker + result backend |
| `api`      | Custom (python:3.12-slim)    | 8000  | FastAPI application |
| `web`      | Custom (node:20-alpine)      | 5173  | React dev server |

---

## Future Phases

1. **Phase 2**: Scan pipeline — file walker, code entity extraction, Celery task orchestration
2. **Phase 3**: Dependency analysis — parse npm/pip/cargo/maven manifests
3. **Phase 4**: Security analysis — pattern matching, secrets detection
4. **Phase 5**: Architecture analysis — module graph, React Flow visualization
5. **Phase 6**: Health scoring and recommendations
6. **Phase 7**: GitHub OAuth integration + repository import
7. **Phase 8**: AI codebase assistant (configurable provider abstraction)
8. **Phase 9**: E2E tests, performance optimization, production hardening
