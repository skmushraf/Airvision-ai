/**
 * AirVision AI — map legend (AQI color scale)
 */

import { AQI_CATEGORIES } from '../../utils/aqi'

export default function MapLegend() {
  return (
    <div className="pointer-events-none absolute bottom-5 right-5 z-[1000] rounded-2xl border border-slate-200 bg-white/90 p-3.5 shadow-card-lg backdrop-blur dark:border-slate-700 dark:bg-slate-900/90">
      <p className="mb-2 text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        AQI Scale
      </p>
      <div className="space-y-1.5">
        {AQI_CATEGORIES.map((c) => (
          <div key={c.category} className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
            <span className="h-3 w-3 rounded-full" style={{ background: c.color }} />
            <span className="w-24 font-medium">{c.category}</span>
            <span className="text-slate-400">
              {c.min}–{c.max}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
