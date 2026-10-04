/**
 * AirVision AI — Pollution Hotspots
 * Top polluted/cleanest cities, country & continent aggregates.
 */

import { useMemo } from 'react'
import { motion } from 'framer-motion'
import { useFetch } from '../hooks/useFetch'
import { getHotspots } from '../api/endpoints'
import { ChartSkeleton } from '../components/LoadingSkeleton'
import ChartCard from '../components/charts/ChartCard'
import BarChart from '../components/charts/BarChart'
import { aqiColor } from '../utils/aqi'

function RankList({ title, items, tone = 'red', icon }) {
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-2 border-b border-slate-200 px-5 py-4 dark:border-slate-800">
        {icon}
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">{title}</h3>
      </div>
      <ol className="divide-y divide-slate-100 dark:divide-slate-800/60">
        {items.map((c, i) => (
          <li key={c.id} className="flex items-center gap-3 px-5 py-2.5">
            <span
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-extrabold ${
                i === 0 ? 'bg-amber-500/20 text-amber-500' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
              }`}
            >
              {i + 1}
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">
                {c.name}
                <span className="ml-2 text-xs font-normal text-slate-400">{c.country}</span>
              </p>
              <p className="text-[11px] text-slate-400">
                {c.temperature != null ? `${Math.round(c.temperature)}°C · ` : ''}
                PM2.5 {c.pm2_5 ?? '—'}
              </p>
            </div>
            <span className="text-lg font-extrabold" style={{ color: aqiColor(c.aqi) }}>
              {c.aqi}
            </span>
          </li>
        ))}
        {!items.length && (
          <li className="px-5 py-8 text-center text-sm text-slate-400">No live data yet</li>
        )}
      </ol>
    </div>
  )
}

export default function HotspotsPage() {
  const { data, loading, error } = useFetch(() => getHotspots(), [])

  const continentData = useMemo(
    () => (data?.by_continent || []).map((c) => ({ name: c.continent, aqi: c.average_aqi })),
    [data],
  )

  const countryData = useMemo(
    () => (data?.country_ranking || []).map((c) => ({ name: c.country, aqi: c.average_aqi })),
    [data],
  )

  if (loading) return <ChartSkeleton height={420} />

  return (
    <div className="space-y-5">
      {error && <div className="card border-red-500/40 p-4 text-sm text-red-500">{error}</div>}

      {/* Stat strip */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-5 text-center">
          <p className="text-3xl font-extrabold text-red-500">{data?.highest_country?.average_aqi ?? '—'}</p>
          <p className="stat-label">Highest country · {data?.highest_country?.country || '—'}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.05 }} className="card p-5 text-center">
          <p className="text-3xl font-extrabold text-emerald-500">{data?.lowest_country?.average_aqi ?? '—'}</p>
          <p className="stat-label">Lowest country · {data?.lowest_country?.country || '—'}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="card p-5 text-center">
          <p className="text-3xl font-extrabold text-brand-500">{data?.average_global_aqi ?? '—'}</p>
          <p className="stat-label">Average global AQI</p>
        </motion.div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }} className="card p-5 text-center">
          <p className="text-3xl font-extrabold text-slate-600 dark:text-slate-200">
            {data?.coverage?.with_data ?? 0}
            <span className="text-base text-slate-400">/{data?.coverage?.cities ?? 0}</span>
          </p>
          <p className="stat-label">Cities reporting live</p>
        </motion.div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <RankList title="Top 10 Most Polluted Cities" items={data?.top_polluted || []}
          icon={<span className="text-lg">🔴</span>} />
        <RankList title="Top 10 Cleanest Cities" items={data?.cleanest || []}
          icon={<span className="text-lg">🟢</span>} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Average AQI by Continent" subtitle="Live readings aggregated by continent">
          <BarChart data={continentData} xKey="name" series={[{ key: 'aqi', name: 'Avg AQI' }]}
            colorsByCell={continentData.map((c) => aqiColor(c.aqi))} height={300} />
        </ChartCard>
        <ChartCard title="Country Ranking" subtitle="All monitored countries by average AQI">
          <BarChart data={countryData} xKey="name" series={[{ key: 'aqi', name: 'Avg AQI' }]}
            colorsByCell={countryData.map((c) => aqiColor(c.aqi))} height={300} />
        </ChartCard>
      </div>

      <p className="text-center text-xs text-slate-400">
        Hotspots recompute automatically on every live refresh · last updated {data?.live_last_updated || '—'}
      </p>
    </div>
  )
}
