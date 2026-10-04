/**
 * AirVision AI — application shell
 * Responsive sidebar + topbar around the routed page content.
 */

import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import WarningBanner from '../WarningBanner'
import StatusBar from '../StatusBar'
import { useLiveData } from '../../context/LiveDataContext'
import { APP } from '../../config'

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { status, source, lastUpdated, error, isStale, refresh, apiHealth, demoMode, cpcbCount } = useLiveData()

  const showWarning =
    status === 'error' ||
    status === 'degraded' ||
    (status === 'ok' && isStale())

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="lg:pl-64">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />

        <main className="mx-auto max-w-[1500px] space-y-4 p-4 sm:p-6">
          {/* DEMO MODE banner (clearly labelled — never mistaken for live) */}
          {demoMode && (
            <div className="flex items-start gap-3 rounded-xl border border-violet-500/40 bg-violet-500/10 px-4 py-3 text-sm text-violet-800 dark:text-violet-300">
              <span className="text-lg leading-none">🧪</span>
              <div className="min-w-0 flex-1">
                <p className="font-semibold">
                  DEMO DATA MODE — readings are simulated (ML-grounded), not live
                </p>
                <p className="mt-0.5 text-xs opacity-80">
                  The OpenWeather API key on the server is invalid or not yet activated. Every
                  value is clearly tagged as demo. To go live: put a valid key in{' '}
                  <code className="rounded bg-violet-500/15 px-1 font-mono text-[11px]">backend/.env</code>,
                  set <code className="rounded bg-violet-500/15 px-1 font-mono text-[11px]">ENABLE_DEMO_DATA=0</code>,
                  and restart the server.
                </p>
              </div>
            </div>
          )}

          {/* Global warning area (non-blocking) */}
          {showWarning && (
            <WarningBanner
              variant={status === 'error' ? 'error' : 'warning'}
              message={
                apiHealth && apiHealth.api_key_configured && apiHealth.api_key_valid === false
                  ? 'The OpenWeather API key on the server is invalid or unconfigured — live data cannot be fetched. Add a valid key to backend/.env and restart the server.'
                  : error || 'Live data is temporarily unavailable.'
              }
              onRefresh={refresh}
            />
          )}

          <div className="flex flex-wrap items-center justify-between gap-2">
            <h1 className="text-lg font-bold text-slate-900 dark:text-white">
              {APP.name} <span className="font-normal text-slate-400">· {APP.tagline}</span>
            </h1>
            <StatusBar status={status} source={source} lastUpdated={lastUpdated} demo={demoMode} cpcbCount={cpcbCount} />
          </div>

          <Outlet />
        </main>

        <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400 dark:border-slate-800 dark:text-slate-600">
          AirVision AI v{APP.version} · Real-time data © OpenWeather · ML model trained on Air
          Quality Data in India (2015–2020) · Built for the final-year engineering project.
        </footer>
      </div>
    </div>
  )
}
