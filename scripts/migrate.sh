#!/usr/bin/env bash
# Run Alembic migrations against the configured database.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT/apps/api"

COMMAND="${1:-upgrade head}"

echo "🐦 Canary — running migration: alembic $COMMAND"
cd "$API_DIR"
source .venv/bin/activate 2>/dev/null || true
alembic $COMMAND
echo "✓ Done"
