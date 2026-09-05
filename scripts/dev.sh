#!/usr/bin/env bash
# Start the full Canary development stack.
# Starts infrastructure in the background, runs migrations, then starts API and web.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT/apps/api"
WEB_DIR="$ROOT/apps/web"

echo "🐦 Canary dev stack starting…"
echo ""

# ── 1. Infrastructure ────────────────────────────────────────────────────────
echo "▶ Starting postgres + redis…"
docker compose -f "$ROOT/docker-compose.yml" up postgres redis -d
echo "  Waiting for postgres to be healthy…"
until docker compose -f "$ROOT/docker-compose.yml" exec -T postgres pg_isready -U canary -d canary > /dev/null 2>&1; do
  sleep 1
done
echo "  ✓ Postgres ready"

# ── 2. Migrations ────────────────────────────────────────────────────────────
echo ""
echo "▶ Running migrations…"
(cd "$API_DIR" && source .venv/bin/activate 2>/dev/null || true && PYTHONPATH="$API_DIR/src" alembic upgrade head)

# ── 3. API (background) ──────────────────────────────────────────────────────
echo ""
echo "▶ Starting API (http://localhost:8000)…"
(cd "$API_DIR" && source .venv/bin/activate 2>/dev/null || true && \
  PYTHONPATH="$API_DIR/src" uvicorn canary_api.main:app --reload --host 0.0.0.0 --port 8000) &
API_PID=$!

# ── 4. Web ────────────────────────────────────────────────────────────────────
echo "▶ Starting Web (http://localhost:5173)…"
(cd "$WEB_DIR" && npm run dev) &
WEB_PID=$!

echo ""
echo "✅ All services started."
echo "   API  → http://localhost:8000"
echo "   Docs → http://localhost:8000/docs"
echo "   Web  → http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop."

# Wait and clean up
trap "kill $API_PID $WEB_PID 2>/dev/null; exit 0" INT TERM
wait
