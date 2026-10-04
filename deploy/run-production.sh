#!/usr/bin/env bash
# =============================================================================
# AirVision AI — run the PRODUCTION build locally (single container)
# Serves the compiled React SPA + the Flask API from one process on :5000.
#
# Usage:  bash deploy/run-production.sh
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

echo "▸ 1/4  Installing backend dependencies…"
pip install -r backend/requirements.txt

echo "▸ 2/4  Installing frontend dependencies…"
(cd frontend && npm install)

echo "▸ 3/4  Building the React app…"
(cd frontend && npm run build)

echo "▸ 4/4  Staging SPA into backend/static…"
rm -rf backend/static
mkdir -p backend/static
cp -r frontend/dist/* backend/static/

echo "🚀 Starting production server on http://0.0.0.0:5000"
cd backend && python3 app.py
