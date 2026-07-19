"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  GitBranch,
  RefreshCw,
  Loader2,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Send,
  XCircle,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface PipelineStage {
  id: string
  name: string
  description: string
  post_count: number
  platform_entries: number
}

interface PipelineData {
  stages: PipelineStage[]
  total_posts: number
  total_entries: number
  bottleneck: { stage: string; count: number; suggestion: string } | null
}

const STAGE_ICONS: Record<string, typeof Clock> = {
  draft: Clock,
  review: AlertTriangle,
  scheduled: Send,
  publishing: Loader2,
  published: CheckCircle2,
  failed: XCircle,
}

const STAGE_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  review: "bg-yellow-100 text-yellow-700",
  scheduled: "bg-blue-100 text-blue-700",
  publishing: "bg-orange-100 text-orange-700",
  published: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
}

export function ContentPipelineVisualizer() {
  const [data, setData] = useState<PipelineData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchPipeline = useCallback(async () => {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/pipeline/status`, { headers })
      if (response.ok) setData(await response.json())
    } catch (err) {
      console.error("Failed to load pipeline:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void (async () => { await fetchPipeline() })() }, [fetchPipeline])

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Loader2 className="h-5 w-5 animate-spin mx-auto mb-2" />
        </CardContent>
      </Card>
    )
  }

  if (!data) return null

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <GitBranch className="h-4 w-4" />
            Content Pipeline
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{data.total_entries} entries</Badge>
            <Button variant="ghost" size="icon" onClick={fetchPipeline}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Bottleneck warning */}
        {data.bottleneck && (
          <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-2.5 text-xs text-yellow-800 flex items-start gap-2">
            <AlertTriangle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
            <span>{data.bottleneck.suggestion}</span>
          </div>
        )}

        {/* Pipeline stages */}
        <div className="flex items-stretch gap-1 overflow-x-auto pb-2">
          {data.stages.map((stage, i) => {
            const Icon = STAGE_ICONS[stage.id] || Clock
            const colorClass = STAGE_COLORS[stage.id] || "bg-gray-100"
            const hasItems = stage.platform_entries > 0

            return (
              <div key={stage.id} className="flex items-center">
                <div className={`rounded-lg border p-2 min-w-[100px] text-center ${hasItems ? colorClass : "bg-muted"}`}>
                  <Icon className={`h-4 w-4 mx-auto mb-1 ${hasItems ? "" : "text-muted-foreground"}`} />
                  <div className="text-[10px] font-medium">{stage.name}</div>
                  <div className="text-lg font-bold">{stage.platform_entries}</div>
                  <div className="text-[9px] text-muted-foreground">{stage.post_count} posts</div>
                </div>
                {i < data.stages.length - 1 && (
                  <div className="text-muted-foreground px-0.5">→</div>
                )}
              </div>
            )
          })}
        </div>

        {/* Stage descriptions */}
        <div className="grid grid-cols-2 gap-1 text-[10px] text-muted-foreground">
          {data.stages.map((stage) => (
            <div key={stage.id}>
              <span className="font-medium">{stage.name}:</span> {stage.description}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
