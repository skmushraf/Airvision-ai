"""
AirVision AI — Live Air Quality & Weather Endpoints
===================================================
GET /api/live-air-quality  — live AQI + weather + prediction for all cities
GET /api/live-weather      — live weather only

Response envelope:
    {status, source, last_updated, count, cities: [...], error}
"""

import time

from services import timeutil

from flask import Blueprint, jsonify, request

from services.cities import CITIES, get_city_by_name
from services.live import build_city_record, force_refresh_all, get_all_records

bp = Blueprint("live", __name__, url_prefix="/api")


def _filter(records, city=None, country=None, category=None):
    """Apply optional filters to a list of city records."""
    out = []
    for r in records:
        if city and r["id"] != city and r["name"].lower() != city.lower():
            continue
        if country and r["country"].lower() != country.lower():
            continue
        if category and (r.get("aqi_category") or "").lower() != category.lower():
            continue
        out.append(r)
    return out


@bp.route("/live-air-quality", methods=["GET"])
def live_air_quality():
    city = request.args.get("city")
    country = request.args.get("country")
    category = request.args.get("category")

    if city:
        c = get_city_by_name(city)
        if c is None:
            return jsonify({"error": f"Unknown city '{city}'",
                            "available": [x["id"] for x in CITIES]}), 404
        record = build_city_record(c, live=True)
        return jsonify({"status": "ok", "source": record["source"],
                        "last_updated": timeutil.utc_iso(),
                        "count": 1, "cities": [record], "error": record.get("api_error")})

    # ?refresh=1 — the dashboard sends this on every open so weather is
    # re-read from OpenWeather (server-side throttled, see force_refresh_all).
    if request.args.get("refresh") in ("1", "true", "yes"):
        meta = force_refresh_all()
        records = meta.get("cities", [])
    else:
        records, meta = get_all_records()
    filtered = _filter(records, city=city, country=country, category=category)
    meta = {**meta, "count": len(filtered), "cities": filtered}
    return jsonify(meta)


@bp.route("/live-weather", methods=["GET"])
def live_weather():
    city = request.args.get("city")
    if city:
        c = get_city_by_name(city)
        if c is None:
            return jsonify({"error": f"Unknown city '{city}'"}), 404
        record = build_city_record(c, live=True)
        return jsonify({"status": "ok", "city": record["name"],
                        "weather": record.get("weather"),
                        "last_updated": record.get("last_updated"),
                        "source": record["source"]})

    records, meta = get_all_records()
    weather_only = [
        {
            "id": r["id"], "name": r["name"], "country": r["country"],
            "lat": r["lat"], "lon": r["lon"],
            "weather": r.get("weather"), "aqi": r.get("aqi"),
            "last_updated": r.get("last_updated"), "source": r["source"],
        }
        for r in records
    ]
    return jsonify({**meta, "cities": weather_only})
