/**
 * AirVision AI — non-blocking warning banner
 * Shown when live data is unavailable / stale, or when the API key is
 * invalid. Never blocks the UI; dismissible.
 */

import { useState } from 'react'
import CloseIcon from '@mui/icons-material/Close'
import CloudOffIcon from '@mui/icons-material/CloudOff'
import KeyIcon from '@mui/icons-material/Key'
import HistoryIcon from '@mui/icons-material/History'

export default function WarningBanner({ message, variant = 'warning', onRefresh }) {
  const [hidden, setHidden] = useState(false)
  if (hidden) return null

  const styles = {
    warning: 'border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-300',
    error: 'border-red-500/40 bg-red-500/10 text-red-800 dark:text-red-300',
    info: 'border-brand-500/40 bg-brand-500/10 text-brand-800 dark:text-brand-300',
  }[variant]

  const Icon = variant === 'error' ? KeyIcon : variant === 'info' ? HistoryIcon : CloudOffIcon

  return (
    <div className={`flex items-start gap-3 rounded-xl border px-4 py-3 text-sm ${styles}`}>
      <Icon className="mt-0.5 shrink-0 text-lg" />
      <div className="min-w-0 flex-1">
        <p className="font-medium">{message}</p>
        <p className="mt-0.5 text-xs opacity-80">
          Showing the last successful reading. The system retries automatically every 5 minutes.
        </p>
      </div>
      {onRefresh && (
        <button type="button" className="shrink-0 rounded-lg px-2 py-1 text-xs font-semibold underline-offset-2 hover:underline" onClick={onRefresh}>
          Retry now
        </button>
      )}
      <button type="button" aria-label="Dismiss" className="shrink-0 opacity-60 hover:opacity-100" onClick={() => setHidden(true)}>
        <CloseIcon fontSize="small" />
      </button>
    </div>
  )
}
