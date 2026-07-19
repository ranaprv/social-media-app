"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  CalendarDays,
  Loader2,
  Sparkles,
  CheckCircle2,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface CalendarDay {
  day: number
  weekday: string
  posts: {
    platform: string
    content_type: string
    title: string
    content: string
    best_time: string
    pillar: string
    hashtags: string[]
    cta: string
  }[]
}

interface CalendarResult {
  calendar: CalendarDay[]
  total_days: number
  total_posts: number
  content_mix: Record<string, number>
  themes_by_week: string[]
  platforms: string[]
}

interface AICalendarGeneratorProps {
  initialTopic?: string
  platforms?: Platform[]
}

export function AICalendarGenerator({ initialTopic = "", platforms = ["linkedin", "x"] }: AICalendarGeneratorProps) {
  const [topic, setTopic] = useState(initialTopic)
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>(platforms)
  const [frequency, setFrequency] = useState("daily")
  const [result, setResult] = useState<CalendarResult | null>(null)
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    if (!topic) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/calendar/generate`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          topic,
          platforms: selectedPlatforms,
          posting_frequency: frequency,
        }),
      })
      if (response.ok) setResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  const togglePlatform = (p: Platform) => {
    setSelectedPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <CalendarDays className="h-4 w-4" />
          AI Calendar Generator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Topic (e.g. SaaS growth strategies)"
          className="text-sm"
        />

        <div className="flex flex-wrap gap-1.5">
          {(["linkedin", "x", "instagram", "facebook", "youtube"] as Platform[]).map((p) => (
            <button
              key={p}
              onClick={() => togglePlatform(p)}
              className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium transition-all ${
                selectedPlatforms.includes(p)
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        <select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value)}
          className="rounded-md border border-border bg-background px-2 py-1 text-sm w-full"
        >
          <option value="daily">Daily</option>
          <option value="weekdays">Weekdays only</option>
          <option value="3x_week">3 times per week</option>
          <option value="weekly">Weekly</option>
        </select>

        <Button onClick={generate} disabled={loading || !topic} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          {loading ? "Generating..." : "Generate Monthly Calendar"}
        </Button>

        {result && (
          <div className="space-y-3 pt-2 border-t">
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-green-500" />
                {result.total_days} days
              </span>
              <span>{result.total_posts} posts</span>
              <span>{result.platforms.join(", ")}</span>
            </div>

            {/* Content mix */}
            {Object.keys(result.content_mix).length > 0 && (
              <div className="flex flex-wrap gap-1">
                {Object.entries(result.content_mix).map(([type, pct]) => (
                  <Badge key={type} variant="outline" className="text-[9px] capitalize">
                    {type}: {pct}%
                  </Badge>
                ))}
              </div>
            )}

            {/* Calendar preview */}
            <div className="space-y-1.5 max-h-[300px] overflow-y-auto">
              {result.calendar.slice(0, 14).map((day) => (
                <div key={day.day} className="rounded border p-2 text-[10px]">
                  <div className="font-medium mb-0.5">
                    Day {day.day} ({day.weekday})
                  </div>
                  {day.posts.map((post, i) => (
                    <div key={i} className="flex items-center gap-2 text-muted-foreground">
                      <Badge variant="outline" className="text-[8px] px-1 py-0">{post.platform}</Badge>
                      <span>{post.best_time}</span>
                      <span className="truncate flex-1">{post.title}</span>
                    </div>
                  ))}
                </div>
              ))}
              {result.calendar.length > 14 && (
                <p className="text-[10px] text-muted-foreground text-center">
                  +{result.calendar.length - 14} more days
                </p>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
