import { useState } from 'react'
import { usePolling } from '../hooks/usePolling'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import AgentCostCard from './AgentCostCard'
import { StackedCostChart, CumulativeCostChart } from './CostChart'

export default function CostTracker() {
  const [days, setDays] = useState(7)
  const { data: summary } = usePolling('/costs/summary', 30000)
  const { data: daily } = usePolling(`/costs/daily?days=${days}`, 30000)

  const agents = summary || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold">Cost Tracker</h1>
        <div className="flex gap-1">
          {[7, 14, 30].map(d => (
            <Button
              key={d}
              variant={days === d ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setDays(d)}
            >
              {d}d
            </Button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {agents.map(a => <AgentCostCard key={a.agent_name} data={a} />)}
        {agents.length === 0 && (
          <div className="col-span-full text-center text-muted-foreground py-8">No cost data recorded yet</div>
        )}
      </div>

      <Card className="bg-surface-50 border-border/50">
        <CardHeader>
          <CardTitle className="text-muted-foreground">Daily Cost by Agent</CardTitle>
        </CardHeader>
        <CardContent>
          <StackedCostChart data={daily} />
        </CardContent>
      </Card>

      <Card className="bg-surface-50 border-border/50">
        <CardHeader>
          <CardTitle className="text-muted-foreground">Cumulative Spend</CardTitle>
        </CardHeader>
        <CardContent>
          <CumulativeCostChart data={daily} />
        </CardContent>
      </Card>
    </div>
  )
}
