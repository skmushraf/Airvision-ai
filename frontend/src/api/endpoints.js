/**
 * AirVision AI — typed API endpoint wrappers
 * ==========================================
 * One function per backend route; keeps pages free of URL strings.
 * Each wrapper returns the parsed JSON payload (see backend routes).
 */

import { apiGet } from './client'

/**
 * GET /api/live-air-quality — live AQI + weather + prediction for cities.
 * `refresh: true` asks the backend to re-read OpenWeather right now (used
 * when the dashboard is opened); the backend throttles it to protect quota.
 */
export const getLiveAirQuality = ({ refresh = false, ...opts } = {}) =>
  apiGet(`/live-air-quality${refresh ? '?refresh=1' : ''}`, { ttlMs: 0, ...opts })

/** GET /api/live-weather — live weather for all cities */
export const getLiveWeather = () => apiGet('/live-weather')

/** GET /api/forecast?city= — AQI + weather forecast for one city */
export const getForecast = (city, opts = {}) =>
  apiGet(`/forecast?city=${encodeURIComponent(city)}`, { ttlMs: 0, ...opts })


/** GET /api/cities — full city catalog (optional ?search=) */
export const getCities = (search = '') =>
  apiGet(`/cities${search ? `?search=${encodeURIComponent(search)}` : ''}`, {
    ttlMs: 10 * 60 * 1000,
  })

/** GET /api/cities/autocomplete?q= — lightweight search */
export const autocompleteCities = (q) =>
  apiGet(`/cities/autocomplete?q=${encodeURIComponent(q)}`, { ttlMs: 60_000 })

/** GET /api/countries — country summaries */
export const getCountries = (opts = {}) =>
  apiGet('/countries', { ttlMs: 0, ...opts })

/** GET /api/comparison?city1=&city2= — side-by-side comparison */
export const getComparison = (city1, city2) =>
  apiGet(`/comparison?city1=${encodeURIComponent(city1)}&city2=${encodeURIComponent(city2)}`, {
    ttlMs: 0,
  })

/** GET /api/hotspots — pollution rankings & aggregates */
export const getHotspots = (opts = {}) =>
  apiGet('/hotspots', { ttlMs: 0, ...opts })

/** GET /api/health?aqi= — health recommendation for a value */
export const getHealth = (aqi) => apiGet(`/health?aqi=${aqi}`, { ttlMs: 5 * 60 * 1000 })

/** GET /api/map-data — lightweight payload for the global map */
export const getMapData = (opts = {}) =>
  apiGet('/map-data', { ttlMs: 0, ...opts })

/** GET /api/status — system diagnostics */
export const getStatus = (opts = {}) =>
  apiGet('/status', { ttlMs: 30_000, ...opts })
