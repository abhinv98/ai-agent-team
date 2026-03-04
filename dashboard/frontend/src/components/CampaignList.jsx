import { useState } from 'react'
import { usePolling } from '../hooks/usePolling'
import { useApi } from '../hooks/useApi'
import { AGENTS } from '../utils/constants'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'
import { Separator } from '@/components/ui/separator'

const statusVariant = {
  active: 'default',
  completed: 'secondary',
  paused: 'outline',
  cancelled: 'destructive',
}

export default function CampaignList() {
  const { data: campaigns, refresh } = usePolling('/campaigns', 15000)
  const { post } = useApi()
  const [name, setName] = useState('')
  const [brief, setBrief] = useState('')
  const [expandedId, setExpandedId] = useState(null)
  const [expandedData, setExpandedData] = useState(null)

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    await post('/campaigns', { name: name.trim(), brief: brief.trim() || null })
    setName('')
    setBrief('')
    refresh()
  }

  const toggleExpand = async (id) => {
    if (expandedId === id) {
      setExpandedId(null)
      return
    }
    setExpandedId(id)
    try {
      const res = await fetch(`/api/campaigns/${id}`)
      const data = await res.json()
      setExpandedData(data)
    } catch { setExpandedData(null) }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-bold">Campaigns</h1>

      <Card className="bg-surface-50 border-border/50">
        <CardContent className="p-4">
          <form onSubmit={handleCreate} className="flex gap-3">
            <Input
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Campaign name"
              className="flex-1 bg-surface-200"
            />
            <Input
              value={brief}
              onChange={e => setBrief(e.target.value)}
              placeholder="Brief (optional)"
              className="flex-[2] bg-surface-200"
            />
            <Button type="submit">Create</Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-3">
        {(campaigns || []).map(c => (
          <Collapsible key={c.id} open={expandedId === c.id} onOpenChange={() => toggleExpand(c.id)}>
            <Card className="bg-surface-50 border-border/50 overflow-hidden">
              <CollapsibleTrigger asChild>
                <button className="w-full flex items-center gap-4 p-4 text-left hover:bg-accent transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-foreground truncate">{c.name}</p>
                    {c.brief && <p className="text-xs text-muted-foreground truncate mt-0.5">{c.brief}</p>}
                  </div>
                  <Badge variant={statusVariant[c.status] || 'default'}>{c.status}</Badge>
                  <span className="text-xs text-muted-foreground">{new Date(c.created_at).toLocaleDateString()}</span>
                  <span className="text-muted-foreground">{expandedId === c.id ? '▾' : '▸'}</span>
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                {expandedData && (
                  <div className="px-4 pb-4">
                    <Separator className="mb-3" />
                    <div className="flex items-center gap-4 mb-3">
                      <span className="text-sm text-muted-foreground">Total Cost: <strong className="text-foreground">${(expandedData.total_cost || 0).toFixed(4)}</strong></span>
                      <span className="text-sm text-muted-foreground">Tasks: <strong className="text-foreground">{(expandedData.tasks || []).length}</strong></span>
                    </div>
                    <div className="space-y-2">
                      {(expandedData.tasks || []).map(t => {
                        const agent = AGENTS[t.assigned_agent] || { color: '#888' }
                        return (
                          <div key={t.id} className="flex items-center gap-3 px-3 py-2 bg-surface-200 rounded-md">
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: agent.color }} />
                            <span className="text-sm flex-1 truncate">{t.title}</span>
                            <Badge variant="outline" className="text-xs">{t.status}</Badge>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </CollapsibleContent>
            </Card>
          </Collapsible>
        ))}
        {(!campaigns || campaigns.length === 0) && (
          <div className="text-center text-muted-foreground py-12">No campaigns yet. Create one above or use /campaign in Slack.</div>
        )}
      </div>
    </div>
  )
}
