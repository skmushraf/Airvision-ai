# =============================================================================
# AirVision AI — single-container image (Flask API + built React SPA)
# Build:  docker build -f deploy/Dockerfile -t airvision-ai .
# Run:    docker run -p 8000:8000 -e OPENWEATHER_API_KEY=... airvision-ai
# =============================================================================

# --- Stage 1: build the React frontend ---------------------------------------
FROM node:20-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python backend serving API + static SPA -------------------------
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000
WORKDIR /app

COPY backend/ backend/
COPY models/ models/
COPY ml/ ml/
COPY --from=frontend-build /build/frontend/dist /app/backend/static

RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health-check')" || exit 1

CMD ["sh", "-c", "cd backend && gunicorn -b 0.0.0.0:${PORT} app:app --workers 1 --threads 8 --timeout 120"]