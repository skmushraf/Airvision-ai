/**
 * AirVision AI — donut / pie chart (Recharts)
 */

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

export default function DonutChart({ data, height = 260, innerRadius = 55, outerRadius = 85 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Tooltip
          contentStyle={{ borderRadius: 12, border: '1px solid #334155', background: '#0f172a', color: '#e2e8f0' }}
          labelStyle={{ color: '#cbd5e1' }}
        />
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={innerRadius}
          outerRadius={outerRadius}
          paddingAngle={2}
          strokeWidth={0}
        >
          {data.map((entry, i) => (
            <Cell key={i} fill={entry.color} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  )
}
