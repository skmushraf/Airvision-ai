/**
 * AirVision AI — weather card (current conditions)
 */

import DeviceThermostatIcon from '@mui/icons-material/DeviceThermostat'
import WaterDropIcon from '@mui/icons-material/WaterDrop'
import AirIcon from '@mui/icons-material/Air'
import CompressIcon from '@mui/icons-material/Compress'
import VisibilityIcon from '@mui/icons-material/Visibility'
import CloudIcon from '@mui/icons-material/Cloud'
import UmbrellaIcon from '@mui/icons-material/Umbrella'
import WbTwilightIcon from '@mui/icons-material/WbTwilight'
import { formatTime } from '../../utils/format'

function Row({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 rounded-xl bg-slate-100/80 px-3 py-2.5 dark:bg-slate-800/60">
      <Icon fontSize="small" className="shrink-0 text-brand-500" />
      <div className="min-w-0 flex-1">
        <p className="stat-label">{label}</p>
        <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-100">{value}</p>
      </div>
    </div>
  )
}

export default function WeatherCard({ weather, sunrise, sunset, timezoneOffset = 0 }) {
  if (!weather) {
    return (
      <div className="card flex h-full items-center justify-center p-6 text-sm text-slate-400">
        Weather data unavailable
      </div>
    )
  }

  const description = weather.description ? (
    <span className="capitalize">{weather.description}</span>
  ) : null

  return (
    <div className="card h-full p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="section-title">Current Weather</p>
        <DeviceThermostatIcon className="text-brand-500" />
      </div>

      <div className="mb-4 flex items-center gap-3">
        <span className="text-4xl font-extrabold text-slate-900 dark:text-white">
          {Math.round(weather.temp ?? 0)}°
        </span>
        <div className="text-sm text-slate-500 dark:text-slate-400">
          <p>Feels like {Math.round(weather.feels_like ?? 0)}°C</p>
          {description && <p className="capitalize">{description}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2.5">
        <Row icon={WaterDropIcon} label="Humidity" value={`${weather.humidity ?? '—'}%`} />
        <Row icon={AirIcon} label="Wind" value={`${weather.wind_speed ?? '—'} m/s`} />
        <Row icon={CompressIcon} label="Pressure" value={`${weather.pressure ?? '—'} hPa`} />
        <Row icon={VisibilityIcon} label="Visibility" value={weather.visibility ? `${(weather.visibility / 1000).toFixed(1)} km` : '—'} />
        <Row icon={CloudIcon} label="Clouds" value={`${weather.clouds ?? '—'}%`} />
        <Row icon={UmbrellaIcon} label="Rain (1h)" value={weather.rain_1h ? `${weather.rain_1h} mm` : '0 mm'} />
        <Row icon={WbTwilightIcon} label="Sunrise" value={formatTime(sunrise, timezoneOffset)} />
        <Row icon={WbTwilightIcon} label="Sunset" value={formatTime(sunset, timezoneOffset)} />
      </div>
    </div>
  )
}
