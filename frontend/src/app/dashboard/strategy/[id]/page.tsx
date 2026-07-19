"use client"

import { useState, useEffect, use } from "react"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Play, Pause, BarChart3, Target, Loader2, CheckCircle, XCircle, Clock, Calendar } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Strategy { id: string; name: string; status: string; goals: string[]; content_pillars: string[]; posting_frequency: Record<string, string>; computed_stats: Record<string, number>; last_generated_at: string | null }
interface Plan { id: string; week_start: string; status: string; slot_count: number; approved_count: number }
interface Slot { id: string; pillar_name: string; platform: string; scheduled_date: string; scheduled_time: string; status: string; topic: string | null; generated_content: string | null; brand_voice_score: number | null }
interface Adherence { adherence_score: number; total_slots: number; published: number; approved: number; rejected: number; pillar_distribution: Record<string, number>; platform_distribution: Record<string, number>; recommendations: string[] }

const platformIcons: Record<string, string> = { linkedin: "💼", x: "🐦", instagram: "📸", facebook: "📘", youtube: "📺" }
const pillarColors: Record<string, string> = { "Industry Insights": "bg-blue-100 border-blue-300", "Educational Tips": "bg-yellow-100 border-yellow-300", "Behind the Scenes": "bg-green-100 border-green-300" }

export default function StrategyDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const [strategy, setStrategy] = useState<Strategy | null>(null)
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [slots, setSlots] = useState<Slot[]>([])
  const [adherence, setAdherence] = useState<Adherence | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => { fetchData() }, [id])

  async function fetchData() {
    const token = localStorage.getItem("token")
    const headers = { Authorization: `Bearer ${token}` }
    try {
      const [sRes, pRes, aRes] = await Promise.all([
        fetch(`${API_URL}/strategies/${id}`, { headers }),
        fetch(`${API_URL}/strategies/${id}/plans`, { headers }),
        fetch(`${API_URL}/strategies/${id}/adherence`, { headers }),
      ])
      if (sRes.ok) setStrategy(await sRes.json())
      if (pRes.ok) setPlans(await pRes.json())
      if (aRes.ok) setAdherence(await aRes.json())
    } catch (e) { console.error("Failed to load strategy") }
    setLoading(false)
  }

  async function loadPlan(planId: string) {
    const token = localStorage.getItem("token")
    const res = await fetch(`${API_URL}/strategies/${id}/plans/${planId}`, { headers: { Authorization: `Bearer ${token}` } })
    if (res.ok) { const data = await res.json(); setSlots(data.slots); setSelectedPlan({ id: data.id, week_start: data.week_start, status: data.status, slot_count: data.slot_count, approved_count: data.approved_count }) }
  }

  async function generate() {
    setGenerating(true)
    const token = localStorage.getItem("token")
    await fetch(`${API_URL}/strategies/${id}/generate`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ days_ahead: 7 }) })
    await fetchData()
    setGenerating(false)
  }

  async function approveSlot(slotId: string) {
    const token = localStorage.getItem("token")
    await fetch(`${API_URL}/slots/${slotId}/approve`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ comment: "" }) })
    setSlots(slots.map(s => s.id === slotId ? { ...s, status: "approved" } : s))
  }

  async function rejectSlot(slotId: string) {
    const token = localStorage.getItem("token")
    await fetch(`${API_URL}/slots/${slotId}/reject`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ reason: "Needs revision", category: "custom" }) })
    setSlots(slots.map(s => s.id === slotId ? { ...s, status: "rejected" } : s))
  }

  async function toggleStrategy() {
    const token = localStorage.getItem("token")
    const action = strategy?.status === "active" ? "pause" : "activate"
    await fetch(`${API_URL}/strategies/${id}/${action}`, { method: "POST", headers: { Authorization: `Bearer ${token}` } })
    await fetchData()
  }

  if (loading) return <DashboardLayout><div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin" /></div></DashboardLayout>
  if (!strategy) return <DashboardLayout><div className="p-6 text-center">Strategy not found</div></DashboardLayout>

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto p-6">
        <Link href="/dashboard/strategy" className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6">
          <ArrowLeft className="h-4 w-4" /> Strategies
        </Link>

        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{strategy.name}</h1>
            <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${strategy.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>{strategy.status}</span>
              <span>{strategy.computed_stats.total_posts_per_week} posts/week</span>
              <span>{Object.keys(strategy.computed_stats.pillar_balance).length} pillars</span>
            </div>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={toggleStrategy}>
              {strategy.status === "active" ? <><Pause className="h-4 w-4 mr-2" /> Pause</> : <><Play className="h-4 w-4 mr-2" /> Activate</>}
            </Button>
            <Button onClick={generate} disabled={generating}>
              {generating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Calendar className="h-4 w-4 mr-2" />}
              Generate Content
            </Button>
          </div>
        </div>

        {adherence && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <Card><CardContent className="p-4 text-center">
              <div className="text-3xl font-bold">{adherence.adherence_score}%</div>
              <div className="text-sm text-muted-foreground">Adherence Score</div>
            </CardContent></Card>
            <Card><CardContent className="p-4 text-center">
              <div className="text-3xl font-bold">{adherence.total_slots}</div>
              <div className="text-sm text-muted-foreground">Total Slots</div>
            </CardContent></Card>
            <Card><CardContent className="p-4 text-center">
              <div className="text-3xl font-bold text-green-600">{adherence.approved}</div>
              <div className="text-sm text-muted-foreground">Approved</div>
            </CardContent></Card>
            <Card><CardContent className="p-4 text-center">
              <div className="text-3xl font-bold text-red-600">{adherence.rejected}</div>
              <div className="text-sm text-muted-foreground">Rejected</div>
            </CardContent></Card>
          </div>
        )}

        {plans.length > 0 && !selectedPlan && (
          <Card className="mb-6">
            <CardHeader><CardTitle>Content Plans</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-2">
                {plans.map((p) => (
                  <div key={p.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted cursor-pointer" onClick={() => loadPlan(p.id)}>
                    <div>
                      <span className="font-medium">Week of {new Date(p.week_start).toLocaleDateString()}</span>
                      <span className="ml-3 text-sm text-muted-foreground">{p.slot_count} slots, {p.approved_count} approved</span>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs ${p.status === "completed" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"}`}>{p.status}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {selectedPlan && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Content Plan — Week of {new Date(selectedPlan.week_start).toLocaleDateString()}</CardTitle>
              <Button variant="outline" size="sm" onClick={() => { setSelectedPlan(null); setSlots([]) }}>Back to Plans</Button>
            </CardHeader>
            <CardContent>
              {slots.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No slots in this plan</p>
              ) : (
                <div className="space-y-3">
                  {slots.map((slot) => (
                    <div key={slot.id} className={`border rounded-lg p-4 ${pillarColors[slot.pillar_name] || "bg-muted"}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">{platformIcons[slot.platform] || "📱"}</span>
                            <span className="font-medium capitalize">{slot.platform}</span>
                            <span className="text-sm text-muted-foreground">{slot.scheduled_date} at {slot.scheduled_time}</span>
                            <span className="px-2 py-0.5 rounded text-xs bg-white/50">{slot.pillar_name}</span>
                          </div>
                          {slot.generated_content ? (
                            <p className="text-sm mt-2 whitespace-pre-wrap">{slot.generated_content}</p>
                          ) : (
                            <p className="text-sm text-muted-foreground italic mt-2">No content generated yet</p>
                          )}
                        </div>
                        <div className="flex gap-2 ml-4">
                          {slot.status === "empty" || slot.status === "pending_approval" ? (
                            <>
                              <Button size="sm" variant="outline" onClick={() => approveSlot(slot.id)}><CheckCircle className="h-4 w-4" /></Button>
                              <Button size="sm" variant="outline" onClick={() => rejectSlot(slot.id)}><XCircle className="h-4 w-4" /></Button>
                            </>
                          ) : (
                            <span className={`px-2 py-1 rounded text-xs ${slot.status === "approved" ? "bg-green-100 text-green-800" : slot.status === "rejected" ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-800"}`}>{slot.status}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
