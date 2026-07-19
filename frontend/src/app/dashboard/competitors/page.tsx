"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Loader2, Trash2, BarChart3, ArrowUpRight, ArrowDownRight } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Competitor { id: string; name: string; platforms: string[]; followers: number; avg_engagement_rate: number; posts_per_week: number; top_content_type: string }

export default function CompetitorsPage() {
  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [loading, setLoading] = useState(true)
  const [newName, setNewName] = useState("")
  const [comparison, setComparison] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [compRes, compRes2] = await Promise.allSettled([
          fetch(`${API_URL}/competitors`), fetch(`${API_URL}/competitors/compare`),
        ])
        if (compRes.status === "fulfilled" && compRes.value.ok) { const d = await compRes.value.json(); setCompetitors(d.competitors || []) }
        if (compRes2.status === "fulfilled" && compRes2.value.ok) setComparison(await compRes2.value.json())
      } catch {} finally { setLoading(false) }
    }
    load()
  }, [])

  const addCompetitor = async () => {
    if (!newName.trim()) return
    const res = await fetch(`${API_URL}/competitors`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: newName }) })
    if (res.ok) { const data = await res.json(); setCompetitors((p) => [...p, data]); setNewName("") }
  }

  const removeCompetitor = async (id: string) => {
    await fetch(`${API_URL}/competitors/${id}`, { method: "DELETE" })
    setCompetitors((p) => p.filter((c) => c.id !== id))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Competitors</h1><p className="text-muted-foreground">Track competitor performance and compare strategies.</p></div>

        <Card><CardContent className="pt-6"><div className="flex gap-3">
          <Input placeholder="Competitor name or handle..." value={newName} onChange={(e) => setNewName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addCompetitor()} />
          <Button onClick={addCompetitor} className="gap-2" disabled={!newName.trim()}><Plus className="h-4 w-4" /> Track</Button>
        </div></CardContent></Card>

        {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : (
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {competitors.map((c) => (
                <Card key={c.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium text-lg">{c.name}</h4>
                      <Button variant="ghost" size="sm" onClick={() => removeCompetitor(c.id)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
                    </div>
                    <div className="flex gap-1 mb-3">{c.platforms.map((p) => <span key={p} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary capitalize">{p}</span>)}</div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><p className="text-muted-foreground">Followers</p><p className="font-bold">{(c.followers / 1000).toFixed(0)}K</p></div>
                      <div><p className="text-muted-foreground">Eng. Rate</p><p className="font-bold">{c.avg_engagement_rate}%</p></div>
                      <div><p className="text-muted-foreground">Posts/Week</p><p className="font-bold">{c.posts_per_week}</p></div>
                      <div><p className="text-muted-foreground">Top Type</p><p className="font-bold capitalize">{c.top_content_type}</p></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {comparison && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5 text-primary" /> Your Performance vs Competitors</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    {["followers", "engagement_rate", "posts_per_week", "avg_reach"].map((metric) => {
                      const own = (comparison as Record<string, Record<string, number>>).own?.[metric] ?? 0
                      const avg = (comparison as Record<string, Record<string, number>>).competitors_avg?.[metric] ?? 0
                      const better = own > avg
                      return (<div key={metric} className="rounded-lg border p-3"><p className="text-xs text-muted-foreground capitalize">{metric.replace(/_/g, " ")}</p><p className="text-lg font-bold">{typeof own === "number" && own > 1000 ? (own / 1000).toFixed(1) + "K" : own}</p><p className={`text-xs ${better ? "text-green-600" : "text-red-600"}`}>{better ? <ArrowUpRight className="inline h-3 w-3" /> : <ArrowDownRight className="inline h-3 w-3" />} vs avg {avg}</p></div>)
                    })}
                  </div>
                  {Boolean(comparison.verdict) && <p className="text-sm text-muted-foreground mt-2">{String(comparison.verdict)}</p>}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
