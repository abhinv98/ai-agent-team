import { AGENTS } from '../utils/constants'
import { usePolling } from '../hooks/usePolling'

export default function AgentActivityFeed() {
  const { data } = usePolling('/agents/activity?limit=15', 10000)
  const activities = data || []

  return (
    <div className="p-4">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Live Activity</h2>
      <div className="space-y-2">
        {activities.length === 0 && (
          <p className="text-xs text-muted-foreground">No activity yet</p>
        )}
        {activities.map((a, i) => {
          const agent = AGENTS[a.agent_name] || { color: '#888', name: a.agent_name }
          const time = a.created_at ? new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''
          return (
            <div key={a.id || i} className="flex gap-2 text-xs">
              <span className="w-2 h-2 rounded-full mt-1 shrink-0" style={{ backgroundColor: agent.color }} />
              <div className="min-w-0 flex-1">
                <span style={{ color: agent.color }} className="font-medium">{agent.name.split(' ')[0]}</span>
                <span className="text-muted-foreground"> {a.action}</span>
                {a.details && <p className="text-muted-foreground truncate mt-0.5">{a.details.slice(0, 80)}</p>}
              </div>
              <span className="text-muted-foreground/60 shrink-0">{time}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
