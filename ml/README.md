# AirVision AI — Machine Learning Module

## Overview
End-to-end AQI forecasting model built on the **Air Quality Data in India
(2015–2020)** dataset (29,531 rows, 26 cities).

| Step | Implementation |
|------|----------------|
| Preprocessing | duplicates, per-city median imputation, IQR outlier capping, temporal features, StandardScaler (`pipeline.py`) |
| Feature engineering | `month`, `day`, `day_of_week`, `is_weekend`, `season` + pollutant concentrations (`features.py`) |
| Models | Linear Regression · Random Forest · XGBoost |
| Evaluation | MAE, RMSE, R² on a chronological 80/20 split |
| Selection | lowest RMSE wins (XGBoost: MAE 24.58 · RMSE 39.40 · R² 0.8655) |
| Persistence | `models/model.pkl` (self-contained `PredictionPipeline`) + `models/model_metadata.json` |

## Train
```bash
pip install -r requirements.txt
python train.py
# or with a custom dataset:
python train.py --data path/to/city_day.csv
```

## Use from the backend
The Flask backend loads `models/model.pkl` via `services/ml_pipeline_wrapper.py`
and calls:
- `predict_from_live(pollutants)` — current AQI from live concentrations
- `predict_from_live(pollutants, temporal)` — future AQI with forecast-time
  temporal features (used by the 1h/6h/12h/24h forecast)

## Tests
```bash
pip install pytest
pytest -q
```
