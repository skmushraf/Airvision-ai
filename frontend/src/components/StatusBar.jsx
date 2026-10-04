/**
 * AirVision AI — live status pill (API status + last updated)
 */

import CloudDoneIcon from '@mui/icons-material/CloudDone'
import CloudOffIcon from '@mui/icons-material/CloudOff'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { timeAgo } from '../utils/format'

export default function StatusBar({ status, source, lastUpdated, demo, cpcbCount = 0, className = '' }) {
  const ok = status === 'ok'
  return (
    <div className={`flex flex-wrap items-center gap-2 text-xs ${className}`}>
      {demo ? (
        <span className="chip bg-violet-500/20 text-violet-600 dark:text-violet-400">
          🧪 Demo data
        </span>
      ) : (
        <span
          className={`chip ${ok ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400' : 'bg-amber-500/15 text-amber-600 dark:text-amber-400'}`}
        >
          {ok ? <CloudDoneIcon fontSize="inherit" /> : <CloudOffIcon fontSize="inherit" />}
          {ok ? 'Live' : source === 'cache' ? 'Cached' : 'Unavailable'}
        </span>
      )}
      {source && source !== 'live' && !demo && (
        <span className="chip bg-slate-500/15 text-slate-500 dark:text-slate-400">
          {source}
        </span>
      )}
      {cpcbCount > 0 && (
        <span
          className="chip bg-emerald-500/15 text-emerald-600 dark:text-emerald-400"
          title={`${cpcbCount} Indian cities sourced from CPCB real-time monitoring stations (data.gov.in)`}
        >
          🇮🇳 CPCB × {cpcbCount}
        </span>
      )}
      {lastUpdated && (
        <span className="flex items-center gap-1 text-slate-500 dark:text-slate-400">
          <ScheduleIcon fontSize="inherit" />
          updated {timeAgo(lastUpdated)}
        </span>
      )}
    </div>
  )
}
