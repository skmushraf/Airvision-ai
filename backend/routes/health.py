"""
AirVision AI — Health Recommendation Endpoint
=============================================
GET /api/health?city=delhi   → recommendation for a city's current AQI
GET /api/health?aqi=275      → recommendation for an arbitrary AQI value
"""

from flask import Blueprint, jsonify, request

from services.cities import get_city_by_name
from services.health import health_response
from services.live import build_city_record

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.route("/health", methods=["GET"])
def health():
    city = request.args.get("city")
    aqi_param = request.args.get("aqi")

    if aqi_param is not None:
        try:
            aqi = max(0, min(500, float(aqi_param)))
        except ValueError:
            return jsonify({"error": "aqi must be numeric"}), 400
        return jsonify(health_response(aqi, city))

    if city:
        city_obj = get_city_by_name(city)
        if city_obj is None:
            return jsonify({"error": f"Unknown city '{city}'"}), 404
        record = build_city_record(city_obj, live=True)
        if record.get("aqi") is None:
            return jsonify({"error": "Live AQI currently unavailable for this city",
                            "city": city}), 503
        return jsonify(health_response(record["aqi"], city))

    return jsonify({"error": "Provide either ?city= or ?aqi="}), 400
