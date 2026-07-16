"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Share2, Users, BarChart3, Loader2, ExternalLink, Copy, Check } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface Shareable { id: string; title: string; platform: string; share_text: string; url: string; shares_count: number }
interface Metrics { total_shares: number; total_reach_from_shares: number; active_advocates: number; top_advocates: Array<{ name: string; shares: number; reach: number }> }

export default function AdvocacyPage() {
  const [shareable, setShareable] = useState<Shareable[]>([])
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  useEffect(() => {
    Promise.allSettled([
      fetch(`${API_URL}/advocacy/shareable`).then(r => r.json()),
      fetch(`${API_URL}/advocacy/metrics`).then(r => r.json()),
    ]).then(([s, m]) => {
      if (s.status === "fulfilled") setShareable(s.value.shareable || [])
      if (m.status === "fulfilled") setMetrics(m.value)
    }).finally(() => setLoading(false))
  }, [])

  const share = async (id: string, platform: string) => {
    await fetch(`${API_URL}/advocacy/share`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ post_id: id, platform }) })
  }

  const copyText = (text: string, id: string) => { navigator.clipboard.writeText(text); setCopiedId(id); setTimeout(() => setCopiedId(null), 2000) }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Employee Advocacy</h1><p className="text-muted-foreground">Share approved content on your personal networks.</p></div>

        {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : (
          <>
            {metrics && (
              <div className="grid gap-4 md:grid-cols-4">
                <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Total Shares</p><p className="text-2xl font-bold">{metrics.total_shares}</p></CardContent></Card>
                <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Reach from Shares</p><p className="text-2xl font-bold">{(metrics.total_reach_from_shares / 1000).toFixed(1)}K</p></CardContent></Card>
                <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Active Advocates</p><p className="text-2xl font-bold">{metrics.active_advocates}</p></CardContent></Card>
                <Card><CardContent className="pt-4"><p className="text-xs text-muted-foreground">Top Advocate</p><p className="text-2xl font-bold">{metrics.top_advocates[0]?.name || "—"}</p></CardContent></Card>
              </div>
            )}

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Share2 className="h-5 w-5 text-primary" /> Shareable Content</CardTitle></CardHeader>
              <CardContent><div className="space-y-3">
                {shareable.map((s) => (
                  <div key={s.id} className="rounded-lg border p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">{s.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{s.share_text}</p>
                        <p className="text-xs text-muted-foreground mt-1">{s.shares_count} shares</p>
                      </div>
                      <div className="flex gap-1 ml-3">
                        <Button size="sm" variant="ghost" onClick={() => copyText(s.share_text, s.id)}>{copiedId === s.id ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}</Button>
                        <Button size="sm" variant="outline" onClick={() => share(s.id, "linkedin")}>LinkedIn</Button>
                        <Button size="sm" variant="outline" onClick={() => share(s.id, "x")}>X</Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div></CardContent>
            </Card>

            {metrics?.top_advocates && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-5 w-5 text-primary" /> Top Advocates</CardTitle></CardHeader>
                <CardContent><div className="space-y-2">
                  {metrics.top_advocates.map((a, i) => (
                    <div key={i} className="flex items-center justify-between rounded-lg border p-3">
                      <div className="flex items-center gap-3"><span className="text-lg font-bold text-muted-foreground">#{i + 1}</span><span className="font-medium">{a.name}</span></div>
                      <div className="flex gap-4 text-sm text-muted-foreground"><span>{a.shares} shares</span><span>{a.reach.toLocaleString()} reach</span></div>
                    </div>
                  ))}
                </div></CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
