/**
 * AirVision AI — Live data context
 * ================================
 * Single source of truth for live city data. Polls the backend every 5 min
 * (per requirement), keeps the last successful payload when a poll fails,
 * and exposes loading / error / stale state for the whole app.
 */

import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { getLiveAirQuality, getStatus } from '../api/endpoints'
import { REFRESH_INTERVAL_MS, STALE_AFTER_MS } from '../config'
import { parseServerTime } from '../utils/format'

const LiveDataContext = createContext(null)

export function LiveDataProvider({ children }) {
  const [cities, setCities] = useState([])
  const [lastUpdated, setLastUpdated] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState(null)          // last fetch error
  const [status, setStatus] = useState('loading')    // ok | degraded | error
  const [source, setSource] = useState(null)         // live | cache | snapshot | demo
  const [demoMode, setDemoMode] = useState(false)    // true when serving demo readings
  const [cpcbCount, setCpcbCount] = useState(0)      // cities served by CPCB (data.gov.in)
  const [apiHealth, setApiHealth] = useState(null)   // /api/status payload
  const [lastRefreshInfo, setLastRefreshInfo] = useState(null) // forced-refresh result
  const mounted = useRef(true)

  const fetchAll = useCallback(async ({ silent = false, refresh = false } = {}) => {
    if (!silent) setRefreshing(true)
    try {
      const payload = await getLiveAirQuality({ force: true, refresh })
      if (!mounted.current) return
      setCities(payload.cities || [])
      setLastUpdated(payload.last_updated)
      setSource(payload.source)
      setDemoMode(Boolean(payload.demo_mode))
      setCpcbCount(Number(payload.cpcb_count) || 0)
      if (payload.refreshed !== undefined) setLastRefreshInfo({
        refreshed: Boolean(payload.refreshed),
        throttled: Boolean(payload.throttled),
        nextRefreshIn: payload.next_refresh_in ?? null,
      })
      setError(payload.error || null)
      setStatus(payload.status === 'ok' ? 'ok' : 'degraded')
    } catch (e) {
      if (!mounted.current) return
      setError(e?.message || 'Unable to reach the API')
      setStatus('error')
    } finally {
      if (mounted.current) {
        setLoading(false)
        setRefreshing(false)
      }
    }
  }, [])

  // --- initial load + periodic refresh --------------------------------------
  useEffect(() => {
    mounted.current = true
    fetchAll()
    const id = setInterval(() => fetchAll({ silent: true }), REFRESH_INTERVAL_MS)
    return () => {
      mounted.current = false
      clearInterval(id)
    }
  }, [fetchAll])

  // --- periodic status probe (key validity, model availability) -------------
  useEffect(() => {
    let id
    const probe = async () => {
      try {
        const s = await getStatus()
        if (mounted.current) setApiHealth(s)
      } catch {
        /* keep last status */
      }
    }
    probe()
    id = setInterval(probe, 60_000)
    return () => clearInterval(id)
  }, [])

  // --- staleness detection (warning banner logic) ---------------------------
  const isStale = useCallback(() => {
    if (!lastUpdated) return false
    const d = parseServerTime(lastUpdated)
    if (!d) return false            // unparseable → never raise a false alarm
    const age = Date.now() - d.getTime()
    if (age < 0) return false       // clock skew → not stale
    return age > STALE_AFTER_MS
  }, [lastUpdated])

  return (
    <LiveDataContext.Provider
      value={{
        cities, lastUpdated, loading, refreshing, error, status, source,
        demoMode, cpcbCount, apiHealth, isStale, refresh: fetchAll, lastRefreshInfo,
      }}
    >
      {children}
    </LiveDataContext.Provider>
  )
}

export const useLiveData = () => useContext(LiveDataContext)
