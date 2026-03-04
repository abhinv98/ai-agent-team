import { Droppable, Draggable } from '@hello-pangea/dnd'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import TaskCard from './TaskCard'

const statusColors = {
  backlog: '#6B7280',
  in_progress: '#3B82F6',
  pending_review: '#F59E0B',
  changes_requested: '#EF4444',
  approved: '#10B981',
  done: '#6366F1',
}

export default function KanbanColumn({ column, tasks }) {
  const color = statusColors[column.id] || '#6B7280'

  return (
    <div className="flex flex-col w-72 shrink-0">
      <div className="flex items-center gap-2 mb-3 px-1">
        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
        <h3 className="text-sm font-semibold text-foreground/80">{column.label}</h3>
        <Badge variant="secondary" className="ml-auto text-xs px-1.5 py-0">{tasks.length}</Badge>
      </div>
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <ScrollArea className="flex-1">
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`rounded-lg p-2 min-h-[200px] transition-colors ${
                snapshot.isDraggingOver ? 'bg-accent/50' : 'bg-surface-50/30'
              }`}
            >
              {tasks.map((task, index) => (
                <Draggable key={task.id} draggableId={task.id} index={index}>
                  {(provided) => <TaskCard task={task} provided={provided} />}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          </ScrollArea>
        )}
      </Droppable>
    </div>
  )
}
