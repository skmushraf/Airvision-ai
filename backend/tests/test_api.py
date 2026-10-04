"""
AirVision AI — backend API test suite
=====================================
Run:  cd backend && pytest -q
Covers endpoint contracts, error handling and the resilience envelope
(live endpoints must never crash when the upstream API key is invalid).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Core / diagnostics
# ---------------------------------------------------------------------------
def test_health_check(client):
    res = client.get("/api/health-check")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_status_shape(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    body = res.get_json()
    assert "api_key_configured" in body
    assert "model" in body
    assert "api_calls_last_24h" in body


def test_api_index(client):
    # "/" is the SPA when a production build is present, otherwise JSON.
    res = client.get("/")
    assert res.status_code == 200


def test_api_index_json(client):
    res = client.get("/api")
    body = res.get_json()
    assert res.status_code == 200
    assert body["app"] == "AirVision AI"


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------
def test_cities_catalog(client):
    res = client.get("/api/cities")
    body = res.get_json()
    assert res.status_code == 200
    assert body["count"] >= 58
    for c in body["cities"]:
        assert c["lat"] is not None and c["lon"] is not None
        assert c["continent"]


def test_cities_search(client):
    res = client.get("/api/cities?search=gunt")
    names = [c["name"] for c in res.get_json()["cities"]]
    assert "Guntur" in names


def test_autocomplete(client):
    res = client.get("/api/cities/autocomplete?q=tena")
    names = [r["name"] for r in res.get_json()["results"]]
    assert "Tenali" in names


def test_countries(client):
    res = client.get("/api/countries")
    body = res.get_json()
    assert res.status_code == 200
    assert body["count"] >= 25
    assert all("cities" in c for c in body["countries"])


# ---------------------------------------------------------------------------
# Historical analytics (dataset driven — offline, always available)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("aqi,category", [(20, "Good"), (75, "Satisfactory"),
                                          (150, "Moderate"), (250, "Poor"),
                                          (350, "Very Poor"), (450, "Severe")])
def test_health_categories(client, aqi, category):
    res = client.get(f"/api/health?aqi={aqi}")
    body = res.get_json()
    assert res.status_code == 200
    assert body["category"] == category
    assert body["recommendation"]


def test_health_requires_param(client):
    assert client.get("/api/health").status_code == 400


# ---------------------------------------------------------------------------
# Live endpoints (resilience: must degrade, never crash)
# ---------------------------------------------------------------------------
def test_live_air_quality_envelope(client):
    res = client.get("/api/live-air-quality")
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 58
    for c in body["cities"]:
        # Either a real reading, or an explicit api_error — never a 500.
        assert "api_error" in c or c.get("aqi") is not None


def test_live_unknown_city_404(client):
    assert client.get("/api/live-air-quality?city=atlantis").status_code == 404


def test_map_data_shape(client):
    res = client.get("/api/map-data")
    body = res.get_json()
    assert res.status_code == 200
    assert body["count"] == 58
    m = body["markers"][0]
    for key in ("lat", "lon", "name", "country", "aqi", "color"):
        assert key in m


def test_forecast_unknown_city_404(client):
    assert client.get("/api/forecast?city=atlantis").status_code == 404


def test_comparison_unknown_city_404(client):
    assert client.get("/api/comparison?city1=delhi&city2=atlantis").status_code == 404


def test_hotspots_envelope(client):
    res = client.get("/api/hotspots")
    body = res.get_json()
    assert res.status_code == 200
    for key in ("top_polluted", "cleanest", "average_global_aqi", "by_continent"):
        assert key in body


# ---------------------------------------------------------------------------
# Historical analytics removal
# ---------------------------------------------------------------------------
def test_historical_endpoint_removed(client):
    """/api/historical was removed from the product — must 404 as JSON."""
    res = client.get("/api/historical?city=delhi")
    assert res.status_code == 404
    assert res.is_json


def test_historical_not_advertised_in_api_index(client):
    res = client.get("/api")
    assert res.status_code == 200
    assert "historical" not in res.get_data(as_text=True).lower()


# ---------------------------------------------------------------------------
# Forced refresh on dashboard open (throttled)
# ---------------------------------------------------------------------------
def test_refresh_param_returns_refresh_metadata(client):
    res = client.get("/api/live-air-quality?refresh=1")
    assert res.status_code == 200
    body = res.get_json()
    assert "refreshed" in body and "next_refresh_in" in body
    assert isinstance(body["cities"], list)


def test_second_immediate_refresh_is_throttled(client):
    """Two opens in quick succession must not trigger two upstream sweeps."""
    client.get("/api/live-air-quality?refresh=1")
    body = client.get("/api/live-air-quality?refresh=1").get_json()
    assert body["throttled"] is True
    assert body["refreshed"] is False
    assert body["next_refresh_in"] > 0


def test_throttle_window_is_configurable():
    from config import Config
    from services import live as live_svc

    assert Config.FORCE_REFRESH_MIN_INTERVAL >= 1
    assert hasattr(live_svc, "force_refresh_all")


def test_plain_request_does_not_force_refresh(client):
    """Without ?refresh=1 the cached payload is served (no quota spent)."""
    body = client.get("/api/live-air-quality").get_json()
    assert "refreshed" not in body


# ---------------------------------------------------------------------------
# Timestamp correctness (false "data unavailable" staleness bug)
# ---------------------------------------------------------------------------
def test_last_updated_is_iso_utc(client):
    """
    Naive timestamps are parsed as *local* time by browsers, so a UTC server
    and an IST user disagreed by 5.5h and fresh data looked stale. Every
    timestamp must now be explicit ISO-8601 UTC ending in 'Z'.
    """
    body = client.get("/api/live-air-quality").get_json()
    ts = body["last_updated"]
    assert ts.endswith("Z") and "T" in ts, f"not ISO-8601 UTC: {ts}"


def test_status_server_time_is_iso_utc(client):
    body = client.get("/api/status").get_json()
    assert body["server_time"].endswith("Z")
    assert client.get("/api/health-check").get_json()["time"].endswith("Z")


def test_last_updated_parses_and_is_recent(client):
    from datetime import datetime, timezone

    ts = client.get("/api/live-air-quality").get_json()["last_updated"]
    parsed = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - parsed).total_seconds()
    assert -60 < age < 3600, f"timestamp {ts} is {age}s away from now"


def test_timeutil_roundtrip():
    from datetime import datetime

    from services import timeutil

    assert timeutil.utc_iso(0) == "1970-01-01T00:00:00Z"
    assert timeutil.to_utc_iso(datetime(2026, 10, 3, 4, 26, 2)).endswith("Z")
