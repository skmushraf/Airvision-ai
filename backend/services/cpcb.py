"""
AirVision AI — CPCB Real-Time AQI Provider (data.gov.in)
=========================================================
PRIMARY source of air-quality data for Indian cities.

Upstream
--------
Open Government Data (OGD) Platform India — resource
``3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69``
("Real time Air Quality Index from various locations", published by the
Central Pollution Control Board, Ministry of Environment, Forest & Climate
Change). The feed is station-level and updates roughly hourly.

Each upstream row is ONE pollutant at ONE monitoring station::

    {
      "country": "India", "state": "Andhra_Pradesh", "city": "Amaravati",
      "station": "Secretariat, Amaravati - APPCB",
      "last_update": "03-10-2026 11:00:00",
      "latitude": "16.515083", "longitude": "80.518167",
      "pollutant_id": "PM2.5", "pollutant_min": "12",
      "pollutant_max": "61", "pollutant_avg": "31"
    }

This module turns that into one record per city:
  * averages every station's `pollutant_avg` per pollutant,
  * computes the official **CPCB National AQI** (not the US EPA scale),
  * keeps the contributing station list for the map's station layer.

Design notes
------------
* The API key is read from the environment (``DATA_GOV_API_KEY``) and is
  never exposed to the frontend — all calls go through this backend.
* Results are cached in memory (TTL) and persisted to SQLite, so a slow or
  unreachable upstream never breaks the dashboard.
* Some networks (notably non-Indian datacentres) cannot reach
  ``api.data.gov.in``. In that case this provider reports itself as
  unavailable and ``services.live`` transparently falls back to OpenWeather,
  labelling the record's source accordingly.
"""

import re
import threading
import time
from collections import defaultdict

import requests

from config import Config
from services import aqi as aqi_svc

_lock = threading.Lock()
_cache = {"payload": None, "expires_at": 0.0, "error": None, "fetched_at": None}

_SESSION = requests.Session()

# Upstream pollutant_id → our canonical pollutant key
_POLLUTANT_MAP = {
    "PM2.5": "pm2_5",
    "PM25": "pm2_5",
    "PM10": "pm10",
    "NO2": "no2",
    "SO2": "so2",
    "CO": "co",
    "OZONE": "o3",
    "O3": "o3",
    "NH3": "nh3",
}

_MISSING = {"", "na", "n/a", "nan", "none", "-", "null"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _num(value):
    """Parse an upstream numeric string, tolerating 'NA' and blanks."""
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in _MISSING:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    return None if out != out else out  # drop NaN


def normalize_city(name: str) -> str:
    """
    Normalise a city name for matching between the CPCB feed and our catalog.
    'Amaravati ', 'AMARAVATI', 'Amaravati_City' → 'amaravati'
    """
    if not name:
        return ""
    text = str(name).strip().lower()
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_timestamp(text):
    """CPCB 'DD-MM-YYYY HH:MM:SS' → epoch seconds (None when unparseable)."""
    if not text:
        return None
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return time.mktime(time.strptime(str(text).strip(), fmt))
        except (ValueError, OverflowError):
            continue
    return None


def _co_to_mg_m3(value):
    """
    The CPCB sub-index for CO is defined in mg/m³, but the OGD feed reports CO
    in µg/m³ for most stations (and already in mg/m³ for a few).

    ``CPCB_CO_UNIT`` controls the behaviour:
      * ``auto`` (default) — values above 50 are treated as µg/m³ and divided
        by 1000. 50 mg/m³ is beyond the top of the CPCB CO scale (34 mg/m³ is
        already 'Severe'), so a reading that large is unambiguously µg/m³.
      * ``ug``  — always divide by 1000.
      * ``mg``  — never convert.
    """
    if value is None:
        return None
    mode = (Config.CPCB_CO_UNIT or "auto").lower()
    if mode == "mg":
        return value
    if mode == "ug":
        return value / 1000.0
    return value / 1000.0 if value > 50 else value


# ---------------------------------------------------------------------------
# Upstream fetch
# ---------------------------------------------------------------------------
def _fetch_page(offset: int, limit: int):
    """Fetch one page of the resource. Returns (records, error_message)."""
    params = {
        "api-key": Config.DATA_GOV_API_KEY,
        "format": "json",
        "offset": offset,
        "limit": limit,
    }
    try:
        resp = _SESSION.get(
            f"{Config.DATA_GOV_BASE_URL}/resource/{Config.CPCB_RESOURCE_ID}",
            params=params,
            timeout=Config.CPCB_TIMEOUT,
        )
    except requests.RequestException as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}: {resp.text[:160]}"
    try:
        body = resp.json()
    except ValueError:
        return None, "Upstream returned non-JSON payload"
    if not isinstance(body, dict):
        return None, "Unexpected payload shape"
    return body.get("records") or [], None


def fetch_raw_records(force: bool = False):
    """
    Fetch every record of the CPCB resource (paginated).
    Returns (records, error_message). Never raises.
    """
    if not Config.ENABLE_CPCB:
        return None, "CPCB provider disabled (ENABLE_CPCB=0)"
    if not Config.DATA_GOV_API_KEY:
        return None, "DATA_GOV_API_KEY is not configured"

    records, offset = [], 0
    page_size = Config.CPCB_PAGE_SIZE
    while offset < Config.CPCB_MAX_RECORDS:
        page, error = _fetch_page(offset, page_size)
        if error:
            # Partial data is still useful; only fail hard when we have nothing
            return (records, None) if records else (None, error)
        if not page:
            break
        records.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return records, None


# ---------------------------------------------------------------------------
# Aggregation: station rows → city records
# ---------------------------------------------------------------------------
def aggregate_by_city(raw_records: list) -> dict:
    """
    Collapse station/pollutant rows into one entry per normalised city name::

        {"delhi": {"city": "Delhi", "state": "Delhi",
                   "pollutants": {"pm2_5": 84.0, ...},   # µg/m³, CO in mg/m³
                   "aqi": 171, "aqi_category": "Moderate", "driver": "PM2.5",
                   "sub_aqis": {...}, "reliable": True,
                   "stations": [...], "station_count": 7,
                   "last_update": "03-10-2026 11:00:00", "updated_epoch": ...}}
    """
    by_city = defaultdict(lambda: {
        "city": None, "state": None, "country": "India",
        "values": defaultdict(list), "stations": {},
        "last_update": None, "updated_epoch": None,
    })

    for row in raw_records or []:
        city_raw = row.get("city")
        key = normalize_city(city_raw)
        if not key:
            continue
        pollutant_key = _POLLUTANT_MAP.get(
            str(row.get("pollutant_id", "")).strip().upper()
        )
        if not pollutant_key:
            continue
        avg = _num(row.get("pollutant_avg"))
        if avg is None:
            # Fall back to the midpoint of min/max when avg is 'NA'
            low, high = _num(row.get("pollutant_min")), _num(row.get("pollutant_max"))
            if low is not None and high is not None:
                avg = (low + high) / 2.0
        if avg is None:
            continue

        bucket = by_city[key]
        bucket["city"] = bucket["city"] or str(city_raw).strip()
        bucket["state"] = bucket["state"] or str(row.get("state") or "").replace("_", " ").strip()
        bucket["values"][pollutant_key].append(avg)

        station_name = str(row.get("station") or "").strip()
        if station_name:
            station = bucket["stations"].setdefault(station_name, {
                "station": station_name,
                "lat": _num(row.get("latitude")),
                "lon": _num(row.get("longitude")),
                "pollutants": {},
                "last_update": row.get("last_update"),
            })
            station["pollutants"][pollutant_key] = avg

        stamp = row.get("last_update")
        epoch = _parse_timestamp(stamp)
        if epoch and (bucket["updated_epoch"] is None or epoch > bucket["updated_epoch"]):
            bucket["updated_epoch"] = epoch
            bucket["last_update"] = stamp

    out = {}
    for key, bucket in by_city.items():
        pollutants = {}
        for pollutant_key, values in bucket["values"].items():
            if values:
                pollutants[pollutant_key] = round(sum(values) / len(values), 2)

        # CPCB's CO sub-index is defined in mg/m³
        naqi_input = dict(pollutants)
        if "co" in naqi_input:
            naqi_input["co"] = _co_to_mg_m3(naqi_input["co"])

        result = aqi_svc.compute_cpcb_aqi(naqi_input)
        out[key] = {
            "city": bucket["city"],
            "state": bucket["state"],
            "country": "India",
            "pollutants": pollutants,
            "co_mg_m3": naqi_input.get("co"),
            "aqi": result["aqi"],
            "aqi_category": aqi_svc.aqi_category(result["aqi"]),
            "aqi_color": aqi_svc.aqi_color(result["aqi"]),
            "sub_aqis": result["sub_aqis"],
            "driver": result["driver"],
            "reliable": result["reliable"],
            "standard": "CPCB NAQI",
            "stations": sorted(bucket["stations"].values(), key=lambda s: s["station"]),
            "station_count": len(bucket["stations"]),
            "last_update": bucket["last_update"],
            "updated_epoch": bucket["updated_epoch"],
        }
    return out


# ---------------------------------------------------------------------------
# Public API (cached)
# ---------------------------------------------------------------------------
def get_city_index(force: bool = False) -> dict:
    """
    Return the cached {normalised_city: record} index, refreshing when stale.
    Always returns a dict (possibly empty); inspect `last_error()` for status.
    """
    now = time.time()
    with _lock:
        fresh = _cache["payload"] is not None and _cache["expires_at"] > now
    if fresh and not force:
        return _cache["payload"]

    raw, error = fetch_raw_records(force=force)
    if error or raw is None:
        with _lock:
            _cache["error"] = error
            # Serve the stale payload rather than nothing
            return _cache["payload"] or {}

    index = aggregate_by_city(raw)
    with _lock:
        _cache["payload"] = index
        _cache["expires_at"] = now + Config.CPCB_TTL_SECONDS
        _cache["error"] = None
        _cache["fetched_at"] = now

    # Persist so a restart during an upstream outage still has data
    try:
        from database import db

        db.cache_set("cpcb:index", index, ttl_seconds=Config.CPCB_TTL_SECONDS * 6)
    except Exception:
        pass
    return index


def get_city(city_name: str, aliases=None):
    """Look up one city in the CPCB index by name (or any of its aliases)."""
    index = get_city_index()
    if not index:
        return None
    for candidate in [city_name] + list(aliases or []):
        hit = index.get(normalize_city(candidate))
        if hit and hit.get("aqi") is not None:
            return hit
    return None


def last_error():
    return _cache["error"]


def is_available() -> bool:
    return bool(get_city_index())


def provider_status() -> dict:
    """Diagnostics block surfaced by /api/status and /api/cpcb/status."""
    index = _cache["payload"] or {}
    return {
        "provider": "CPCB — Central Pollution Control Board (data.gov.in)",
        "resource_id": Config.CPCB_RESOURCE_ID,
        "enabled": Config.ENABLE_CPCB,
        "api_key_configured": bool(Config.DATA_GOV_API_KEY),
        "available": bool(index),
        "cities_indexed": len(index),
        "stations_indexed": sum(c.get("station_count", 0) for c in index.values()),
        "standard": "CPCB National AQI (NAQI)",
        "last_fetched": (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_cache["fetched_at"]))
            if _cache["fetched_at"] else None
        ),
        "ttl_seconds": Config.CPCB_TTL_SECONDS,
        "error": _cache["error"],
    }


def invalidate():
    with _lock:
        _cache["payload"] = None
        _cache["expires_at"] = 0.0
        _cache["error"] = None
