#!/usr/bin/env bash
# Seed the database with a development user and sample project.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

API_BASE="${CANARY_API_URL:-http://localhost:8000/api/v1}"

echo "🐦 Canary dev seed — target: $API_BASE"
echo ""

# ── Register dev user ─────────────────────────────────────────────────────────
echo "▶ Registering dev user (dev@canary.dev / password123)…"
RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@canary.dev","password":"password123","full_name":"Dev User"}' \
  -w "\n%{http_code}")

BODY=$(echo "$RESPONSE" | head -n1)
STATUS=$(echo "$RESPONSE" | tail -n1)

if [ "$STATUS" = "201" ]; then
  echo "  ✓ User created"
  TOKEN=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
elif [ "$STATUS" = "409" ]; then
  echo "  ℹ User already exists — logging in…"
  LOGIN=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"dev@canary.dev","password":"password123"}')
  TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
else
  echo "  ✗ Unexpected status $STATUS: $BODY"
  exit 1
fi

# ── Create sample projects ────────────────────────────────────────────────────
echo ""
echo "▶ Creating sample projects…"

create_project() {
  local name="$1"
  local source="$2"
  local desc="$3"
  curl -s -X POST "$API_BASE/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"name\":\"$name\",\"source_type\":\"$source\",\"description\":\"$desc\"}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  ✓ {d[\"name\"]} ({d[\"id\"]})')" \
    2>/dev/null || echo "  ℹ Project '$name' may already exist"
}

create_project "canary-platform"      "local_workspace"    "The Canary platform itself"
create_project "sample-react-app"     "zip_upload"         "A sample React application for testing"
create_project "open-source-library"  "github_repository"  "An open-source library imported from GitHub"

echo ""
echo "✅ Seed complete."
echo "   Login: dev@canary.dev / password123"
echo "   Token: ${TOKEN:0:40}…"
