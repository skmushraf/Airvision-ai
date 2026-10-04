"""
AirVision AI — Global Map Endpoint
==================================
GET /api/map-data
Lightweight payload for the React Leaflet map: one compact object per city
with everything the markers and popups need.
"""

from flask import Blueprint, jsonify

from services.live import get_all_records

bp = Blueprint("mapdata", __name__, url_prefix="/api")


@bp.route("/map-data", methods=["GET"])
def map_data():
    records, meta = get_all_records()
    markers = []
    for r in records:
        weather = r.get("weather") or {}
        markers.append({
            "id": r["id"],
            "name": r["name"],
            "country": r["country"],
            "country_code": r["country_code"],
            "continent": r["continent"],
            "lat": r["lat"],
            "lon": r["lon"],
            "aqi": r.get("aqi"),
            "category": r.get("aqi_category"),
            "color": r.get("aqi_color"),
            "pm2_5": (r.get("pollutants") or {}).get("pm2_5"),
            "pm10": (r.get("pollutants") or {}).get("pm10"),
            "co": (r.get("pollutants") or {}).get("co"),
            "no2": (r.get("pollutants") or {}).get("no2"),
            "so2": (r.get("pollutants") or {}).get("so2"),
            "o3": (r.get("pollutants") or {}).get("o3"),
            "temperature": weather.get("temp"),
            "humidity": weather.get("humidity"),
            "wind_speed": weather.get("wind_speed"),
            "pressure": weather.get("pressure"),
            "predicted_aqi": r.get("predicted_aqi"),
            "health_recommendation": (r.get("health") or {}).get("recommendation"),
            "last_updated": r.get("last_updated"),
            "source": r.get("source"),
            "provider": r.get("provider"),
            "aqi_standard": r.get("aqi_standard"),
            "station_count": r.get("cpcb_station_count"),
            "cpcb_proxy": r.get("cpcb_proxy", False),
            "cpcb_proxy_note": r.get("cpcb_proxy_note"),
            "api_error": r.get("api_error"),
        })
    return jsonify({
        "status": meta.get("status", "ok"),
        "source": meta.get("source"),
        "last_updated": meta.get("last_updated"),
        "sources": meta.get("sources"),
        "cpcb_count": meta.get("cpcb_count"),
        "count": len(markers),
        "markers": markers,
        "error": meta.get("error"),
    })
