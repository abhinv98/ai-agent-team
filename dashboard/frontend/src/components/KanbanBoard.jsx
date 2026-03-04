import { useState, useCallback } from 'react'
import { DragDropContext } from '@hello-pangea/dnd'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import KanbanColumn from './KanbanColumn'
import { COLUMNS, AGENTS } from '../utils/constants'
import { usePolling } from '../hooks/usePolling'
import { useApi } from '../hooks/useApi'

export default function KanbanBoard() {
  const { data: board, refresh } = usePolling('/tasks/board', 10000)
  const { patch } = useApi()
  const [filterAgent, setFilterAgent] = useState('all')

  const handleDragEnd = useCallback(async (result) => {
    if (!result.destination) return
    const { draggableId, destination } = result
    const newStatus = destination.droppableId
    await patch(`/tasks/${draggableId}`, { status: newStatus })
    refresh()
  }, [patch, refresh])

  const filterTasks = (tasks) => {
    if (!tasks) return []
    if (filterAgent && filterAgent !== 'all') return tasks.filter(t => t.assigned_agent === filterAgent)
    return tasks
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-3 mb-4 shrink-0">
        <h1 className="text-lg font-bold">Kanban Board</h1>
        <Select value={filterAgent} onValueChange={setFilterAgent}>
          <SelectTrigger className="w-[200px] h-9">
            <SelectValue placeholder="All Agents" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Agents</SelectItem>
            {Object.entries(AGENTS).map(([key, a]) => (
              <SelectItem key={key} value={key}>{a.emoji} {a.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto flex-1 pb-4">
          {COLUMNS.map(col => (
            <KanbanColumn
              key={col.id}
              column={col}
              tasks={filterTasks(board?.[col.id] || [])}
            />
          ))}
        </div>
      </DragDropContext>
    </div>
  )
}
