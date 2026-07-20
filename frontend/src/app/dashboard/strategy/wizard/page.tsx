"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ArrowLeft, ArrowRight, Target, BookOpen, Users, Clock, Mic, Check, Lightbulb } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Pillar { name: string; description: string; weight: number; platforms: string[]; tone: string; example_hooks: string[]; content_types: string[] }
interface Goal { type: string; target: number; platform: string; period: string; baseline: number }
interface Persona { name: string; demographics: Record<string, string>; pain_points: string[]; content_preferences: string[] }
interface Frequency { posts_per_week: number; preferred_days: number[]; preferred_hours: number[] }

const STEPS = ["Goals", "Pillars", "Audience", "Frequency", "Brand Voice", "Review"]
const STEP_ICONS = [Target, BookOpen, Users, Clock, Mic, Check]

export default function StrategyWizard() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [name, setName] = useState("My Content Strategy")
  const [goals, setGoals] = useState<Goal[]>([{ type: "engagement_rate", target: 4.5, platform: "all", period: "quarterly", baseline: 2.0 }])
  const [pillars, setPillars] = useState<Pillar[]>([
    { name: "Industry Insights", description: "Trends, analysis, and professional opinions", weight: 0.4, platforms: ["linkedin", "x"], tone: "authoritative", example_hooks: ["Here's what most people get wrong about..."], content_types: ["text_post"] },
    { name: "Educational Tips", description: "How-to guides, tutorials, best practices", weight: 0.35, platforms: ["linkedin", "x"], tone: "friendly", example_hooks: ["3 things I wish I knew before..."], content_types: ["text_post", "thread"] },
    { name: "Behind the Scenes", description: "Company culture, team stories, day-in-the-life", weight: 0.25, platforms: ["linkedin", "x"], tone: "casual", example_hooks: ["What our mornings look like..."], content_types: ["text_post"] },
  ])
  const [personas, setPersonas] = useState<Persona[]>([{ name: "General Audience", demographics: {}, pain_points: [], content_preferences: [] }])
  const [frequency, setFrequency] = useState<Record<string, Frequency>>({
    linkedin: { posts_per_week: 3, preferred_days: [1, 2, 3], preferred_hours: [9, 12, 17] },
    x: { posts_per_week: 5, preferred_days: [0, 1, 2, 3, 4], preferred_hours: [8, 12, 17, 20] },
  })
  const [submitting, setSubmitting] = useState(false)
  const [researchItems, setResearchItems] = useState<Array<{ topic: string; category: string; pillar?: string; score?: number }>>([])
  const [researchLoaded, setResearchLoaded] = useState(false)

  // Load research items from localStorage on mount
  useEffect(() => {
    try {
      const items = JSON.parse(localStorage.getItem("research_strategy_items") || "[]")
      setResearchItems(items)
    } catch { setResearchItems([]) }
  }, [])

  function loadFromResearch() {
    if (researchItems.length === 0) return
    const topics = researchItems.map(r => r.topic)
    const uniqueTopics = [...new Set(topics)].slice(0, 5)
    const newPillars: Pillar[] = uniqueTopics.map((topic, i) => ({
      name: topic,
      description: researchItems.find(r => r.topic === topic)?.category ? `Researched ${researchItems.find(r => r.topic === topic)!.category} topic` : "From research",
      weight: i === 0 ? 0.4 : i === 1 ? 0.3 : 0.3 / Math.max(1, uniqueTopics.length - 2),
      platforms: ["linkedin", "x"],
      tone: "professional",
      example_hooks: [`Here's what we found about ${topic}...`],
      content_types: ["text_post"],
    }))
    setPillars(newPillars)
    setResearchLoaded(true)
  }

  async function handleCreate(activate: boolean = false) {
    setSubmitting(true)
    try {
      const token = localStorage.getItem("token")
      const body = { name, goals, content_pillars: pillars, audience_personas: personas, posting_frequency: frequency, auto_generate: true, generate_ahead_days: 7, approval_required: true }
      const res = await fetch(`${API_URL}/strategies/`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      })
      if (res.ok) {
        const data = await res.json()
        if (activate) {
          await fetch(`${API_URL}/strategies/${data.id}/activate`, { method: "POST", headers: { Authorization: `Bearer ${token}` } })
        }
        router.push(`/dashboard/strategy/${data.id}`)
      }
    } catch (e) {
      console.error("Failed to create strategy")
    } finally {
      setSubmitting(false)
    }
  }

  function addPillar() {
    if (pillars.length < 5) setPillars([...pillars, { name: "", description: "", weight: 0.2, platforms: [], tone: "professional", example_hooks: [], content_types: ["text_post"] }])
  }

  function updatePillar(idx: number, field: string, value: string | number | string[]) {
    const updated = [...pillars]; (updated[idx] as unknown as Record<string, unknown>)[field] = value; setPillars(updated)
  }

  const totalPerWeek = Object.values(frequency).reduce((sum, f) => sum + f.posts_per_week, 0)

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto p-6">
        <button onClick={() => router.back()} className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6">
          <ArrowLeft className="h-4 w-4" /> Back to Strategies
        </button>

        <div className="flex items-center gap-4 mb-8">
          {STEPS.map((s, i) => {
            const Icon = STEP_ICONS[i]
            return (
              <div key={s} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium ${i === step ? "bg-primary text-primary-foreground" : i < step ? "bg-green-100 text-green-800" : "bg-muted text-muted-foreground"}`}>
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{s}</span>
              </div>
            )
          })}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{STEPS[step]} {step === 0 && <Input value={name} onChange={(e) => setName(e.target.value)} className="mt-2" placeholder="Strategy name" />}</CardTitle>
          </CardHeader>
          <CardContent>
            {step === 0 && (
              <div className="space-y-4">
                {goals.map((g, i) => (
                  <div key={i} className="flex gap-3 items-center">
                    <select value={g.type} onChange={(e) => { const u = [...goals]; u[i].type = e.target.value; setGoals(u) }} className="border rounded px-3 py-2">
                      <option value="engagement_rate">Engagement Rate</option>
                      <option value="follower_growth">Follower Growth</option>
                      <option value="lead_generation">Lead Generation</option>
                      <option value="brand_awareness">Brand Awareness</option>
                    </select>
                    <Input type="number" value={g.target} onChange={(e) => { const u = [...goals]; u[i].target = Number(e.target.value); setGoals(u) }} className="w-24" placeholder="Target" />
                    <select value={g.period} onChange={(e) => { const u = [...goals]; u[i].period = e.target.value; setGoals(u) }} className="border rounded px-3 py-2">
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="quarterly">Quarterly</option>
                    </select>
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={() => setGoals([...goals, { type: "engagement_rate", target: 0, platform: "all", period: "monthly", baseline: 0 }])}>+ Add Goal</Button>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {researchItems.length > 0 && (
                      <Button variant="outline" size="sm" onClick={loadFromResearch} className="gap-1 text-xs">
                        <Lightbulb className="h-3 w-3" /> Load from Research ({researchItems.length} items)
                      </Button>
                    )}
                    {researchLoaded && <span className="text-xs text-green-600">Pre-populated from research</span>}
                  </div>
                </div>
                {pillars.map((p, i) => (
                  <div key={i} className="border rounded-lg p-4 space-y-3">
                    <div className="flex gap-3">
                      <Input value={p.name} onChange={(e) => updatePillar(i, "name", e.target.value)} placeholder="Pillar name" className="flex-1" />
                      <Input type="number" value={p.weight} onChange={(e) => updatePillar(i, "weight", Number(e.target.value))} className="w-24" placeholder="Weight" step="0.05" />
                    </div>
                    <Input value={p.description} onChange={(e) => updatePillar(i, "description", e.target.value)} placeholder="Description" />
                    <Input value={p.example_hooks.join(", ")} onChange={(e) => updatePillar(i, "example_hooks", e.target.value.split(",").map((s: string) => s.trim()))} placeholder="Example hooks (comma separated)" />
                  </div>
                ))}
                {pillars.length < 5 && <Button variant="outline" size="sm" onClick={addPillar}>+ Add Pillar</Button>}
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                {personas.map((p, i) => (
                  <div key={i} className="border rounded-lg p-4 space-y-3">
                    <Input value={p.name} onChange={(e) => { const u = [...personas]; u[i].name = e.target.value; setPersonas(u) }} placeholder="Persona name" />
                    <Input value={p.pain_points.join(", ")} onChange={(e) => { const u = [...personas]; u[i].pain_points = e.target.value.split(",").map((s: string) => s.trim()); setPersonas(u) }} placeholder="Pain points (comma separated)" />
                    <Input value={p.content_preferences.join(", ")} onChange={(e) => { const u = [...personas]; u[i].content_preferences = e.target.value.split(",").map((s: string) => s.trim()); setPersonas(u) }} placeholder="Content preferences (comma separated)" />
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={() => setPersonas([...personas, { name: "", demographics: {}, pain_points: [], content_preferences: [] }])}>+ Add Persona</Button>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                {Object.entries(frequency).map(([platform, f]) => (
                  <div key={platform} className="flex items-center gap-4 border rounded-lg p-4">
                    <span className="w-24 font-medium capitalize">{platform}</span>
                    <div className="flex items-center gap-2">
                      <label className="text-sm text-muted-foreground">Posts/week:</label>
                      <Input type="number" value={f.posts_per_week} onChange={(e) => setFrequency({ ...frequency, [platform]: { ...f, posts_per_week: Number(e.target.value) } })} className="w-20" min={1} max={14} />
                    </div>
                  </div>
                ))}
                <p className="text-sm text-muted-foreground">Total: {totalPerWeek} posts/week ({totalPerWeek * 4} posts/month)</p>
              </div>
            )}

            {step === 4 && (
              <div className="text-center py-8 text-muted-foreground">
                <Mic className="h-12 w-12 mx-auto mb-4" />
                <p>Brand voice settings can be configured later in Settings → Brand Voice</p>
              </div>
            )}

            {step === 5 && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div><strong>Name:</strong> {name}</div>
                  <div><strong>Goals:</strong> {goals.length}</div>
                  <div><strong>Pillars:</strong> {pillars.length}</div>
                  <div><strong>Personas:</strong> {personas.length}</div>
                  <div><strong>Platforms:</strong> {Object.keys(frequency).join(", ")}</div>
                  <div><strong>Posts/week:</strong> {totalPerWeek}</div>
                </div>
                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Pillar Breakdown</h4>
                  {pillars.map((p) => (
                    <div key={p.name} className="flex justify-between text-sm">
                      <span>{p.name}</span>
                      <span>{(p.weight * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex justify-between mt-6">
          <Button variant="outline" onClick={() => step > 0 && setStep(step - 1)} disabled={step === 0}>
            <ArrowLeft className="h-4 w-4 mr-2" /> Back
          </Button>
          <div className="flex gap-3">
            {step < STEPS.length - 1 ? (
              <Button onClick={() => setStep(step + 1)}>
                Next <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <>
                <Button variant="outline" onClick={() => handleCreate(false)} disabled={submitting}>
                  {submitting ? "Saving..." : "Save as Draft"}
                </Button>
                <Button onClick={() => handleCreate(true)} disabled={submitting}>
                  {submitting ? "Activating..." : "Activate Strategy"}
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
