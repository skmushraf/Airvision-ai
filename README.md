<div align="center">

# 🌍 AirVision AI

### Real-Time Global Air Quality Monitoring & Forecasting System Using Machine Learning

A production-ready, full-stack environmental intelligence platform for **final-year engineering projects**.

![React](https://img.shields.io/badge/React-18-blue) ![Vite](https://img.shields.io/badge/Vite-5-purple) ![Tailwind](https://img.shields.io/badge/TailwindCSS-3-38bdf8) ![Flask](https://img.shields.io/badge/Flask-3-green) ![ML](https://img.shields.io/badge/Scikit--learn%20%2B%20XGBoost-orange) ![SQLite](https://img.shields.io/badge/SQLite-database-lightgrey)

</div>

---

## ✨ What is AirVision AI?

AirVision AI monitors **real-time air quality anywhere in the world**, forecasts **AQI up to 24 hours ahead with machine learning**, and presents everything on a professional, animated dashboard:

- 🗺️ **Interactive global marker map** — 58 cities across 30 countries, live AQI markers colour-coded by category
- 📊 **KPI dashboards** — current & predicted AQI, weather, pollutants, health advisory
- 🤖 **ML forecasting** — XGBoost (auto-selected from Linear / Random Forest / XGBoost by RMSE) predicts AQI from live pollutants
- 📈 **Historical analytics** — 5 years of trends, distributions, correlations, feature importance & seasonal analysis
- 🔥 **Pollution hotspots** — top-10 polluted/cleanest cities, country & continent rankings
- ⚖️ **City comparison** — side-by-side AQI, pollutants, weather & forecast for any two cities
- 🏥 **Health recommendation engine** — dynamic advice for every AQI category
- 🌓 **Dark / light mode**, 📱 fully responsive, ⚡ animated (Framer Motion)

**Live data only.** Indian readings come from the **CPCB real-time station network** (data.gov.in); the rest of the world and all weather/forecast/geocoding come from the OpenWeather APIs in real time (air pollution, current weather, 5-day forecast, geocoding). The dashboard refreshes every 5 minutes and *never* shows dummy values — when the API is unreachable it keeps the last successful readings and shows a non-blocking warning.

---

## 🧱 Tech Stack

| Layer      | Technologies |
|------------|--------------|
| Frontend   | React 18 · Vite · Tailwind CSS · React Router · Axios · React Leaflet · Recharts · Framer Motion · MUI Icons · html2canvas · jsPDF |
| Backend    | Python · Flask · REST API · SQLite (persistent cache) · ThreadPoolExecutor concurrency |
| ML         | Pandas · NumPy · Scikit-learn · XGBoost · Joblib |
| Live data  | **CPCB real-time AQI (data.gov.in)** for India · OpenWeather Air Pollution · Current Weather · 5-Day Forecast · Geocoding |
| Deployment | Vercel (frontend) · Render (backend) · Docker-ready |

---

## 📁 Project Structure

```
airvision-ai/
├── backend/                  # Flask REST API
│   ├── app.py                # Application factory + server entry
│   ├── config.py             # Env-driven configuration
│   ├── requirements.txt
│   ├── .env.example          # Copy to .env and add your API key
│   ├── database/             # SQLite schema + data-access layer
│   ├── routes/               # 13 REST endpoints (blueprints)
│   ├── services/             # OpenWeather client, AQI engine, predictor,
│   │                         # forecast, hotspots, health, historical
│   └── tests/                # pytest test suite
├── ml/                       # Machine-learning pipeline
│   ├── data/city_day.csv     # Air Quality Data in India (2015-2020)
│   ├── features.py           # Feature engineering
│   ├── pipeline.py           # Preprocess → train → evaluate → select → save
│   ├── train.py              # Training entrypoint (python train.py)
│   └── requirements.txt
├── models/                   # Trained artifacts (generated)
│   ├── model.pkl             # Best model + scaler + imputer (auto-selected)
│   └── model_metadata.json   # Metrics, feature importance, training info
├── frontend/                 # React + Vite dashboard
│   ├── src/api/              # Axios client (retry, cache) + endpoints
│   ├── src/components/       # Layout, cards, charts, maps, UI
│   ├── src/context/          # Theme + live-data providers
│   ├── src/hooks/            # useFetch, useInterval, useDebounce
│   ├── src/pages/            # 8 routed pages
│   ├── src/utils/            # AQI helpers, formatters, exporters
│   └── vite.config.js        # Dev proxy: /api → Flask (5000)
├── dataset/                  # Dataset documentation
├── documentation/            # Architecture, ER, DFD, flowcharts, API docs,
│                             # testing & deployment guides
├── deploy/                   # render.yaml, Dockerfile, vercel.json
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+** (tested on 3.13)
- Node.js **18+** and npm
- A free **OpenWeather API key** → <https://home.openweathermap.org/api_keys>

> ⚠️ The key shipped in `backend/.env` is a **placeholder and returns HTTP 401**.
> Replace it with your own free key (the Air Pollution, Current Weather,
> 5-Day Forecast and Geocoding APIs are all included in the free tier).

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env → set OPENWEATHER_API_KEY=<your key>
python app.py
# → http://localhost:5000
```

### 2. Train the ML model (optional — model.pkl is already included)

```bash
cd ml
pip install -r requirements.txt
python train.py
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173  (Vite proxies /api → http://localhost:5000)
```

---


## 🔑 API Configuration & Environment Variables

The API key is **never hardcoded and never exposed to the browser**. All
requests go through the Flask backend, which reads the key from environment
variables:

| Variable | Where | Description |
|----------|-------|-------------|
| `OPENWEATHER_API_KEY` | `backend/.env` | **Required.** OpenWeather API key (weather, forecast, geocoding, global air quality) |
| `DATA_GOV_API_KEY` | `backend/.env` | **Required for Indian live data.** data.gov.in key for the CPCB feed |
| `CPCB_RESOURCE_ID` | `backend/.env` | CPCB resource UUID (default `3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69`) |
| `ENABLE_CPCB` | `backend/.env` | `1` (default) = CPCB is primary for India, `0` = OpenWeather everywhere |
| `CPCB_TTL_SECONDS` | `backend/.env` | CPCB cache lifetime (default 900 — the feed updates hourly) |
| `CPCB_CO_UNIT` | `backend/.env` | `auto` (default) / `ug` / `mg` — CO unit handling in the feed |
| `CACHE_TTL_SECONDS` | `backend/.env` | Live-data cache lifetime (default 300 = 5 min) |
| `ENABLE_AUTO_REFRESH` | `backend/.env` | `1` = background thread refreshes all cities every TTL (default `0` to respect free-tier limits) |
| `FETCH_CONCURRENCY` | `backend/.env` | Parallel requests to OpenWeather (default 10) |
| `REQUEST_TIMEOUT` | `backend/.env` | Outbound HTTP timeout (default 12 s) |
| `RETRY_ATTEMPTS` | `backend/.env` | Retries per API call (default 2) |
| `FORCE_REFRESH_MIN_INTERVAL` | `backend/.env` | Min seconds between forced refreshes triggered by opening the dashboard (default 120) |
| `CORS_ORIGINS` | `backend/.env` | Allowed browser origins |
| `VITE_API_BASE` | `frontend/.env` | Backend base URL when deployed separately (e.g. `https://api.example.com`) |

> 🔒 `.env` files are git-ignored. Only `.env.example` is committed.

### 🇮🇳 Data Sources — CPCB is primary for India

AirVision AI uses the **most authoritative source available for each region**:

| Region | Air-quality source | AQI standard |
|--------|--------------------|--------------|
| **India** | **CPCB — Central Pollution Control Board**, real-time station feed via [data.gov.in](https://data.gov.in) resource `3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69` | **CPCB National AQI (NAQI)** — official Indian breakpoints incl. NH₃ |
| Rest of world | OpenWeather Air Pollution API | US EPA breakpoints, displayed in CPCB categories |
| Weather · forecast · geocoding (everywhere) | OpenWeather | — |

**How the CPCB integration works**

1. The backend pulls every station row from the CPCB resource (paginated) and
   caches it for 15 minutes — the feed itself only updates hourly.
2. Rows are station-level and one-pollutant-per-row, so they are grouped by
   city and **averaged across all stations** in that city.
3. The **official CPCB NAQI sub-index table** is applied (PM2.5, PM10, NO₂,
   SO₂, CO in mg/m³, O₃, NH₃); the city AQI is the worst sub-index, and the
   dominant pollutant is reported as the AQI *driver*.
4. CPCB's validity rule (≥3 pollutants, at least one of PM2.5/PM10) is
   enforced via a `reliable` flag.
5. Towns with no monitoring station of their own (Tenali, Ponnur, Bapatla,
   Chirala…) borrow the nearest monitored city's reading and are **explicitly
   labelled** `cpcb_proxy` with a note naming that city — never silently
   misattributed.
6. If data.gov.in is unreachable (some non-Indian hosts are blocked by the
   government network), the city **automatically falls back to OpenWeather**
   and the reason is reported in `/api/cpcb/status`.

Each record carries its provenance (`source: "cpcb" | "live" | "cache" | "demo"`,
plus `provider`, `aqi_standard`, `cpcb_station_count`), and the UI shows a green
**CPCB** chip on those cities.

> Get a free data.gov.in key: sign in at <https://data.gov.in> → *My Account* →
> *API key*. The bundled key is the public OGD sample key (heavily rate-limited).

---

### 🧪 Demo Data Mode (optional)

New OpenWeather keys can take up to ~2 hours to activate, and invalid keys
return `401`. To demonstrate **every feature and layer** while the key is
pending, set `ENABLE_DEMO_DATA=1` in `backend/.env` (default is `0` = live only):

- Readings are **clearly labelled** as demo (`source="demo"`, violet "Demo data"
  chip + banner in the UI) — never confused with real data.
- Pollutants are generated deterministically per city with realistic
  regional ranges; AQI is computed with the **real EPA engine**, predictions
  come from the **real trained ML model**, and health advice from the **real
  recommendation engine**.
- When a valid key is set and `ENABLE_DEMO_DATA=0`, demo code never runs —
  every value comes from OpenWeather.

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/live-air-quality` | Live AQI + pollutants + weather + ML prediction for all cities |
| GET | `/api/live-air-quality?refresh=1` | Same, but forces a fresh OpenWeather read (throttled server-side; sent by the dashboard on open) |
| GET | `/api/live-weather` | Live weather for all cities |
| GET | `/api/forecast?city=delhi` | AQI forecast (Now/1h/6h/12h/24h) + hourly/daily weather |
| GET | `/api/cities` | 58-city catalog with lat/lon |
| GET | `/api/cities/autocomplete?q=` | Search autocomplete |
| GET | `/api/countries` | Country summaries & rankings |
| GET | `/api/comparison?city1=&city2=` | Side-by-side comparison |
| GET | `/api/hotspots` | Top polluted/cleanest + aggregates |
| GET | `/api/health?aqi=` or `?city=` | Health recommendation engine |
| GET | `/api/map-data` | Lightweight payload for the global map |
| GET | `/api/cpcb/status` | CPCB provider diagnostics (key, cities/stations indexed, errors) |
| GET | `/api/cpcb/cities` | Every Indian city in the CPCB feed with its NAQI |
| GET | `/api/cpcb/stations?city=` | Station-level CPCB readings (map station layer) |
| GET | `/api/cpcb/refresh` | Force-refresh the CPCB cache |
| GET | `/api/status` | System diagnostics (incl. active source per region) |
| GET | `/api/health-check` | Deployment liveness probe |

Full contract: [`documentation/api-docs.md`](documentation/api-docs.md)

---

## 🤖 Machine Learning

**Dataset:** Air Quality Data in India (2015–2020) — 29,531 city-day rows, 26 Indian cities, 16 columns including `AQI` and `AQI_Bucket`.

**Preprocessing:** duplicate removal · per-city median imputation · IQR outlier capping · date parsing · temporal feature engineering (month, day, day-of-week, weekend, Indian season) · StandardScaler.

**Models evaluated** (chronological 80/20 split):

| Model | MAE | RMSE | R² |
|-------|-----|------|----|
| Linear Regression | 44.08 | 59.49 | 0.6935 |
| Random Forest | 25.22 | 40.22 | 0.8599 |
| **XGBoost** ✅ | **24.58** | **39.40** | **0.8655** |

The best model (lowest RMSE) is **auto-selected** and persisted as
`models/model.pkl` — switch the dataset or hyperparameters and the pipeline
picks the winner for you. Feature importance (from the selected model):
PM2.5 0.44 · CO 0.23 · NO₂ 0.08.

**Forecasting approach:** live AQI is computed from pollutant concentrations using **US EPA breakpoints** (0–500). The ML model predicts AQI from live pollutants. For 1h/6h/12h/24h forecasts, live pollutants are adjusted with a **meteorological dispersion model** (wind dispersion, rain scavenging, humidity growth, ozone photochemistry) using the OpenWeather 5-day forecast, then passed to the ML model with future temporal features.

---

## ☁️ Deployment

### Recommended: Render + Docker (single service)

This repository is configured to deploy the complete application as one Render web service:

- React/Vite is built during the Docker image build.
- Flask serves the compiled React SPA and `/api/*` endpoints.
- `models/model.pkl` and the ML code are included in the image.
- API keys are supplied through Render environment variables and are never committed.

Render automatically detects the root [`render.yaml`](render.yaml) Blueprint. The Dockerfile is [`deploy/Dockerfile`](deploy/Dockerfile).

Required secret variables in Render:

- `OPENWEATHER_API_KEY`
- `DATA_GOV_API_KEY` (optional if CPCB integration is not needed)

Do **not** commit `backend/.env`; use `backend/.env.example` as the local template.

### Other deployment options

A separate Render backend + Vercel frontend setup is still possible, but it requires setting `VITE_API_BASE` to the deployed backend URL and configuring CORS. The Docker deployment above avoids that split configuration.

See [`documentation/deployment.md`](documentation/deployment.md) for additional details.

---

## 🧪 Testing

```bash
cd backend && pytest -q          # API contract tests
cd frontend && npm run build     # production build check
```

See [`documentation/testing.md`](documentation/testing.md).

---

## 📚 Documentation

| Doc | Contents |
|-----|----------|
| [`documentation/system-architecture.md`](documentation/system-architecture.md) | Architecture diagram, component flow, technology rationale |
| [`documentation/er-diagram.md`](documentation/er-diagram.md) | ER diagram of the SQLite schema |
| [`documentation/data-flow-diagram.md`](documentation/data-flow-diagram.md) | DFD levels 0/1/2 |
| [`documentation/flowcharts.md`](documentation/flowcharts.md) | Live-data, forecasting, ML-training & recommendation flowcharts |
| [`documentation/api-docs.md`](documentation/api-docs.md) | Full REST API reference with examples |
| [`documentation/testing.md`](documentation/testing.md) | Test plan + results |
| [`documentation/deployment.md`](documentation/deployment.md) | Render + Vercel + Docker guides |
| [`dataset/README.md`](dataset/README.md) | Dataset description & schema |

---

## 🔮 Future Improvements

- Deep-learning models (LSTM/GRU) for pollutant time-series forecasting
- Additional data sources (WAQI, CPCB live stations, Sentinel-5P satellite)
- User accounts, saved cities and alert subscriptions (email/push)
- Map heat layer + isopleth contours of pollutant spread
- API rate-limit-aware scheduling with per-endpoint quotas
- Kubernetes / serverless deployment with CI/CD pipelines

---

## 📄 License

MIT — free to use for academic projects and research. Live data © OpenWeather; dataset © its original Kaggle authors.
