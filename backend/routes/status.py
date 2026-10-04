"""
AirVision AI — Status & Health Endpoints
========================================
GET /api/status       — system diagnostics (API key, model, cache, rate usage)
GET /api/health-check — liveness probe for deployment platforms (Render etc.)
"""

import time

from flask import Blueprint, jsonify

from config import Config
from services import timeutil
from database import db
from services import predictor

bp = Blueprint("status", __name__, url_prefix="/api")


@bp.route("/status", methods=["GET"])
def status():
    # Try a tiny live probe to verify the API key works (uses the Delhi cache)
    from services.cities import CITIES
    from services.openweather import fetch_air_quality

    probe = fetch_air_quality(CITIES[0]["lat"], CITIES[0]["lon"], CITIES[0]["id"])
    key_ok = isinstance(probe, dict) and "error" not in probe

    from services import cpcb as cpcb_svc

    cpcb_svc.get_city_index()  # warm cache so the diagnostics are accurate
    cpcb_block = cpcb_svc.provider_status()

    return jsonify({
        "app": {"name": Config.APP_NAME, "version": Config.APP_VERSION},
        "api_key_configured": bool(Config.OPENWEATHER_API_KEY),
        "api_key_valid": key_ok,
        "demo_mode": Config.ENABLE_DEMO_DATA,
        "sources": {
            "india_primary": "CPCB (data.gov.in)" if cpcb_block["available"]
                             else "OpenWeather (CPCB unavailable)",
            "global": "OpenWeather Air Pollution API",
            "weather_forecast_geocoding": "OpenWeather",
        },
        "cpcb": cpcb_block,
        "model": {
            "available": predictor.is_available(),
            "selected": (predictor.model_metadata() or {}).get("selected_model"),
            "metadata": predictor.model_metadata(),
        },
        "cache": {
            "ttl_seconds": Config.CACHE_TTL_SECONDS,
            "auto_refresh": Config.ENABLE_AUTO_REFRESH,
        },
        "api_calls_last_24h": db.api_call_count_last_24h(),
        "server_time": timeutil.utc_iso(),
        "timezone": time.tzname,
    })


@bp.route("/health-check", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": Config.APP_NAME,
                    "version": Config.APP_VERSION,
                    "time": timeutil.utc_iso()})
