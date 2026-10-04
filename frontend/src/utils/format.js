/**
 * AirVision AI — formatting helpers
 */

/**
 * Parse any timestamp the backend may send into a Date.
 *
 * Handles:
 *   - ISO-8601 with a zone        → "2026-10-03T04:26:02Z"   (what we emit now)
 *   - unix epoch seconds / millis → 1790244885 / 1790244885000
 *   - legacy naive "YYYY-MM-DD HH:MM:SS" — treated as **UTC**, not local.
 *
 * That last case is the important one: browsers parse a naive string as local
 * time, so a UTC server + an IST user disagreed by 5½ hours and fresh data was
 * wrongly flagged stale.
 */
export function parseServerTime(value) {
  if (value == null || value === '') return null
  if (value instanceof Date) return value
  if (typeof value === 'number') {
    return new Date(value < 1e12 ? value * 1000 : value)
  }
  const text = String(value).trim()
  if (/^\d+(\.\d+)?$/.test(text)) {
    const n = Number(text)
    return new Date(n < 1e12 ? n * 1000 : n)
  }
  // Naive "YYYY-MM-DD HH:MM:SS" (no T, no zone) → pin it to UTC
  const naive = /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}(:\d{2})?)$/.exec(text)
  if (naive) return new Date(`${naive[1]}T${naive[2]}Z`)
  const d = new Date(text)
  return Number.isNaN(d.getTime()) ? null : d
}

/** 12-hour time from a unix epoch (seconds). */
export function formatTime(epochSeconds, tzOffsetSec = 0) {
  if (!epochSeconds) return '—'
  const d = new Date((epochSeconds + tzOffsetSec) * 1000)
  return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

/** Date/time from an ISO string or epoch. */
export function formatDateTime(value) {
  if (!value) return '—'
  const d = parseServerTime(value)
  if (!d || Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

/** "5 min ago" style relative time. */
export function timeAgo(value) {
  if (!value) return '—'
  const d = parseServerTime(value)
  if (!d) return '—'
  const diff = Date.now() - d.getTime()
  if (Number.isNaN(diff)) return '—'
  const sec = Math.round(diff / 1000)
  if (sec < 45) return 'just now'
  const min = Math.round(sec / 60)
  if (min < 60) return `${min} min ago`
  const hr = Math.round(min / 60)
  if (hr < 24) return `${hr} hr ago`
  return `${Math.round(hr / 24)} days ago`
}

export function round1(v) {
  return v == null || Number.isNaN(v) ? '—' : Math.round(v * 10) / 10
}

export function round0(v) {
  return v == null || Number.isNaN(v) ? '—' : Math.round(v)
}

export function percent(v) {
  return v == null || Number.isNaN(v) ? '—' : `${Math.round(v)}%`
}

export function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

export function truncate(s, n = 24) {
  if (!s) return ''
  return s.length > n ? `${s.slice(0, n)}…` : s
}

export const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
]
