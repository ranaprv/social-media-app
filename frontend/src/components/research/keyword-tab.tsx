"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { SkeletonResearchCard, EmptyState } from "@/components/ui/skeleton"
import { VideoSEOGauge } from "./video-seo-gauge"
import { Search, Loader2, Save, TrendingUp } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Keyword {
  keyword: string
  search_volume: string
  keyword_difficulty: number
  competition_level: string
  video_seo_score: number
  platform_relevance?: Record<string, number>
}

export function KeywordTab({ onSave }: { onSave: (item: unknown) => void }) {
  const [topic, setTopic] = useState("")
  const [loading, setLoading] = useState(false)
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [meta, setMeta] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  const search = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/research/keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ topic, platform: "all", niche: topic }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      setKeywords(data.keywords || [])
      setMeta(data)
    } catch (e) { setKeywords([]); setMeta(null); setError(e instanceof Error ? e.message : "Failed to fetch keywords") }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Search className="h-4 w-4" /> Keyword Research</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input placeholder="Enter topic (e.g., 'react hooks tutorial')" value={topic} onChange={e => setTopic(e.target.value)} onKeyDown={e => e.key === "Enter" && search()} />
            <Button onClick={search} disabled={loading || !topic.trim()} className="gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Research
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading && <SkeletonResearchCard count={4} />}

      {error && (
        <Card>
          <CardContent className="py-6 text-center">
            <p className="text-sm text-destructive">{error}</p>
            <Button size="sm" variant="outline" className="mt-2" onClick={search}>Retry</Button>
          </CardContent>
        </Card>
      )}

      {!loading && !error && keywords.length === 0 && !meta && (
        <EmptyState icon="🔑" title="No keywords yet" description="Enter a topic above and click Research to discover Video SEO keywords." />
      )}

      {!loading && keywords.length > 0 && (
        <div className="grid gap-3 md:grid-cols-2">
          {keywords.map((kw, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h4 className="font-medium">{kw.keyword}</h4>
                    <div className="flex gap-2 text-xs text-muted-foreground">
                      <span>Volume: {kw.search_volume}</span>
                      <span>Difficulty: {kw.keyword_difficulty}/100</span>
                      <span>Competition: {kw.competition_level}</span>
                    </div>
                    <div className="flex gap-1 mt-1">
                      {kw.platform_relevance && Object.entries(kw.platform_relevance).map(([p, score]) => (
                        <Badge key={p} variant="outline" className="text-[10px]">{p}: {String(score)}</Badge>
                      ))}
                    </div>
                  </div>
                  <VideoSEOGauge score={kw.video_seo_score} size="sm" />
                </div>
                <Button size="sm" variant="ghost" className="mt-2 gap-1" onClick={() => onSave({ category: "keyword", topic: kw.keyword, data: kw, platform: "all" })}>
                  <Save className="h-3 w-3" /> Save
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {meta && !!(meta as Record<string, unknown>).long_tail_opportunities && (
        <Card>
          <CardHeader><CardTitle className="text-sm flex items-center gap-2"><TrendingUp className="h-4 w-4" /> Long-tail Opportunities</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {((meta as Record<string, unknown>).long_tail_opportunities as string[]).map((lt, i) => (
                <Badge key={i} variant="secondary">{lt}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
