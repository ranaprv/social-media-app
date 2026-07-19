"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  TrendingUp,
  BarChart3,
  Lightbulb,
  Loader2,
  Sparkles,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ForecastResult {
  forecast: {
    predicted_impressions: number
    predicted_engagement: number
    predicted_engagement_rate: number
    confidence: string
  } | null
  basis: {
    data_points: number
    avg_impressions: number
    avg_engagement_rate: number
    best_day: string
    best_hour: number
  }
  suggestions: string[]
  message?: string
}

interface ContentForecastProps {
  platform?: Platform
}

export function ContentForecast({ platform = "linkedin" }: ContentForecastProps) {
  const [contentLength, setContentLength] = useState(200)
  const [hasMedia, setHasMedia] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [result, setResult] = useState<ForecastResult | null>(null)
  const [loading, setLoading] = useState(false)

  const forecast = async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/forecast`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          platform: selectedPlatform,
          content_length: contentLength,
          has_media: hasMedia,
          proposed_date: new Date().toISOString(),
        }),
      })
      if (response.ok) setResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  const confidenceColor = (c: string) => {
    if (c === "high") return "bg-green-100 text-green-700"
    if (c === "medium") return "bg-yellow-100 text-yellow-700"
    return "bg-gray-100 text-gray-600"
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <TrendingUp className="h-4 w-4" />
          Content Forecast
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Inputs */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1 block">Platform</label>
            <select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value as Platform)}
              className="rounded-md border border-border bg-background px-2 py-1 text-sm w-full"
            >
              <option value="linkedin">LinkedIn</option>
              <option value="x">X (Twitter)</option>
              <option value="instagram">Instagram</option>
              <option value="facebook">Facebook</option>
              <option value="youtube">YouTube</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground mb-1 block">Content Length</label>
            <Input
              type="number"
              value={contentLength}
              onChange={(e) => setContentLength(Number(e.target.value))}
              className="text-sm"
            />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={hasMedia}
              onChange={(e) => setHasMedia(e.target.checked)}
              className="rounded"
            />
            Has media attached
          </label>
        </div>

        <Button onClick={forecast} disabled={loading} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          {loading ? "Forecasting..." : "Predict Engagement"}
        </Button>

        {/* Results */}
        {result && (
          <div className="space-y-3 border-t pt-3">
            {result.message ? (
              <p className="text-sm text-muted-foreground text-center py-4">{result.message}</p>
            ) : result.forecast && (
              <>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-lg border p-2">
                    <div className="text-lg font-bold">{result.forecast.predicted_impressions.toLocaleString()}</div>
                    <div className="text-[10px] text-muted-foreground">Impressions</div>
                  </div>
                  <div className="rounded-lg border p-2">
                    <div className="text-lg font-bold">{result.forecast.predicted_engagement.toLocaleString()}</div>
                    <div className="text-[10px] text-muted-foreground">Engagement</div>
                  </div>
                  <div className="rounded-lg border p-2">
                    <div className="text-lg font-bold">{result.forecast.predicted_engagement_rate}%</div>
                    <div className="text-[10px] text-muted-foreground">Eng. Rate</div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Badge className={`text-[10px] ${confidenceColor(result.forecast.confidence)}`}>
                    {result.forecast.confidence} confidence
                  </Badge>
                  <span className="text-[10px] text-muted-foreground">
                    Based on {result.basis.data_points} posts
                  </span>
                </div>
              </>
            )}

            {result.suggestions.length > 0 && (
              <div className="space-y-1.5">
                <h4 className="text-xs font-medium flex items-center gap-1">
                  <Lightbulb className="h-3 w-3" /> Suggestions
                </h4>
                {result.suggestions.map((s, i) => (
                  <p key={i} className="text-xs text-muted-foreground pl-4">• {s}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
