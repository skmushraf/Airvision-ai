/**
 * AirVision AI — Weather Forecast
 * AQI forecast (Now/1h/6h/12h/24h), hourly & daily weather, trends and rain.
 */

import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useFetch } from '../hooks/useFetch'
import { getForecast, getCities } from '../api/endpoints'
import { ChartSkeleton } from '../components/LoadingSkeleton'
import ChartCard from '../components/charts/ChartCard'
import LineTrendChart from '../components/charts/LineTrendChart'
import BarChart from '../components/charts/BarChart'
import { aqiColor } from '../utils/aqi'
import { MONTH_NAMES } from '../utils/format'

function AqiForecastTile({ point, active }) {
  const color = aqiColor(point.aqi)
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card card-hover p-4 text-center ${active ? 'ring-2 ring-brand-500/60' : ''}`}
    >
      <p className="stat-label">{point.label}</p>
      <p className="mt-2 text-2xl font-extrabold" style={{ color: color != '#64748b' ? color : undefined }}>
        {point.aqi ?? '—'}
      </p>
      <p className="mt-1 text-xs font-medium" style={{ color }}>
        {point.category || '—'}
      </p>
      <p className="mt-1 text-[10px] text-slate-400">{point.time?.slice(5, 16)}</p>
    </motion.div>
  )
}

export default function ForecastPage() {
  const [params] = useSearchParams()
  const [city, setCity] = useState(params.get('city') || 'delhi')

  const { data: citiesData } = useFetch(() => getCities(), [], { skip: false })
  const { data, loading, error } = useFetch(() => getForecast(city), [city])

  const cityList = useMemo(
    () => (citiesData?.cities || []).map((c) => ({ id: c.id, name: c.name, country: c.country })),
    [citiesData],
  )

  const hourly = (data?.hourly || []).map((h, i) => ({
    ...h,
    key: i,
    timeLabel: h.time ? `${Number(h.time.slice(11, 13))}:00` : `t+${i * 3}h`,
    dayLabel: h.time ? `${MONTH_NAMES[Number(h.time.slice(5, 7)) - 1]} ${Number(h.time.slice(8, 10))}` : '',
  }))

  const tempData = hourly.map((h) => ({ name: h.timeLabel, temp: h.temp, humidity: h.humidity, wind: h.wind_speed, rain: h.rain_prob }))
  const aqiSeries = hourly.map((h) => ({ name: h.timeLabel, aqi: h.aqi }))
  const rainData = hourly.map((h) => ({ name: h.timeLabel, rain: h.rain_prob }))

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <select className="input !w-72" value={city} onChange={(e) => setCity(e.target.value)}>
          {cityList.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}, {c.country}
            </option>
          ))}
        </select>
        {data?.city && (
          <span className="text-sm text-slate-400">
            Forecast for <b className="text-slate-700 dark:text-slate-200">{data.city.name}</b> · updated {data.last_updated}
          </span>
        )}
      </div>

      {error && (
        <div className="card border-red-500/40 p-4 text-sm text-red-500">
          {error} — live forecast data unavailable. Add a valid OpenWeather API key to backend/.env.
        </div>
      )}

      {/* AQI forecast tiles */}
      <div>
        <p className="section-title mb-3">ML AQI Forecast</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {(data?.aqi_forecast || []).map((p, i) => (
            <AqiForecastTile key={p.label} point={p} active={i === 0} />
          ))}
        </div>
      </div>

      {/* Hourly + daily */}
      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Hourly Temperature Trend" subtitle="Next 5 days · °C" className={loading ? '' : ''}>
          {loading ? (
            <ChartSkeleton height={240} />
          ) : (
            <LineTrendChart data={tempData} xKey="name" series={[{ key: 'temp', name: 'Temperature' }]}
              colors={['#f59e0b']} unit="°C" height={240} />
          )}
        </ChartCard>

        <ChartCard title="Rain Probability" subtitle="Chance of precipitation · %">
          {loading ? (
            <ChartSkeleton height={240} />
          ) : (
            <BarChart data={rainData} xKey="name" series={[{ key: 'rain', name: 'Rain %' }]}
              color="#0ea5e9" height={240} unit="%" />
          )}
        </ChartCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Predicted AQI Trend" subtitle="ML forecast on adjusted pollutants">
          {loading ? (
            <ChartSkeleton height={240} />
          ) : (
            <LineTrendChart data={aqiSeries} xKey="name" series={[{ key: 'aqi', name: 'AQI' }]}
              colors={['#3384fb']} height={240} />
          )}
        </ChartCard>

        <ChartCard title="Humidity & Wind" subtitle="Relative humidity (%) and wind (m/s)">
          {loading ? (
            <ChartSkeleton height={240} />
          ) : (
            <LineTrendChart data={tempData} xKey="name"
              series={[{ key: 'humidity', name: 'Humidity %' }, { key: 'wind', name: 'Wind m/s' }]}
              colors={['#0ea5e9', '#10b981']} height={240} />
          )}
        </ChartCard>
      </div>

      {/* Daily cards */}
      <div>
        <p className="section-title mb-3">Daily Forecast</p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {(data?.daily || []).map((d, i) => (
            <motion.div
              key={d.date}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="card card-hover p-4"
            >
              <div className="mb-2 flex items-center justify-between">
                <p className="text-sm font-bold text-slate-800 dark:text-slate-100">
                  {d.date ? `${MONTH_NAMES[Number(d.date.slice(5, 7)) - 1]} ${Number(d.date.slice(8, 10))}` : '—'}
                </p>
                <span className="chip" style={{ background: `${aqiColor(d.aqi)}1c`, color: aqiColor(d.aqi) }}>
                  AQI {d.aqi ?? '—'}
                </span>
              </div>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {d.temp_min}° <span className="text-sm text-slate-400">/ {d.temp_max}°</span>
              </p>
              <p className="mt-1 text-xs capitalize text-slate-500 dark:text-slate-400">{d.description || '—'}</p>
              <div className="mt-3 space-y-1 text-xs text-slate-500 dark:text-slate-400">
                <p>💧 Humidity {d.humidity ?? '—'}%</p>
                <p>💨 Wind {d.wind_speed ?? '—'} m/s</p>
                <p>🌧 Rain {d.rain_prob ?? '—'}%</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
