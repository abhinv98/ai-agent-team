import { Droppable, Draggable } from '@hello-pangea/dnd'
import { Badge } from '@/components/ui/badge'
import TaskCard from './TaskCard'

const statusColors = {
  backlog: '#8B8D94',
  in_progress: '#4A7FBF',
  pending_review: '#C47E2A',
  changes_requested: '#B85450',
  approved: '#3D8B6E',
  done: '#5B5FC7',
}

export default function KanbanColumn({ column, tasks }) {
  const color = statusColors[column.id] || '#8B8D94'

  return (
    <div className="flex flex-col min-w-0 min-h-0">
      <div className="flex items-center gap-1.5 mb-2 px-1">
        <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color }} />
        <h3 className="text-xs font-medium text-foreground/70 truncate">{column.label}</h3>
        <Badge variant="secondary" className="ml-auto text-[10px] px-1.5 py-0 h-4 font-medium">{tasks.length}</Badge>
      </div>
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`flex-1 rounded-md p-1.5 min-h-[120px] overflow-y-auto transition-colors ${
              snapshot.isDraggingOver ? 'bg-primary/5 ring-1 ring-primary/20' : 'bg-surface-50/60'
            }`}
          >
            {tasks.map((task, index) => (
              <Draggable key={task.id} draggableId={task.id} index={index}>
                {(provided) => <TaskCard task={task} provided={provided} />}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  )
}
