"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Repeat,
  Copy,
  Loader2,
  Sparkles,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface RepurposeResult {
  route: string
  platform: string
  content: string
  pieces?: any[]
  error?: string
}

interface ContentRepurposingProps {
  initialContent?: string
}

export function ContentRepurposingEngine({ initialContent = "" }: ContentRepurposingProps) {
  const [content, setContent] = useState(initialContent)
  const [selectedRoutes, setSelectedRoutes] = useState<string[]>(["blog_to_thread", "blog_to_linkedin"])
  const [results, setResults] = useState<Record<string, RepurposeResult>>({})
  const [loading, setLoading] = useState(false)

  const routes = [
    { key: "blog_to_thread", label: "→ X Thread", color: "text-black" },
    { key: "blog_to_linkedin", label: "→ LinkedIn", color: "text-blue-600" },
    { key: "blog_to_carousel", label: "→ IG Carousel", color: "text-pink-500" },
    { key: "blog_to_reel", label: "→ Reel Script", color: "text-pink-500" },
    { key: "video_to_shorts", label: "→ YT Shorts", color: "text-red-600" },
    { key: "post_to_story", label: "→ IG Story", color: "text-pink-500" },
  ]

  const toggleRoute = (key: string) => {
    setSelectedRoutes((prev) =>
      prev.includes(key) ? prev.filter((r) => r !== key) : [...prev, key]
    )
  }

  const repurpose = async () => {
    if (!content || selectedRoutes.length === 0) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/repurpose`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          content,
          source_format: "blog",
          target_formats: selectedRoutes,
        }),
      })
      if (response.ok) {
        const data = await response.json()
        setResults(data.results || {})
      }
    } finally {
      setLoading(false)
    }
  }

  const copyContent = async (text: string) => {
    await navigator.clipboard.writeText(text)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Repeat className="h-4 w-4" />
          Content Repurposing Engine
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste your blog post, article, or content here..."
          className="min-h-[80px] text-sm"
        />

        <div className="flex flex-wrap gap-1.5">
          {routes.map((route) => (
            <button
              key={route.key}
              onClick={() => toggleRoute(route.key)}
              className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
                selectedRoutes.includes(route.key)
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {route.label}
            </button>
          ))}
        </div>

        <Button onClick={repurpose} disabled={loading || !content || selectedRoutes.length === 0} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          {loading ? "Repurposing..." : `Repurpose to ${selectedRoutes.length} format(s)`}
        </Button>

        {Object.keys(results).length > 0 && (
          <div className="space-y-2 pt-2 border-t">
            {Object.entries(results).map(([key, result]) => (
              <div key={key} className="rounded-lg border p-2.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[9px] capitalize">{result.platform}</Badge>
                    <span className="text-[10px] font-medium">{result.route}</span>
                  </div>
                  {!result.error && (
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => copyContent(result.content)}>
                      <Copy className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                {result.error ? (
                  <p className="text-[10px] text-red-500">{result.error}</p>
                ) : (
                  <p className="text-xs whitespace-pre-wrap">{result.content}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
