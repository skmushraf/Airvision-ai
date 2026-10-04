/**
 * AirVision AI — chart wrapper card
 * Adds a title, subtitle and a "save as PNG" action for any chart.
 */

import { useRef, useState } from 'react'
import DownloadIcon from '@mui/icons-material/Download'
import { exportChartAsPNG } from '../../utils/exporters'

export default function ChartCard({ title, subtitle, children, action, className = '' }) {
  const ref = useRef(null)
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    try {
      await exportChartAsPNG(ref.current, `${(title || 'chart').toLowerCase().replace(/\s+/g, '-')}.png`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div ref={ref} className={`card p-5 ${className}`}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">{title}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-slate-400">{subtitle}</p>}
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {action}
          <button
            type="button"
            onClick={save}
            disabled={saving}
            title="Export chart as PNG"
            className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-brand-500 disabled:opacity-50 dark:hover:bg-slate-800"
          >
            <DownloadIcon fontSize="small" />
          </button>
        </div>
      </div>
      {children}
    </div>
  )
}
