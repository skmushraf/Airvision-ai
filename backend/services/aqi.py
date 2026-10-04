"""
AirVision AI — AQI Computation & Classification
===============================================
Converts raw pollutant concentrations (µg/m³) from the OpenWeather Air
Pollution API into a continuous 0–500 AQI value using the US EPA breakpoints
(interpolated), then classifies it into the Indian CPCB AQI categories used
throughout the application.

Categories (CPCB):
    0–50      Good
    51–100    Satisfactory
    101–200   Moderate
    201–300   Poor
    301–400   Very Poor
    401–500   Severe
"""

def aqi_bucket(aqi) -> str:
    """Map a numeric AQI to the Indian CPCB category name."""
    if aqi is None or aqi != aqi:  # handles None and NaN
        return "Unknown"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Satisfactory"
    if aqi <= 200:
        return "Moderate"
    if aqi <= 300:
        return "Poor"
    if aqi <= 400:
        return "Very Poor"
    return "Severe"


# ---------------------------------------------------------------------------
# US EPA pollutant breakpoints → sub-AQI
# Each entry: (breakpoint_concentration, breakpoint_aqi) sorted ascending.
# Units: PM2.5 µg/m³ (24h), PM10 µg/m³ (24h), O3 ppm (8h), SO2 ppb (24h),
#        NO2 ppb (1h), CO ppm (8h)
# ---------------------------------------------------------------------------
_BP = {
    "pm2_5": [(0.0, 0), (12.0, 50), (35.4, 100), (55.4, 150), (150.4, 200),
              (250.4, 300), (350.4, 400), (500.4, 500)],
    "pm10":  [(0.0, 0), (54.0, 50), (154.0, 100), (254.0, 150), (354.0, 200),
              (424.0, 300), (504.0, 400), (604.0, 500)],
    "o3":    [(0.0, 0), (0.054, 50), (0.070, 100), (0.085, 150), (0.105, 200),
              (0.200, 300)],
    "so2":   [(0.0, 0), (35.0, 50), (75.0, 100), (185.0, 150), (304.0, 200),
              (604.0, 300), (804.0, 400), (1004.0, 500)],
    "no2":   [(0.0, 0), (53.0, 50), (100.0, 100), (360.0, 150), (649.0, 200),
              (1249.0, 300), (1649.0, 400), (2049.0, 500)],
    "co":    [(0.0, 0), (4.4, 50), (9.4, 100), (12.4, 150), (15.4, 200),
              (30.4, 300), (40.4, 400), (50.4, 500)],
}

# Unit conversions (25 °C, 1 atm) from µg/m³ to the breakpoint unit
_TO_PPB = {"no2": 1.88, "so2": 2.62}                 # 1 ppb = X µg/m³
_TO_PPM = {"o3": 1960.0}                             # 1 ppm O3 = 1960 µg/m³
_CO_PPM = 1150.0                                     # 1 ppm CO = 1150 µg/m³


def _sub_aqi(breakpoints: list, conc: float) -> float:
    """Piecewise-linear interpolation of concentration → sub-AQI."""
    if conc <= breakpoints[0][0]:
        return breakpoints[0][1]
    for i in range(1, len(breakpoints)):
        c_lo, aqi_lo = breakpoints[i - 1]
        c_hi, aqi_hi = breakpoints[i]
        if conc <= c_hi:
            frac = (conc - c_lo) / (c_hi - c_lo)
            return aqi_lo + frac * (aqi_hi - aqi_lo)
    return breakpoints[-1][1]


def compute_aqi_from_components(components: dict) -> dict:
    """
    Compute the overall AQI (0–500) from OpenWeather `components` dict.
    Returns {aqi, sub_aqis, driver} where driver is the pollutant that
    dominates the AQI.
    """
    sub_aqis = {}

    pm25 = components.get("pm2_5")
    pm10 = components.get("pm10")
    o3 = components.get("o3")
    so2 = components.get("so2")
    no2 = components.get("no2")
    co = components.get("co")

    if pm25 is not None:
        sub_aqis["PM2.5"] = _sub_aqi(_BP["pm2_5"], float(pm25))
    if pm10 is not None:
        sub_aqis["PM10"] = _sub_aqi(_BP["pm10"], float(pm10))
    if o3 is not None:
        sub_aqis["O3"] = _sub_aqi(_BP["o3"], float(o3) / _TO_PPM["o3"])
    if so2 is not None:
        sub_aqis["SO2"] = _sub_aqi(_BP["so2"], float(so2) / _TO_PPB["so2"])
    if no2 is not None:
        sub_aqis["NO2"] = _sub_aqi(_BP["no2"], float(no2) / _TO_PPB["no2"])
    if co is not None:
        sub_aqis["CO"] = _sub_aqi(_BP["co"], float(co) / _CO_PPM)

    if not sub_aqis:
        return {"aqi": None, "sub_aqis": {}, "driver": None}

    driver = max(sub_aqis, key=sub_aqis.get)
    return {
        "aqi": round(max(sub_aqis.values())),
        "sub_aqis": {k: round(v) for k, v in sub_aqis.items()},
        "driver": driver,
    }


# ---------------------------------------------------------------------------
# CPCB National AQI (NAQI) — official Indian breakpoints
# ---------------------------------------------------------------------------
# Used for Indian cities whose readings come from the CPCB real-time feed on
# data.gov.in. Unlike the US EPA scale, the Indian NAQI works directly in
# µg/m³ (CO in mg/m³) and adds NH3 as a criteria pollutant.
#
# Sub-index bands: 0–50 / 51–100 / 101–200 / 201–300 / 301–400 / 401–500
# Reference: CPCB "National Air Quality Index" report (CPCB, 2014).
_CPCB_BP = {
    # pollutant: [(concentration, sub-index), ...] ascending
    "pm2_5": [(0, 0), (30, 50), (60, 100), (90, 200), (120, 300), (250, 400), (380, 500)],
    "pm10":  [(0, 0), (50, 50), (100, 100), (250, 200), (350, 300), (430, 400), (510, 500)],
    "no2":   [(0, 0), (40, 50), (80, 100), (180, 200), (280, 300), (400, 400), (520, 500)],
    "o3":    [(0, 0), (50, 50), (100, 100), (168, 200), (208, 300), (748, 400), (1288, 500)],
    "co":    [(0, 0), (1, 50), (2, 100), (10, 200), (17, 300), (34, 400), (51, 500)],   # mg/m³
    "so2":   [(0, 0), (40, 50), (80, 100), (380, 200), (800, 300), (1600, 400), (2400, 500)],
    "nh3":   [(0, 0), (200, 50), (400, 100), (800, 200), (1200, 300), (1800, 400), (2400, 500)],
}

# Display labels for each pollutant key
_LABEL = {"pm2_5": "PM2.5", "pm10": "PM10", "no2": "NO2", "o3": "O3",
          "co": "CO", "so2": "SO2", "nh3": "NH3"}


def compute_cpcb_aqi(pollutants: dict) -> dict:
    """
    Compute the Indian National AQI (CPCB) from pollutant concentrations.

    Expects a dict keyed pm2_5 / pm10 / no2 / o3 / co / so2 / nh3 where every
    value is in µg/m³ **except CO, which must already be in mg/m³** (that is
    the unit the CPCB sub-index table is defined in).

    CPCB validity rule: the AQI is only published when at least three
    pollutants are available AND one of them is PM2.5 or PM10. When that rule
    is not satisfied we still return the computed value but flag it via
    `reliable: False` so the UI can mark it as provisional.

    Returns {aqi, sub_aqis, driver, reliable, standard}.
    """
    sub_aqis = {}
    for key, breakpoints in _CPCB_BP.items():
        value = pollutants.get(key)
        if value is None:
            continue
        try:
            conc = float(value)
        except (TypeError, ValueError):
            continue
        if conc < 0:
            continue
        sub_aqis[_LABEL[key]] = _sub_aqi(breakpoints, conc)

    if not sub_aqis:
        return {"aqi": None, "sub_aqis": {}, "driver": None,
                "reliable": False, "standard": "CPCB NAQI"}

    has_pm = "PM2.5" in sub_aqis or "PM10" in sub_aqis
    driver = max(sub_aqis, key=sub_aqis.get)
    return {
        "aqi": int(round(min(500.0, max(sub_aqis.values())))),
        "sub_aqis": {k: int(round(v)) for k, v in sub_aqis.items()},
        "driver": driver,
        "reliable": bool(has_pm and len(sub_aqis) >= 3),
        "standard": "CPCB NAQI",
    }


# ---------------------------------------------------------------------------
# Category metadata (colors used by map markers & charts)
# ---------------------------------------------------------------------------
AQI_CATEGORIES = [
    {"category": "Good",         "min": 0,   "max": 50,   "color": "#22c55e"},
    {"category": "Satisfactory", "min": 51,  "max": 100,  "color": "#a3e635"},
    {"category": "Moderate",     "min": 101, "max": 200,  "color": "#f97316"},
    {"category": "Poor",         "min": 201, "max": 300,  "color": "#ef4444"},
    {"category": "Very Poor",    "min": 301, "max": 400,  "color": "#b91c1c"},
    {"category": "Severe",       "min": 401, "max": 500,  "color": "#a855f7"},
]


def aqi_category(aqi: float) -> str:
    """Classify an AQI value into a CPCB category name."""
    return aqi_bucket(aqi)


def aqi_color(aqi: float) -> str:
    """Return the marker/chart color for an AQI value."""
    cat = aqi_category(aqi)
    for c in AQI_CATEGORIES:
        if c["category"] == cat:
            return c["color"]
    return "#64748b"


def aqi_category_info(aqi: float) -> dict:
    """Return {category, color, min, max, ordinal} for an AQI value."""
    cat = aqi_category(aqi)
    ordinal = {"Good": 1, "Satisfactory": 2, "Moderate": 3,
               "Poor": 4, "Very Poor": 5, "Severe": 6}.get(cat, 0)
    for c in AQI_CATEGORIES:
        if c["category"] == cat:
            return {**c, "ordinal": ordinal}
    return {"category": cat, "color": "#64748b", "min": 0, "max": 500, "ordinal": ordinal}
