/**
 * AirVision AI — pollutant concentration cards
 */

import { motion } from 'framer-motion'
import { POLLUTANT_LABELS, POLLUTANT_UNITS } from '../../utils/aqi'

const ORDER = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3', 'nh3']

const COLORS = {
  pm2_5: '#3384fb',
  pm10: '#14b8a6',
  no2: '#f97316',
  so2: '#a855f7',
  co: '#eab308',
  o3: '#10b981',
  nh3: '#f43f5e',
}

export default function PollutantCard({ pollutants, loading = false }) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="card h-24 animate-pulse p-4 dark:bg-slate-800/60" />
        ))}
      </div>
    )
  }

  const entries = ORDER.filter((k) => pollutants?.[k] != null).map((k) => ({
    key: k,
    label: POLLUTANT_LABELS[k],
    value: pollutants[k],
    unit: POLLUTANT_UNITS[k],
    color: COLORS[k],
  }))

  if (!entries.length) {
    return (
      <div className="card p-6 text-center text-sm text-slate-400">
        Pollutant data unavailable
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {entries.map((e, i) => (
        <motion.div
          key={e.key}
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.05 }}
          className="card card-hover p-4"
        >
          <p className="stat-label">{e.label}</p>
          <p className="mt-1 text-xl font-bold" style={{ color: e.color }}>
            {e.value}
            <span className="ml-1 text-[11px] font-medium text-slate-400">{e.unit}</span>
          </p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
            <motion.div
              className="h-full rounded-full"
              style={{ background: e.color }}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(100, (e.value / 250) * 100)}%` }}
              transition={{ duration: 0.8 }}
            />
          </div>
        </motion.div>
      ))}
    </div>
  )
}
