"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton, EmptyState } from "@/components/ui/skeleton"
import { Users, Loader2, Save } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export function CompetitorTab({ onSave }: { onSave: (item: unknown) => void }) {
  const [topic, setTopic] = useState("")
  const [competitors, setCompetitors] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  const search = async () => {
    if (!competitors.trim()) return
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/research/competitors`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ competitors: competitors.split(",").map(c => c.trim()).filter(Boolean), niche: topic, provider: "openai" }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      setResult(await res.json())
    } catch (e) { setResult(null); setError(e instanceof Error ? e.message : "Failed to analyze competitors") }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-4 w-4" /> Competitor Analysis</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <Input placeholder="Niche or topic (e.g., 'fitness content')" value={topic} onChange={e => setTopic(e.target.value)} />
          <Input placeholder="Competitors (comma-separated, e.g., 'Athlean-X, Jeff Nippard')" value={competitors} onChange={e => setCompetitors(e.target.value)} />
          <Button onClick={search} disabled={loading || !competitors.trim()} className="gap-2 w-full">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Users className="h-4 w-4" />}
            Analyze Competitors
          </Button>
        </CardContent>
      </Card>

      {loading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-lg border p-4 space-y-2">
              <Skeleton className="h-4 w-[120px]" />
              <div className="flex gap-2"><Skeleton className="h-5 w-[80px] rounded-full" /><Skeleton className="h-5 w-[60px] rounded-full" /></div>
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

      {!loading && !error && !result && (
        <EmptyState icon="👥" title="No competitor data yet" description="Enter competitors above and click Analyze to discover content gaps and strengths." />
      )}

      {!loading && result && (
        <div className="space-y-3">
          {!!result.gaps && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Content Gaps</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {(result.gaps as string[]).map((gap, i) => <Badge key={i} variant="destructive">{gap}</Badge>)}
                </div>
              </CardContent>
            </Card>
          )}
          {!!result.strengths && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Your Strengths</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {(result.strengths as string[]).map((s, i) => <Badge key={i} variant="default">{s}</Badge>)}
                </div>
              </CardContent>
            </Card>
          )}
          {!!result.insights && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Insights</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{String(result.insights)}</p>
              </CardContent>
            </Card>
          )}
          <Button size="sm" variant="outline" className="gap-1" onClick={() => onSave({ category: "competitor", topic: topic || competitors, data: result, platform: "all" })}>
            <Save className="h-3 w-3" /> Save Analysis
          </Button>
        </div>
      )}
    </div>
  )
}
