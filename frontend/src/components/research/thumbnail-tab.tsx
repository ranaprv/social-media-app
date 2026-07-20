"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/skeleton"
import { VideoSEOGauge } from "./video-seo-gauge"
import { Film, Loader2, Save } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface TitleVariant {
  title: string
  predicted_ctr: number
  hook_type: string
  why_it_works: string
}

export function ThumbnailTab({ onSave }: { onSave: (item: unknown) => void }) {
  const [topic, setTopic] = useState("")
  const [loading, setLoading] = useState(false)
  const [variants, setVariants] = useState<TitleVariant[]>([])
  const [error, setError] = useState<string | null>(null)

  const search = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/research/thumbnails`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ topic, platform: "youtube", variant_count: 5, provider: "openai" }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      setVariants(data.variants || [])
    } catch (e) { setVariants([]); setError(e instanceof Error ? e.message : "Failed to generate title variants") }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Film className="h-4 w-4" /> Thumbnail & Title Testing</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input placeholder="Enter topic for title variants" value={topic} onChange={e => setTopic(e.target.value)} onKeyDown={e => e.key === "Enter" && search()} />
            <Button onClick={search} disabled={loading || !topic.trim()} className="gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Film className="h-4 w-4" />}
              Test Titles
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-lg border p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div className="space-y-2 flex-1"><Skeleton className="h-4 w-[200px]" /><div className="flex gap-2"><Skeleton className="h-5 w-[80px] rounded-full" /><Skeleton className="h-5 w-[60px] rounded-full" /></div></div>
                <Skeleton className="h-12 w-12 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <Card>
          <CardContent className="py-6 text-center">
            <p className="text-sm text-destructive">{error}</p>
            <Button size="sm" variant="outline" className="mt-2" onClick={search}>Retry</Button>
          </CardContent>
        </Card>
      )}

      {!loading && !error && variants.length === 0 && (
        <EmptyState icon="🎬" title="No title variants yet" description="Enter a topic above and click Test Titles to generate CTR-optimized title options." />
      )}

      {!loading && variants.length > 0 && (
        <div className="space-y-3">
          {variants.map((v, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1 flex-1">
                    <h4 className="font-medium">{v.title}</h4>
                    <div className="flex gap-2 mt-1">
                      <Badge variant="outline">Hook: {v.hook_type}</Badge>
                      <Badge variant="outline">CTR: {v.predicted_ctr}%</Badge>
                    </div>
                    {v.why_it_works && (
                      <p className="text-xs text-muted-foreground mt-1">💡 {v.why_it_works}</p>
                    )}
                  </div>
                  <VideoSEOGauge score={v.predicted_ctr} size="sm" />
                </div>
                <Button size="sm" variant="ghost" className="mt-2 gap-1" onClick={() => onSave({ category: "thumbnail", topic: topic, data: v, platform: "youtube" })}>
                  <Save className="h-3 w-3" /> Save
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
