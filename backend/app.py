"""
AirVision AI — Flask Application Factory
========================================
Entry point:  python app.py   (or  gunicorn app:app / waitress)
"""

import os
import threading
import time

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from database import db

# Directory that holds the compiled React SPA (created by the deploy step or
# the Docker image). When present, the backend serves the dashboard AND the
# API from one process (single-container deployment).
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
HAS_SPA = os.path.isdir(STATIC_DIR) and os.path.exists(os.path.join(STATIC_DIR, "index.html"))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- CORS ---------------------------------------------------------------
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}},
         supports_credentials=False)

    # --- Initialise the database --------------------------------------------
    db._get_connection()  # creates schema

    # --- Register API blueprints ---------------------------------------------
    from routes import register_blueprints

    register_blueprints(app)

    # --- Root: JSON API index, or the SPA when a production build exists -------
    @app.route("/")
    @app.route("/<path:path>")
    def root_handler(path=""):
        # API routes registered by the blueprints take precedence; anything
        # under /api that is not a real endpoint is a 404 JSON.
        if path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404

        if not HAS_SPA:
            if path == "":
                return jsonify({
                    "app": Config.APP_NAME,
                    "version": Config.APP_VERSION,
                    "message": "Real-Time Global Air Quality Monitoring & Forecasting System",
                    "endpoints": [
                        "/api/live-air-quality", "/api/live-weather", "/api/forecast",
                        "/api/cities", "/api/countries",
                        "/api/comparison", "/api/hotspots", "/api/health",
                        "/api/map-data", "/api/status", "/api/health-check",
                    ],
                    "docs": "See documentation/ for the full API reference.",
                })
            return jsonify({"error": "Not found"}), 404

        # Serve the React SPA with history-API fallback (deep links → index.html)
        if path == "":
            return send_from_directory(STATIC_DIR, "index.html")
        full = os.path.join(STATIC_DIR, path)
        if os.path.isfile(full):
            return send_from_directory(STATIC_DIR, path)
        return send_from_directory(STATIC_DIR, "index.html")

    # --- API index (always available as JSON) ----------------------------------
    @app.route("/api")
    def api_index():
        return jsonify({
            "app": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "message": "Real-Time Global Air Quality Monitoring & Forecasting System",
            "endpoints": [
                "/api/live-air-quality", "/api/live-weather", "/api/forecast",
                "/api/cities", "/api/countries",
                "/api/comparison", "/api/hotspots", "/api/health",
                "/api/map-data", "/api/status", "/api/health-check",
            ],
        })

    # --- Global JSON error handlers ------------------------------------------
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(err):
        return jsonify({"error": "Internal server error",
                        "detail": str(err)}), 500

    # --- Optional background auto-refresh (see Config.ENABLE_AUTO_REFRESH) ---
    if Config.ENABLE_AUTO_REFRESH:
        threading.Thread(target=_auto_refresh_loop, daemon=True).start()

    return app


def _auto_refresh_loop():
    """Background thread: refresh the live cache every TTL (opt-in)."""
    from services.live import refresh_all_records

    while True:
        time.sleep(Config.CACHE_TTL_SECONDS)
        try:
            refresh_all_records()
        except Exception:
            pass  # keep the loop alive; stale cache serves as fallback


app = create_app()


if __name__ == "__main__":
    # Production-ish local server via waitress; debug mode via flask run.
    try:
        from waitress import serve

        print(f"🚀 {Config.APP_NAME} backend running on http://0.0.0.0:5000")
        serve(app, host="0.0.0.0", port=5000, threads=8)
    except ImportError:
        app.run(host="0.0.0.0", port=5000, debug=True)
