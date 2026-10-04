"""
AirVision AI — ML Pipeline (Preprocessing → Training → Evaluation → Selection)
==============================================================================
End-to-end pipeline for building the AQI forecasting model.

Steps
-----
1. Load the raw dataset (ml/data/city_day.csv)
2. Preprocess:
   - Parse dates, drop duplicates, remove all-null rows
   - Missing-value handling (per-city median imputation)
   - Outlier handling (IQR winsorization/capping)
   - Feature engineering (temporal features — see features.py)
   - Feature scaling (StandardScaler)
3. Chronological train/test split (80/20 — time-series aware)
4. Train & evaluate three regressors:
   - Linear Regression
   - Random Forest Regressor
   - XGBoost Regressor
5. Metrics: MAE, RMSE, R²
6. Auto-select the best model (lowest RMSE)
7. Persist a self-contained PredictionPipeline to models/model.pkl

Author: AirVision AI Team
"""

import json
import os
import pickle
import time
from dataclasses import dataclass, field

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from features import (
    ALL_FEATURES,
    POLLUTANT_FEATURES,
    TEMPORAL_FEATURES,
    add_temporal_features,
    aqi_bucket,
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "city_day.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

TARGET = "AQI"
IQR_MULTIPLIER = 1.5

# ---------------------------------------------------------------------------
# Model registry — candidates evaluated by the pipeline
# ---------------------------------------------------------------------------
MODEL_REGISTRY = {
    "linear_regression": lambda: LinearRegression(),
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=180, max_depth=16, min_samples_leaf=3,
        max_features="sqrt", n_jobs=-1, random_state=42,
    ),
    "xgboost": lambda: XGBRegressor(
        n_estimators=500, learning_rate=0.05, max_depth=7,
        subsample=0.9, colsample_bytree=0.9, random_state=42,
        n_jobs=-1,
    ),
}


@dataclass
class PreprocessResult:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    impute_values: dict          # per-feature imputation medians (global)
    outlier_bounds: dict         # {feature: (low, high)} used for capping
    original_shape: tuple


def load_dataset(path: str = DATA_PATH) -> pd.DataFrame:
    """Load and parse the raw CSV dataset."""
    df = pd.read_csv(path, parse_dates=["Date"])
    return df


def preprocess(df: pd.DataFrame) -> PreprocessResult:
    """
    Complete preprocessing pipeline.
    Returns train/test feature matrices, targets and learned transforms
    (imputation medians + outlier bounds) for reuse at inference time.
    """
    df = df.copy()

    # --- 1. Duplicate removal -------------------------------------------------
    n_before = len(df)
    df = df.drop_duplicates()
    n_dups = n_before - len(df)

    # --- 2. Drop rows with no AQI target and no pollutant signal -------------
    pollutant_cols = [c for c in POLLUTANT_FEATURES if c in df.columns]
    df = df.dropna(subset=[TARGET])
    df = df.dropna(subset=pollutant_cols, how="all")
    n_null_dropped = n_before - len(df) - n_dups

    # --- 3. Feature engineering (temporal) -----------------------------------
    df = add_temporal_features(df)

    # --- 4. Missing-value handling: per-city median imputation ----------------
    impute_values = {}
    for col in pollutant_cols:
        med = df.groupby("City")[col].transform("median").median()
        if pd.isna(med):
            med = df[col].median()
        impute_values[col] = med
        df[col] = df[col].fillna(med)

    # --- 5. Outlier handling: IQR winsorization (capping) ---------------------
    outlier_bounds = {}
    for col in pollutant_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - IQR_MULTIPLIER * iqr, q3 + IQR_MULTIPLIER * iqr
        outlier_bounds[col] = (float(low), float(high))
        df[col] = df[col].clip(lower=low, upper=high)

    # Cap the target too (protects against the extreme 2049 spike)
    q1, q3 = df[TARGET].quantile(0.25), df[TARGET].quantile(0.75)
    df[TARGET] = df[TARGET].clip(lower=q1 - 3 * (q3 - q1), upper=q3 + 3 * (q3 - q1))

    # --- 6. Assemble features & targets ---------------------------------------
    features = [c for c in ALL_FEATURES if c in df.columns]
    X = df[features].astype(float)
    y = df[TARGET].astype(float)

    # --- 7. Chronological (time-series aware) split: 80/20 --------------------
    split_idx = int(len(df) * 0.80)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    return PreprocessResult(
        X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test,
        impute_values=impute_values, outlier_bounds=outlier_bounds,
        original_shape=df.shape,
    )


def evaluate(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Return MAE, RMSE, R² for a fitted model."""
    preds = model.predict(X_test)
    return {
        "mae": float(mean_absolute_error(y_test, preds)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
        "r2": float(r2_score(y_test, preds)),
    }


class PredictionPipeline:
    """
    Self-contained prediction object persisted to model.pkl.
    Exposes:
      - .predict(features_df)          -> array of AQI values
      - .predict_from_live(pollutants) -> single AQI from a dict of pollutant
                                          concentrations (keyed by PM2.5, PM10,
                                          NO2, CO, SO2, O3, NH3)
    """

    def __init__(self, model, scaler, feature_names, impute_values,
                 outlier_bounds, metadata):
        self.model = model
        self.scaler = scaler
        self.feature_names = list(feature_names)
        self.impute_values = impute_values
        self.outlier_bounds = outlier_bounds
        self.metadata = metadata

    # -- internal: build a feature row from live pollutant concentrations -----
    def _pollutant_row(self, pollutants: dict, temporal: dict = None) -> np.ndarray:
        temporal = temporal or {}
        row = np.zeros(len(self.feature_names))
        for i, col in enumerate(self.feature_names):
            if col in pollutants and pollutants[col] is not None:
                row[i] = float(pollutants[col])
            elif col in temporal and temporal.get(col) is not None:
                row[i] = float(temporal[col])
            elif col in self.impute_values:
                row[i] = self.impute_values[col]
        return row.reshape(1, -1)

    # -- scale + predict on an already-assembled feature matrix ---------------
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X = X[self.feature_names].astype(float)
        return self.model.predict(self.scaler.transform(X))

    # -- predict AQI from live pollutant concentrations -----------------------
    def predict_from_live(self, pollutants: dict, temporal: dict = None) -> float:
        X_scaled = self.scaler.transform(self._pollutant_row(pollutants, temporal))
        value = float(self.model.predict(X_scaled)[0])
        # AQI is defined on a 0–500 scale — clamp model output to stay in range
        return round(max(0.0, min(500.0, value)), 1)

    def save(self, path: str = MODEL_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            pickle.dump(self, fh)

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "PredictionPipeline":
        """Deserialise a saved pipeline object (requires ml/ on sys.path)."""
        with open(path, "rb") as fh:
            return pickle.load(fh)


def load_pipeline(path: str = MODEL_PATH) -> PredictionPipeline:
    with open(path, "rb") as fh:
        return pickle.load(fh)


def run_pipeline(data_path: str = DATA_PATH, save: bool = True,
                 verbose: bool = True) -> tuple:
    """Run the full pipeline: preprocess → train → evaluate → select → save."""
    t0 = time.time()
    df = load_dataset(data_path)
    prep = preprocess(df)

    # --- 5b. Feature scaling (fit on train only — no data leakage) -----------
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(prep.X_train.values)

    results, fitted = {}, {}
    for name, factory in MODEL_REGISTRY.items():
        model = factory()
        model.fit(X_train_scaled, prep.y_train)
        fitted[name] = model
        results[name] = evaluate(model, scaler.transform(prep.X_test), prep.y_test)
        if verbose:
            print(f"[{name:18s}] MAE={results[name]['mae']:7.2f}  "
                  f"RMSE={results[name]['rmse']:7.2f}  R²={results[name]['r2']:.4f}")

    # --- Auto-select best model by RMSE --------------------------------------
    best_name = min(results, key=lambda k: results[k]["rmse"])
    best_model = fitted[best_name]

    # --- Feature importance (from the best model when available) -------------
    feature_importance = {}
    try:
        if hasattr(best_model, "feature_importances_"):
            imp = best_model.feature_importances_
        elif hasattr(best_model, "coef_"):
            imp = np.abs(best_model.coef_)
        else:
            imp = None
        if imp is not None:
            total = float(np.sum(imp)) or 1.0
            feature_importance = {
                name: round(float(v) / total, 4)
                for name, v in zip(ALL_FEATURES, imp)
            }
    except Exception:
        feature_importance = {}

    metadata = {
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset": os.path.basename(data_path),
        "dataset_rows": int(len(df)),
        "dataset_cities": int(df["City"].nunique()),
        "date_range": [str(df["Date"].min().date()), str(df["Date"].max().date())],
        "features": ALL_FEATURES,
        "target": TARGET,
        "split": {"train_size": len(prep.X_train), "test_size": len(prep.X_test)},
        "model_metrics": results,
        "selected_model": best_name,
        "selected_model_metrics": results[best_name],
        "feature_importance": feature_importance,
        "preprocessing": {
            "impute_values": {k: float(v) for k, v in prep.impute_values.items()},
            "outlier_bounds": {k: list(v) for k, v in prep.outlier_bounds.items()},
            "outlier_method": f"IQR x {IQR_MULTIPLIER} winsorization",
            "scaler": "StandardScaler",
        },
    }

    pipeline = PredictionPipeline(
        model=best_model,
        scaler=scaler,
        feature_names=ALL_FEATURES,
        impute_values=prep.impute_values,
        outlier_bounds=prep.outlier_bounds,
        metadata=metadata,
    )

    if save:
        pipeline.save(MODEL_PATH)
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(METADATA_PATH, "w") as fh:
            json.dump(metadata, fh, indent=2)

    if verbose:
        print(f"\n✔ Best model: {best_name} "
              f"(RMSE={results[best_name]['rmse']:.2f}, "
              f"R²={results[best_name]['r2']:.4f})")
        print(f"✔ Saved pipeline -> {MODEL_PATH}")
        print(f"✔ Total time: {time.time() - t0:.1f}s")
    return pipeline, results


if __name__ == "__main__":
    run_pipeline(verbose=True)
