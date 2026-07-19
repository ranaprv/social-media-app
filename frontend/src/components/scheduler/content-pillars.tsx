"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Layers,
  TrendingUp,
  RefreshCw,
  Loader2,
  BarChart3,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Pillar {
  id: string
  name: string
  description: string
  color: string
  target_percentage: number
  actual_percentage: number
  total_posts: number
  avg_engagement_rate: number
  performance_score: number
}

export function ContentPillarManager() {
  const [pillars, setPillars] = useState<Pillar[]>([])
  const [loading, setLoading] = useState(true)
  const [recommendations, setRecommendations] = useState<string[]>([])

  const fetchData = useCallback(async () => {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/pillars`, { headers })
      if (response.ok) {
        const data = await response.json()
        setPillars(data.pillars || [])
        setRecommendations(data.recommendations || [])
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Loader2 className="h-5 w-5 animate-spin mx-auto" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Content Pillars
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={fetchData}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Pillars */}
        <div className="space-y-2">
          {pillars.map((pillar) => (
            <div key={pillar.id} className="rounded-lg border p-3 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: pillar.color }}
                  />
                  <span className="text-xs font-medium">{pillar.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[9px]">
                    {pillar.total_posts} posts
                  </Badge>
                  <Badge variant="secondary" className="text-[9px]">
                    {pillar.avg_engagement_rate}% eng
                  </Badge>
                </div>
              </div>
              <p className="text-[10px] text-muted-foreground">{pillar.description}</p>
              {/* Target vs Actual bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px]">
                  <span>Target: {pillar.target_percentage}%</span>
                  <span>Actual: {pillar.actual_percentage}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${Math.min(pillar.actual_percentage, 100)}%`,
                      backgroundColor: pillar.color,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="space-y-1.5 pt-2 border-t">
            <h4 className="text-xs font-medium text-muted-foreground">Recommendations</h4>
            {recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-2 text-[10px]">
                <BarChart3 className="h-3 w-3 text-primary mt-0.5 shrink-0" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
