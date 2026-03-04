import { AGENTS } from '../utils/constants'
import { useRealtime } from '../hooks/useRealtime'

export default function AgentActivityFeed() {
  const { data } = useRealtime('/agents/activity?limit=15', 'agent_activity', 10000)
  const activities = data || []

  return (
    <div className="p-3">
      <h2 className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-2">Live Activity</h2>
      <div className="space-y-1.5">
        {activities.length === 0 && (
          <p className="text-xs text-muted-foreground">No activity yet</p>
        )}
        {activities.map((a, i) => {
          const agent = AGENTS[a.agent_name] || { color: '#666', name: a.agent_name }
          const time = a.created_at ? new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''
          return (
            <div key={a.id || i} className="flex gap-2 text-xs">
              <span className="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" style={{ backgroundColor: agent.color }} />
              <div className="min-w-0 flex-1">
                <span className="font-medium text-foreground">{agent.name.split(' ')[0]}</span>
                <span className="text-foreground/60"> {a.action}</span>
                {a.details && <p className="text-muted-foreground truncate mt-0.5">{a.details.slice(0, 60)}</p>}
              </div>
              <span className="text-muted-foreground shrink-0 text-[10px]">{time}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
