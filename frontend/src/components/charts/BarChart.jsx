/**
 * AirVision AI — responsive bar chart (Recharts)
 */

import {
  Bar, BarChart as RCBarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { useTheme } from '../../context/ThemeContext'

export default function BarChart({
  data, xKey, series, height = 280, color = '#3384fb',
  colorsByCell, radius = 8, horizontal = false, unit = '',
}) {
  const { theme } = useTheme()
  const dark = theme === 'dark'
  const gridColor = dark ? '#1e293b' : '#e2e8f0'
  const axisColor = dark ? '#94a3b8' : '#64748b'

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RCBarChart
        data={data}
        margin={{ top: 8, right: 12, left: horizontal ? 8 : -14, bottom: 0 }}
        layout={horizontal ? 'vertical' : 'horizontal'}
      >
        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={!horizontal} horizontal={horizontal} />
        {horizontal ? (
          <>
            <XAxis type="number" tick={{ fontSize: 11, fill: axisColor }} tickLine={false} axisLine={false} />
            <YAxis type="category" dataKey={xKey} width={130} tick={{ fontSize: 11, fill: axisColor }} tickLine={false} axisLine={false} />
          </>
        ) : (
          <>
            <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: axisColor }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 11, fill: axisColor }} tickLine={false} axisLine={false} width={52} />
          </>
        )}
        <Tooltip
          cursor={{ fill: dark ? '#1e293b55' : '#e2e8f055' }}
          contentStyle={{
            borderRadius: 12, border: '1px solid #334155',
            background: dark ? '#0f172a' : '#fff', color: dark ? '#e2e8f0' : '#0f172a',
          }}
          labelStyle={{ color: dark ? '#cbd5e1' : '#475569' }}
        />
        {series.map((s) => (
          <Bar key={s.key} dataKey={s.key} name={s.name} radius={radius} fill={color} maxBarSize={46}>
            {colorsByCell &&
              data.map((_, i) => <Cell key={i} fill={colorsByCell[i]} />)}
          </Bar>
        ))}
      </RCBarChart>
    </ResponsiveContainer>
  )
}
