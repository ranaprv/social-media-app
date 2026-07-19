"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Hash,
  Copy,
  Loader2,
  Sparkles,
  TrendingUp,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface HashtagItem {
  tag: string
  category: string
  estimated_reach: string
  relevance: string
}

interface HashtagResult {
  hashtags: HashtagItem[]
  count: number
  platform: string
  topic: string
}

interface HashtagStrategistProps {
  initialTopic?: string
  platform?: Platform
}

export function HashtagStrategist({ initialTopic = "", platform = "linkedin" }: HashtagStrategistProps) {
  const [topic, setTopic] = useState(initialTopic)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [count, setCount] = useState(5)
  const [result, setResult] = useState<HashtagResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const generate = async () => {
    if (!topic) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/hashtags/generate`, {
        method: "POST",
        headers,
        body: JSON.stringify({ topic, platform: selectedPlatform, count }),
      })
      if (response.ok) setResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  const copyAll = async () => {
    if (!result) return
    const text = result.hashtags.map((h) => h.tag).join(" ")
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const categoryColor = (cat: string) => {
    if (cat === "brand") return "bg-purple-100 text-purple-700"
    if (cat === "broad") return "bg-blue-100 text-blue-700"
    if (cat === "mid") return "bg-yellow-100 text-yellow-700"
    return "bg-green-100 text-green-700"
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Hash className="h-4 w-4" />
          Hashtag Strategist
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Topic (e.g. content marketing tips)"
          className="text-sm"
        />

        <div className="grid grid-cols-2 gap-2">
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value as Platform)}
            className="rounded-md border border-border bg-background px-2 py-1 text-sm"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="x">X (Twitter)</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="youtube">YouTube</option>
          </select>
          <Input
            type="number"
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            min={1}
            max={15}
            className="text-sm"
          />
        </div>

        <Button onClick={generate} disabled={loading || !topic} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          {loading ? "Generating..." : "Generate Hashtags"}
        </Button>

        {result && (
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">{result.count} hashtags for {result.platform}</span>
              <Button variant="ghost" size="sm" onClick={copyAll} className="h-6 text-[10px] gap-1">
                <Copy className="h-3 w-3" />
                {copied ? "Copied!" : "Copy All"}
              </Button>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {result.hashtags.map((h, i) => (
                <div key={i} className="flex items-center gap-1 rounded-full border px-2 py-0.5">
                  <span className="text-xs font-medium">{h.tag}</span>
                  <Badge className={`text-[8px] px-1 py-0 ${categoryColor(h.category)}`}>
                    {h.category}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
