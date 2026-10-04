"""
AirVision AI — Hotspots Endpoint
================================
GET /api/hotspots
Top-10 polluted/cleanest cities, best/worst country, global + continent averages.
"""

from flask import Blueprint, jsonify

from services.hotspots import compute_hotspots
from services.live import get_all_records

bp = Blueprint("hotspots", __name__, url_prefix="/api")


@bp.route("/hotspots", methods=["GET"])
def hotspots():
    records, meta = get_all_records()
    payload = compute_hotspots(records)
    payload["live_source"] = meta.get("source")
    payload["live_last_updated"] = meta.get("last_updated")
    return jsonify(payload)
