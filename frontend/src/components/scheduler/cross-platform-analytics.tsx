"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  BarChart3,
  TrendingUp,
  Trophy,
  RefreshCw,
  Loader2,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const PLATFORM_COLORS: Record<string, string> = {
  linkedin: "text-blue-600",
  x: "text-black",
  instagram: "text-pink-500",
  facebook: "text-blue-500",
  youtube: "text-red-600",
}

interface PlatformData {
  impressions: number
  engagement: number
  reach: number
  clicks: number
  post_count: number
  engagement_rate: number
}

interface CrossPlatformData {
  totals: { impressions: number; engagement: number; reach: number; clicks: number }
  by_platform: Record<string, PlatformData>
  platform_ranking: { rank: number; platform: string; engagement_rate: number }[]
  best_platform: string | null
  overall_engagement_rate: number
}

export function CrossPlatformAnalytics() {
  const [data, setData] = useState<CrossPlatformData | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/analytics/cross-platform`, { headers })
      if (response.ok) setData(await response.json())
    } catch (err) {
      console.error("Failed to load cross-platform analytics:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const formatNum = (n: number) => {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
    return n.toString()
  }

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
            <BarChart3 className="h-4 w-4" />
            Cross-Platform Analytics
          </CardTitle>
          <div className="flex items-center gap-2">
            {data.best_platform && (
              <Badge variant="default" className="text-[10px]">
                <Trophy className="h-3 w-3 mr-0.5" />
                Best: {data.best_platform}
              </Badge>
            )}
            <Button variant="ghost" size="icon" onClick={fetchData}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Totals */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <div className="text-center p-2 rounded border">
            <div className="text-lg font-bold">{formatNum(data.totals.impressions)}</div>
            <div className="text-[10px] text-muted-foreground">Impressions</div>
          </div>
          <div className="text-center p-2 rounded border">
            <div className="text-lg font-bold">{formatNum(data.totals.engagement)}</div>
            <div className="text-[10px] text-muted-foreground">Engagement</div>
          </div>
          <div className="text-center p-2 rounded border">
            <div className="text-lg font-bold">{formatNum(data.totals.reach)}</div>
            <div className="text-[10px] text-muted-foreground">Reach</div>
          </div>
          <div className="text-center p-2 rounded border">
            <div className="text-lg font-bold text-primary">{data.overall_engagement_rate}%</div>
            <div className="text-[10px] text-muted-foreground">Eng. Rate</div>
          </div>
        </div>

        {/* Per platform */}
        <div className="space-y-1.5">
          {data.platform_ranking.map((r) => {
            const pd = data.by_platform[r.platform]
            if (!pd) return null
            return (
              <div key={r.platform} className="flex items-center gap-3 rounded border p-2">
                <span className="text-xs font-bold text-muted-foreground w-5">#{r.rank}</span>
                <span className={`text-xs font-medium capitalize flex-1 ${PLATFORM_COLORS[r.platform] || ""}`}>
                  {r.platform}
                </span>
                <span className="text-[10px] text-muted-foreground">{formatNum(pd.impressions)} imp</span>
                <span className="text-[10px] text-muted-foreground">{formatNum(pd.engagement)} eng</span>
                <span className="text-xs font-bold">{r.engagement_rate}%</span>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
