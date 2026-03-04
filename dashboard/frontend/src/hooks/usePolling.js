import { useState, useEffect, useCallback, useRef } from 'react'
import { API_BASE } from '../utils/constants'

export function usePolling(path, intervalMs = 10000) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}${path}`)
      const json = await res.json()
      setData(json)
      setError(null)
    } catch (e) {
      setError(e.message)
    }
  }, [path])

  useEffect(() => {
    fetchData()
    intervalRef.current = setInterval(fetchData, intervalMs)
    return () => clearInterval(intervalRef.current)
  }, [fetchData, intervalMs])

  return { data, error, refresh: fetchData }
}
