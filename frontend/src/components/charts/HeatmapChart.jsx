/**
 * AirVision AI — correlation heatmap (custom grid, no chart lib needed)
 * Cell color encodes correlation strength: blue = positive, red = negative.
 */

import { motion } from 'framer-motion'

function heatColor(v) {
  if (v == null || Number.isNaN(v)) return 'rgba(100,116,139,0.12)'
  const t = Math.min(1, Math.abs(v))
  const isPos = v >= 0
  const base = isPos ? [51, 132, 251] : [244, 63, 94] // brand blue / red
  return `rgba(${base[0]}, ${base[1]}, ${base[2]}, ${0.15 + t * 0.75})`
}

export default function HeatmapChart({ matrix, height = 320 }) {
  const rows = Object.keys(matrix || {})
  const cols = rows.length ? Object.keys(matrix[rows[0]] || {}) : []

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[520px]">
        <div className="mb-1 grid" style={{ gridTemplateColumns: `92px repeat(${cols.length}, 1fr)` }}>
          <div />
          {cols.map((c) => (
            <div key={c} className="pb-1 text-center text-[10px] font-semibold text-slate-400">
              {c}
            </div>
          ))}
        </div>
        {rows.map((r, ri) => (
          <motion.div
            key={r}
            className="mb-1 grid items-center"
            style={{ gridTemplateColumns: `92px repeat(${cols.length}, 1fr)` }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: ri * 0.03 }}
          >
            <div className="pr-2 text-right text-[10px] font-semibold text-slate-400">{r}</div>
            {cols.map((c) => {
              const v = matrix[r]?.[c]
              return (
                <div
                  key={c}
                  className="mx-0.5 flex h-9 items-center justify-center rounded-md text-[10px] font-bold text-white"
                  style={{ background: heatColor(v), color: v != null && Math.abs(v) > 0.5 ? '#fff' : undefined }}
                  title={`${r} × ${c} = ${v ?? 'n/a'}`}
                >
                  {v != null ? v.toFixed(2) : ''}
                </div>
              )
            })}
          </motion.div>
        ))}
      </div>
    </div>
  )
}
