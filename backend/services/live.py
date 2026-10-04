"""
AirVision AI — Live Data Assembly Service
=========================================
Combines raw OpenWeather responses into the unified city record consumed by
every endpoint: current AQI (EPA-converted), pollutants, weather, ML-predicted
AQI and health recommendations. Also handles the SQLite "last successful data"
snapshot fallback.
"""

import threading
import time

from config import Config
from services import timeutil
from database import db
from services import aqi as aqi_svc
from services import health as health_svc
from services import predictor
from services.cities import CITIES
from services.openweather import fetch_air_quality, fetch_weather

CACHE_KEY = "live:air_quality"


def _parse_air(ow_aq: dict) -> dict:
    """Parse an OpenWeather air-pollution response into our AQI structure."""
    if not ow_aq or "list" not in ow_aq:
        return {"error": "no data"}
    entry = ow_aq["list"][0]
    components = entry.get("components", {})
    result = aqi_svc.compute_aqi_from_components(components)
    return {
        "aqi": result["aqi"],
        "sub_aqis": result["sub_aqis"],
        "driver": result["driver"],
        "components": components,
        "dt": entry.get("dt"),
    }


def _parse_weather(ow_w: dict) -> dict:
    """Parse an OpenWeather current-weather response into a flat dict."""
    if not ow_w or "main" not in ow_w:
        return {"error": "no data"}
    rain = ow_w.get("rain", {})
    hourly = rain.get("1h") if isinstance(rain, dict) else None
    return {
        "temp": ow_w["main"].get("temp"),
        "feels_like": ow_w["main"].get("feels_like"),
        "humidity": ow_w["main"].get("humidity"),
        "pressure": ow_w["main"].get("pressure"),
        "wind_speed": ow_w["wind"].get("speed") if ow_w.get("wind") else None,
        "wind_deg": ow_w.get("wind", {}).get("deg"),
        "visibility": ow_w.get("visibility"),
        "clouds": ow_w.get("clouds", {}).get("all"),
        "rain_1h": hourly,
        "sunrise": ow_w.get("sys", {}).get("sunrise"),
        "sunset": ow_w.get("sys", {}).get("sunset"),
        "description": ow_w.get("weather", [{}])[0].get("description"),
        "icon": ow_w.get("weather", [{}])[0].get("icon"),
        "dt": ow_w.get("dt"),
    }


def _cpcb_air(city: dict):
    """
    Try the CPCB (data.gov.in) feed for an Indian city.
    Returns (air_dict, meta) or (None, None) when unavailable.
    """
    if not Config.ENABLE_CPCB or city.get("cc") != "IN":
        return None, None

    from services import cpcb as cpcb_svc
    from services.cities import cpcb_lookup_names, cpcb_proxy_name

    hit = cpcb_svc.get_city(city["name"], aliases=cpcb_lookup_names(city))
    proxy_of = None
    if hit is None:
        proxy = cpcb_proxy_name(city)
        if proxy:
            hit = cpcb_svc.get_city(proxy)
            proxy_of = proxy if hit else None
    if hit is None or hit.get("aqi") is None:
        return None, None

    air = {
        "aqi": hit["aqi"],
        "sub_aqis": hit["sub_aqis"],
        "driver": hit["driver"],
        "components": hit["pollutants"],
        "dt": hit.get("updated_epoch"),
    }
    meta = {
        "aqi_standard": "CPCB NAQI",
        "provider": "CPCB — Central Pollution Control Board (data.gov.in)",
        "cpcb_station_count": hit.get("station_count"),
        "cpcb_stations": hit.get("stations", []),
        "cpcb_city": hit.get("city"),
        "cpcb_state": hit.get("state"),
        "cpcb_last_update": hit.get("last_update"),
        "cpcb_reliable": hit.get("reliable"),
        "cpcb_proxy": bool(proxy_of),
        "cpcb_proxy_note": (
            f"No CPCB station in {city['name']}; showing the nearest monitored "
            f"CPCB city ({proxy_of})." if proxy_of else None
        ),
    }
    return air, meta


def build_city_record(city: dict, live: bool = True) -> dict:
    """
    Build the full city record. When live fetching fails, falls back to the
    last successful snapshot stored in SQLite (never dummy data).
    """
    now = time.time()
    base = {
        "id": city["id"],
        "name": city["name"],
        "country": city["country"],
        "country_code": city["cc"],
        "continent": city["continent"],
        "lat": city["lat"],
        "lon": city["lon"],
        "source": "live",
        "api_error": None,
    }

    if live:
        # Weather always comes from OpenWeather (CPCB publishes no weather).
        ow_w = fetch_weather(city["lat"], city["lon"], city["id"])
        weather = _parse_weather(ow_w) if "error" not in ow_w else None

        # --- Source selection -------------------------------------------
        # Indian cities: CPCB (data.gov.in) is the PRIMARY air-quality source.
        # Everything else — and India when CPCB is unreachable — uses the
        # OpenWeather Air Pollution API.
        air, cpcb_meta = _cpcb_air(city)
        if air is not None:
            base["source"] = "cpcb"
            base.update(cpcb_meta)
        else:
            ow_aq = fetch_air_quality(city["lat"], city["lon"], city["id"])
            air = _parse_air(ow_aq) if "error" not in ow_aq else None
            base["aqi_standard"] = "US EPA (CPCB categories)"
            base["provider"] = "OpenWeather Air Pollution API"
            if city.get("cc") == "IN" and Config.ENABLE_CPCB:
                from services import cpcb as cpcb_svc

                base["cpcb_fallback_reason"] = (
                    cpcb_svc.last_error() or "No CPCB station data for this city"
                )

        aqi_value = air["aqi"] if air else None
        components = air["components"] if air else {}

        # ML prediction on live pollutant concentrations
        predicted = predictor.predict_aqi(components) if components else None

        if aqi_value is not None:
            record = {
                **base,
                "aqi": aqi_value,
                "aqi_category": aqi_svc.aqi_category(aqi_value),
                "aqi_color": aqi_svc.aqi_color(aqi_value),
                "pollutants": components,
                "weather": weather,
                "predicted_aqi": predicted,
                "predicted_category": (
                    aqi_svc.aqi_category(predicted) if predicted is not None else None
                ),
                "health": health_svc.health_response(aqi_value, city["name"]),
                "last_updated": now,
            }
            db_snapshot_set(city["id"], record)
            return record

        # --- Demo mode fallback (OPT-IN, clearly labelled) -------------------
        if Config.ENABLE_DEMO_DATA:
            from services import demo as demo_svc

            record = demo_svc.city_record(city)
            record["source"] = "demo"
            record["api_error"] = None
            return record

        # Live fetch failed → fall back to last successful snapshot
        snapshot = db_snapshot_get(city["id"])
        if snapshot:
            snap = dict(snapshot)
            snap["source"] = "cache"
            snap["api_error"] = "Live data temporarily unavailable — showing last successful reading"
            snap["last_updated"] = snap.get("last_updated", now)
            return snap

        # Never invent data: return a structurally-complete record with nulls
        return {
            **base,
            "aqi": None,
            "aqi_category": "Unknown",
            "aqi_color": "#64748b",
            "pollutants": {},
            "weather": None,
            "predicted_aqi": None,
            "predicted_category": None,
            "health": None,
            "api_error": "Live data temporarily unavailable",
            "last_updated": now,
        }

    # Non-live path: snapshot only (demo first when enabled)
    if Config.ENABLE_DEMO_DATA:
        from services import demo as demo_svc

        return demo_svc.city_record(city)
    snapshot = db_snapshot_get(city["id"])
    if snapshot:
        return snapshot
    return {**base, "aqi": None, "source": "unavailable", "api_error": "no data"}


# ---------------------------------------------------------------------------
# Bulk retrieval (shared by many endpoints)
# ---------------------------------------------------------------------------
def build_envelope(records, status="ok", source="live", error=None):
    """Assemble the standard live-data response envelope."""
    live_count = sum(1 for r in records if r.get("aqi") is not None)
    demo_count = sum(1 for r in records if r.get("source") == "demo")
    cpcb_count = sum(1 for r in records if r.get("source") == "cpcb")
    source_breakdown = {}
    for r in records:
        key = r.get("source") or "unknown"
        source_breakdown[key] = source_breakdown.get(key, 0) + 1
    if status == "ok" and live_count == 0:
        status = "degraded"
    return {
        "status": status,
        "source": source,
        "demo_mode": demo_count > 0,
        "cpcb_count": cpcb_count,
        "sources": source_breakdown,
        "last_updated": timeutil.utc_iso(),
        "count": len(records),
        "live_count": live_count,
        "cities": records,
        "error": error or ("Live data temporarily unavailable — API key may be "
                           "invalid or the upstream service is unreachable. "
                           "Showing cached snapshots where available."
                           if status == "degraded" else None),
    }


def refresh_all_records() -> dict:
    """Fetch live data for every city and cache the combined payload."""
    records = [build_city_record(city, live=True) for city in CITIES]
    payload = build_envelope(records)
    db.cache_set(CACHE_KEY, payload, ttl_seconds=Config.CACHE_TTL_SECONDS)
    return payload


# --- Forced refresh (dashboard open) ---------------------------------------
# The dashboard asks for fresh weather every time it is opened. A full sweep
# costs ~2 OpenWeather calls per city, so a server-side throttle protects the
# free-tier quota no matter how often the page is opened or how many browser
# tabs are pointed at the backend.
_force_state = {"at": 0.0}
_force_lock = threading.Lock()


def force_refresh_all() -> dict:
    """
    Bypass every cache layer and re-fetch live weather + air quality for all
    cities — throttled to once per FORCE_REFRESH_MIN_INTERVAL seconds.

    Returns the payload with two extra fields:
      refreshed            — True when an upstream sweep actually happened
      next_refresh_in      — seconds until a forced refresh is allowed again
    """
    interval = Config.FORCE_REFRESH_MIN_INTERVAL
    now = time.time()

    with _force_lock:
        elapsed = now - _force_state["at"]
        if elapsed < interval:
            cached = db.cache_get(CACHE_KEY)
            if cached:
                return {**cached, "refreshed": False,
                        "throttled": True,
                        "next_refresh_in": int(interval - elapsed)}
        _force_state["at"] = now

    # Drop the in-memory OpenWeather TTL cache so weather is genuinely re-read.
    # The CPCB feed keeps its own (longer) TTL — it only publishes hourly.
    from services.openweather import invalidate_mem_cache

    invalidate_mem_cache()
    payload = refresh_all_records()
    return {**payload, "refreshed": True, "throttled": False,
            "next_refresh_in": interval}


def get_all_records():
    """Return (records, meta). Refreshes the cache only when it is stale."""
    cached = db.cache_get(CACHE_KEY)
    if cached:
        return cached["cities"], cached
    try:
        payload = refresh_all_records()
        return payload["cities"], payload
    except Exception as exc:
        snapshots = [build_city_record(c, live=False) for c in CITIES]
        meta = build_envelope(snapshots, status="degraded", source="snapshot",
                              error=str(exc))
        return snapshots, meta


# ---------------------------------------------------------------------------
# SQLite snapshot helpers (isolated here to avoid circular imports)
# ---------------------------------------------------------------------------
def db_snapshot_get(city_id: str):
    from database import db

    row = db.snapshot_get(city_id)
    return row["payload"] if row else None


def db_snapshot_set(city_id: str, record: dict):
    from database import db

    db.snapshot_set(city_id, record)
