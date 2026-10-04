"""
AirVision AI — Pollution Hotspots Service
=========================================
Computes rankings and aggregates from the live city records:
  - Top 10 most polluted cities
  - Top 10 cleanest cities
  - Highest / lowest AQI country
  - Average global AQI
  - Average AQI by continent
"""

import statistics


def _minimal(record: dict) -> dict:
    """A compact view of a city record for ranking payloads."""
    weather = record.get("weather") or {}
    return {
        "id": record.get("id"),
        "name": record.get("name"),
        "country": record.get("country"),
        "country_code": record.get("country_code"),
        "continent": record.get("continent"),
        "lat": record.get("lat"),
        "lon": record.get("lon"),
        "aqi": record.get("aqi"),
        "category": record.get("aqi_category"),
        "color": record.get("aqi_color"),
        "temperature": weather.get("temp"),
        "humidity": weather.get("humidity"),
        "wind_speed": weather.get("wind_speed"),
        "pm2_5": (record.get("pollutants") or {}).get("pm2_5"),
        "predicted_aqi": record.get("predicted_aqi"),
        "last_updated": record.get("last_updated"),
    }


def compute_hotspots(records: list) -> dict:
    """Compute all hotspot statistics from a list of city records."""
    valid = [r for r in records if r.get("aqi") is not None]
    if not valid:
        return {
            "top_polluted": [],
            "cleanest": [],
            "highest_country": None,
            "lowest_country": None,
            "average_global_aqi": None,
            "by_continent": {},
            "coverage": {"cities": len(records), "with_data": 0},
        }

    ranked = sorted(valid, key=lambda r: r["aqi"], reverse=True)
    top_polluted = [_minimal(r) for r in ranked[:10]]
    cleanest = [_minimal(r) for r in ranked[-10:][::-1]]

    # Country aggregation
    by_country = {}
    for r in valid:
        bucket = by_country.setdefault(
            r["country"], {"country": r["country"], "aqis": [], "cities": 0}
        )
        bucket["aqis"].append(r["aqi"])
        bucket["cities"] += 1

    country_stats = []
    for bucket in by_country.values():
        country_stats.append({
            "country": bucket["country"],
            "average_aqi": round(statistics.mean(bucket["aqis"]), 1),
            "max_aqi": max(bucket["aqis"]),
            "cities": bucket["cities"],
        })
    country_stats.sort(key=lambda c: c["average_aqi"], reverse=True)

    # Continent aggregation
    by_continent = {}
    for r in valid:
        bucket = by_continent.setdefault(
            r["continent"], {"continent": r["continent"], "aqis": [], "cities": 0}
        )
        bucket["aqis"].append(r["aqi"])
        bucket["cities"] += 1
    continent_stats = [
        {
            "continent": b["continent"],
            "average_aqi": round(statistics.mean(b["aqis"]), 1),
            "cities": b["cities"],
        }
        for b in by_continent.values()
    ]
    continent_stats.sort(key=lambda c: c["average_aqi"], reverse=True)

    all_aqis = [r["aqi"] for r in valid]
    return {
        "top_polluted": top_polluted,
        "cleanest": cleanest,
        "highest_country": country_stats[0] if country_stats else None,
        "lowest_country": country_stats[-1] if country_stats else None,
        "country_ranking": country_stats,
        "average_global_aqi": round(statistics.mean(all_aqis), 1),
        "by_continent": continent_stats,
        "coverage": {"cities": len(records), "with_data": len(valid)},
        "computed_at": __import__("time").time(),
    }
