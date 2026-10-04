/**
 * AirVision AI — Home Dashboard
 * KPI cards, focus-city panel (AQI gauge, weather, pollutants, health),
 * city ranking table, and one-click export (PDF / CSV report).
 */

import { useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import SpeedIcon from '@mui/icons-material/Speed'
import DeviceThermostatIcon from '@mui/icons-material/DeviceThermostat'
import WaterDropIcon from '@mui/icons-material/WaterDrop'
import AirIcon from '@mui/icons-material/Air'
import CompressIcon from '@mui/icons-material/Compress'
import BiotechIcon from '@mui/icons-material/Biotech'
import HistoryIcon from '@mui/icons-material/History'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import RefreshIcon from '@mui/icons-material/Refresh'
import { useLiveData } from '../context/LiveDataContext'
import KpiCard from '../components/cards/KpiCard'
import AqiGauge from '../components/cards/AqiGauge'
import WeatherCard from '../components/cards/WeatherCard'
import PollutantCard from '../components/cards/PollutantCard'
import HealthCard from '../components/cards/HealthCard'
import { KpiSkeleton } from '../components/LoadingSkeleton'
import { aqiColor } from '../utils/aqi'
import { formatDateTime, round1 } from '../utils/format'
import { downloadAqiReportCSV, exportElementAsPDF } from '../utils/exporters'

export default function DashboardPage() {
  const { cities, loading, lastUpdated, refreshing, refresh, lastRefreshInfo } = useLiveData()
  const [focusCity, setFocusCity] = useState('delhi')
  const dashRef = useRef(null)
  const [exporting, setExporting] = useState(false)

  // Re-read live weather from OpenWeather every time the dashboard is opened
  // (mount / navigating back to it). The backend throttles the sweep to once
  // every FORCE_REFRESH_MIN_INTERVAL seconds so the API quota is safe.
  useEffect(() => {
    refresh({ refresh: true, silent: true })
  }, [refresh])

  const focus = useMemo(
    () => cities.find((c) => c.id === focusCity) || cities[0] || null,
    [cities, focusCity],
  )

  const ranking = useMemo(
    () =>
      [...cities]
        .filter((c) => c.aqi != null)
        .sort((a, b) => b.aqi - a.aqi)
        .slice(0, 12),
    [cities],
  )

  const exportPDF = async () => {
    setExporting(true)
    try {
      await exportElementAsPDF(dashRef.current, 'airvision-dashboard.pdf')
    } finally {
      setExporting(false)
    }
  }

  const w = focus?.weather || {}
  const p = focus?.pollutants || {}

  return (
    <div className="space-y-5">
      {/* Action row */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <select
            className="input !w-56"
            value={focus?.id || ''}
            onChange={(e) => setFocusCity(e.target.value)}
          >
            {cities.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}, {c.country}
              </option>
            ))}
          </select>
          <button type="button" onClick={() => refresh({ refresh: true })} className="btn-ghost !px-3">
            <RefreshIcon fontSize="small" className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={exportPDF} disabled={exporting} className="btn-ghost !text-xs">
            <PictureAsPdfIcon fontSize="small" /> Export Dashboard (PDF)
          </button>
          <button type="button" onClick={() => downloadAqiReportCSV(cities)} className="btn-ghost !text-xs">
            <TableChartIcon fontSize="small" /> Download AQI Report (CSV)
          </button>
        </div>
      </div>

      <div ref={dashRef} className="space-y-5">
        {/* KPI row */}
        {loading ? (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-6">
            {Array.from({ length: 9 }).map((_, i) => (
              <KpiSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-6">
            <KpiCard delay={0} label="Current AQI" value={focus?.aqi} color={aqiColor(focus?.aqi)}
              icon={SpeedIcon} sub={focus?.aqi_category || '—'} />
            <KpiCard delay={0.05} label="Predicted AQI (ML)" value={focus?.predicted_aqi}
              color="#818cf8" icon={BiotechIcon} sub="Auto-selected XGBoost model" />
            <KpiCard delay={0.1} label="Temperature" value={w.temp != null ? `${Math.round(w.temp)}°C` : '—'}
              color="#f59e0b" icon={DeviceThermostatIcon} sub={`Feels ${w.feels_like != null ? Math.round(w.feels_like) : '—'}°C`} />
            <KpiCard delay={0.15} label="Humidity" value={w.humidity != null ? `${w.humidity}%` : '—'}
              color="#0ea5e9" icon={WaterDropIcon} sub={w.description ? w.description : '—'} />
            <KpiCard delay={0.2} label="Wind Speed" value={w.wind_speed != null ? `${w.wind_speed} m/s` : '—'}
              color="#10b981" icon={AirIcon} sub="3h average" />
            <KpiCard delay={0.25} label="Pressure" value={w.pressure != null ? `${w.pressure} hPa` : '—'}
              color="#8b5cf6" icon={CompressIcon} sub="Sea level" />
            <KpiCard delay={0.3} label="AQI Category" value={focus?.aqi_category || '—'}
              color={aqiColor(focus?.aqi)} icon={SpeedIcon}
              sub={focus?.aqi != null ? `Health: ${focus?.health?.level || '—'}` : '—'} />
            <KpiCard delay={0.35} label="Health Status" value={focus?.health?.status || '—'}
              color="#ec4899" icon={BiotechIcon} sub={focus?.health?.level || '—'} />
            <KpiCard delay={0.4} label="Last Updated" value={lastUpdated ? formatDateTime(lastUpdated) : '—'}
              color="#64748b" icon={HistoryIcon} sub={lastRefreshInfo?.throttled ? `Cached · new fetch in ${lastRefreshInfo.nextRefreshIn}s` : "Weather refreshed on open"} />
          </div>
        )}

        {/* Focus city panel */}
        {focus && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="grid gap-4 lg:grid-cols-3"
          >
            <div className="card flex flex-col items-center justify-center gap-3 p-6">
              <div>
                <h2 className="text-center text-lg font-extrabold text-slate-900 dark:text-white">
                  {focus.name}
                  <span className="ml-2 text-sm font-medium text-slate-400">{focus.country}</span>
                </h2>
                <p className="text-center text-xs text-slate-400">
                  {focus.continent} · {focus.lat.toFixed(2)}°, {focus.lon.toFixed(2)}°
                </p>
              </div>
              <AqiGauge aqi={focus.aqi} />
              <p className="text-center text-xs text-slate-400">
                ML predicted: <b className="text-slate-600 dark:text-slate-200">{focus.predicted_aqi ?? '—'}</b>
                {focus.predicted_category ? ` (${focus.predicted_category})` : ''}
              </p>
            </div>

            <WeatherCard
              weather={focus.weather}
              sunrise={w.sunrise}
              sunset={w.sunset}
            />

            <HealthCard aqi={focus.aqi} health={focus.health} />
          </motion.div>
        )}

        {/* Pollutants */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }}>
          <p className="section-title mb-3">
            Pollutant Concentrations {focus ? `· ${focus.name}` : ''}
          </p>
          <PollutantCard pollutants={p} loading={loading} />
        </motion.div>

        {/* Ranking table */}
        <div className="card overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">
              Highest AQI right now
            </h3>
            <span className="text-xs text-slate-400">Live ranking</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400 dark:border-slate-800">
                  <th className="px-5 py-3 font-semibold">#</th>
                  <th className="px-5 py-3 font-semibold">City</th>
                  <th className="px-5 py-3 font-semibold">Country</th>
                  <th className="px-5 py-3 font-semibold">AQI</th>
                  <th className="px-5 py-3 font-semibold">Category</th>
                  <th className="px-5 py-3 font-semibold">PM2.5</th>
                  <th className="px-5 py-3 font-semibold">Temp</th>
                  <th className="px-5 py-3 font-semibold">Predicted</th>
                </tr>
              </thead>
              <tbody>
                {ranking.map((c, i) => (
                  <tr
                    key={c.id}
                    className="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
                  >
                    <td className="px-5 py-3 text-slate-400">{i + 1}</td>
                    <td className="px-5 py-3 font-semibold text-slate-800 dark:text-slate-100">{c.name}</td>
                    <td className="px-5 py-3 text-slate-500 dark:text-slate-400">{c.country}</td>
                    <td className="px-5 py-3">
                      <span className="font-extrabold" style={{ color: c.aqi_color }}>
                        {c.aqi}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className="chip" style={{ background: `${c.aqi_color}1c`, color: c.aqi_color }}>
                        {c.aqi_category}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-500 dark:text-slate-400">
                      {round1(p && c.id === focus?.id ? p.pm2_5 : c.pollutants?.pm2_5)}
                    </td>
                    <td className="px-5 py-3 text-slate-500 dark:text-slate-400">
                      {c.weather?.temp != null ? `${Math.round(c.weather.temp)}°C` : '—'}
                    </td>
                    <td className="px-5 py-3 text-slate-500 dark:text-slate-400">
                      {c.predicted_aqi ?? '—'}
                    </td>
                  </tr>
                ))}
                {!ranking.length && (
                  <tr>
                    <td colSpan={8} className="px-5 py-8 text-center text-slate-400">
                      No live AQI readings yet — add a valid OpenWeather API key to backend/.env
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
