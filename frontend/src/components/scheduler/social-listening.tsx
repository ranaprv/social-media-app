"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Radio,
  Loader2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Mention {
  platform: string
  keyword: string
  author: string
  content: string
  sentiment: string
  timestamp: string
}

interface ScanResult {
  total_mentions: number
  mentions: Mention[]
  sentiment_summary: { positive: number; neutral: number; negative: number }
  keywords_tracked: string[]
}

export function SocialListening() {
  const [keywords, setKeywords] = useState("")
  const [result, setResult] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(false)

  const scan = async () => {
    if (!keywords) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/listening/scan`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
          platforms: ["x", "linkedin", "instagram", "facebook"],
        }),
      })
      if (response.ok) setResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Radio className="h-4 w-4" />
          Social Listening
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Keywords (comma separated)"
          className="text-sm"
        />

        <Button onClick={scan} disabled={loading || !keywords} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Radio className="h-4 w-4 mr-2" />}
          Scan Mentions
        </Button>

        {result && (
          <div className="space-y-3 pt-2 border-t">
            <div className="flex items-center gap-3">
              <Badge variant="outline">{result.total_mentions} mentions</Badge>
              <div className="flex gap-2 text-[10px]">
                <span className="text-green-600">+{result.sentiment_summary.positive}</span>
                <span className="text-gray-500">={result.sentiment_summary.neutral}</span>
                <span className="text-red-600">-{result.sentiment_summary.negative}</span>
              </div>
            </div>

            <div className="space-y-1.5 max-h-[200px] overflow-y-auto">
              {result.mentions.slice(0, 10).map((m, i) => (
                <div key={i} className="flex items-center gap-2 text-xs rounded border p-2">
                  <span className="capitalize font-medium">{m.platform}</span>
                  <span className="flex-1 truncate text-muted-foreground">{m.content}</span>
                  {m.sentiment === "positive" && <TrendingUp className="h-3 w-3 text-green-500" />}
                  {m.sentiment === "negative" && <TrendingDown className="h-3 w-3 text-red-500" />}
                  {m.sentiment === "neutral" && <Minus className="h-3 w-3 text-gray-400" />}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
