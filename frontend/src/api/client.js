/**
 * AirVision AI — Axios API client
 * ===============================
 * Central HTTP client with:
 *   - automatic retry with exponential backoff (network errors & 5xx)
 *   - in-memory + localStorage TTL cache (GET requests)
 *   - uniform error shape for the rest of the app
 */

import axios from 'axios'
import { API_BASE } from '../config'

// ---------------------------------------------------------------------------
// Tiny TTL cache (memory + localStorage persistence)
// ---------------------------------------------------------------------------
const memCache = new Map()

export function cacheGet(key) {
  if (memCache.has(key)) {
    const { value, expires } = memCache.get(key)
    if (expires > Date.now()) return value
    memCache.delete(key)
  }
  try {
    const raw = localStorage.getItem(`avc:${key}`)
    if (raw) {
      const { value, expires } = JSON.parse(raw)
      if (expires > Date.now()) return value
      localStorage.removeItem(`avc:${key}`)
    }
  } catch {
    /* storage unavailable — ignore */
  }
  return null
}

export function cacheSet(key, value, ttlMs = 5 * 60 * 1000) {
  const expires = Date.now() + ttlMs
  memCache.set(key, { value, expires })
  try {
    localStorage.setItem(`avc:${key}`, JSON.stringify({ value, expires }))
  } catch {
    /* storage full/unavailable — memory cache still works */
  }
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
const client = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
})

// --- Response interceptor: uniform error handling ---------------------------
client.interceptors.response.use(
  (res) => res,
  (error) => {
    const cfg = error.config || {}
    const status = error.response?.status

    // Retry idempotent GETs on network errors / 5xx (max 2 retries, backoff)
    const isRetryable = !status || (status >= 500 && status < 600)
    if (cfg.method === 'get' && isRetryable && (cfg._retry || 0) < 2) {
      cfg._retry = (cfg._retry || 0) + 1
      return new Promise((resolve) => {
        setTimeout(() => resolve(client(cfg)), 400 * cfg._retry)
      })
    }

    return Promise.reject({
      message:
        error.response?.data?.error ||
        (error.code === 'ECONNABORTED' ? 'Request timed out' : error.message) ||
        'Unexpected network error',
      status,
    })
  },
)

// ---------------------------------------------------------------------------
// Public helpers
// ---------------------------------------------------------------------------
/** GET with optional TTL caching. Returns the parsed JSON body. */
export async function apiGet(path, { ttlMs = 0, force = false } = {}) {
  const cacheKey = `GET:${path}`
  if (!force && ttlMs > 0) {
    const hit = cacheGet(cacheKey)
    if (hit !== null) return hit
  }
  const res = await client.get(path)
  if (ttlMs > 0) cacheSet(cacheKey, res.data, ttlMs)
  return res.data
}

/** POST helper (used for any future mutations). */
export function apiPost(path, body) {
  return client.post(path, body).then((r) => r.data)
}

export default client
