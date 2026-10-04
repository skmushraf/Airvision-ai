import { useEffect, useState } from 'react'

/**
 * Returns the input value, updated only after `delay` ms of quiet.
 * Dependencies are compared by *serialized value*, not reference, so inline
 * arrays/objects (e.g. `[city]`) do not retrigger on every render.
 */
export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value)
  const serialized = JSON.stringify(value ?? null)

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [serialized, delay])

  return debounced
}
