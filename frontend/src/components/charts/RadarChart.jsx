/**
 * AirVision AI — radar chart (Recharts) for pollutant profiles
 */

import {
  PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart as RCRadarChart,
  ResponsiveContainer, Tooltip,
} from 'recharts'
import { useTheme } from '../../context/ThemeContext'

export default function RadarChart({ data, series, height = 280, color = '#3384fb' }) {
  const { theme } = useTheme()
  const dark = theme === 'dark'

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RCRadarChart data={data} outerRadius="72%">
        <PolarGrid stroke={dark ? '#334155' : '#cbd5e1'} />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: dark ? '#94a3b8' : '#64748b' }} />
        <PolarRadiusAxis tick={false} axisLine={false} />
        <Tooltip
          contentStyle={{ borderRadius: 12, border: '1px solid #334155', background: dark ? '#0f172a' : '#fff', color: dark ? '#e2e8f0' : '#0f172a' }}
        />
        {series.map((s, i) => (
          <Radar
            key={s.key}
            name={s.name}
            dataKey={s.key}
            stroke={s.color || color}
            fill={s.color || color}
            fillOpacity={i === 0 ? 0.28 : 0.1}
            strokeWidth={2}
          />
        ))}
      </RCRadarChart>
    </ResponsiveContainer>
  )
}
