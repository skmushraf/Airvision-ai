"""
AirVision AI — AQI & Weather Forecasting Service
================================================
Produces the /api/forecast payload:

  * Current AQI + pollutants + weather (live from OpenWeather)
  * AQI forecast at Now / 1h / 6h / 12h / 24h
  * Hourly weather forecast (5 days, 3-hour steps)
  * Daily aggregated forecast (5 days)

AQI forecasting approach (documented in the README):
  1. The trained ML model maps pollutant concentrations → AQI.
  2. For each future forecast step we estimate the pollutant concentrations
     by applying a *meteorological dispersion adjustment* to today's live
     readings, using the forecast weather (wind, rain probability, humidity,
     temperature). Higher wind → stronger dispersion → lower concentration;
     rain → wet scavenging; temperature drives ozone photochemistry.
  3. The adjusted pollutants + the *future* temporal features (month, day,
     season...) are fed to the ML model to obtain the forecast AQI.
"""

import datetime as dt

from config import Config
from services import timeutil
from services import aqi as aqi_svc
from services import health as health_svc
from services import predictor
from services.openweather import fetch_air_quality, fetch_forecast, fetch_weather
from services.live import _parse_air, _parse_weather


# ---------------------------------------------------------------------------
# Temporal feature helper (reuses ml/features.py via the wrapper sys.path fix)
# ---------------------------------------------------------------------------
def _temporal_features(ts):
    from features import temporal_features_from_dt  # noqa

    return temporal_features_from_dt(ts)


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def _dispersion_multipliers(current_weather, fc_weather) -> dict:
    """
    Estimate a per-pollutant concentration multiplier from the forecast
    weather relative to the current weather.
    """
    cw, fw = current_weather or {}, fc_weather or {}

    cur_wind = cw.get("wind_speed") or 3.0
    fc_wind = fw.get("wind_speed") or cur_wind
    wind_mult = _clamp(cur_wind / max(fc_wind, 0.5), 0.6, 1.6)

    rain_prob = (fw.get("rain_prob") or 0) / 100.0
    rain_mult = 0.7 if rain_prob > 0.4 else 1.0

    cur_hum = cw.get("humidity") or 50.0
    fc_hum = fw.get("humidity") or cur_hum
    hum_mult = _clamp(1.0 + (fc_hum - cur_hum) / 100.0 * 0.15, 0.92, 1.12)

    cur_temp = cw.get("temp") or 25.0
    fc_temp = fw.get("temp") or cur_temp
    o3_mult = _clamp(1.0 + (fc_temp - cur_temp) * 0.01, 0.85, 1.30)

    base = wind_mult * rain_mult * hum_mult
    return {
        "PM2.5": base,
        "PM10": base,
        "NO2": base * 0.9,        # NO2 reacts away a little faster when sunny
        "CO": base,
        "SO2": base,
        "O3": base * o3_mult,     # ozone rises with temperature & sunlight
        "NH3": base,
    }


def _adjust_pollutants(current, multipliers) -> dict:
    """Apply multipliers to the current pollutant concentrations."""
    out = {}
    for key, val in (current or {}).items():
        if val is None:
            continue
        mult = multipliers.get(key.upper().replace(".", "_"), 1.0)
        out[key] = max(0.0, round(float(val) * mult, 2))
    return out


def _weather_at_point(point) -> dict:
    """Extract a flat weather dict from a forecast API list item."""
    rain = point.get("rain", {})
    return {
        "time": point.get("dt_txt"),
        "dt": point.get("dt"),
        "temp": point["main"].get("temp"),
        "feels_like": point["main"].get("feels_like"),
        "humidity": point["main"].get("humidity"),
        "pressure": point["main"].get("pressure"),
        "wind_speed": point["wind"].get("speed") if point.get("wind") else None,
        "clouds": point.get("clouds", {}).get("all"),
        "rain_prob": round(float(point.get("pop", 0)) * 100),
        "rain_3h": rain.get("3h"),
        "description": point.get("weather", [{}])[0].get("description"),
        "icon": point.get("weather", [{}])[0].get("icon"),
    }


def build_forecast(city: dict) -> dict:
    """Build the full forecast payload for one city (live, with demo fallback)."""
    now = dt.datetime.now()

    ow_aq = fetch_air_quality(city["lat"], city["lon"], city["id"])
    ow_w = fetch_weather(city["lat"], city["lon"], city["id"])
    ow_fc = fetch_forecast(city["lat"], city["lon"], city["id"])

    air = _parse_air(ow_aq) if "error" not in ow_aq else None
    weather = _parse_weather(ow_w) if "error" not in ow_w else None
    points = ow_fc.get("list", []) if isinstance(ow_fc, dict) else []

    # --- Demo mode fallback (OPT-IN, clearly labelled) -----------------------
    if Config.ENABLE_DEMO_DATA and (air is None or weather is None or not points):
        from services import demo as demo_svc

        return demo_svc.forecast(city)

    pollutants = air["components"] if air else {}
    current_aqi = air["aqi"] if air else None
    live_predicted = predictor.predict_aqi(pollutants) if pollutants else None

    base = {
        "id": city["id"],
        "name": city["name"],
        "country": city["country"],
        "lat": city["lat"],
        "lon": city["lon"],
    }

    # ---- hourly series ------------------------------------------------------
    hourly = []
    for point in points:
        fc_weather = _weather_at_point(point)
        mult = _dispersion_multipliers(weather, fc_weather)
        est_pollutants = _adjust_pollutants(pollutants, mult)
        ts = dt.datetime.fromisoformat(point["dt_txt"].replace("Z", "+00:00")).replace(tzinfo=None)
        temporal = _temporal_features(ts)
        aqi_pred = predictor.predict_aqi_with_temporal(est_pollutants, temporal)
        hourly.append({
            **fc_weather,
            "aqi": aqi_pred,
            "category": aqi_svc.aqi_category(aqi_pred) if aqi_pred is not None else None,
        })

    # ---- daily aggregation --------------------------------------------------
    daily = []
    grouped = {}
    for h in hourly:
        day = h["time"][:10]
        grouped.setdefault(day, []).append(h)
    for day, items in list(grouped.items())[:5]:
        temps = [i["temp"] for i in items if i["temp"] is not None]
        aqis = [i["aqi"] for i in items if i["aqi"] is not None]
        daily.append({
            "date": day,
            "temp_min": round(min(temps)) if temps else None,
            "temp_max": round(max(temps)) if temps else None,
            "humidity": round(sum(i["humidity"] for i in items if i["humidity"] is not None) / max(1, sum(1 for i in items if i["humidity"] is not None))),
            "wind_speed": round(max((i["wind_speed"] or 0) for i in items), 1),
            "rain_prob": max((i["rain_prob"] or 0) for i in items),
            "description": items[len(items) // 2].get("description"),
            "icon": items[len(items) // 2].get("icon"),
            "aqi": round(sum(aqis) / len(aqis)) if aqis else None,
            "category": aqi_svc.aqi_category(sum(aqis) / len(aqis)) if aqis else None,
        })

    # ---- key AQI forecast points (Now, 1h, 6h, 12h, 24h) --------------------
    aqi_forecast = [{
        "label": "Now",
        "offset_hours": 0,
        "time": now.strftime("%Y-%m-%d %H:%M"),
        "aqi": live_predicted,
        "category": aqi_svc.aqi_category(live_predicted) if live_predicted is not None else None,
    }]
    for offset in (1, 6, 12, 24):
        target = now + dt.timedelta(hours=offset)
        best, best_diff = None, None
        for h in hourly:
            h_time = dt.datetime.fromisoformat(h["time"].replace("Z", "+00:00")).replace(tzinfo=None)
            diff = abs((h_time - target).total_seconds())
            if best_diff is None or diff < best_diff:
                best, best_diff = h, diff
        if best and best["aqi"] is not None:
            aqi_forecast.append({
                "label": f"{offset}h",
                "offset_hours": offset,
                "time": target.strftime("%Y-%m-%d %H:%M"),
                "aqi": best["aqi"],
                "category": best["category"],
            })

    meta = predictor.model_metadata() or {}
    return {
        "city": base,
        "last_updated": timeutil.to_utc_iso(now),
        "source": "live" if (air and weather) else "unavailable",
        "current": {
            "aqi": current_aqi,
            "aqi_category": aqi_svc.aqi_category(current_aqi) if current_aqi is not None else None,
            "predicted_aqi": live_predicted,
            "pollutants": pollutants,
            "weather": weather,
        },
        "aqi_forecast": aqi_forecast,
        "hourly": hourly,
        "daily": daily,
        "health": health_svc.health_response(live_predicted or current_aqi, city["name"])
        if (live_predicted or current_aqi) else None,
        "model": {
            "selected_model": meta.get("selected_model"),
            "metrics": (meta.get("selected_model_metrics") or {}),
            "trained_at": meta.get("trained_at"),
        },
    }
