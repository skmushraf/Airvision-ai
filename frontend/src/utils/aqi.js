/**
 * AirVision AI — AQI helpers shared across the frontend
 * Mirrors backend/services/aqi.py (CPCB categories + colors).
 */

export const AQI_CATEGORIES = [
  { category: 'Good', min: 0, max: 50, color: '#22c55e', ordinal: 1 },
  { category: 'Satisfactory', min: 51, max: 100, color: '#a3e635', ordinal: 2 },
  { category: 'Moderate', min: 101, max: 200, color: '#f97316', ordinal: 3 },
  { category: 'Poor', min: 201, max: 300, color: '#ef4444', ordinal: 4 },
  { category: 'Very Poor', min: 301, max: 400, color: '#b91c1c', ordinal: 5 },
  { category: 'Severe', min: 401, max: 500, color: '#a855f7', ordinal: 6 },
]

export function aqiCategory(aqi) {
  if (aqi == null || Number.isNaN(aqi)) return 'Unknown'
  if (aqi <= 50) return 'Good'
  if (aqi <= 100) return 'Satisfactory'
  if (aqi <= 200) return 'Moderate'
  if (aqi <= 300) return 'Poor'
  if (aqi <= 400) return 'Very Poor'
  return 'Severe'
}

export function aqiColor(aqi) {
  if (aqi == null || Number.isNaN(aqi)) return '#64748b'
  return AQI_CATEGORIES.find((c) => c.category === aqiCategory(aqi))?.color || '#64748b'
}

export function aqiCategoryInfo(aqi) {
  if (aqi == null || Number.isNaN(aqi)) {
    return { category: 'Unknown', min: 0, max: 500, color: '#64748b', ordinal: 0 }
  }
  const cat = aqiCategory(aqi)
  return AQI_CATEGORIES.find((c) => c.category === cat) || AQI_CATEGORIES[2]
}

/** 0-1 progress used by the AQI gauge (500 = max scale). */
export function aqiProgress(aqi) {
  if (aqi == null || Number.isNaN(aqi)) return 0
  return Math.min(1, Math.max(0, aqi / 500))
}

/** Marker color for map circles (per requirement). */
export function markerColor(aqi) {
  return aqiColor(aqi)
}

/** Human label for pollutant keys from the API. */
export const POLLUTANT_LABELS = {
  pm2_5: 'PM2.5',
  pm10: 'PM10',
  co: 'CO',
  no2: 'NO₂',
  so2: 'SO₂',
  o3: 'O₃',
  nh3: 'NH₃',
  no: 'NO',
  nox: 'NOx',
}

export const POLLUTANT_UNITS = {
  pm2_5: 'µg/m³',
  pm10: 'µg/m³',
  co: 'µg/m³',
  no2: 'µg/m³',
  so2: 'µg/m³',
  o3: 'µg/m³',
  nh3: 'µg/m³',
}
