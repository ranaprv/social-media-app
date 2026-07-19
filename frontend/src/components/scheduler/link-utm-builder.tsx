"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Link2,
  Copy,
  ExternalLink,
  Loader2,
  Tag,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface UTMResult {
  original_url: string
  tagged_url: string
  platform: string
  utm_params: Record<string, string>
  url_length: number
  max_length: number
  needs_shortening: boolean
}

interface LinkUTMBuilderProps {
  initialUrl?: string
  platform?: Platform
}

export function LinkUTMBuilder({ initialUrl = "", platform = "linkedin" }: LinkUTMBuilderProps) {
  const [url, setUrl] = useState(initialUrl)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [campaign, setCampaign] = useState("")
  const [contentType, setContentType] = useState("")
  const [results, setResults] = useState<UTMResult[]>([])
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)

  const buildUTM = async (multi = false) => {
    if (!url) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const endpoint = multi ? "/scheduler/utm/build-multi" : "/scheduler/utm/build"
      const body = multi
        ? { url, platforms: ["linkedin", "x", "instagram", "facebook", "youtube"], campaign_name: campaign, content_type: contentType }
        : { url, platform: selectedPlatform, campaign_name: campaign, content_type: contentType }

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      })

      if (response.ok) {
        const data = await response.json()
        setResults(multi ? Object.values(data) : [data])
      }
    } finally {
      setLoading(false)
    }
  }

  const copyUrl = async (taggedUrl: string, platform: string) => {
    await navigator.clipboard.writeText(taggedUrl)
    setCopied(platform)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Link2 className="h-4 w-4" />
          Link & UTM Builder
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* URL input */}
        <div>
          <label className="text-xs font-medium text-muted-foreground mb-1 block">URL</label>
          <Input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/your-page"
            className="text-sm"
          />
        </div>

        {/* Platform + Campaign */}
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
            <label className="text-xs font-medium text-muted-foreground mb-1 block">Campaign</label>
            <Input
              value={campaign}
              onChange={(e) => setCampaign(e.target.value)}
              placeholder="e.g. product_launch_q3"
              className="text-sm"
            />
          </div>
        </div>

        <Input
          value={contentType}
          onChange={(e) => setContentType(e.target.value)}
          placeholder="Content type (optional, e.g. blog_post, video)"
          className="text-sm"
        />

        {/* Buttons */}
        <div className="flex gap-2">
          <Button onClick={() => buildUTM(false)} disabled={loading || !url} size="sm" className="flex-1 gap-1">
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Tag className="h-3.5 w-3.5" />}
            Build UTM
          </Button>
          <Button onClick={() => buildUTM(true)} disabled={loading || !url} variant="outline" size="sm" className="flex-1 gap-1">
            All Platforms
          </Button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-2 pt-2 border-t">
            {results.map((r, i) => (
              <div key={i} className="rounded-lg border p-2.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[10px] capitalize">{r.platform}</Badge>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-muted-foreground">{r.url_length} chars</span>
                    {r.needs_shortening && (
                      <Badge variant="destructive" className="text-[10px]">Needs shortening</Badge>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <code className="text-[10px] bg-muted px-1.5 py-0.5 rounded flex-1 truncate">
                    {r.tagged_url}
                  </code>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0"
                    onClick={() => copyUrl(r.tagged_url, r.platform)}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
                {copied === r.platform && (
                  <span className="text-[10px] text-green-600">Copied!</span>
                )}
                <div className="flex flex-wrap gap-1">
                  {Object.entries(r.utm_params).map(([key, val]) => (
                    <Badge key={key} variant="secondary" className="text-[9px]">
                      {key}={val}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
