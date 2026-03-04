import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'
import { Separator } from '@/components/ui/separator'
import { AGENTS } from '../utils/constants'

export default function TaskCard({ task, provided }) {
  const [expanded, setExpanded] = useState(false)
  const agent = AGENTS[task.assigned_agent] || { emoji: '🤖', color: '#888', name: task.assigned_agent, bg: 'rgba(255,255,255,0.05)' }
  const campaign = task.campaigns?.name || ''
  const age = task.updated_at ? timeAgo(new Date(task.updated_at)) : ''

  return (
    <div
      ref={provided.innerRef}
      {...provided.draggableProps}
      {...provided.dragHandleProps}
    >
      <Collapsible open={expanded} onOpenChange={setExpanded}>
        <Card className="mb-2 bg-surface-100 border-border/50 hover:border-border transition-colors cursor-grab active:cursor-grabbing">
          <CollapsibleTrigger asChild>
            <CardContent className="p-3">
              <div className="flex items-start gap-2">
                <span className="w-2 h-2 rounded-full mt-1.5 shrink-0" style={{ backgroundColor: agent.color }} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground leading-tight">{task.title}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <Badge variant="outline" className="text-xs px-1.5 py-0 border-0 font-normal" style={{ backgroundColor: agent.bg, color: agent.color }}>
                      {agent.emoji} {agent.name.split('(')[0].trim()}
                    </Badge>
                    {campaign && <span className="text-xs text-muted-foreground truncate">{campaign}</span>}
                  </div>
                  {age && <p className="text-xs text-muted-foreground/60 mt-1">{age}</p>}
                </div>
              </div>
            </CardContent>
          </CollapsibleTrigger>
          <CollapsibleContent>
            {task.output_content && (
              <div className="px-3 pb-3">
                <Separator className="mb-3" />
                <p className="text-xs text-muted-foreground whitespace-pre-wrap max-h-48 overflow-auto">{task.output_content.slice(0, 1000)}</p>
                {task.feedback && (
                  <div className="mt-2 p-2 bg-yellow-900/20 rounded-md border border-yellow-800/30">
                    <p className="text-xs text-yellow-300">Feedback: {task.feedback}</p>
                  </div>
                )}
              </div>
            )}
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  )
}

function timeAgo(date) {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}
