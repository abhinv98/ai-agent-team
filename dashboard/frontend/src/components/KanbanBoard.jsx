import { useState, useCallback } from 'react'
import { DragDropContext } from '@hello-pangea/dnd'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import KanbanColumn from './KanbanColumn'
import { COLUMNS, AGENTS } from '../utils/constants'
import { useRealtime } from '../hooks/useRealtime'
import { useApi } from '../hooks/useApi'

export default function KanbanBoard() {
  const { data: board, refresh } = useRealtime('/tasks/board', 'tasks', 10000)
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
      <div className="flex items-center gap-3 mb-3 shrink-0">
        <h1 className="text-sm font-semibold text-foreground">Tasks</h1>
        <Select value={filterAgent} onValueChange={setFilterAgent}>
          <SelectTrigger className="w-[160px] h-8 text-xs">
            <SelectValue placeholder="All Agents" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Agents</SelectItem>
            {Object.entries(AGENTS).map(([key, a]) => (
              <SelectItem key={key} value={key}>{a.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-6 gap-2 flex-1 min-h-0">
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
