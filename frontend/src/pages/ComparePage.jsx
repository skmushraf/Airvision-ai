/**
 * AirVision AI — City Comparison
 * Side-by-side AQI, pollutants, weather and forecast for two cities.
 */

import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useFetch } from '../hooks/useFetch'
import { getComparison, getCities } from '../api/endpoints'
import { ChartSkeleton } from '../components/LoadingSkeleton'
import ChartCard from '../components/charts/ChartCard'
import LineTrendChart from '../components/charts/LineTrendChart'
import { aqiColor } from '../utils/aqi'
import { round1 } from '../utils/format'

function CityColumn({ title, side }) {
  const w = side?.weather || {}
  const p = side?.pollutants || {}
  const color = aqiColor(side?.aqi)
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-extrabold text-slate-900 dark:text-white">{title}</h3>
          <p className="text-xs text-slate-400">{side?.city?.country || '—'} · {side?.city?.lat?.toFixed(2)}°, {side?.city?.lon?.toFixed(2)}°</p>
        </div>
        <span className="text-3xl font-extrabold" style={{ color }}>
          {side?.aqi ?? '—'}
        </span>
      </div>

      <span className="chip mb-4" style={{ background: `${color}1c`, color }}>
        {side?.aqi_category || 'No data'} · ML predicted {side?.predicted_aqi ?? '—'}
      </span>

      <div className="grid grid-cols-2 gap-2.5 text-sm">
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">PM2.5</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{round1(p.pm2_5)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">PM10</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{round1(p.pm10)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">NO₂</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{round1(p.no2)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">SO₂</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{round1(p.so2)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">O₃</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{round1(p.o3)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">CO</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{round1(p.co)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">Temperature</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{w.temp != null ? `${Math.round(w.temp)}°C` : '—'}</p>
        </div>
        <div className="rounded-xl bg-slate-100 p-3 dark:bg-slate-800/60">
          <p className="stat-label">Humidity</p>
          <p className="font-bold text-slate-800 dark:text-slate-100">{w.humidity != null ? `${w.humidity}%` : '—'}</p>
        </div>
      </div>

      {side?.health && (
        <div className="mt-4 rounded-xl p-3 text-xs" style={{ background: `${color}14`, color }}>
          <b>Health:</b> {side.health.recommendation}
        </div>
      )}
    </motion.div>
  )
}

export default function ComparePage() {
  const [city1, setCity1] = useState('delhi')
  const [city2, setCity2] = useState('mumbai')

  const { data: citiesData } = useFetch(() => getCities(), [])
  const { data, loading, error } = useFetch(() => getComparison(city1, city2), [city1, city2])

  const cityList = useMemo(
    () => (citiesData?.cities || []).map((c) => ({ id: c.id, name: c.name, country: c.country })),
    [citiesData],
  )

  const forecastChart = useMemo(() => {
    const a = (data?.city1?.aqi_forecast || []).map((f) => ({ name: f.label, A: f.aqi }))
    const b = (data?.city2?.aqi_forecast || []).map((f) => ({ name: f.label, B: f.aqi }))
    const map = new Map()
    a.forEach((r) => map.set(r.name, { ...r, B: null }))
    b.forEach((r) => {
      const existing = map.get(r.name)
      if (existing) existing.B = r.aqi
      else map.set(r.name, { name: r.name, A: null, B: r.aqi })
    })
    return [...map.values()]
  }, [data])

  const diff = data?.comparison

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs font-semibold text-slate-400">City 1</label>
          <select className="input !w-60" value={city1} onChange={(e) => setCity1(e.target.value)}>
            {cityList.map((c) => (
              <option key={c.id} value={c.id}>{c.name}, {c.country}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-semibold text-slate-400">City 2</label>
          <select className="input !w-60" value={city2} onChange={(e) => setCity2(e.target.value)}>
            {cityList.map((c) => (
              <option key={c.id} value={c.id}>{c.name}, {c.country}</option>
            ))}
          </select>
        </div>
        {diff?.aqi_difference != null && (
          <div className="card px-4 py-3 text-sm">
            AQI difference:{' '}
            <b className={diff.aqi_difference > 0 ? 'text-red-500' : 'text-emerald-500'}>
              {diff.aqi_difference > 0 ? '+' : ''}{diff.aqi_difference}
            </b>{' '}
            <span className="text-slate-400">(city1 − city2)</span>
          </div>
        )}
      </div>

      {error && <div className="card border-red-500/40 p-4 text-sm text-red-500">{error}</div>}

      {loading ? (
        <ChartSkeleton height={320} />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <CityColumn title={data?.city1?.city?.name || city1} side={data?.city1} />
          <CityColumn title={data?.city2?.city?.name || city2} side={data?.city2} />
        </div>
      )}

      <ChartCard title="AQI Forecast Comparison" subtitle="ML forecast: Now / 1h / 6h / 12h / 24h">
        {loading ? (
          <ChartSkeleton height={260} />
        ) : (
          <LineTrendChart
            data={forecastChart}
            xKey="name"
            series={[
              { key: 'A', name: city1 },
              { key: 'B', name: city2 },
            ]}
            colors={['#3384fb', '#f97316']}
            height={260}
          />
        )}
      </ChartCard>
    </div>
  )
}
