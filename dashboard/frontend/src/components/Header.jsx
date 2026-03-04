import { TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function Header() {
  return (
    <header className="bg-white border-b border-border px-5 py-2.5 flex items-center justify-between shrink-0">
      <span className="text-base font-semibold tracking-tight text-foreground">
        Ecultify Virtual Team
      </span>
      <TabsList className="bg-surface-50">
        <TabsTrigger value="kanban">Board</TabsTrigger>
        <TabsTrigger value="costs">Costs</TabsTrigger>
        <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
      </TabsList>
      <div className="w-32" />
    </header>
  )
}
