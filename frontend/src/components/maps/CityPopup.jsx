/**
 * AirVision AI — city marker popup content
 * Shows AQI, pollutants, weather, prediction, health advice and timestamp.
 */

import { POLLUTANT_LABELS } from '../../utils/aqi'
import { formatDateTime, round1 } from '../../utils/format'

function Meta({ label, value, strong = false }) {
  return (
    <div className="flex items-center justify-between gap-6">
      <span className="text-slate-400">{label}</span>
      <span className={`${strong ? 'font-bold text-white' : 'font-medium text-slate-200'}`}>
        {value ?? '—'}
      </span>
    </div>
  )
}

/** Provenance chip: CPCB (official Indian monitors) vs OpenWeather. */
function SourceChip({ city }) {
  const isCpcb = city.source === 'cpcb'
  const label = isCpcb ? 'CPCB' : city.source === 'demo' ? 'Demo' : 'OpenWeather'
  const tone = isCpcb
    ? 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30'
    : city.source === 'demo'
      ? 'bg-violet-500/15 text-violet-300 ring-violet-500/30'
      : 'bg-sky-500/15 text-sky-300 ring-sky-500/30'
  return (
    <span className={`rounded-md px-1.5 py-0.5 text-[10px] font-bold ring-1 ${tone}`}>
      {label}
      {isCpcb && city.station_count ? ` · ${city.station_count} stn` : ''}
    </span>
  )
}

export default function CityPopup({ city }) {
  const p = city.pollutants || {}
  const w = city.weather || {}
  const missing = city.aqi == null

  return (
    <div className="w-64 text-xs">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-sm font-extrabold text-white">{city.name}</p>
          <p className="text-[11px] text-slate-400">{city.country}</p>
        </div>
        {!missing && (
          <span
            className="rounded-lg px-2.5 py-1 text-sm font-extrabold"
            style={{ background: `${city.color}22`, color: city.color }}
          >
            {city.aqi}
          </span>
        )}
      </div>

      {missing ? (
        <p className="rounded-lg bg-slate-800 p-2 text-[11px] text-amber-300">
          Live data unavailable{city.api_error ? ` — ${city.api_error}` : ''}
        </p>
      ) : (
        <>
          <div className="mb-2 rounded-lg px-2.5 py-1.5" style={{ background: `${city.color}18` }}>
            <p className="font-bold" style={{ color: city.color }}>
              {city.category} AQI
            </p>
            <p className="text-[11px] text-slate-300">
              Predicted: <b>{city.predicted_aqi ?? '—'}</b>
            </p>
          </div>

          <div className="space-y-1">
            <Meta label="PM2.5" value={round1(p.pm2_5)} />
            <Meta label="PM10" value={round1(p.pm10)} />
            <Meta label="CO" value={round1(p.co)} />
            <Meta label="NO₂" value={round1(p.no2)} />
            <Meta label="SO₂" value={round1(p.so2)} />
            <Meta label="O₃" value={round1(p.o3)} />
          </div>

          <div className="my-2 h-px bg-slate-700" />

          <div className="space-y-1">
            <Meta label="Temperature" value={`${round1(w.temp)}°C`} />
            <Meta label="Humidity" value={`${round1(w.humidity)}%`} />
            <Meta label="Wind" value={`${round1(w.wind_speed)} m/s`} />
            <Meta label="Pressure" value={`${round1(w.pressure)} hPa`} />
          </div>

          {city.health_recommendation && (
            <div className="mt-2 rounded-lg bg-slate-800/80 p-2 text-[11px] text-slate-300">
              <span className="text-slate-400">Health: </span>
              {city.health_recommendation}
            </div>
          )}
        </>
      )}

      {city.cpcb_proxy && city.cpcb_proxy_note && (
        <p className="mt-2 rounded-lg bg-amber-500/10 p-1.5 text-[10px] text-amber-300">
          {city.cpcb_proxy_note}
        </p>
      )}

      <div className="mt-2 flex items-center justify-between gap-2">
        <p className="text-[10px] text-slate-500">
          Updated {formatDateTime(city.last_updated * 1000)}
        </p>
        <SourceChip city={city} />
      </div>
      {city.aqi_standard && (
        <p className="mt-0.5 text-[10px] text-slate-500">Scale: {city.aqi_standard}</p>
      )}
    </div>
  )
}
