"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import {
  Wand2,
  Copy,
  RefreshCw,
  Loader2,
  Sparkles,
  Hash,
  MessageSquare,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface CaptionResult {
  caption: string
  platform: string
  char_count: number
  word_count: number
  hashtags: string[]
  has_cta: boolean
  error?: string
}

interface AICaptionGeneratorProps {
  initialTopic?: string
  platform?: Platform
}

export function AICaptionGenerator({ initialTopic = "", platform = "linkedin" }: AICaptionGeneratorProps) {
  const [topic, setTopic] = useState(initialTopic)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [tone, setTone] = useState("professional")
  const [keywords, setKeywords] = useState("")
  const [result, setResult] = useState<CaptionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const generate = async () => {
    if (!topic) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/captions/generate`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          topic,
          platform: selectedPlatform,
          tone,
          keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
        }),
      })

      if (response.ok) setResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  const copyCaption = async () => {
    if (!result?.caption) return
    await navigator.clipboard.writeText(result.caption)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Wand2 className="h-4 w-4" />
          AI Caption Generator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Topic */}
        <div>
          <label className="text-xs font-medium text-muted-foreground mb-1 block">Topic</label>
          <Input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. 5 tips for better content creation"
            className="text-sm"
          />
        </div>

        {/* Platform + Tone */}
        <div className="grid grid-cols-2 gap-2">
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
            <label className="text-xs font-medium text-muted-foreground mb-1 block">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="rounded-md border border-border bg-background px-2 py-1 text-sm w-full"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="humorous">Humorous</option>
              <option value="inspirational">Inspirational</option>
              <option value="educational">Educational</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        {/* Keywords */}
        <Input
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          placeholder="Keywords (comma separated)"
          className="text-sm"
        />

        {/* Generate */}
        <Button onClick={generate} disabled={loading || !topic} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Sparkles className="h-4 w-4 mr-2" />}
          {loading ? "Generating..." : "Generate Caption"}
        </Button>

        {/* Result */}
        {result && !result.error && (
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="text-[10px] capitalize">{result.platform}</Badge>
              <span className="text-[10px] text-muted-foreground">
                {result.char_count} chars · {result.word_count} words
              </span>
            </div>

            <div className="relative">
              <Textarea
                value={result.caption}
                readOnly
                className="min-h-[100px] text-sm pr-16"
              />
              <div className="absolute top-2 right-2 flex gap-1">
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={copyCaption}>
                  <Copy className="h-3 w-3" />
                </Button>
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={generate}>
                  <RefreshCw className="h-3 w-3" />
                </Button>
              </div>
              {copied && (
                <span className="absolute top-2 right-20 text-[10px] text-green-600">Copied!</span>
              )}
            </div>

            {/* Hashtags */}
            {result.hashtags.length > 0 && (
              <div className="flex items-center gap-1 flex-wrap">
                <Hash className="h-3 w-3 text-muted-foreground" />
                {result.hashtags.map((tag, i) => (
                  <Badge key={i} variant="secondary" className="text-[9px]">{tag}</Badge>
                ))}
              </div>
            )}

            {/* Indicators */}
            <div className="flex gap-2">
              {result.has_cta && (
                <Badge variant="default" className="text-[9px] bg-green-600">
                  <MessageSquare className="h-2.5 w-2.5 mr-0.5" /> Has CTA
                </Badge>
              )}
              {!result.has_cta && (
                <Badge variant="outline" className="text-[9px]">
                  No CTA
                </Badge>
              )}
            </div>
          </div>
        )}

        {result?.error && (
          <p className="text-xs text-red-500 text-center py-2">{result.error}</p>
        )}
      </CardContent>
    </Card>
  )
}
