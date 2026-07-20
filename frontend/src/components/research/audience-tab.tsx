"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/skeleton"
import { BarChart3, Loader2, Save, Clock } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export function AudienceTab({ onSave }: { onSave: (item: unknown) => void }) {
  const [topic, setTopic] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  const search = async () => {
    if (!topic.trim()) return
    setLoading(true)
    setError(null)
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/research/audience`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ platform: "all", niche: topic, provider: "openai" }),
      })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      setResult(await res.json())
    } catch (e) { setResult(null); setError(e instanceof Error ? e.message : "Failed to analyze audience") }
    finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Audience Analytics</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input placeholder="Enter your niche (e.g., 'fitness coaching')" value={topic} onChange={e => setTopic(e.target.value)} onKeyDown={e => e.key === "Enter" && search()} />
            <Button onClick={search} disabled={loading || !topic.trim()} className="gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <BarChart3 className="h-4 w-4" />}
              Analyze Audience
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading && (
        <div className="grid gap-3 md:grid-cols-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-lg border p-4 space-y-2">
              <Skeleton className="h-4 w-[100px]" />
              <div className="space-y-1.5">
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
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

      {!loading && !error && !result && (
        <EmptyState icon="📊" title="No audience data yet" description="Enter your niche above and click Analyze Audience to discover demographics and peak hours." />
      )}

      {!loading && result && (
        <div className="grid gap-3 md:grid-cols-2">
          {!!result.demographics && (
            <Card>
              <CardHeader><CardTitle className="text-sm">Demographics</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(result.demographics as Record<string, string>).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm">
                      <span className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</span>
                      <span className="font-medium">{v}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {!!result.peak_hours && (
            <Card>
              <CardHeader><CardTitle className="text-sm flex items-center gap-2"><Clock className="h-4 w-4" /> Peak Hours</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {(Array.isArray(result.peak_hours) ? result.peak_hours : [result.peak_hours]).map((h, i) => (
                    <Badge key={i} variant="outline">{String(h)}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {!!result.content_preferences && (
            <Card className="md:col-span-2">
              <CardHeader><CardTitle className="text-sm">Content Preferences</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {(result.content_preferences as string[]).map((p, i) => (
                    <Badge key={i} variant="secondary">{p}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          <Button size="sm" variant="outline" className="gap-1 md:col-span-2" onClick={() => onSave({ category: "audience", topic, data: result, platform: "all" })}>
            <Save className="h-3 w-3" /> Save Audience Data
          </Button>
        </div>
      )}
    </div>
  )
}
