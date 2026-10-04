/**
 * AirVision AI — map filter controls
 * Search, AQI-category filter, "only polluted / only clean" toggles, reset.
 */

import { useState } from 'react'
import RestartAltIcon from '@mui/icons-material/RestartAlt'
import FilterAltIcon from '@mui/icons-material/FilterAlt'
import { AQI_CATEGORIES } from '../../utils/aqi'

export default function MapControls({ filters, onChange, counts }) {
  const [expanded, setExpanded] = useState(false)

  const toggle = (key) => onChange({ ...filters, [key]: !filters[key] })

  return (
    <div className="card p-4">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          className={`chip px-3 py-1.5 ${expanded ? 'bg-brand-600 text-white' : 'bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300'}`}
          onClick={() => setExpanded((v) => !v)}
        >
          <FilterAltIcon fontSize="inherit" /> Filters
        </button>

        {counts && (
          <span className="text-xs text-slate-400">
            Showing <b className="text-slate-600 dark:text-slate-200">{counts.shown}</b> of{' '}
            {counts.total} cities
          </span>
        )}

        <div className="ml-auto flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => toggle('pollutedOnly')}
            className={`chip px-3 py-1.5 ${filters.pollutedOnly ? 'bg-red-500/20 text-red-500' : 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}`}
          >
            Only polluted (AQI &gt; 200)
          </button>
          <button
            type="button"
            onClick={() => toggle('cleanOnly')}
            className={`chip px-3 py-1.5 ${filters.cleanOnly ? 'bg-emerald-500/20 text-emerald-500' : 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}`}
          >
            Only clean (AQI ≤ 100)
          </button>
          <button
            type="button"
            onClick={() => onChange({ search: '', category: 'all', pollutedOnly: false, cleanOnly: false })}
            className="btn-ghost !px-3 !py-1.5 !text-xs"
          >
            <RestartAltIcon fontSize="small" /> Reset
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 grid gap-3 border-t border-slate-200 pt-3 sm:grid-cols-2 dark:border-slate-800">
          <input
            className="input"
            placeholder="Search city or country…"
            value={filters.search}
            onChange={(e) => onChange({ ...filters, search: e.target.value })}
          />
          <select
            className="input"
            value={filters.category}
            onChange={(e) => onChange({ ...filters, category: e.target.value })}
          >
            <option value="all">All AQI categories</option>
            {AQI_CATEGORIES.map((c) => (
              <option key={c.category} value={c.category}>
                {c.category} ({c.min}–{c.max})
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  )
}
