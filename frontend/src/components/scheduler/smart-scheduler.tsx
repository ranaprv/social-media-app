"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  TrendingUp,
  TrendingDown,
  Clock,
  BarChart3,
  Lightbulb,
  RefreshCw,
  Loader2,
  Sparkles,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const PLATFORM_COLORS: Record<Platform, string> = {
  linkedin: "text-blue-600",
  x: "text-black",
  instagram: "text-pink-500",
  facebook: "text-blue-500",
  youtube: "text-red-600",
}

interface BestTimeSlot {
  day: number
  hour: number
  score: number
  label: string
  avg_engagement?: number
  post_count?: number
}

interface ContentSuggestion {
  type: string
  priority: "high" | "medium" | "low"
  message: string
  confidence: number
  data?: Record<string, number>
}

interface BestTimeData {
  source: "analytics" | "static"
  data_points: number
  platforms: Record<string, BestTimeSlot[]>
}

interface ContentData {
  suggestions: ContentSuggestion[]
  stats: {
    total_posts: number
    period_days: number
    avg_engagement_rate: number
    total_impressions: number
    total_engagement: number
  }
}

interface SmartSchedulerProps {
  selectedPlatform?: Platform
}

export function SmartScheduler({ selectedPlatform }: SmartSchedulerProps) {
  const [bestTimes, setBestTimes] = useState<BestTimeData | null>(null)
  const [contentSuggestions, setContentSuggestions] = useState<ContentData | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"times" | "suggestions">("times")

  const fetchData = useCallback(async () => {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const platformParam = selectedPlatform ? `?platform=${selectedPlatform}` : ""

      const [timesRes, suggestionsRes] = await Promise.all([
        fetch(`${API_BASE}/scheduler/recommendations/best-times${platformParam}`, { headers }),
        fetch(`${API_BASE}/scheduler/recommendations/content${platformParam}`, { headers }),
      ])

      if (timesRes.ok) setBestTimes(await timesRes.json())
      if (suggestionsRes.ok) setContentSuggestions(await suggestionsRes.json())
    } catch (err) {
      console.error("Failed to load recommendations:", err)
    } finally {
      setLoading(false)
    }
  }, [selectedPlatform])

  useEffect(() => { void (async () => { await fetchData() })() }, [fetchData])

  const priorityColor = (p: string) => {
    if (p === "high") return "bg-red-100 text-red-700"
    if (p === "medium") return "bg-yellow-100 text-yellow-700"
    return "bg-gray-100 text-gray-600"
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Analyzing your data...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === "times" ? "default" : "outline"}
          size="sm"
          onClick={() => setActiveTab("times")}
          className="gap-1.5"
        >
          <Clock className="h-3.5 w-3.5" />
          Best Times
        </Button>
        <Button
          variant={activeTab === "suggestions" ? "default" : "outline"}
          size="sm"
          onClick={() => setActiveTab("suggestions")}
          className="gap-1.5"
        >
          <Sparkles className="h-3.5 w-3.5" />
          Content Tips
        </Button>
        <Button variant="ghost" size="icon" onClick={fetchData}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Best Times Tab */}
      {activeTab === "times" && bestTimes && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Optimal Posting Times
              </CardTitle>
              <Badge variant={bestTimes.source === "analytics" ? "default" : "secondary"}>
                {bestTimes.source === "analytics" ? "From your data" : "Industry averages"}
              </Badge>
            </div>
            {bestTimes.data_points > 0 && (
              <p className="text-xs text-muted-foreground">
                Based on {bestTimes.data_points} data points
              </p>
            )}
          </CardHeader>
          <CardContent>
            {Object.entries(bestTimes.platforms).map(([platform, slots]) => (
              <div key={platform} className="mb-4 last:mb-0">
                <h4 className={`text-sm font-medium mb-2 capitalize ${PLATFORM_COLORS[platform as Platform] || ""}`}>
                  {platform}
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                  {slots.map((slot, i) => (
                    <div
                      key={i}
                      className="rounded-lg border p-2 text-center"
                    >
                      <div className="text-xs font-medium">{slot.label}</div>
                      <div className="text-lg font-bold text-primary">
                        {(slot.score * 100).toFixed(0)}%
                      </div>
                      {slot.post_count && (
                        <div className="text-[10px] text-muted-foreground">
                          {slot.post_count} posts
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {Object.keys(bestTimes.platforms).length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4">
                Publish more posts to get personalized time recommendations.
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Content Suggestions Tab */}
      {activeTab === "suggestions" && contentSuggestions && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <Lightbulb className="h-4 w-4" />
                Content Improvement Suggestions
              </CardTitle>
              <Badge variant="outline">
                {contentSuggestions.suggestions.length} tips
              </Badge>
            </div>
            {contentSuggestions.stats.total_posts > 0 && (
              <div className="flex gap-4 text-xs text-muted-foreground mt-1">
                <span>{contentSuggestions.stats.total_posts} posts analyzed</span>
                <span>Avg engagement: {contentSuggestions.stats.avg_engagement_rate}%</span>
                <span>{(contentSuggestions.stats.total_impressions / 1000).toFixed(0)}K impressions</span>
              </div>
            )}
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {contentSuggestions.suggestions.map((suggestion, i) => (
                <div
                  key={i}
                  className="rounded-lg border p-3"
                >
                  <div className="flex items-start gap-2">
                    <div className="mt-0.5">
                      {suggestion.type === "trend" && suggestion.priority === "high" ? (
                        <TrendingUp className="h-4 w-4 text-green-500" />
                      ) : suggestion.type === "trend" ? (
                        <TrendingDown className="h-4 w-4 text-red-500" />
                      ) : (
                        <Lightbulb className="h-4 w-4 text-yellow-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`text-[10px] px-1.5 py-0 ${priorityColor(suggestion.priority)}`}>
                          {suggestion.priority}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground capitalize">
                          {suggestion.type.replace(/_/g, " ")}
                        </span>
                        <span className="text-[10px] text-muted-foreground">
                          {Math.round(suggestion.confidence * 100)}% confidence
                        </span>
                      </div>
                      <p className="text-sm">{suggestion.message}</p>
                    </div>
                  </div>
                </div>
              ))}

              {contentSuggestions.suggestions.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No suggestions yet. Publish more content to get personalized tips.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
