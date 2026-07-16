"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { DollarSign, Eye, MousePointerClick, TrendingUp, Loader2 } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface Campaign { id: string; name: string; platform: string; status: string; budget: number; spent: number; impressions: number; clicks: number; conversions: number; ctr: number; roas: number }

export default function AdsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [pvOrg, setPvOrg] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetch(`${API_URL}/ads/campaigns`).then(r => r.json()),
      fetch(`${API_URL}/ads/paid-vs-organic`).then(r => r.json()),
    ]).then(([c, p]) => {
      if (c.status === "fulfilled") setCampaigns(c.value.campaigns || [])
      if (p.status === "fulfilled") setPvOrg(p.value)
    }).finally(() => setLoading(false))
  }, [])

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Ad Campaigns</h1><p className="text-muted-foreground">Track paid campaign performance vs organic.</p></div>
        {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : (
          <>
            {/* Campaign Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {campaigns.map((c) => (
                <Card key={c.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-medium">{c.name}</h4>
                        <p className="text-xs text-muted-foreground capitalize">{c.platform}</p>
                      </div>
                      <span className={`rounded-full px-2 py-0.5 text-xs ${c.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}`}>{c.status}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-3 text-center text-sm">
                      <div><DollarSign className="mx-auto h-4 w-4 text-muted-foreground" /><p className="font-bold">${c.spent.toLocaleString()}</p><p className="text-xs text-muted-foreground">/ ${c.budget.toLocaleString()}</p></div>
                      <div><Eye className="mx-auto h-4 w-4 text-muted-foreground" /><p className="font-bold">{(c.impressions / 1000).toFixed(1)}K</p><p className="text-xs text-muted-foreground">impressions</p></div>
                      <div><MousePointerClick className="mx-auto h-4 w-4 text-muted-foreground" /><p className="font-bold">{c.ctr}%</p><p className="text-xs text-muted-foreground">CTR</p></div>
                    </div>
                    <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                      <span>{c.conversions} conversions</span>
                      <span>ROAS: {c.roas}x</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Paid vs Organic */}
            <PaidVsOrganic />
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

function PaidVsOrganic() {
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  useEffect(() => { fetch(`${API_URL}/ads/paid-vs-organic`).then(r=>r.json()).then(setData).catch(()=>{}) }, [])
  if (!data) return null
  const organic = data.organic as Record<string, number> || {}
  const paid = data.paid as Record<string, number> || {}
  return (
    <Card>
      <CardHeader><CardTitle>Paid vs Organic Performance</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Organic Reach</p><p className="text-lg font-bold">{(organic.reach || 0).toLocaleString()}</p></div>
          <div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Paid Reach</p><p className="text-lg font-bold">{(paid.reach || 0).toLocaleString()}</p></div>
          <div className="rounded-lg border p-3"><p className="text-xs text-muted-00">Organic Cost</p><p className="text-lg font-bold text-green-600">$0</p></div>
          <div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Paid Cost</p><p className="text-lg font-bold">${(paid.cost || 0).toLocaleString()}</p></div>
        </div>
        {Boolean(data.insights) && (
          <div className="mt-4 space-y-2">{(data.insights as string[]).map((ins, i) => <p key={i} className="text-sm text-muted-foreground">💡 {ins}</p>)}</div>
        )}
      </CardContent>
    </Card>
  )
}
