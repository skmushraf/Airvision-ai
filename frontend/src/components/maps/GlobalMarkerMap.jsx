/**
 * AirVision AI — interactive global marker map
 * React Leaflet + OpenStreetMap tiles. Circle markers colored by live AQI
 * (green → light green → orange → red → dark red → purple). Clicking a marker
 * opens a rich popup with AQI, pollutants, weather, prediction and advice.
 */

import { CircleMarker, MapContainer, Popup, TileLayer, Tooltip } from 'react-leaflet'
import { aqiColor } from '../../utils/aqi'
import MapLegend from './MapLegend'
import CityPopup from './CityPopup'

function radiusFor(aqi) {
  if (aqi == null) return 9
  return Math.min(22, 9 + aqi / 28)
}

export default function GlobalMarkerMap({ markers, height = '72vh', center = [20, 20], zoom = 2, theme = 'dark' }) {
  const cartoKey = import.meta.env.VITE_CARTO_API_KEY

const tileUrl =
  theme === 'dark'
    ? `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?key=${cartoKey}`
    : `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?key=${cartoKey}`
  return (
    <div className="relative" style={{ height }}>
      <MapContainer
        center={center}
        zoom={zoom}
        minZoom={2}
        maxZoom={13}
        scrollWheelZoom
        className="h-full w-full"
        zoomControl
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
          url={tileUrl}
          subdomains="abcd"
        />

        {markers.map((m) => {
          const color = m.color || aqiColor(m.aqi)
          const hasAqi = m.aqi != null
          return (
            <CircleMarker
              key={m.id}
              center={[m.lat, m.lon]}
              radius={radiusFor(m.aqi)}
              pathOptions={{
                color: '#ffffff',
                weight: 1.5,
                fillColor: color,
                fillOpacity: hasAqi ? 0.85 : 0.25,
              }}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                <span className="font-semibold">{m.name}</span>
                {hasAqi && <span style={{ color }}> · AQI {m.aqi}</span>}
              </Tooltip>
              <Popup maxWidth={300}>
                <CityPopup city={m} />
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>

      <MapLegend />
    </div>
  )
}
