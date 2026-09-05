# Canary — Database Design

PostgreSQL 16 with the pgvector extension.

---

## Design Principles

- **UUID primary keys** on all tables (avoids integer enumeration)
- **Foreign key constraints** with appropriate cascade rules
- **Indexed foreign keys** for all join-heavy columns
- **JSONB** for semi-structured metadata per entity
- **Timestamps** (`created_at`, `updated_at`) on every row
- **Soft delete** via `is_archived` flag where applicable
- **pgvector** for embedding-based similarity search on code entities

---

## Entity Relationship Overview

```
users
  ├── projects (owner_id)
  │     ├── project_sources (project_id)
  │     ├── scans (project_id)
  │     │     ├── files (scan_id)
  │     │     │     └── code_entities (file_id)
  │     │     ├── architecture_nodes (scan_id)
  │     │     │     └── architecture_edges (source_node_id, target_node_id)
  │     │     ├── dependencies (scan_id)
  │     │     ├── security_findings (scan_id)
  │     │     ├── health_scores (scan_id)
  │     │     ├── recommendations (scan_id)
  │     │     └── scan_changes (scan_id)
  │     ├── activity_events (project_id)
  │     └── conversations (project_id)
  │           └── messages (conversation_id)
  ├── workspaces (owner_id)
  └── github_connections (user_id)
        └── github_repositories (connection_id)
```

---

## Table Reference

### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR(320) | unique index |
| hashed_password | VARCHAR(255) | bcrypt |
| full_name | VARCHAR(255) | nullable |
| is_active | BOOLEAN | default true |
| is_superuser | BOOLEAN | default false |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### `projects`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| owner_id | UUID FK→users | CASCADE delete, indexed |
| name | VARCHAR(255) | |
| description | TEXT | nullable |
| source_type | ENUM | `local_workspace`, `zip_upload`, `github_repository` |
| status | ENUM | `created`, `importing`, `ready`, `scanning`, `analyzing`, `completed`, `failed` |
| is_archived | BOOLEAN | soft delete |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

**Unique constraint**: `(owner_id, name)`

---

### `project_sources`
Stores the origin metadata for a project's code without duplicating file contents.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | CASCADE delete |
| source_type | ENUM | same values as projects.source_type |
| metadata_json | JSONB | e.g. `{"root_path": "/home/..."}` for local, `{"zip_key": "..."}` for ZIP |

---

### `workspaces`
Registered local filesystem roots that can be imported.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| owner_id | UUID FK→users | |
| root_path | VARCHAR(4096) | absolute filesystem path |
| display_name | VARCHAR(255) | |

---

### `scans`
One scan run per project invocation.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | CASCADE delete, indexed |
| status | ENUM | `queued`, `running`, `completed`, `failed` |
| triggered_by | UUID FK→users | SET NULL on delete, nullable |
| started_at | TIMESTAMPTZ | nullable |
| completed_at | TIMESTAMPTZ | nullable |
| error_message | TEXT | nullable |
| stats | JSONB | file counts, entity counts, etc. |

---

### `files`
Every file discovered during a scan.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| path | VARCHAR(4096) | relative to project root |
| language | VARCHAR(64) | nullable |
| size_bytes | INTEGER | |
| content_hash | VARCHAR(64) | SHA-256, nullable |

---

### `code_entities`
Functions, classes, methods, and other named code constructs.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| file_id | UUID FK→files | |
| kind | VARCHAR(32) | `function`, `class`, `method`, etc. |
| name | VARCHAR(512) | |
| start_line | INTEGER | |
| end_line | INTEGER | |
| metadata_json | JSONB | docstring, parameters, etc. |
| embedding | VECTOR(1536) | pgvector — nullable until AI is configured |

---

### `architecture_nodes`
Modules, packages, services, or other architectural components.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| node_type | VARCHAR(64) | `module`, `package`, `service`, etc. |
| label | VARCHAR(512) | display name |
| metadata_json | JSONB | file paths, language, etc. |

---

### `architecture_edges`
Directed relationships between architecture nodes.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| source_node_id | UUID FK→architecture_nodes | CASCADE delete |
| target_node_id | UUID FK→architecture_nodes | CASCADE delete |
| edge_type | VARCHAR(64) | `imports`, `uses`, `depends_on`, etc. |
| metadata_json | JSONB | weight, call count, etc. |

---

### `dependencies`
Third-party packages detected in manifest files.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| ecosystem | VARCHAR(64) | `npm`, `pip`, `cargo`, `maven`, etc. |
| name | VARCHAR(255) | |
| version | VARCHAR(128) | nullable |
| is_direct | BOOLEAN | direct vs. transitive |
| metadata_json | JSONB | license, latest version, CVEs, etc. |

---

### `security_findings`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| severity | VARCHAR(16) | `critical`, `high`, `medium`, `low`, `info` |
| category | VARCHAR(64) | `secret`, `vuln`, `misconfig`, etc. |
| title | VARCHAR(512) | |
| description | TEXT | nullable |
| file_path | VARCHAR(4096) | nullable |
| line_number | INTEGER | nullable |
| metadata_json | JSONB | cwe, cvss, remediation, etc. |
| status | VARCHAR(32) | `open`, `acknowledged`, `resolved` |

---

### `health_scores`
One row per dimension per scan.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| overall_score | FLOAT | 0.0–100.0 |
| dimension | VARCHAR(64) | `security`, `dependencies`, `architecture`, etc. |
| score | FLOAT | dimension-specific score |
| details | JSONB | breakdown |

---

### `recommendations`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | |
| scan_id | UUID FK→scans | |
| priority | VARCHAR(16) | `critical`, `high`, `medium`, `low` |
| category | VARCHAR(64) | `security`, `dependencies`, `architecture`, etc. |
| title | VARCHAR(512) | |
| description | TEXT | nullable |
| status | VARCHAR(32) | `open`, `dismissed`, `resolved` |
| metadata_json | JSONB | references, effort estimate, etc. |

---

### `activity_events`
Append-only audit log.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| project_id | UUID FK→projects | nullable, SET NULL on delete |
| actor_id | UUID FK→users | nullable |
| event_type | VARCHAR(128) | e.g. `project.created`, `scan.completed` |
| summary | VARCHAR(512) | human-readable one-liner |
| metadata_json | JSONB | |

---

### `conversations` and `messages`
AI assistant conversation history.

| Column | Type | Notes |
|--------|------|-------|
| conversation.project_id | UUID FK→projects | |
| conversation.user_id | UUID FK→users | |
| message.role | VARCHAR(16) | `user`, `assistant`, `system` |
| message.content | TEXT | |

---

### `github_connections` and `github_repositories`
| Column | Type | Notes |
|--------|------|-------|
| connection.encrypted_access_token | VARCHAR(2048) | AES-encrypted at rest (future) |
| connection.scopes | VARCHAR(512) | granted OAuth scopes |
| repository.owner | VARCHAR(255) | GitHub org or user |
| repository.default_branch | VARCHAR(255) | |
| repository.metadata_json | JSONB | stars, language, private flag, etc. |

---

## Migration Strategy

Migrations are managed with **Alembic**:
- Config: `apps/api/alembic.ini`
- Environment: `apps/api/src/canary_api/persistence/migrations/env.py`
- Uses async engine; database URL injected from `Settings` (not hardcoded in ini)

```bash
# Apply all migrations
cd apps/api && alembic upgrade head

# Create a new migration (after editing models)
alembic revision --autogenerate -m "description"

# Rollback one step
alembic downgrade -1
```
