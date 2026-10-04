/**
 * AirVision AI — top bar: menu toggle, global search, theme switch
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import MenuIcon from '@mui/icons-material/Menu'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import LightModeIcon from '@mui/icons-material/LightMode'
import SearchBar from '../SearchBar'
import { useTheme } from '../../context/ThemeContext'

export default function Topbar({ onMenuClick }) {
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [mobileSearch, setMobileSearch] = useState(false)

  const goToCity = (id) => navigate(`/forecast?city=${id}`)

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/80">
      <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden dark:text-slate-400 dark:hover:bg-slate-900"
          aria-label="Open menu"
        >
          <MenuIcon />
        </button>

        <div className="hidden flex-1 md:block">
          <SearchBar onSelect={goToCity} />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 md:hidden dark:text-slate-400 dark:hover:bg-slate-900"
            onClick={() => setMobileSearch((v) => !v)}
            aria-label="Search"
          >
            <MenuIcon style={{ transform: 'scaleX(-1)' }} />
          </button>

          <button
            type="button"
            onClick={toggleTheme}
            className="rounded-xl border border-slate-200 p-2 text-slate-500 transition-colors hover:bg-slate-100 dark:border-slate-800 dark:text-amber-300 dark:hover:bg-slate-900"
            aria-label="Toggle theme"
            title="Toggle dark / light mode"
          >
            {theme === 'dark' ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {mobileSearch && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-200 px-4 py-3 md:hidden dark:border-slate-800"
          >
            <SearchBar autoFocus onSelect={goToCity} />
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
