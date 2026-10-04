/**
 * AirVision AI — navigation sidebar
 */

import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import CloseIcon from '@mui/icons-material/Close'
import DashboardIcon from '@mui/icons-material/Dashboard'
import PublicIcon from '@mui/icons-material/Public'
import WbSunnyIcon from '@mui/icons-material/WbSunny'
import CompareArrowsIcon from '@mui/icons-material/CompareArrows'
import FlagIcon from '@mui/icons-material/Flag'
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment'
import InfoIcon from '@mui/icons-material/Info'

const NAV = [
  { to: '/', label: 'Dashboard', icon: DashboardIcon, end: true },
  { to: '/map', label: 'Live Global Map', icon: PublicIcon },
  { to: '/forecast', label: 'Weather Forecast', icon: WbSunnyIcon },
  { to: '/compare', label: 'City Comparison', icon: CompareArrowsIcon },
  { to: '/countries', label: 'Country Dashboard', icon: FlagIcon },
  { to: '/hotspots', label: 'Pollution Hotspots', icon: LocalFireDepartmentIcon },
  { to: '/about', label: 'About & Docs', icon: InfoIcon },
]

function Logo() {
  return (
    <div className="flex items-center gap-3 px-5 py-5">
      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-cyan-400 shadow-glow">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M12 2C12 2 5 10 5 15a7 7 0 0014 0c0-5-7-13-7-13z" fill="white" opacity="0.95" />
          <circle cx="12" cy="15" r="3" fill="#1d63f0" />
        </svg>
      </div>
      <div>
        <p className="text-base font-extrabold leading-tight text-white">
          AirVision <span className="text-cyan-300">AI</span>
        </p>
        <p className="text-[10px] font-medium uppercase tracking-widest text-slate-400">
          Air Quality Intelligence
        </p>
      </div>
    </div>
  )
}

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-sm lg:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800 bg-slate-950 transition-transform duration-300 lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between">
          <Logo />
          <button className="mr-3 text-slate-400 lg:hidden" onClick={onClose} aria-label="Close menu">
            <CloseIcon />
          </button>
        </div>

        <nav className="mt-2 flex-1 space-y-1 overflow-y-auto px-3">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-600/20 text-brand-200'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-white'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.span
                      layoutId="sidebar-active"
                      className="absolute left-0 top-1/2 h-6 w-1 -translate-y-1/2 rounded-r-full bg-cyan-400"
                    />
                  )}
                  <Icon fontSize="small" className={isActive ? 'text-cyan-300' : ''} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mx-4 mb-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
          <p className="mb-1 text-xs font-semibold text-white">System status</p>
          <p className="text-[11px] leading-relaxed text-slate-400">
            58 cities · 30 countries · 7 continents monitored in real time.
          </p>
          <div className="mt-2 flex items-center gap-1.5 text-[11px] text-emerald-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            ML pipeline active
          </div>
        </div>
      </aside>
    </>
  )
}
