/**
 * AirVision AI — frontend configuration
 * The API base URL defaults to a same-origin /api (proxied by Vite in dev,
 * by a reverse proxy in production). Override with VITE_API_BASE when the
 * backend is hosted separately (e.g. Render).
 */
export const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const APP = {
  name: 'AirVision AI',
  tagline: 'Real-Time Global Air Quality Intelligence',
  version: '1.0.0',
}

/** Live data refresh interval (ms) — aligns with backend cache TTL (5 min). */
export const REFRESH_INTERVAL_MS = 5 * 60 * 1000

/** How stale (ms) cached live data may be before we show the warning banner. */
export const STALE_AFTER_MS = 6 * 60 * 1000
