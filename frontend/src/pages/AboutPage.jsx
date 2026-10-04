/**
 * AirVision AI — About & Documentation
 * Project overview, architecture, tech stack, API endpoints, ML details.
 */

import { motion } from 'framer-motion'
import { useFetch } from '../hooks/useFetch'
import { getStatus } from '../api/endpoints'

const ENDPOINTS = [
  ['GET', '/api/live-air-quality', 'Live AQI + weather + ML prediction for every city'],
  ['GET', '/api/live-weather', 'Live weather only'],
  ['GET', '/api/forecast?city=', 'AQI forecast (Now/1h/6h/12h/24h) + hourly/daily weather'],
  ['GET', '/api/cities', 'City catalog (58 cities, lat/lon, continent)'],
  ['GET', '/api/countries', 'Country summaries & rankings'],
  ['GET', '/api/comparison?city1=&city2=', 'Side-by-side city comparison'],
  ['GET', '/api/hotspots', 'Top polluted/cleanest + aggregates'],
  ['GET', '/api/health?aqi=', 'Health recommendation engine'],
  ['GET', '/api/map-data', 'Lightweight payload for the global map'],
  ['GET', '/api/status', 'System diagnostics (API key, model, cache)'],
]

const STACK = [
  ['Frontend', 'React 18 · Vite · Tailwind CSS · React Router · Axios · React Leaflet · Recharts · Framer Motion · MUI Icons'],
  ['Backend', 'Python · Flask · REST API · SQLite (persistent cache) · ThreadPool concurrency'],
  ['Machine Learning', 'Pandas · NumPy · Scikit-learn · XGBoost · Joblib · Random Forest (auto-selected)'],
  ['Live Data', 'OpenWeather Air Pollution API · Current Weather API · 5-Day Forecast API · Geocoding API'],
]

function Pill({ label }) {
  return (
    <span className="chip bg-slate-200/70 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
      {label}
    </span>
  )
}

export default function AboutPage() {
  const { data: status } = useFetch(() => getStatus(), [], { skip: false })

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-7">
        <h2 className="mb-2 text-2xl font-extrabold text-slate-900 dark:text-white">
          🌍 AirVision AI
        </h2>
        <p className="mb-4 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
          A production-ready <b>real-time global air quality monitoring and forecasting system</b> built
          with machine learning. It streams live AQI and weather for 58 cities across 30 countries,
          forecasts AQI up to 24 hours ahead using an auto-selected XGBoost model trained on the
          <i> Air Quality Data in India (2015–2020)</i> dataset, and surfaces professional analytics —
          hotspots, trends, correlations, comparisons and health advice.
        </p>
        <div className="flex flex-wrap gap-2">
          <Pill label="React + Vite" />
          <Pill label="Flask REST API" />
          <Pill label="XGBoost / Random Forest" />
          <Pill label="OpenWeather Live" />
          <Pill label="SQLite" />
          <Pill label="Render + Vercel ready" />
        </div>
      </motion.div>

      {/* System diagnostics */}
      <div className="card p-6">
        <h3 className="mb-3 text-sm font-bold text-slate-800 dark:text-slate-100">System Diagnostics</h3>
        <div className="grid gap-2 text-sm sm:grid-cols-2">
          <div className="flex justify-between rounded-xl bg-slate-100 px-4 py-3 dark:bg-slate-800/60">
            <span className="text-slate-400">API key configured</span>
            <b className={status?.api_key_configured ? 'text-emerald-500' : 'text-red-500'}>
              {status?.api_key_configured ? 'Yes' : 'No'}
            </b>
          </div>
          <div className="flex justify-between rounded-xl bg-slate-100 px-4 py-3 dark:bg-slate-800/60">
            <span className="text-slate-400">API key valid</span>
            <b className={status?.api_key_valid ? 'text-emerald-500' : 'text-amber-500'}>
              {status?.api_key_valid ? 'Yes' : 'Check backend/.env'}
            </b>
          </div>
          <div className="flex justify-between rounded-xl bg-slate-100 px-4 py-3 dark:bg-slate-800/60">
            <span className="text-slate-400">ML model</span>
            <b className="text-brand-500">{status?.model?.selected || 'not loaded'}</b>
          </div>
          <div className="flex justify-between rounded-xl bg-slate-100 px-4 py-3 dark:bg-slate-800/60">
            <span className="text-slate-400">API calls (24h)</span>
            <b>{status?.api_calls_last_24h ?? '—'}</b>
          </div>
        </div>
      </div>

      {/* Stack */}
      <div className="card p-6">
        <h3 className="mb-4 text-sm font-bold text-slate-800 dark:text-slate-100">Technology Stack</h3>
        <div className="space-y-3">
          {STACK.map(([k, v]) => (
            <div key={k} className="flex flex-col gap-1 text-sm sm:flex-row sm:gap-6">
              <span className="w-32 shrink-0 font-bold text-brand-600 dark:text-brand-400">{k}</span>
              <span className="text-slate-500 dark:text-slate-400">{v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Endpoints */}
      <div className="card overflow-hidden">
        <div className="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">REST API Endpoints</h3>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
          {ENDPOINTS.map(([method, path, desc]) => (
            <div key={path} className="flex flex-col gap-1 px-6 py-3 text-sm sm:flex-row sm:items-center sm:gap-4">
              <span className={`w-12 shrink-0 text-xs font-extrabold ${method === 'GET' ? 'text-emerald-500' : 'text-amber-500'}`}>
                {method}
              </span>
              <code className="shrink-0 font-mono text-xs text-brand-600 dark:text-brand-400">{path}</code>
              <span className="text-slate-500 dark:text-slate-400">{desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ML methodology */}
      <div className="card p-6">
        <h3 className="mb-3 text-sm font-bold text-slate-800 dark:text-slate-100">ML Methodology</h3>
        <ul className="list-disc space-y-2 pl-5 text-sm text-slate-500 dark:text-slate-400">
          <li>Preprocessing: duplicate removal, per-city median imputation, IQR outlier capping, temporal feature engineering, StandardScaler.</li>
          <li>Three regressors evaluated on a chronological 80/20 split: <b>Linear Regression</b>, <b>Random Forest</b>, <b>XGBoost</b>.</li>
          <li>Best model auto-selected by RMSE and persisted as <code className="font-mono text-xs">models/model.pkl</code>.</li>
          <li>Live AQI (0–500) is computed from pollutant concentrations using US EPA breakpoints; the ML model predicts AQI from live pollutants.</li>
          <li>Future AQI (1h/6h/12h/24h) = ML prediction on live pollutants adjusted by forecast meteorology (wind dispersion, rain scavenging, ozone photochemistry).</li>
        </ul>
      </div>
    </div>
  )
}
