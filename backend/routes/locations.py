"""
AirVision AI — Cities & Countries Endpoints
===========================================
GET /api/cities                 — full city catalog (+ optional ?search=)
GET /api/cities/autocomplete    — lightweight search for the search box
GET /api/countries              — country summaries (avg AQI where available)
"""

from flask import Blueprint, jsonify, request

from services.cities import (
    CITIES,
    COUNTRIES,
    cities_by_country,
    search_cities,
)
from services.live import get_all_records

bp = Blueprint("locations", __name__, url_prefix="/api")


@bp.route("/cities", methods=["GET"])
def cities():
    search = request.args.get("search", "")
    if search:
        results = search_cities(search, limit=25)
        return jsonify({"count": len(results), "cities": results})
    return jsonify({"count": len(CITIES), "cities": CITIES})


@bp.route("/cities/autocomplete", methods=["GET"])
def autocomplete():
    q = request.args.get("q", "")
    results = search_cities(q, limit=10)
    return jsonify({
        "results": [
            {
                "id": c["id"],
                "name": c["name"],
                "country": c["country"],
                "cc": c["cc"],
                "lat": c["lat"],
                "lon": c["lon"],
            }
            for c in results
        ]
    })


@bp.route("/countries", methods=["GET"])
def countries():
    records, _ = get_all_records()

    summaries = []
    for country in COUNTRIES:
        city_rows = [r for r in records if r["country"] == country]
        aqis = [r["aqi"] for r in city_rows if r.get("aqi") is not None]
        temps = [
            r["weather"]["temp"] for r in city_rows
            if r.get("weather") and r["weather"].get("temp") is not None
        ]
        summaries.append({
            "name": country,
            "cc": city_rows[0]["country_code"] if city_rows else None,
            "continent": city_rows[0]["continent"] if city_rows else None,
            "cities": [{"id": r["id"], "name": r["name"], "aqi": r.get("aqi"),
                        "category": r.get("aqi_category")} for r in city_rows],
            "city_count": len(city_rows),
            "average_aqi": round(sum(aqis) / len(aqis), 1) if aqis else None,
            "average_temperature": round(sum(temps) / len(temps), 1) if temps else None,
            "worst_aqi": max(aqis) if aqis else None,
        })

    summaries.sort(key=lambda c: (c["average_aqi"] is None, -(c["average_aqi"] or 0)))
    return jsonify({"count": len(summaries), "countries": summaries})
