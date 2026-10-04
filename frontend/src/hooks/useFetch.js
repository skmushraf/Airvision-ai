/**
 * AirVision AI — generic fetch hook
 * Handles loading/error/data state for any API function.
 * Dependencies are serialised so `[city]`-style inline arrays only refetch
 * when their *values* actually change.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { useDebounce } from './useDebounce'

export function useFetch(fetcher, deps = [], { skip = false, delay = 0 } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(!skip)
  const [error, setError] = useState(null)
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const debounced = useDebounce(deps, delay)
  const depsKey = JSON.stringify(debounced ?? null)

  const run = useCallback(async () => {
    if (skip) return
    setLoading(true)
    try {
      const result = await fetcherRef.current()
      setData(result)
      setError(null)
    } catch (e) {
      setError(e?.message || 'Request failed')
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skip, depsKey])

  useEffect(() => {
    run()
  }, [run])

  return { data, loading, error, refetch: run }
}
