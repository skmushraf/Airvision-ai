"""
AirVision AI — Route Blueprint Registration
===========================================
Import each blueprint and register it on the Flask app.
"""

from routes import (
    comparison,
    cpcb,
    forecast,
    health,
    live,
    locations,
    mapdata,
    hotspots,
    status,
)


def register_blueprints(app):
    app.register_blueprint(live.bp)
    app.register_blueprint(forecast.bp)
    app.register_blueprint(locations.bp)
    app.register_blueprint(comparison.bp)
    app.register_blueprint(hotspots.bp)
    app.register_blueprint(health.bp)
    app.register_blueprint(mapdata.bp)
    app.register_blueprint(status.bp)
    app.register_blueprint(cpcb.bp)
