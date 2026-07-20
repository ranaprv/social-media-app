"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { VideoSEOGauge } from "./video-seo-gauge"
import { Bookmark, Trash2, ExternalLink, Lightbulb } from "lucide-react"

interface SavedItem {
  id: string
  category: string
  topic: string
  platform: string
  data: Record<string, unknown>
}

const categoryIcons: Record<string, string> = {
  keyword: "🔑",
  competitor: "👥",
  trend: "📈",
  thumbnail: "🎬",
  audience: "📊",
}

export function ResearchSidebar({ items, onRemove }: { items: SavedItem[]; onRemove: (id: string) => void }) {
  const [expanded, setExpanded] = useState<string | null>(null)
  const [savedToast, setSavedToast] = useState<string | null>(null)

  function saveToStrategy(item: SavedItem) {
    const existing: Array<{ topic: string; category: string; pillar?: string; score?: number }> = JSON.parse(localStorage.getItem("research_strategy_items") || "[]")
    if (!existing.some(e => e.topic === item.topic)) {
      existing.push({ topic: item.topic, category: item.category, pillar: item.data?.content_type as string | undefined, score: item.data?.video_seo_score as number | undefined })
      localStorage.setItem("research_strategy_items", JSON.stringify(existing))
    }
    setSavedToast(item.topic)
    setTimeout(() => setSavedToast(null), 2000)
  }

  const grouped = items.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = []
    acc[item.category].push(item)
    return acc
  }, {} as Record<string, SavedItem[]>)

  return (
    <aside className="w-72 border-r bg-card p-4 space-y-4 h-screen overflow-y-auto">
      <div className="flex items-center gap-2">
        <Bookmark className="h-4 w-4" />
        <h3 className="font-semibold text-sm">Saved Research</h3>
        <Badge variant="outline" className="ml-auto text-xs">{items.length}</Badge>
      </div>
      
      {items.length === 0 && (
        <p className="text-xs text-muted-foreground text-center py-8">
          No saved items yet. Run research and click Save to add items here.
        </p>
      )}

      {Object.entries(grouped).map(([category, catItems]) => (
        <div key={category} className="space-y-1">
          <h4 className="text-xs font-medium text-muted-foreground uppercase">{categoryIcons[category] || "📌"} {category}</h4>
          {catItems.map(item => (
            <div
              key={item.id}
              className={`rounded-lg border p-2 cursor-pointer transition-colors ${expanded === item.id ? "bg-accent" : "hover:bg-accent/50"}`}
              onClick={() => setExpanded(expanded === item.id ? null : item.id)}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium truncate max-w-[180px]">{item.topic}</span>
                <div className="flex items-center gap-1">
                  {!!item.data?.video_seo_score && <VideoSEOGauge score={Number(item.data.video_seo_score)} size="sm" />}
                  <Button size="sm" variant="ghost" className="h-6 w-6 p-0" onClick={(e) => { e.stopPropagation(); onRemove(item.id) }}>
                    <Trash2 className="h-3 w-3 text-muted-foreground" />
                  </Button>
                </div>
              </div>
              {expanded === item.id && (
                <div className="mt-2 space-y-1">
                  <Badge variant="outline" className="text-[10px]">{item.platform}</Badge>
                  <Button size="sm" variant="outline" className="w-full h-7 text-[10px] gap-1 mt-1" onClick={(e) => { e.stopPropagation(); saveToStrategy(item) }}>
                    <Lightbulb className="h-3 w-3" /> Save to Strategy
                  </Button>
                  {savedToast === item.topic && (
                    <p className="text-[10px] text-green-600 font-medium">Saved to strategy — go to Strategy Wizard to use</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ))}
    </aside>
  )
}
