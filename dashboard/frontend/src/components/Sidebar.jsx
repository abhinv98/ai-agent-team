import { AGENTS } from '../utils/constants'
import { useRealtime } from '../hooks/useRealtime'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import AgentActivityFeed from './AgentActivityFeed'

const statusDot = {
  idle: 'bg-emerald-500',
  working: 'bg-amber-500 animate-pulse',
  waiting: 'bg-orange-500',
  error: 'bg-red-500',
}

const statusLabel = { idle: 'Idle', working: 'Working', waiting: 'Waiting for approval', error: 'Error' }

export default function Sidebar() {
  const { data: statuses } = useRealtime('/agents/status', 'agent_activity', 10000)
  const agentStatuses = statuses || []

  return (
    <aside className="w-56 bg-white border-r border-border flex flex-col shrink-0 overflow-hidden">
      <div className="p-3">
        <h2 className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-2">Agents</h2>
        <div className="space-y-0.5">
          {Object.entries(AGENTS).map(([key, agent]) => {
            const live = agentStatuses.find(s => s.name === key)
            const st = live?.status || 'idle'
            return (
              <div key={key} className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-accent/50 transition-colors">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 cursor-default ${statusDot[st] || statusDot.idle}`} />
                  </TooltipTrigger>
                  <TooltipContent side="right">{statusLabel[st] || 'Idle'}</TooltipContent>
                </Tooltip>
                <span className="text-xs font-semibold w-4 text-center" style={{ color: agent.color }}>{agent.name.charAt(0)}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-foreground truncate">{agent.name}</p>
                  {live?.current_task && (
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
