import { useState, useEffect, useCallback } from 'react'
import { TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { API_BASE } from '../utils/constants'

export default function Header() {
  const [paused, setPaused] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchPaused = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/agents/paused`)
      const data = await res.json()
      setPaused(data.paused)
    } catch {}
  }, [])

  useEffect(() => {
    fetchPaused()
    const interval = setInterval(fetchPaused, 5000)
    return () => clearInterval(interval)
  }, [fetchPaused])

  const togglePause = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/agents/paused`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paused: !paused }),
      })
      const data = await res.json()
      setPaused(data.paused)
    } catch {}
    setLoading(false)
  }

  return (
    <header className="bg-white border-b border-border px-5 py-2.5 flex items-center justify-between shrink-0">
      <span className="text-base font-semibold tracking-tight text-foreground">
        Ecultify Virtual Team
      </span>
      <TabsList className="bg-surface-50">
        <TabsTrigger value="kanban">Board</TabsTrigger>
        <TabsTrigger value="costs">Costs</TabsTrigger>
        <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
      </TabsList>
      <Button
        variant={paused ? 'default' : 'destructive'}
        size="sm"
        onClick={togglePause}
        disabled={loading}
        className="min-w-[120px] text-xs font-medium"
      >
        {loading ? '...' : paused ? 'Resume Agents' : 'Stop All Agents'}
      </Button>
    </header>
  )
}
