/**
 * AirVision AI — Country Dashboard
 * Country list with average AQI/temperature, plus a detail panel with
 * city table and charts for the selected country.
 */

import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useFetch } from '../hooks/useFetch'
import { getCountries } from '../api/endpoints'
import { ChartSkeleton } from '../components/LoadingSkeleton'
import ChartCard from '../components/charts/ChartCard'
import BarChart from '../components/charts/BarChart'
import { aqiColor, aqiCategory } from '../utils/aqi'

export default function CountriesPage() {
  const [selected, setSelected] = useState('India')
  const { data, loading, error } = useFetch(() => getCountries(), [])

  // Show every country (AQI may be null when live data is unavailable).
  const countries = useMemo(() => data?.countries || [], [data])
  const detail = useMemo(
    () => (data?.countries || []).find((c) => c.name === selected) || null,
    [data, selected],
  )

  const rankingData = useMemo(
    () =>
      countries
        .filter((c) => c.average_aqi != null)
        .map((c) => ({ name: c.name, aqi: c.average_aqi }))
        .slice(0, 15),
    [countries],
  )

  const cityBars = useMemo(
    () =>
      (detail?.cities || [])
        .filter((c) => c.aqi != null)
        .sort((a, b) => b.aqi - a.aqi)
        .map((c) => ({ name: c.name, aqi: c.aqi })),
    [detail],
  )

  return (
    <div className="space-y-5">
      {error && <div className="card border-red-500/40 p-4 text-sm text-red-500">{error}</div>}

      <div className="grid gap-4 xl:grid-cols-3">
        {/* Country list */}
        <div className="card overflow-hidden xl:col-span-1">
          <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">
              Countries by Average AQI
            </h3>
            <p className="text-xs text-slate-400">Live readings · tap to explore</p>
          </div>
          <div className="max-h-[560px] overflow-y-auto">
            {loading ? (
              <ChartSkeleton height={400} />
            ) : (
              countries.map((c) => (
                <button
                  key={c.name}
                  type="button"
                  onClick={() => setSelected(c.name)}
                  className={`flex w-full items-center justify-between border-b border-slate-100 px-5 py-3 text-left text-sm transition-colors last:border-0 hover:bg-slate-50 dark:border-slate-800/60 dark:hover:bg-slate-800/40 ${
                    selected === c.name ? 'bg-brand-600/10 dark:bg-brand-600/15' : ''
                  }`}
                >
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-100">{c.name}</p>
                    <p className="text-xs text-slate-400">{c.city_count} cities · {c.continent}</p>
                  </div>
                  <span className="font-extrabold" style={{ color: aqiColor(c.average_aqi) }}>
                    {c.average_aqi}
                  </span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Country detail */}
        <div className="space-y-4 xl:col-span-2">
          {detail && (
            <>
              <motion.div
                key={selected}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="card flex flex-wrap items-center justify-between gap-4 p-5"
              >
                <div>
                  <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
                    {detail.name}
                    <span className="ml-2 text-sm font-medium text-slate-400">{detail.cc}</span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    {detail.continent} · {detail.city_count} monitored cities · worst AQI {detail.worst_aqi ?? '—'}
                  </p>
                </div>
                <div className="flex gap-6 text-center">
                  <div>
                    <p className="text-2xl font-extrabold" style={{ color: aqiColor(detail.average_aqi) }}>
                      {detail.average_aqi ?? '—'}
                    </p>
                    <p className="stat-label">Avg AQI</p>
                  </div>
                  <div>
                    <p className="text-2xl font-extrabold text-amber-500">
                      {detail.average_temperature ?? '—'}°
                    </p>
                    <p className="stat-label">Avg Temp (°C)</p>
                  </div>
                </div>
              </motion.div>

              <ChartCard title="City AQI Ranking" subtitle={`Live AQI across ${detail.city_count} cities`}>
                {loading ? (
                  <ChartSkeleton height={240} />
                ) : (
                  <BarChart
                    data={cityBars}
                    xKey="name"
                    series={[{ key: 'aqi', name: 'AQI' }]}
                    colorsByCell={cityBars.map((b) => aqiColor(b.aqi))}
                    height={260}
                  />
                )}
              </ChartCard>

              <div className="card overflow-hidden">
                <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
                  <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">
                    Major Cities — {detail.name}
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-xs uppercase text-slate-400 dark:border-slate-800">
                        <th className="px-5 py-3 font-semibold">City</th>
                        <th className="px-5 py-3 font-semibold">AQI</th>
                        <th className="px-5 py-3 font-semibold">Category</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(detail.cities || []).map((c) => (
                        <tr key={c.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800/60">
                          <td className="px-5 py-2.5 font-semibold text-slate-800 dark:text-slate-100">{c.name}</td>
                          <td className="px-5 py-2.5 font-extrabold" style={{ color: aqiColor(c.aqi) }}>
                            {c.aqi ?? '—'}
                          </td>
                          <td className="px-5 py-2.5">
                            <span className="chip" style={{ background: `${aqiColor(c.aqi)}1c`, color: aqiColor(c.aqi) }}>
                              {c.category || aqiCategory(c.aqi)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {rankingData.length > 0 && (
        <ChartCard title="Global Country Ranking" subtitle="Top 15 by average live AQI">
          <BarChart
            data={rankingData}
            xKey="name"
            series={[{ key: 'aqi', name: 'Avg AQI' }]}
            colorsByCell={rankingData.map((r) => aqiColor(r.aqi))}
            height={320}
          />
        </ChartCard>
      )}
    </div>
  )
}
