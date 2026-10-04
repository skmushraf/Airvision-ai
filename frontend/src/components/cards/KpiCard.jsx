/**
 * AirVision AI — KPI card (dashboard tiles)
 */

import { motion } from 'framer-motion'
import { Skeleton } from '../LoadingSkeleton'

export default function KpiCard({
  label, value, unit, icon: Icon, color = '#3384fb',
  sub, delay = 0, loading = false,
}) {
  if (loading) return <Skeleton className="h-[118px] w-full rounded-2xl" />

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.35 }}
      className="card card-hover relative overflow-hidden p-5"
    >
      <div
        className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full opacity-[0.12]"
        style={{ background: color }}
      />
      <div className="flex items-start justify-between">
        <p className="stat-label">{label}</p>
        {Icon && (
          <span
            className="flex h-9 w-9 items-center justify-center rounded-xl"
            style={{ background: `${color}1a`, color }}
          >
            <Icon fontSize="small" />
          </span>
        )}
      </div>
      <p className="mt-2 flex items-baseline gap-1.5">
        <span className="stat-value" style={{ color }}>
          {value ?? '—'}
        </span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </p>
      {sub && <p className="mt-1 truncate text-xs text-slate-400">{sub}</p>}
    </motion.div>
  )
}
