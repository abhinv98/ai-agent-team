import { TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function Header() {
  return (
    <header className="bg-surface-50 border-b px-6 py-3 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-xl font-bold tracking-tight">
          <span className="text-primary">AI</span> Marketing Team
        </span>
      </div>
      <TabsList>
        <TabsTrigger value="kanban">Kanban Board</TabsTrigger>
        <TabsTrigger value="costs">Cost Tracker</TabsTrigger>
        <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
      </TabsList>
      <div className="w-40" />
    </header>
  )
}
