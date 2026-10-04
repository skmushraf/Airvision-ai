"""
AirVision AI — Demo Data Mode (OPT-IN)
======================================
Generates plausible, ML-grounded readings for every city so the full feature
set can be demonstrated while a live OpenWeather API key is pending, expired
or not yet activated.

**Important:**
  - OFF by default (`ENABLE_DEMO_DATA=0` in backend/.env).
  - When OFF, no demo code runs anywhere in the live path — every value is
    fetched from OpenWeather, exactly as the production spec requires.
  - When ON, every record is clearly tagged `source="demo"`, `demo=True`,
    and the UI shows a "DEMO MODE" banner so it can never be mistaken for
    real data.

How the demo stays honest:
  - Pollutants are sampled deterministically per city (seeded by city id)
    with realistic ranges per continent, then nudged slightly on each refresh
    to simulate movement.
  - AQI is computed from those pollutants using the REAL EPA breakpoint engine.
  - The REAL trained ML model (XGBoost) predicts AQI from the same components.
  - Health recommendations come from the REAL recommendation engine.
"""

import datetime as dt
import hashlib
import math
import random
import time

from config import Config
from services import timeutil
from services import aqi as aqi_svc
from services import health as health_svc
from services import predictor

# ---------------------------------------------------------------------------
# Base pollution profile (a moderately polluted Indian city, µg/m³)
# ---------------------------------------------------------------------------
_BASE = {"pm2_5": 95.0, "pm10": 185.0, "no2": 42.0, "so2": 15.0,
         "co": 1.6, "o3": 50.0, "nh3": 14.0}

# Continent multipliers → realistic regional variation
_CONTINENT_FACTORS = {
    "Asia":          {"pm2_5": 1.05, "pm10": 1.05, "no2": 1.00, "so2": 1.00, "co": 1.00, "o3": 0.95, "nh3": 1.00},
    "Middle East":   {"pm2_5": 0.95, "pm10": 1.75, "no2": 0.85, "so2": 0.90, "co": 0.85, "o3": 1.10, "nh3": 0.60},
    "Africa":        {"pm2_5": 0.85, "pm10": 1.10, "no2": 0.70, "so2": 0.65, "co": 0.75, "o3": 1.05, "nh3": 0.70},
    "South America": {"pm2_5": 0.50, "pm10": 0.55, "no2": 0.60, "so2": 0.45, "co": 0.60, "o3": 1.00, "nh3": 0.55},
    "North America": {"pm2_5": 0.32, "pm10": 0.35, "no2": 0.45, "so2": 0.35, "co": 0.45, "o3": 0.90, "nh3": 0.40},
    "Europe":        {"pm2_5": 0.40, "pm10": 0.42, "no2": 0.55, "so2": 0.40, "co": 0.50, "o3": 0.85, "nh3": 0.45},
    "Oceania":       {"pm2_5": 0.18, "pm10": 0.22, "no2": 0.30, "so2": 0.20, "co": 0.30, "o3": 0.95, "nh3": 0.30},
}


def _seeded_rng(city_id: str, salt: str = "") -> random.Random:
    """Deterministic RNG per city (+ salt for time-varying jitter)."""
    seed = int(hashlib.md5(f"{city_id}:{salt}".encode()).hexdigest()[:8], 16)
    return random.Random(seed)


def _jitter_salt() -> str:
    """Change every ~5 minutes so readings move like real data."""
    return str(int(time.time() // 300))


def _base_temp(lat: float) -> float:
    """Seasonal baseline temperature (°C) from latitude."""
    month = dt.datetime.now().month
    hemi = 1 if lat >= 0 else -1
    # seasonal swing: ±9°C, hottest Aug (8) northern / Feb (2) southern
    seasonal = math.cos(2 * math.pi * ((month - 8 * hemi) % 12) / 12)
    abs_lat = abs(lat)
    if abs_lat > 55:
        base = 4
    elif abs_lat > 35:
        base = 14
    elif abs_lat > 15:
        base = 25
    else:
        base = 29
    return base + 8 * seasonal


def _propensity(city: dict) -> float:
    """Stable per-city pollution propensity (0.55–1.75) from the city id."""
    rng = _seeded_rng(city["id"], "propensity")
    return rng.uniform(0.55, 1.75)


def demo_pollutants(city: dict) -> dict:
    """Deterministic, realistic pollutant concentrations for a city."""
    rng = _seeded_rng(city["id"], _jitter_salt())
    factors = _CONTINENT_FACTORS.get(city["continent"], _CONTINENT_FACTORS["Asia"])
    prop = _propensity(city)
    out = {}
    for key, base in _BASE.items():
        factor = factors.get(key, 1.0)
        jitter = rng.uniform(0.82, 1.18)          # ±18% per refresh
        out[key] = round(max(1.0, base * factor * prop * jitter), 1)
    # Rainy monsoon months wash out particulates for South Asian cities
    if city["continent"] == "Asia" and 6 <= dt.datetime.now().month <= 9:
        out["pm2_5"] = round(out["pm2_5"] * 0.75, 1)
        out["pm10"] = round(out["pm10"] * 0.72, 1)
    return out


def demo_weather(city: dict, at: dt.datetime = None) -> dict:
    """Realistic weather for a city (optionally at a future timestamp)."""
    at = at or dt.datetime.now()
    rng = _seeded_rng(city["id"], f"w:{int(at.timestamp() // 3600)}")
    base = _base_temp(city["lat"])
    # diurnal curve: coldest ~05:00, hottest ~15:00
    hour = at.hour + at.minute / 60
    diurnal = 4.5 * math.cos(2 * math.pi * (hour - 15) / 24)
    temp = round(base + diurnal, 1)
    humidity = round(max(25, min(92, 72 - (temp - 25) * 1.8 + rng.uniform(-8, 8))))
    wind = round(rng.uniform(2.0, 9.0), 1)
    pressure = round(rng.uniform(1000, 1016))
    clouds = round(rng.uniform(10, 85))
    visibility = round(rng.uniform(4, 11), 1)
    # local sunrise/sunset approximated from latitude + day-of-year
    doy = at.timetuple().tm_yday
    day_frac = math.sin(2 * math.pi * (doy - 81) / 365)
    sunrise = round((6.0 - 1.2 * day_frac) * 3600)
    sunset = round((18.5 + 1.2 * day_frac) * 3600)
    desc = "clear sky" if clouds < 25 else "scattered clouds" if clouds < 60 else "overcast"
    return {
        "temp": temp,
        "feels_like": round(temp + humidity / 100 * 2, 1),
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind,
        "wind_deg": round(rng.uniform(0, 360)),
        "visibility": int(visibility * 1000),
        "clouds": clouds,
        "rain_1h": round(rng.uniform(0, 0.4), 1),
        "sunrise": sunrise,
        "sunset": sunset,
        "description": desc,
        "icon": "01d" if clouds < 25 else "03d" if clouds < 60 else "04d",
        "dt": int(at.timestamp()),
    }


def city_record(city: dict) -> dict:
    """Full city record (same shape as services.live.build_city_record)."""
    pollutants = demo_pollutants(city)
    weather = demo_weather(city)
    aqi_value = aqi_svc.compute_aqi_from_components(pollutants)["aqi"]
    predicted = predictor.predict_aqi(pollutants)
    now = time.time()
    return {
        "id": city["id"],
        "name": city["name"],
        "country": city["country"],
        "country_code": city["cc"],
        "continent": city["continent"],
        "lat": city["lat"],
        "lon": city["lon"],
        "source": "demo",
        "demo": True,
        "api_error": None,
        "aqi": aqi_value,
        "aqi_category": aqi_svc.aqi_category(aqi_value),
        "aqi_color": aqi_svc.aqi_color(aqi_value),
        "pollutants": pollutants,
        "weather": weather,
        "predicted_aqi": predicted,
        "predicted_category": aqi_svc.aqi_category(predicted) if predicted is not None else None,
        "health": health_svc.health_response(aqi_value, city["name"]),
        "last_updated": now,
    }


def forecast(city: dict) -> dict:
    """Full forecast payload (same shape as services.forecast.build_forecast)."""
    from services import forecast as fc_mod

    now = dt.datetime.now()
    current = city_record(city)
    pollutants = current["pollutants"]
    weather = current["weather"]

    # --- hourly series: 5 days, 3-hour steps --------------------------------
    hourly = []
    for step in range(40):
        ts = now + dt.timedelta(hours=3 * step)
        w = demo_weather(city, ts)
        mult = fc_mod._dispersion_multipliers(weather, w)
        est = fc_mod._adjust_pollutants(pollutants, mult)
        temporal = fc_mod._temporal_features(ts)
        aqi_pred = predictor.predict_aqi_with_temporal(est, temporal)
        hourly.append({
            **w,
            "time": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "dt": int(ts.timestamp()),
            "rain_prob": round(min(90, max(0, (w["clouds"] * 0.7) + step % 7 * 3))),
            "aqi": aqi_pred,
            "category": aqi_svc.aqi_category(aqi_pred) if aqi_pred is not None else None,
        })

    # --- daily aggregation ----------------------------------------------------
    daily = []
    grouped = {}
    for h in hourly:
        grouped.setdefault(h["time"][:10], []).append(h)
    for day, items in list(grouped.items())[:5]:
        temps = [i["temp"] for i in items]
        aqis = [i["aqi"] for i in items if i["aqi"] is not None]
        daily.append({
            "date": day,
            "temp_min": round(min(temps)), "temp_max": round(max(temps)),
            "humidity": round(sum(i["humidity"] for i in items) / len(items)),
            "wind_speed": round(max(i["wind_speed"] for i in items), 1),
            "rain_prob": max(i["rain_prob"] for i in items),
            "description": items[len(items) // 2]["description"],
            "icon": items[len(items) // 2]["icon"],
            "aqi": round(sum(aqis) / len(aqis)) if aqis else None,
            "category": aqi_svc.aqi_category(sum(aqis) / len(aqis)) if aqis else None,
        })

    # --- key AQI forecast points (Now / 1h / 6h / 12h / 24h) -----------------
    live_predicted = predictor.predict_aqi(pollutants)
    aqi_forecast = [{
        "label": "Now", "offset_hours": 0,
        "time": now.strftime("%Y-%m-%d %H:%M"),
        "aqi": live_predicted,
        "category": aqi_svc.aqi_category(live_predicted) if live_predicted is not None else None,
    }]
    for offset in (1, 6, 12, 24):
        target = now + dt.timedelta(hours=offset)
        best, best_diff = None, None
        for h in hourly:
            diff = abs((dt.datetime.fromisoformat(h["time"]) - target).total_seconds())
            if best_diff is None or diff < best_diff:
                best, best_diff = h, diff
        if best and best["aqi"] is not None:
            aqi_forecast.append({
                "label": f"{offset}h", "offset_hours": offset,
                "time": target.strftime("%Y-%m-%d %H:%M"),
                "aqi": best["aqi"], "category": best["category"],
            })

    meta = predictor.model_metadata() or {}
    return {
        "city": {"id": city["id"], "name": city["name"], "country": city["country"],
                 "lat": city["lat"], "lon": city["lon"]},
        "last_updated": timeutil.to_utc_iso(now),
        "source": "demo",
        "demo": True,
        "current": {
            "aqi": current["aqi"],
            "aqi_category": current["aqi_category"],
            "predicted_aqi": live_predicted,
            "pollutants": pollutants,
            "weather": weather,
        },
        "aqi_forecast": aqi_forecast,
        "hourly": hourly,
        "daily": daily,
        "health": health_svc.health_response(live_predicted or current["aqi"], city["name"])
        if (live_predicted or current["aqi"]) else None,
        "model": {
            "selected_model": meta.get("selected_model"),
            "metrics": (meta.get("selected_model_metrics") or {}),
            "trained_at": meta.get("trained_at"),
        },
    }
