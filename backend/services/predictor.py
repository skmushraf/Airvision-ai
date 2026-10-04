"""
AirVision AI — ML Predictor Service
===================================
Loads the trained pipeline (models/model.pkl) produced by ml/train.py and
exposes `predict_aqi(pollutants)` for live AQI prediction.

The model is a Random Forest / XGBoost / Linear regressor (auto-selected at
training time) trained on pollutant concentrations + temporal features from
the Air Quality Data in India (2015-2020) dataset.
"""

import os
import threading

from config import Config
from services import aqi

_lock = threading.Lock()
_pipeline = None
_load_error = None


def load_pipeline():
    """Load the model pipeline lazily (thread-safe, cached)."""
    global _pipeline, _load_error
    with _lock:
        if _pipeline is not None or _load_error is not None:
            return _pipeline
        if not os.path.exists(Config.MODEL_PATH):
            _load_error = f"model.pkl not found at {Config.MODEL_PATH}"
            return None
        try:
            from services.ml_pipeline_wrapper import load as _load_pipeline

            _pipeline = _load_pipeline(Config.MODEL_PATH)
        except Exception as exc:
            _load_error = f"Failed to load model: {exc}"
            _pipeline = None
        return _pipeline


def is_available() -> bool:
    return load_pipeline() is not None


def model_metadata() -> dict:
    """Return training metadata (metrics, selected model) for display."""
    pipe = load_pipeline()
    return getattr(pipe, "metadata", {}) if pipe else {"error": _load_error}


def predict_aqi(pollutants: dict):
    """Predict AQI (0-500) from a dict of pollutant concentrations."""
    pipe = load_pipeline()
    if pipe is None:
        return None
    try:
        # The pipeline expects keys PM2.5, PM10, NO2, CO, SO2, O3, NH3
        mapped = {
            "PM2.5": pollutants.get("pm2_5"),
            "PM10": pollutants.get("pm10"),
            "NO2": pollutants.get("no2"),
            "CO": pollutants.get("co"),
            "SO2": pollutants.get("so2"),
            "O3": pollutants.get("o3"),
            "NH3": pollutants.get("nh3"),
        }
        return pipe.predict_from_live(mapped)
    except Exception:
        return None


def predict_aqi_with_temporal(pollutants: dict, temporal: dict):
    """
    Predict AQI using pollutant concentrations plus explicit temporal features
    (month, day, day_of_week, is_weekend, season) — used for future forecasts.
    """
    pipe = load_pipeline()
    if pipe is None:
        return None
    try:
        mapped = {
            "PM2.5": pollutants.get("pm2_5"),
            "PM10": pollutants.get("pm10"),
            "NO2": pollutants.get("no2"),
            "CO": pollutants.get("co"),
            "SO2": pollutants.get("so2"),
            "O3": pollutants.get("o3"),
            "NH3": pollutants.get("nh3"),
        }
        return pipe.predict_from_live(mapped, temporal)
    except Exception:
        return None


def predicted_category(aqi_value) -> str:
    """CPCB category for a predicted AQI."""
    return aqi.aqi_category(aqi_value) if aqi_value is not None else "Unknown"
