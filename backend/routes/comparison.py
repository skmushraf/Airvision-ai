"""
AirVision AI — City Comparison Endpoint
=======================================
GET /api/comparison?city1=delhi&city2=mumbai
Side-by-side AQI, pollutant and weather comparison + AQI forecast for both.
"""

from flask import Blueprint, jsonify, request

from services.cities import get_city_by_name
from services.forecast import build_forecast
from services.live import build_city_record

bp = Blueprint("comparison", __name__, url_prefix="/api")


@bp.route("/comparison", methods=["GET"])
def comparison():
    city1 = request.args.get("city1", "delhi")
    city2 = request.args.get("city2", "mumbai")

    c1 = get_city_by_name(city1)
    c2 = get_city_by_name(city2)
    if c1 is None or c2 is None:
        missing = city1 if c1 is None else city2
        return jsonify({"error": f"Unknown city '{missing}'"}), 404

    rec1 = build_city_record(c1, live=True)
    rec2 = build_city_record(c2, live=True)
    fc1 = build_forecast(c1)
    fc2 = build_forecast(c2)

    def side(city, rec, fc):
        weather = rec.get("weather") or {}
        return {
            "city": {"id": city["id"], "name": city["name"], "country": city["country"],
                     "lat": city["lat"], "lon": city["lon"]},
            "aqi": rec.get("aqi"),
            "aqi_category": rec.get("aqi_category"),
            "aqi_color": rec.get("aqi_color"),
            "predicted_aqi": rec.get("predicted_aqi"),
            "pollutants": rec.get("pollutants"),
            "weather": weather,
            "aqi_forecast": fc.get("aqi_forecast"),
            "daily": fc.get("daily"),
            "health": rec.get("health"),
            "last_updated": rec.get("last_updated"),
            "source": rec.get("source"),
        }

    return jsonify({
        "city1": side(c1, rec1, fc1),
        "city2": side(c2, rec2, fc2),
        "comparison": {
            "aqi_difference": (
                round((rec1.get("aqi") or 0) - (rec2.get("aqi") or 0), 1)
                if rec1.get("aqi") is not None and rec2.get("aqi") is not None else None
            ),
            "temperature_difference": (
                round((rec1.get("weather") or {}).get("temp", 0) - (rec2.get("weather") or {}).get("temp", 0), 1)
                if rec1.get("weather") and rec2.get("weather") else None
            ),
        },
    })
