"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Lightbulb,
  Loader2,
  Sparkles,
  Copy,
  TrendingUp,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ContentIdea {
  title: string
  description: string
  platform: string
  content_type: string
  engagement_potential: string
  keywords: string[]
  hook: string
}

interface IdeaGeneratorProps {
  initialKeywords?: string
}

export function ContentIdeaGenerator({ initialKeywords = "" }: IdeaGeneratorProps) {
  const [keywords, setKeywords] = useState(initialKeywords)
  const [industry, setIndustry] = useState("technology")
  const [ideas, setIdeas] = useState<ContentIdea[]>([])
  const [loading, setLoading] = useState(false)

  const generate = async () => {
    if (!keywords) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/ideas/generate`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
          industry,
          count: 10,
        }),
      })
      if (response.ok) {
        const data = await response.json()
        setIdeas(data.ideas || [])
      }
    } finally {
      setLoading(false)
    }
  }

  const potentialColor = (p: string) => {
    if (p === "high") return "bg-green-100 text-green-700"
    if (p === "medium") return "bg-yellow-100 text-yellow-700"
    return "bg-gray-100 text-gray-600"
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Lightbulb className="h-4 w-4" />
          Content Idea Generator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Keywords (comma separated)"
          className="text-sm"
        />
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="rounded-md border border-border bg-background px-2 py-1 text-sm w-full"
        >
          <option value="technology">Technology</option>
          <option value="marketing">Marketing</option>
          <option value="ecommerce">E-commerce</option>
          <option value="healthcare">Healthcare</option>
          <option value="finance">Finance</option>
        </select>

        <Button onClick={generate} disabled={loading || !keywords} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          {loading ? "Generating..." : "Generate 10 Ideas"}
        </Button>

        {ideas.length > 0 && (
          <div className="space-y-2 pt-2 border-t max-h-[300px] overflow-y-auto">
            {ideas.map((idea, i) => (
              <div key={i} className="rounded-lg border p-2.5 space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-medium">{idea.title}</h4>
                  <Badge className={`text-[8px] px-1 py-0 ${potentialColor(idea.engagement_potential)}`}>
                    {idea.engagement_potential}
                  </Badge>
                </div>
                <p className="text-[10px] text-muted-foreground">{idea.description}</p>
                {idea.hook && (
                  <p className="text-[10px] text-blue-600 italic">Hook: {idea.hook}</p>
                )}
                <div className="flex gap-1">
                  <Badge variant="outline" className="text-[8px]">{idea.platform}</Badge>
                  <Badge variant="outline" className="text-[8px]">{idea.content_type}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
