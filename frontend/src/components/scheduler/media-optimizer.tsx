"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Image,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Loader2,
  Scissors,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface MediaSpec {
  recommended_size?: [number, number]
  aspect_ratio?: string
  max_size_mb?: number
  formats?: string[]
  notes?: string
}

interface AnalysisResult {
  asset_name?: string
  platform: string
  media_type: string
  status: "ok" | "needs_optimization" | "unknown"
  issues: string[]
  recommendations: string[]
  instructions: { action: string; from?: string; to?: string }[]
  specs: MediaSpec
}

interface MediaOptimizerProps {
  mediaAssets?: { name: string; width?: number; height?: number; format?: string; size_mb?: number; duration_seconds?: number }[]
}

export function MediaOptimizer({ mediaAssets = [] }: MediaOptimizerProps) {
  const [results, setResults] = useState<Record<string, AnalysisResult[]>>({})
  const [loading, setLoading] = useState(false)
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>(["linkedin", "x", "instagram"])

  const analyze = useCallback(async () => {
    if (mediaAssets.length === 0) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/media/optimize-summary`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          media_assets: mediaAssets,
          platforms: selectedPlatforms,
        }),
      })
      if (response.ok) {
        const data = await response.json()
        setResults(data.by_platform || {})
      }
    } finally {
      setLoading(false)
    }
  }, [mediaAssets, selectedPlatforms])

  const totalIssues = Object.values(results).reduce((sum, items) => sum + items.length, 0)

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Scissors className="h-4 w-4" />
            Media Optimizer
          </CardTitle>
          <div className="flex items-center gap-2">
            {totalIssues > 0 ? (
              <Badge variant="destructive">{totalIssues} issues</Badge>
            ) : (
              <Badge variant="default" className="bg-green-600">All clear</Badge>
            )}
            <Button variant="ghost" size="icon" onClick={analyze} disabled={loading}>
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Platform selector */}
        <div className="flex flex-wrap gap-2">
          {(["linkedin", "x", "instagram", "facebook", "youtube"] as Platform[]).map((p) => (
            <button
              key={p}
              onClick={() =>
                setSelectedPlatforms((prev) =>
                  prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
                )
              }
              className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                selectedPlatforms.includes(p)
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Analyze button */}
        <Button onClick={analyze} disabled={loading || mediaAssets.length === 0} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Image className="h-4 w-4 mr-2" />}
          {loading ? "Analyzing..." : `Analyze ${mediaAssets.length} file(s)`}
        </Button>

        {/* Results */}
        {Object.entries(results).map(([platform, items]) => (
          <div key={platform} className="space-y-2">
            <h4 className="text-xs font-medium capitalize text-muted-foreground">{platform}</h4>
            {items.length === 0 ? (
              <div className="flex items-center gap-2 text-xs text-green-600">
                <CheckCircle2 className="h-3.5 w-3.5" />
                All files optimized for {platform}
              </div>
            ) : (
              items.map((item, i) => (
                <div key={i} className="rounded-lg border p-2.5 text-xs">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="h-3.5 w-3.5 text-yellow-500" />
                    <span className="font-medium">{item.asset_name || `File ${i + 1}`}</span>
                  </div>
                  {item.issues?.map((issue, j) => (
                    <p key={j} className="text-red-600 ml-5">{issue}</p>
                  ))}
                  {item.instructions?.map((inst, j) => (
                    <p key={j} className="text-muted-foreground ml-5">
                      {inst.action}: {inst.from} → {inst.to}
                    </p>
                  ))}
                </div>
              ))
            )}
          </div>
        ))}

        {mediaAssets.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-4">
            Add media files to analyze them against platform specs.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
