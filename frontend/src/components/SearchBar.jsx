/**
 * AirVision AI — city search with autocomplete
 * Queries /api/cities/autocomplete (debounced); keyboard navigable.
 */

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import SearchIcon from '@mui/icons-material/Search'
import LocationCityIcon from '@mui/icons-material/LocationCity'
import { autocompleteCities } from '../api/endpoints'
import { useDebounce } from '../hooks/useDebounce'

export default function SearchBar({ onSelect, autoFocus = false, placeholder = 'Search city or country…' }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const debounced = useDebounce(query, 250)
  const boxRef = useRef(null)

  useEffect(() => {
    let active = true
    if (debounced.trim().length < 2) {
      setResults([])
      setLoading(false)
      return undefined
    }
    setLoading(true)
    autocompleteCities(debounced)
      .then((d) => {
        if (active) {
          setResults(d.results || [])
          setOpen(true)
        }
      })
      .catch(() => active && setResults([]))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [debounced])

  useEffect(() => {
    const onDocClick = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const pick = (item) => {
    setQuery('')
    setOpen(false)
    onSelect?.(item)
  }

  return (
    <div ref={boxRef} className="relative max-w-xl">
      <div className="relative">
        <SearchIcon
          fontSize="small"
          className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          autoFocus={autoFocus}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setOpen(true)
          }}
          onFocus={() => query.trim().length >= 2 && setOpen(true)}
          placeholder={placeholder}
          className="input pl-10"
        />
        {loading && (
          <span className="absolute right-3.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 animate-spin rounded-full border-2 border-slate-300 border-t-brand-500 dark:border-slate-600 dark:border-t-brand-400" />
        )}
      </div>

      {open && results.length > 0 && (
        <motion.ul
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute z-50 mt-2 max-h-80 w-full overflow-y-auto rounded-2xl border border-slate-200 bg-white p-1.5 shadow-card-lg dark:border-slate-700 dark:bg-slate-900"
        >
          {results.map((r) => (
            <li key={r.id}>
              <button
                type="button"
                onClick={() => pick(r)}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <LocationCityIcon fontSize="small" className="text-slate-400" />
                <span className="font-medium text-slate-800 dark:text-slate-100">{r.name}</span>
                <span className="text-xs text-slate-400">
                  {r.country} · {r.cc}
                </span>
              </button>
            </li>
          ))}
        </motion.ul>
      )}
    </div>
  )
}
