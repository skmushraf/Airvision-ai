"""
AirVision AI — Forecast Endpoint
================================
GET /api/forecast?city=delhi
Returns AQI forecast (Now/1h/6h/12h/24h), hourly and daily weather forecasts.
"""

from flask import Blueprint, jsonify, request

from services.cities import get_city_by_name
from services.forecast import build_forecast

bp = Blueprint("forecast", __name__, url_prefix="/api")


@bp.route("/forecast", methods=["GET"])
def forecast():
    city = request.args.get("city", "delhi")
    city_obj = get_city_by_name(city)
    if city_obj is None:
        return jsonify({"error": f"Unknown city '{city}'"}), 404
    payload = build_forecast(city_obj)
    return jsonify(payload)
