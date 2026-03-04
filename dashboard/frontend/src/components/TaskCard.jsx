import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'
import { Separator } from '@/components/ui/separator'
import { AGENTS } from '../utils/constants'

export default function TaskCard({ task, provided }) {
  const [expanded, setExpanded] = useState(false)
  const agent = AGENTS[task.assigned_agent] || { color: '#666', name: task.assigned_agent, bg: '#f5f3f0' }
  const campaign = task.campaigns?.name || ''
  const age = task.updated_at ? timeAgo(new Date(task.updated_at)) : ''

  return (
    <div
      ref={provided.innerRef}
      {...provided.draggableProps}
      {...provided.dragHandleProps}
    >
      <Collapsible open={expanded} onOpenChange={setExpanded}>
        <Card className="mb-1.5 bg-white border-border/40 hover:border-border shadow-sm hover:shadow transition-all cursor-grab active:cursor-grabbing">
          <CollapsibleTrigger asChild>
            <CardContent className="p-2">
              <p className="text-xs font-medium text-foreground leading-snug line-clamp-2">{task.title}</p>
              <div className="flex items-center gap-1 mt-1">
                <span
                  className="text-[10px] font-medium px-1.5 py-0.5 rounded"
                  style={{ backgroundColor: agent.bg, color: agent.color }}
                >
                  {agent.name.split('—')[0].trim()}
                </span>
                {age && <span className="text-[10px] text-muted-foreground ml-auto">{age}</span>}
              </div>
              {campaign && <p className="text-[10px] text-muted-foreground mt-0.5 truncate">{campaign}</p>}
            </CardContent>
          </CollapsibleTrigger>
          <CollapsibleContent>
            {task.output_content && (
              <div className="px-2 pb-2">
                <Separator className="mb-2" />
                <p className="text-[11px] text-foreground/70 whitespace-pre-wrap max-h-36 overflow-auto leading-relaxed">{task.output_content.slice(0, 800)}</p>
                {task.feedback && (
                  <div className="mt-1.5 p-1.5 bg-amber-50 rounded border border-amber-200">
                    <p className="text-[10px] text-amber-800">Feedback: {task.feedback}</p>
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
  if (seconds < 60) return 'now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`
  return `${Math.floor(hours / 24)}d`
}
