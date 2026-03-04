import { useState, useCallback } from 'react'
import { API_BASE } from '../utils/constants'

export function useApi() {
  const [loading, setLoading] = useState(false)

  const get = useCallback(async (path) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}${path}`)
      return await res.json()
    } catch (e) {
      console.error('API GET error:', e)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const patch = useCallback(async (path, data) => {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      return await res.json()
    } catch (e) {
      console.error('API PATCH error:', e)
      return null
    }
  }, [])

  const post = useCallback(async (path, data) => {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      return await res.json()
    } catch (e) {
      console.error('API POST error:', e)
      return null
    }
  }, [])

  return { get, patch, post, loading }
}
