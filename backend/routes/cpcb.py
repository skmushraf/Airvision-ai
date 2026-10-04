"""
AirVision AI — CPCB (data.gov.in) Endpoints
============================================
GET /api/cpcb/status    — provider diagnostics (key configured, cities, error)
GET /api/cpcb/cities    — every Indian city in the CPCB feed with its NAQI
GET /api/cpcb/stations  — station-level readings for the map's station layer
                          optional ?city=Delhi

All upstream calls happen server-side; the data.gov.in key is never exposed.
"""

from flask import Blueprint, jsonify, request

from services import cpcb as cpcb_svc

bp = Blueprint("cpcb", __name__, url_prefix="/api/cpcb")


@bp.route("/status", methods=["GET"])
def cpcb_status():
    cpcb_svc.get_city_index()  # warm the cache so the report is meaningful
    return jsonify(cpcb_svc.provider_status())


@bp.route("/cities", methods=["GET"])
def cpcb_cities():
    index = cpcb_svc.get_city_index()
    cities = sorted(
        (
            {
                "city": v["city"], "state": v["state"],
                "aqi": v["aqi"], "aqi_category": v["aqi_category"],
                "aqi_color": v["aqi_color"], "driver": v["driver"],
                "sub_aqis": v["sub_aqis"], "pollutants": v["pollutants"],
                "station_count": v["station_count"],
                "reliable": v["reliable"], "last_update": v["last_update"],
            }
            for v in index.values() if v.get("aqi") is not None
        ),
        key=lambda c: c["aqi"], reverse=True,
    )
    return jsonify({
        "status": "ok" if cities else "unavailable",
        "standard": "CPCB NAQI",
        "provider": "CPCB — Central Pollution Control Board (data.gov.in)",
        "count": len(cities),
        "cities": cities,
        "error": cpcb_svc.last_error(),
    })


@bp.route("/stations", methods=["GET"])
def cpcb_stations():
    city_filter = request.args.get("city")
    index = cpcb_svc.get_city_index()
    stations = []
    for record in index.values():
        if city_filter and cpcb_svc.normalize_city(record["city"]) != \
                cpcb_svc.normalize_city(city_filter):
            continue
        for station in record.get("stations", []):
            stations.append({
                **station,
                "city": record["city"],
                "state": record["state"],
                "city_aqi": record["aqi"],
                "city_aqi_category": record["aqi_category"],
            })
    return jsonify({
        "status": "ok" if stations else "unavailable",
        "provider": "CPCB — Central Pollution Control Board (data.gov.in)",
        "count": len(stations),
        "stations": stations,
        "error": cpcb_svc.last_error(),
    })


@bp.route("/refresh", methods=["GET", "POST"])
def cpcb_refresh():
    """Force-refresh the CPCB cache (useful during a demo)."""
    cpcb_svc.invalidate()
    index = cpcb_svc.get_city_index(force=True)
    return jsonify({"status": "ok" if index else "unavailable",
                    "cities_indexed": len(index),
                    "error": cpcb_svc.last_error()})
