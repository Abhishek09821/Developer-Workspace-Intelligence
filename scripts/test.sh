#!/usr/bin/env bash
# Run all Canary tests.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT/apps/api"
WEB_DIR="$ROOT/apps/web"

FAILED=0

# ── Backend (pytest) ──────────────────────────────────────────────────────────
echo "🐦 Running backend tests (pytest)…"
cd "$API_DIR"
source .venv/bin/activate 2>/dev/null || true

if PYTHONPATH="$API_DIR/src" pytest --tb=short -q "${@}"; then
  echo "✓ Backend tests passed"
else
  echo "✗ Backend tests FAILED"
  FAILED=1
fi

# ── Frontend (vitest) ─────────────────────────────────────────────────────────
echo ""
echo "🐦 Running frontend tests (vitest)…"
cd "$WEB_DIR"

if npm test; then
  echo "✓ Frontend tests passed"
else
  echo "✗ Frontend tests FAILED"
  FAILED=1
fi

echo ""
if [ $FAILED -eq 0 ]; then
  echo "✅ All tests passed."
else
  echo "❌ Some tests failed."
  exit 1
fi
