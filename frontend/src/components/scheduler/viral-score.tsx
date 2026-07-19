"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Zap,
  Loader2,
  Sparkles,
  TrendingUp,
  AlertTriangle,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Factor {
  factor: string
  score: number
}

interface ViralResult {
  score: number
  classification: string
  label: string
  factors: Factor[]
  suggestions: string[]
}

interface ViralScoreProps {
  initialContent?: string
  platform?: Platform
}

export function ViralScorePredictor({ initialContent = "", platform = "linkedin" }: ViralScoreProps) {
  const [content, setContent] = useState(initialContent)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [result, setResult] = useState<ViralResult | null>(null)
  const [loading, setLoading] = useState(false)

  const predict = async () => {
    if (!content) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/viral/score`, {
        method: "POST",
        headers,
        body: JSON.stringify({ content, platform: selectedPlatform }),
      })
      if (response.ok) setResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = (s: number) => {
    if (s >= 80) return "text-green-600"
    if (s >= 60) return "text-yellow-600"
    if (s >= 40) return "text-orange-600"
    return "text-red-600"
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Zap className="h-4 w-4" />
          Viral Score Predictor
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste your content to predict viral potential..."
          className="min-h-[60px] text-sm"
        />
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

        <Button onClick={predict} disabled={loading || !content} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          Predict Viral Score
        </Button>

        {result && (
          <div className="space-y-3 pt-2 border-t">
            {/* Score */}
            <div className="text-center">
              <div className={`text-4xl font-bold ${scoreColor(result.score)}`}>
                {result.score}
              </div>
              <p className="text-sm font-medium mt-1">{result.label}</p>
            </div>

            {/* Factors */}
            <div className="space-y-1.5">
              {result.factors.map((f, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className="flex-1 capitalize">{f.factor.replace(/_/g, " ")}</span>
                  <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${f.score}%` }}
                    />
                  </div>
                  <span className="w-8 text-right text-muted-foreground">{f.score}</span>
                </div>
              ))}
            </div>

            {/* Suggestions */}
            {result.suggestions.length > 0 && (
              <div className="space-y-1">
                <h4 className="text-xs font-medium flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Improvement Tips
                </h4>
                {result.suggestions.map((s, i) => (
                  <p key={i} className="text-[10px] text-muted-foreground pl-4">• {s}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
