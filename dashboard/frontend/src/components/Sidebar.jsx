import { AGENTS } from '../utils/constants'
import { usePolling } from '../hooks/usePolling'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import AgentActivityFeed from './AgentActivityFeed'

const statusDot = {
  idle: 'bg-green-400',
  working: 'bg-yellow-400 animate-pulse',
  waiting: 'bg-orange-400',
  error: 'bg-red-500',
}

const statusLabel = { idle: 'Idle', working: 'Working', waiting: 'Waiting for approval', error: 'Error' }

export default function Sidebar() {
  const { data: statuses } = usePolling('/agents/status', 10000)
  const agentStatuses = statuses || []

  return (
    <aside className="w-64 bg-surface-50 border-r flex flex-col shrink-0 overflow-hidden">
      <div className="p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Agents</h2>
        <div className="space-y-2">
          {Object.entries(AGENTS).map(([key, agent]) => {
            const live = agentStatuses.find(s => s.name === key)
            const st = live?.status || 'idle'
            return (
              <div key={key} className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg hover:bg-accent transition-colors">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className={`w-2 h-2 rounded-full shrink-0 cursor-default ${statusDot[st] || statusDot.idle}`} />
                  </TooltipTrigger>
                  <TooltipContent side="right">{statusLabel[st] || 'Idle'}</TooltipContent>
                </Tooltip>
                <span className="text-sm font-semibold w-5 text-center" style={{ color: agent.color }}>{agent.name.charAt(0)}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate" style={{ color: agent.color }}>{agent.name}</p>
                  {live?.current_task && (
                    <p className="text-xs text-muted-foreground truncate">{live.current_task}</p>
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
