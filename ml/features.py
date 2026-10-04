"""
AirVision AI — Feature Engineering Module
=========================================
Builds engineered features for AQI forecasting from the raw dataset
(Air Quality Data in India, 2015-2020) and for live prediction.

Engineered features
-------------------
Temporal  : month, day, day_of_week, is_weekend, season (Indian 4-season scheme)
Pollutant : PM2.5, PM10, NO2, CO, SO2, O3, NH3 (with missing-value imputation
            and IQR outlier capping applied by the pipeline)

Author    : AirVision AI Team
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Feature column definitions (must match between training and live prediction)
# ---------------------------------------------------------------------------
POLLUTANT_FEATURES = [
    "PM2.5",
    "PM10",
    "NO2",
    "CO",
    "SO2",
    "O3",
    "NH3",
]

TEMPORAL_FEATURES = [
    "month",
    "day",
    "day_of_week",
    "is_weekend",
    "season",
]

ALL_FEATURES = POLLUTANT_FEATURES + TEMPORAL_FEATURES

# Indian seasons (1=Winter, 2=Summer, 3=Monsoon, 4=Post-Monsoon)
SEASON_MAP = {
    12: 1, 1: 1, 2: 1,      # Winter  (Dec, Jan, Feb)
    3: 2, 4: 2, 5: 2,       # Summer  (Mar, Apr, May)
    6: 3, 7: 3, 8: 3, 9: 3,  # Monsoon (Jun - Sep)
    10: 4, 11: 4,            # Post-Monsoon (Oct, Nov)
}


def add_temporal_features(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """Add temporal features from a datetime column. Operates in-place."""
    dates = pd.to_datetime(df[date_col])
    df["month"] = dates.dt.month
    df["day"] = dates.dt.day
    df["day_of_week"] = dates.dt.dayofweek  # Monday = 0
    df["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)
    df["season"] = dates.dt.month.map(SEASON_MAP).astype(int)
    return df


def get_engineered_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return the engineered feature matrix (pollutants + temporal features)
    ready for scaling/prediction. Drops rows that still have NaNs after
    imputation is applied by the caller (see pipeline.preprocess).
    """
    add_temporal_features(df)
    cols = [c for c in ALL_FEATURES if c in df.columns]
    return df[cols].copy()


def aqi_bucket(aqi: float) -> str:
    """Map a numeric AQI to the Indian CPCB category name."""
    if pd.isna(aqi):
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


def aqi_bucket_ordinal(aqi: float) -> int:
    """Ordinal rank of the AQI bucket (1=Good .. 6=Severe)."""
    return {"Good": 1, "Satisfactory": 2, "Moderate": 3,
            "Poor": 4, "Very Poor": 5, "Severe": 6}.get(aqi_bucket(aqi), 0)


def temporal_features_from_dt(dt) -> dict:
    """
    Build the temporal feature dict {month, day, day_of_week, is_weekend,
    season} from a datetime — used when predicting AQI at a *future* point
    in time (forecast), so seasonal/time-of-year effects are respected.
    """
    dt = pd.to_datetime(dt)
    return {
        "month": dt.month,
        "day": dt.day,
        "day_of_week": dt.dayofweek,
        "is_weekend": int(dt.dayofweek >= 5),
        "season": SEASON_MAP.get(dt.month, 1),
    }
