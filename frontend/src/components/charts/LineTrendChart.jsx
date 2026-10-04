/**
 * AirVision AI — responsive line/area trend chart (Recharts)
 */

import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { useTheme } from '../../context/ThemeContext'

function CustomTooltip({ active, payload, label, unit }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl border border-slate-200 bg-white/95 px-3 py-2 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-900/95">
      <p className="mb-1 font-semibold text-slate-700 dark:text-slate-200">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
          <span className="h-2 w-2 rounded-full" style={{ background: p.color || p.stroke }} />
          <span className="font-bold text-slate-800 dark:text-slate-100">
            {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
          </span>
          {unit && <span>{unit}</span>}
        </p>
      ))}
    </div>
  )
}

export default function LineTrendChart({
  data, xKey, series, height = 280,
  colors = ['#3384fb'], unit = '', gradientId = 'lineGrad',
}) {
  const { theme } = useTheme()
  const dark = theme === 'dark'
  const gridColor = dark ? '#1e293b' : '#e2e8f0'
  const axisColor = dark ? '#94a3b8' : '#64748b'

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 12, left: -14, bottom: 0 }}>
        <defs>
          {series.map((s, i) => (
            <linearGradient key={s.key} id={`${gradientId}-${i}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={colors[i % colors.length]} stopOpacity={0.35} />
              <stop offset="100%" stopColor={colors[i % colors.length]} stopOpacity={0.02} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
        <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: axisColor }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11, fill: axisColor }} tickLine={false} axisLine={false} width={52} />
        <Tooltip content={<CustomTooltip unit={unit} />} />
        {series.map((s, i) => (
          <Area
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name}
            stroke={colors[i % colors.length]}
            strokeWidth={2.5}
            fill={`url(#${gradientId}-${i})`}
            dot={false}
            activeDot={{ r: 4 }}
            connectNulls
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  )
}
