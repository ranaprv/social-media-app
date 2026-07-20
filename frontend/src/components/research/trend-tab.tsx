"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/skeleton"
import { TrendingUp, TrendingDown, Minus, Loader2, Save, BarChart3, AlertTriangle } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const directionIcon = (dir: string) => {
  if (dir === "rising") return <TrendingUp className="h-4 w-4 text-green-500" />
  if (dir === "declining") return <TrendingDown className="h-4 w-4 text-red-500" />
  return <Minus className="h-4 w-4 text-yellow-500" />
}

const directionBadge = (dir: string) => {
  const cls = dir === "rising" ? "bg-green-100 text-green-700" : dir === "declining" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"
  return <Badge className={cls}>{dir}</Badge>
}

export function TrendTab({ onSave }: { onSave: (item: unknown) => void }) {
  const [topic, setTopic] = useState("")
  const [loading, setLoading] = useState(false)
  const [trends, setTrends] = useState<Array<Record<string, unknown>>>([])
  const [meta, setMeta] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  const isStale = (item: Record<string, unknown>) => {
    const expires = item.expires_at
    if (!expires) return false
    return new Date(String(expires)) < new Date()
  }

  const search = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/research/trends`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ topic, platform: "all", provider: "openai" }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      setTrends(data.trends || [])
      setMeta(data)
    } catch (e) { setTrends([]); setMeta(null); setError(e instanceof Error ? e.message : "Failed to fetch trends") }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="h-4 w-4" /> Trend Analysis</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input placeholder="Enter topic (e.g., 'AI tools 2026')" value={topic} onChange={e => setTopic(e.target.value)} onKeyDown={e => e.key === "Enter" && search()} />
            <Button onClick={search} disabled={loading || !topic.trim()} className="gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <TrendingUp className="h-4 w-4" />}
              Analyze Trends
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-lg border p-4 space-y-2">
              <Skeleton className="h-4 w-[180px]" />
              <Skeleton className="h-3 w-full" />
              <div className="flex gap-2"><Skeleton className="h-5 w-[70px] rounded-full" /><Skeleton className="h-5 w-[90px] rounded-full" /></div>
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

      {!loading && !error && trends.length === 0 && !meta && (
        <EmptyState icon="📈" title="No trends yet" description="Enter a topic above and click Analyze Trends to discover rising and declining topics." />
      )}

      {!loading && trends.length > 0 && (
        <div className="space-y-3">
          {trends.map((trend, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h4 className="font-medium flex items-center gap-2">
                      {directionIcon(String(trend.trend_direction))}
                      {String(trend.topic)}
                    </h4>
                    <p className="text-sm text-muted-foreground">{String(trend.description)}</p>
                    <div className="flex gap-2 mt-1">
                      {directionBadge(String(trend.trend_direction))}
                      <Badge variant="outline">Popularity: {String(trend.popularity)}</Badge>
                      <Badge variant="outline">{String(trend.platform)}</Badge>
                      {isStale(trend) && (
                        <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-300 gap-1">
                          <AlertTriangle className="h-3 w-3" /> Stale
                        </Badge>
                      )}
                    </div>
                    {!!trend.content_opportunity && (
                      <p className="text-xs text-muted-foreground mt-1 italic">💡 {String(trend.content_opportunity)}</p>
                    )}
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => onSave({ category: "trend", topic: String(trend.topic), data: trend, platform: String(trend.platform) })}>
                    <Save className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {meta && !!(meta as Record<string, unknown>).related_topics && (
        <Card>
          <CardHeader><CardTitle className="text-sm flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Related Topics</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {(meta.related_topics as string[]).map((rt, i) => <Badge key={i} variant="secondary">{rt}</Badge>)}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
