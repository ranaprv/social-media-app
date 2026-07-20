"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { ErrorBoundary } from "@/components/ui/error-boundary"
import { KeywordTab } from "@/components/research/keyword-tab"
import { CompetitorTab } from "@/components/research/competitor-tab"
import { TrendTab } from "@/components/research/trend-tab"
import { ThumbnailTab } from "@/components/research/thumbnail-tab"
import { AudienceTab } from "@/components/research/audience-tab"
import { ResearchSidebar } from "@/components/research/research-sidebar"
import { Search, Users, TrendingUp, Film, BarChart3 } from "lucide-react"

interface SavedItem {
  id: string
  category: string
  topic: string
  platform: string
  data: Record<string, unknown>
}

export default function ResearchPage() {
  const [savedItems, setSavedItems] = useState<SavedItem[]>([])

  const handleSave = (item: unknown) => {
    const newItem = { ...(item as Omit<SavedItem, "id">), id: `saved-${Date.now()}` }
    setSavedItems(prev => [newItem, ...prev])
  }

  const handleRemove = (id: string) => {
    setSavedItems(prev => prev.filter(item => item.id !== id))
  }

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-4rem)]">
        <div className="hidden md:block">
          <ResearchSidebar items={savedItems} onRemove={handleRemove} />
        </div>
        
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold">Research Engine</h1>
            <p className="text-muted-foreground">Video SEO research — keywords, competitors, trends, thumbnails, and audience analytics.</p>
          </div>

          <ErrorBoundary>
            <Tabs defaultValue="keywords" className="space-y-4">
              <div className="overflow-x-auto -mx-4 px-4 md:mx-0 md:px-0">
                <TabsList className="w-max md:w-full">
                  <TabsTrigger value="keywords" className="gap-1 whitespace-nowrap"><Search className="h-3 w-3" /> Keywords</TabsTrigger>
                  <TabsTrigger value="competitors" className="gap-1 whitespace-nowrap"><Users className="h-3 w-3" /> Competitors</TabsTrigger>
                  <TabsTrigger value="trends" className="gap-1 whitespace-nowrap"><TrendingUp className="h-3 w-3" /> Trends</TabsTrigger>
                  <TabsTrigger value="thumbnails" className="gap-1 whitespace-nowrap"><Film className="h-3 w-3" /> Thumbnails</TabsTrigger>
                  <TabsTrigger value="audience" className="gap-1 whitespace-nowrap"><BarChart3 className="h-3 w-3" /> Audience</TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="keywords"><KeywordTab onSave={handleSave} /></TabsContent>
              <TabsContent value="competitors"><CompetitorTab onSave={handleSave} /></TabsContent>
              <TabsContent value="trends"><TrendTab onSave={handleSave} /></TabsContent>
              <TabsContent value="thumbnails"><ThumbnailTab onSave={handleSave} /></TabsContent>
              <TabsContent value="audience"><AudienceTab onSave={handleSave} /></TabsContent>
            </Tabs>
          </ErrorBoundary>
        </main>
      </div>
    </DashboardLayout>
  )
}
