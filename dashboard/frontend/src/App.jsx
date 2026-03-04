import { useState } from 'react'
import { Tabs, TabsContent } from '@/components/ui/tabs'
import { TooltipProvider } from '@/components/ui/tooltip'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import KanbanBoard from './components/KanbanBoard'
import CostTracker from './components/CostTracker'
import CampaignList from './components/CampaignList'

export default function App() {
  const [tab, setTab] = useState('kanban')

  return (
    <TooltipProvider>
      <Tabs value={tab} onValueChange={setTab} className="h-screen flex flex-col overflow-hidden">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-auto p-4">
            <TabsContent value="kanban" className="mt-0 h-full"><KanbanBoard /></TabsContent>
            <TabsContent value="costs" className="mt-0"><CostTracker /></TabsContent>
            <TabsContent value="campaigns" className="mt-0"><CampaignList /></TabsContent>
          </main>
        </div>
      </Tabs>
    </TooltipProvider>
  )
}
