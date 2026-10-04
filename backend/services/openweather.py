"""
AirVision AI — OpenWeather API Client
=====================================
Thin, resilient client for the four OpenWeather endpoints used by the app:

  - Air Pollution API      /data/2.5/air_pollution
  - Current Weather API    /data/2.5/weather
  - 5-Day Forecast API     /data/2.5/forecast
  - Geocoding API          /geo/1.0/direct

Features
--------
* Reads the API key from environment config (never hardcoded, never exposed).
* Automatic retry with exponential backoff on transient failures.
* Concurrency via ThreadPoolExecutor for bulk city fetches.
* In-memory TTL cache + SQLite persistence so the dashboard keeps serving
  the last successful data when the upstream API is down.
* Audit logging of every outbound call (rate-limit tracking).
"""

import concurrent.futures as futures
import threading
import time

import requests

from config import Config
from database import db

_lock = threading.Lock()
_mem_cache = {}  # {key: (payload, expires_at)}

_SESSION = requests.Session()


# ---------------------------------------------------------------------------
# Low-level request helpers
# ---------------------------------------------------------------------------
def _get_json(url: str, params: dict, timeout: int = None):
    """GET with retries + exponential backoff. Returns parsed JSON or None."""
    timeout = timeout or Config.REQUEST_TIMEOUT
    last_exc = None
    for attempt in range(1, Config.RETRY_ATTEMPTS + 1):
        try:
            resp = _SESSION.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            # 401 (bad key) / 404 / 429 are not retried beyond attempt 1
            if resp.status_code in (401, 403, 404, 429):
                return {"error": resp.status_code, "message": resp.text[:200]}
            last_exc = RuntimeError(f"HTTP {resp.status_code}")
        except requests.RequestException as exc:
            last_exc = exc
        time.sleep(0.5 * attempt)  # exponential-ish backoff
    return {"error": -1, "message": str(last_exc)}


def _mem_cache_get(key: str):
    item = _mem_cache.get(key)
    if item and item[1] > time.time():
        return item[0]
    return None


def _mem_cache_set(key: str, payload, ttl: int = None):
    ttl = ttl or Config.CACHE_TTL_SECONDS
    with _lock:
        _mem_cache[key] = (payload, time.time() + ttl)


# ---------------------------------------------------------------------------
# Public fetch helpers (each one caches)
# ---------------------------------------------------------------------------
def fetch_air_quality(lat: float, lon: float, city_id: str = None) -> dict:
    """Return the OpenWeather air pollution response (cached)."""
    key = f"ow:aq:{city_id or f'{lat},{lon}'}"
    cached = _mem_cache_get(key)
    if cached:
        return cached
    data = _get_json(
        f"{Config.OW_BASE_URL}/air_pollution",
        {"lat": lat, "lon": lon, "appid": Config.OPENWEATHER_API_KEY},
    )
    _log("air_pollution", city_id, data)
    _mem_cache_set(key, data)
    return data


def fetch_weather(lat: float, lon: float, city_id: str = None) -> dict:
    """Return the current weather response (cached)."""
    key = f"ow:w:{city_id or f'{lat},{lon}'}"
    cached = _mem_cache_get(key)
    if cached:
        return cached
    data = _get_json(
        f"{Config.OW_BASE_URL}/weather",
        {"lat": lat, "lon": lon, "appid": Config.OPENWEATHER_API_KEY,
         "units": Config.OW_UNITS},
    )
    _log("weather", city_id, data)
    _mem_cache_set(key, data)
    return data


def fetch_forecast(lat: float, lon: float, city_id: str = None) -> dict:
    """Return the 5-day / 3-hour forecast response (cached)."""
    key = f"ow:f:{city_id or f'{lat},{lon}'}"
    cached = _mem_cache_get(key)
    if cached:
        return cached
    data = _get_json(
        f"{Config.OW_BASE_URL}/forecast",
        {"lat": lat, "lon": lon, "appid": Config.OPENWEATHER_API_KEY,
         "units": Config.OW_UNITS},
    )
    _log("forecast", city_id, data)
    _mem_cache_set(key, data)
    return data


def geocode(city_name: str, country_code: str = None) -> dict:
    """Geocode a city name → {lat, lon, name, country}. Returns {} on failure."""
    params = {"q": city_name, "limit": 5, "appid": Config.OPENWEATHER_API_KEY}
    data = _get_json(f"{Config.OW_GEO_URL}/direct", params)
    if not isinstance(data, list) or not data:
        return {}
    if country_code:
        for hit in data:
            if str(hit.get("country", "")).upper() == country_code.upper():
                return hit
    return data[0]


def _log(endpoint: str, city_id, data: dict):
    """Audit-log one upstream call (records HTTP status)."""
    status = data.get("error") if isinstance(data, dict) else 200
    db.log_api_call(endpoint, status or 0, city_id)


# ---------------------------------------------------------------------------
# Bulk fetch helpers (concurrent)
# ---------------------------------------------------------------------------
def fetch_cities(city_configs: list, fetchers: list) -> dict:
    """
    Fetch several data types for many cities concurrently.
    fetchers: list of callables f(city) -> {field: value} | None
    Returns {city_id: {fetched_fields..., "error": msg?}}
    """
    results = {}

    def work(city):
        row = {"id": city["id"]}
        for fn in fetchers:
            try:
                val = fn(city)
                if val is not None:
                    row.update(val)
            except Exception as exc:  # never let one city break the batch
                row["error"] = str(exc)
        return city["id"], row

    with futures.ThreadPoolExecutor(max_workers=Config.FETCH_CONCURRENCY) as pool:
        for city_id, row in pool.map(work, city_configs):
            results[city_id] = row
    return results


def invalidate_mem_cache():
    _mem_cache.clear()
