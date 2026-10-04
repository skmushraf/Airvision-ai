# AirVision AI — Setup (downloaded copy)

Everything needed to run the project is in this archive. Full details live in
`README.md`; this is the 60-second version.

## What's inside

```
airvision-ai/
├── backend/        Flask REST API, AQI engine, CPCB + OpenWeather clients
│   ├── static/     Pre-built React app (so you can run without Node)
│   └── .env        ⚠️ your real API keys — see "Security" below
├── frontend/       React + Vite + Tailwind source
├── ml/             Training pipeline + the Kaggle dataset (city_day.csv)
├── models/         Trained XGBoost model (model.pkl) + metrics metadata
├── documentation/  Architecture, ER diagram, DFD, flowcharts, API docs, testing
├── deploy/         Render blueprint, Vercel config, Dockerfile, run script
└── start.sh        One-command launcher
```

Not included (regenerated automatically): `node_modules/`, `__pycache__/`,
`frontend/dist/`, and the runtime SQLite cache `backend/database/airvision.db`.

## Fastest way to run

```bash
cd airvision-ai
./start.sh
# → http://localhost:5000
```

`start.sh` installs any missing Python packages, rebuilds the frontend only if
`backend/static` is missing, and serves the API + UI together on port 5000.

## Manual run

```bash
# Backend (serves the pre-built UI too)
cd backend
pip install -r requirements.txt
python app.py                 # → http://localhost:5000

# Frontend in dev mode (hot reload, optional)
cd ../frontend
npm install
npm run dev                   # → http://localhost:5173, proxies /api to :5000
```

## Retrain the model (optional)

```bash
cd ml
pip install -r requirements.txt
python train.py               # rewrites ../models/model.pkl + metadata
```

## Run the tests

```bash
cd backend && python -m pytest tests -q     # 46 tests
cd ../ml   && python -m pytest tests -q     # 7 tests
```

## Security — read before pushing to GitHub

`backend/.env` is included so the project runs immediately, and it contains
**your real API keys**. It is listed in `.gitignore`, but double-check before
your first push:

```bash
git status --porcelain | grep -F ".env"     # must print nothing
```

If a key is ever exposed, rotate it at
<https://home.openweathermap.org/api_keys>. Commit `.env.example` instead —
it has the same variables with placeholder values.

## Data sources

| Region | Source |
|---|---|
| India | CPCB real-time station feed via data.gov.in (primary) |
| Rest of world | OpenWeather Air Pollution API |
| Weather / forecast / geocoding | OpenWeather |

The CPCB feed activates automatically when the host can reach
`api.data.gov.in` (reliable from inside India). Confirm with:

```bash
curl http://localhost:5000/api/cpcb/status
```

`"available": true` means Indian cities are being served by CPCB; otherwise the
app transparently falls back to OpenWeather and reports why.
