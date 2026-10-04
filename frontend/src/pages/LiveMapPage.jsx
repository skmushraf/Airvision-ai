/**
 * AirVision AI — Live Global Map
 * Interactive Leaflet map with live AQI markers, filters and search.
 */

import { useMemo, useState } from 'react'
import GlobalMarkerMap from '../components/maps/GlobalMarkerMap'
import MapControls from '../components/maps/MapControls'
import { useLiveData } from '../context/LiveDataContext'
import { useTheme } from '../context/ThemeContext'
import { KpiSkeleton } from '../components/LoadingSkeleton'
import { aqiCategory } from '../utils/aqi'

export default function LiveMapPage() {
  const { cities, loading } = useLiveData()
  const { theme } = useTheme()
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    pollutedOnly: false,
    cleanOnly: false,
  })

  const markers = useMemo(() => {
    const q = filters.search.trim().toLowerCase()
    return cities
      .filter((c) => {
        if (q && !c.name.toLowerCase().includes(q) && !c.country.toLowerCase().includes(q)) {
          return false
        }
        if (filters.category !== 'all' && c.aqi_category !== filters.category) return false
        if (filters.pollutedOnly && !(c.aqi != null && c.aqi > 200)) return false
        if (filters.cleanOnly && !(c.aqi != null && c.aqi <= 100)) return false
        return true
      })
      .map((c) => ({
        id: c.id,
        name: c.name,
        country: c.country,
        country_code: c.country_code,
        continent: c.continent,
        lat: c.lat,
        lon: c.lon,
        aqi: c.aqi,
        category: c.aqi_category,
        color: c.aqi_color,
        pollutants: c.pollutants,
        weather: c.weather,
        predicted_aqi: c.predicted_aqi,
        health_recommendation: c.health?.recommendation,
        last_updated: c.last_updated,
        api_error: c.api_error,
      }))
  }, [cities, filters])

  if (loading) {
    return (
      <div className="grid gap-4">
        <KpiSkeleton />
        <div className="card h-[72vh] animate-pulse" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <MapControls
        filters={filters}
        onChange={setFilters}
        counts={{ total: cities.length, shown: markers.length }}
      />
      <GlobalMarkerMap markers={markers} theme={theme} />
      <p className="text-center text-xs text-slate-400">
        Marker colour updates automatically whenever live AQI changes (green → light green → orange →
        red → dark red → purple). Click any marker for full air-quality & weather details.
      </p>
    </div>
  )
}
