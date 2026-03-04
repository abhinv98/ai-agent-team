import { useState, useEffect, useCallback, useRef } from 'react'
import { supabase } from '../lib/supabase'
import { API_BASE } from '../utils/constants'

/**
 * Fetches data from the API and subscribes to Supabase Realtime for
 * instant re-fetches on any row change. Falls back to polling if the
 * Supabase client isn't configured or the subscription fails.
 *
 * @param {string}   apiPath       API endpoint (e.g. '/tasks/board')
 * @param {string|string[]} tables Supabase table(s) to listen to
 * @param {number}   fallbackMs    Polling interval if realtime unavailable
 */
export function useRealtime(apiPath, tables, fallbackMs = 30000) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)
  const channelRef = useRef(null)

  const tableList = Array.isArray(tables) ? tables : [tables]

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}${apiPath}`)
      const json = await res.json()
      setData(json)
      setError(null)
    } catch (e) {
      setError(e.message)
    }
  }, [apiPath])

  useEffect(() => {
    fetchData()

    let realtimeActive = false

    if (supabase) {
      try {
        const channel = supabase.channel(`rt-${apiPath}`)

        tableList.forEach(table => {
          channel.on(
            'postgres_changes',
            { event: '*', schema: 'public', table },
            () => fetchData()
          )
        })

        channel.subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            realtimeActive = true
            if (intervalRef.current) {
              clearInterval(intervalRef.current)
              intervalRef.current = null
            }
            intervalRef.current = setInterval(fetchData, 60000)
          }
        })

        channelRef.current = channel
      } catch {
        realtimeActive = false
      }
    }

    if (!realtimeActive) {
      intervalRef.current = setInterval(fetchData, fallbackMs)
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
      if (channelRef.current && supabase) {
        supabase.removeChannel(channelRef.current)
        channelRef.current = null
      }
    }
  }, [fetchData, fallbackMs, tableList.join(',')])

  return { data, error, refresh: fetchData }
}
