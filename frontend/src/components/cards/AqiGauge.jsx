/**
 * AirVision AI — animated AQI gauge (semicircular)
 */

import { motion } from 'framer-motion'
import { aqiCategoryInfo, aqiProgress } from '../../utils/aqi'

export default function AqiGauge({ aqi, size = 220 }) {
  const info = aqiCategoryInfo(aqi)
  const progress = aqiProgress(aqi)
  const radius = 80
  const circ = Math.PI * radius // semicircle length

  return (
    <div className="flex flex-col items-center" style={{ width: size }}>
      <svg width={size} height={size * 0.62} viewBox="0 0 200 124">
        <defs>
          <linearGradient id="gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="20%" stopColor="#a3e635" />
            <stop offset="45%" stopColor="#f97316" />
            <stop offset="70%" stopColor="#ef4444" />
            <stop offset="90%" stopColor="#b91c1c" />
            <stop offset="100%" stopColor="#a855f7" />
          </linearGradient>
        </defs>

        {/* track */}
        <path
          d="M 20 110 A 80 80 0 0 1 180 110"
          fill="none"
          stroke="currentColor"
          className="text-slate-200 dark:text-slate-800"
          strokeWidth="16"
          strokeLinecap="round"
        />
        {/* progress */}
        <motion.path
          d="M 20 110 A 80 80 0 0 1 180 110"
          fill="none"
          stroke="url(#gauge-grad)"
          strokeWidth="16"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: progress }}
          transition={{ duration: 1.1, ease: 'easeOut' }}
          style={{ filter: `drop-shadow(0 0 6px ${info.color}88)` }}
        />
        {/* value */}
        <text
          x="100"
          y="92"
          textAnchor="middle"
          className="fill-slate-900 text-[38px] font-extrabold dark:fill-white"
        >
          {aqi ?? '—'}
        </text>
        <text x="100" y="112" textAnchor="middle" className="fill-slate-400 text-[11px] font-semibold">
          AQI
        </text>
      </svg>
      <span
        className="chip mt-1 px-3 py-1 text-sm"
        style={{ background: `${info.color}22`, color: info.color }}
      >
        {info.category}
      </span>
    </div>
  )
}
