"""
AirVision AI — Health Recommendation Engine
===========================================
Generates dynamic, AQI-driven health recommendations (indoor/outdoor
advisory, masks, sensitive groups, air purifiers) for each CPCB category.
"""

HEALTH_PROFILES = {
    "Good": {
        "status": "Good",
        "level": "Low",
        "color": "#22c55e",
        "summary": "Air quality is satisfactory and poses little or no risk.",
        "recommendation": "Safe for outdoor activities. Enjoy your day!",
        "outdoor": "Outdoor activities are fully safe.",
        "sensitive": "No precautions needed for sensitive groups.",
        "mask": "No mask required.",
        "windows": "Keep windows open for ventilation.",
        "exercises": "Running, cycling and all outdoor sports are fine.",
    },
    "Satisfactory": {
        "status": "Satisfactory",
        "level": "Low-Moderate",
        "color": "#a3e635",
        "summary": "Air quality is acceptable; minor risk for unusually sensitive people.",
        "recommendation": "Sensitive groups should reduce prolonged outdoor exposure.",
        "outdoor": "Mostly safe outdoors; sensitive groups should limit prolonged exertion.",
        "sensitive": "Children, elderly and people with asthma should reduce long outdoor sessions.",
        "mask": "Optional for sensitive groups.",
        "windows": "Ventilation is fine.",
        "exercises": "Normal exercise is fine for most; sensitive groups should take breaks.",
    },
    "Moderate": {
        "status": "Moderate",
        "level": "Moderate",
        "color": "#f97316",
        "summary": "Some pollutants may affect people unusually sensitive to air pollution.",
        "recommendation": "Sensitive groups should reduce prolonged outdoor exposure.",
        "outdoor": "Reduce prolonged outdoor activities, especially near busy roads.",
        "sensitive": "Children, elderly and those with respiratory/cardiac conditions should limit exertion.",
        "mask": "Consider a mask if you are in a sensitive group.",
        "windows": "Keep windows closed during peak traffic hours.",
        "exercises": "Prefer indoor workouts; take frequent breaks outdoors.",
    },
    "Poor": {
        "status": "Poor",
        "level": "High",
        "color": "#ef4444",
        "summary": "Increased likelihood of respiratory symptoms in the general population.",
        "recommendation": "Reduce outdoor activities. Sensitive groups should avoid them.",
        "outdoor": "Reduce outdoor activities; avoid exercising outdoors.",
        "sensitive": "Avoid prolonged outdoor exertion; keep medication handy.",
        "mask": "Wear an N95/P95 mask when going outside.",
        "windows": "Keep windows closed; use air purifiers indoors.",
        "exercises": "Avoid outdoor exercise entirely; choose indoor fitness.",
    },
    "Very Poor": {
        "status": "Very Poor",
        "level": "Very High",
        "color": "#b91c1c",
        "summary": "Health alert — everyone may experience more serious health effects.",
        "recommendation": "Avoid strenuous outdoor activities. Stay indoors as much as possible.",
        "outdoor": "Avoid all outdoor exertion; limit time outdoors.",
        "sensitive": "Sensitive groups should stay indoors; seek medical advice if symptoms appear.",
        "mask": "Wear an N95 mask outdoors; ensure it seals properly.",
        "windows": "Keep windows and doors closed; run air purifiers continuously.",
        "exercises": "No outdoor exercise; indoor activity only with filtration.",
    },
    "Severe": {
        "status": "Severe",
        "level": "Emergency",
        "color": "#a855f7",
        "summary": "Health warnings of emergency conditions — serious health effects likely.",
        "recommendation": "Stay indoors and wear an N95 mask when going outside.",
        "outdoor": "Stay indoors. Only essential trips outside.",
        "sensitive": "Everyone should stay indoors; sensitive groups must not go out.",
        "mask": "N95/P95 mask mandatory when outside; double-layer if possible.",
        "windows": "Seal windows and doors; use HEPA air purifiers.",
        "exercises": "No outdoor activity at all. Keep indoor air filtered.",
    },
}

DEFAULT_PROFILE = HEALTH_PROFILES["Moderate"]


def get_health_profile(aqi) -> dict:
    """Return the full health profile for a numeric AQI."""
    from services.aqi import aqi_category  # local import avoids circular deps

    cat = aqi_category(aqi) if aqi is not None else "Moderate"
    return HEALTH_PROFILES.get(cat, DEFAULT_PROFILE)


def health_response(aqi, city: str = None) -> dict:
    """Public API payload: health profile + category metadata."""
    from services.aqi import aqi_category_info

    profile = get_health_profile(aqi)
    meta = aqi_category_info(aqi)
    return {
        "city": city,
        "aqi": aqi,
        "category": meta["category"],
        "color": meta["color"],
        "status": profile["status"],
        "level": profile["level"],
        "summary": profile["summary"],
        "recommendation": profile["recommendation"],
        "advice": {
            "outdoor": profile["outdoor"],
            "sensitive": profile["sensitive"],
            "mask": profile["mask"],
            "windows": profile["windows"],
            "exercises": profile["exercises"],
        },
    }
