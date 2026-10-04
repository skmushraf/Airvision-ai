/**
 * AirVision AI — health recommendation card
 */

import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety'
import { motion } from 'framer-motion'
import { aqiCategoryInfo } from '../../utils/aqi'

export default function HealthCard({ aqi, health }) {
  const info = aqiCategoryInfo(aqi)

  if (!health) {
    return (
      <div className="card flex h-full items-center justify-center p-6 text-sm text-slate-400">
        Health recommendation unavailable
      </div>
    )
  }

  const advices = [
    { label: 'Outdoor activity', value: health.advice?.outdoor },
    { label: 'Sensitive groups', value: health.advice?.sensitive },
    { label: 'Mask guidance', value: health.advice?.mask },
    { label: 'Indoor air', value: health.advice?.windows },
  ]

  return (
    <div
      className="card h-full overflow-hidden p-5"
      style={{ borderColor: `${info.color}55` }}
    >
      <div className="mb-3 flex items-center justify-between">
        <p className="section-title">Health Advisory</p>
        <HealthAndSafetyIcon style={{ color: info.color }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl p-3.5"
        style={{ background: `${info.color}14` }}
      >
        <p className="text-sm font-bold" style={{ color: info.color }}>
          {health.summary}
        </p>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{health.recommendation}</p>
      </motion.div>

      <ul className="mt-4 space-y-2.5">
        {advices.map((a) => (
          <li key={a.label} className="flex gap-3 text-sm">
            <span className="w-32 shrink-0 font-medium text-slate-400">{a.label}</span>
            <span className="text-slate-700 dark:text-slate-200">{a.value || '—'}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
