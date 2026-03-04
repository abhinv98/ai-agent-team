import { useState, useEffect } from 'react'
import { AGENTS } from '../utils/constants'
import { useRealtime } from '../hooks/useRealtime'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import AgentActivityFeed from './AgentActivityFeed'
import { API_BASE } from '../utils/constants'

const statusDot = {
  idle: 'bg-emerald-500',
  working: 'bg-amber-500 animate-pulse',
  waiting: 'bg-orange-500',
  error: 'bg-red-500',
  paused: 'bg-gray-400',
}

const statusLabel = {
  idle: 'Idle',
  working: 'Working',
  waiting: 'Waiting for approval',
  error: 'Error',
  paused: 'Paused',
}

export default function Sidebar() {
  const { data: statuses } = useRealtime('/agents/status', 'agent_activity', 10000)
  const agentStatuses = statuses || []
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API_BASE}/agents/paused`)
        const data = await res.json()
        setPaused(data.paused)
      } catch {}
    }
    check()
    const interval = setInterval(check, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside className="w-56 bg-white border-r border-border flex flex-col shrink-0 overflow-hidden">
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Agents</h2>
          {paused && (
            <span className="text-[9px] font-semibold uppercase tracking-wide text-red-500 bg-red-50 px-1.5 py-0.5 rounded">
              Paused
            </span>
          )}
        </div>
        <div className="space-y-0.5">
          {Object.entries(AGENTS).map(([key, agent]) => {
            const live = agentStatuses.find(s => s.name === key)
            const st = paused ? 'paused' : (live?.status || 'idle')
            return (
              <div key={key} className={`flex items-center gap-2 px-2 py-1.5 rounded hover:bg-accent/50 transition-colors ${paused ? 'opacity-50' : ''}`}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 cursor-default ${statusDot[st] || statusDot.idle}`} />
                  </TooltipTrigger>
                  <TooltipContent side="right">{statusLabel[st] || 'Idle'}</TooltipContent>
                </Tooltip>
                <span className="text-xs font-semibold w-4 text-center" style={{ color: agent.color }}>{agent.name.charAt(0)}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-foreground truncate">{agent.name}</p>
                  {!paused && live?.current_task && (
                    <p className="text-[10px] text-muted-foreground truncate">{live.current_task}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
      <Separator />
      <ScrollArea className="flex-1">
        <AgentActivityFeed />
      </ScrollArea>
    </aside>
  )
}
