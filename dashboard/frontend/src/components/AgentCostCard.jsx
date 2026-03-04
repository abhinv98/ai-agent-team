import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { AGENTS } from '../utils/constants'

export default function AgentCostCard({ data }) {
  const agent = AGENTS[data.agent_name] || { color: '#888', name: data.agent_name }

  return (
    <Card className="bg-surface-100 border-border/50 hover:border-border transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: agent.color }} />
          <span className="text-sm font-semibold" style={{ color: agent.color }}>{agent.name}</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-muted-foreground">Today</p>
            <p className="text-lg font-bold text-foreground">${(data.today_cost || 0).toFixed(4)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Lifetime</p>
            <p className="text-lg font-bold text-foreground/70">${(data.total_cost || 0).toFixed(4)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Calls Today</p>
            <p className="text-sm font-medium text-muted-foreground">{data.today_calls || 0}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Total Calls</p>
            <p className="text-sm font-medium text-muted-foreground">{data.total_calls || 0}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
