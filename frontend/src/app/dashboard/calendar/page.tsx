"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Calendar, Target, TrendingUp, Play, Camera, Globe, Briefcase,
  MessageCircle, Plus, Check, Clock, Save, Loader2, Trash2,
  BarChart3, Image, Film, Video, ChevronLeft, ChevronRight,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface PlatformGoal {
  current: number
  target: number
  months: number
}

interface ContentSlot {
  id: string
  day: string
  time: string
  type: string
  description: string
  frequency: string
  mediaId?: string
  mediaName?: string
}

interface ContentStrategy {
  platform: string
  goal: PlatformGoal
  goalLabel: string
  pillars: string[]
  tone: string
  targetAudience: string
}

interface PlatformSchedule {
  platform: string
  icon: string
  color: string
  bgColor: string
  strategy: ContentStrategy
  slots: ContentSlot[]
  posts_per_week: number
}

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const HOURS = Array.from({ length: 17 }, (_, i) => `${String(i + 6).padStart(2, "0")}:00`)

const PLATFORMS = [
  {
    id: "linkedin", name: "LinkedIn", icon: "Briefcase", color: "text-blue-600",
    bgColor: "bg-blue-50 border-blue-200", goalLabel: "Followers",
    defaultGoal: { current: 5000, target: 10000, months: 6 },
    defaultPillars: ["Industry Insights", "Thought Leadership", "Team Culture", "Product Updates"],
    defaultSlots: [
      { day: "Mon", time: "09:00", type: "Text Post", description: "Industry insight or thought leadership", frequency: "daily" },
      { day: "Tue", time: "12:00", type: "Carousel", description: "Educational slide deck (5-8 slides)", frequency: "3x/week" },
      { day: "Wed", time: "09:00", type: "Video", description: "Short-form video (60-90s)", frequency: "2x/week" },
      { day: "Thu", time: "09:00", type: "Text Post", description: "Personal story or team spotlight", frequency: "daily" },
      { day: "Fri", time: "09:00", type: "Poll", description: "Industry poll for engagement", frequency: "1x/week" },
    ],
  },
  {
    id: "instagram", name: "Instagram", icon: "Camera", color: "text-pink-500",
    bgColor: "bg-pink-50 border-pink-200", goalLabel: "Followers",
    defaultGoal: { current: 3000, target: 8000, months: 6 },
    defaultPillars: ["Reels", "Carousels", "Stories", "Behind the Scenes"],
    defaultSlots: [
      { day: "Mon", time: "11:00", type: "Reel", description: "Trending audio reel (15-30s)", frequency: "daily" },
      { day: "Tue", time: "11:00", type: "Carousel", description: "Tips carousel (10 slides)", frequency: "3x/week" },
      { day: "Wed", time: "11:00", type: "Story", description: "Behind-the-scenes stories", frequency: "daily" },
      { day: "Thu", time: "11:00", type: "Reel", description: "Tutorial or how-to reel", frequency: "daily" },
      { day: "Fri", time: "11:00", type: "Single Post", description: "Quote card or testimonial", frequency: "3x/week" },
    ],
  },
  {
    id: "youtube", name: "YouTube", icon: "Play", color: "text-red-600",
    bgColor: "bg-red-50 border-red-200", goalLabel: "Subscribers",
    defaultGoal: { current: 1000, target: 5000, months: 6 },
    defaultPillars: ["Tutorials", "Shorts", "Product Demos", "Industry Analysis"],
    defaultSlots: [
      { day: "Tue", time: "14:00", type: "Long Video", description: "Deep-dive tutorial (8-15 min)", frequency: "1x/week" },
      { day: "Thu", time: "14:00", type: "Short", description: "YouTube Short (30-60s)", frequency: "3x/week" },
      { day: "Sat", time: "14:00", type: "Short", description: "YouTube Short from long video clip", frequency: "3x/week" },
    ],
  },
  {
    id: "facebook", name: "Facebook", icon: "Globe", color: "text-blue-500",
    bgColor: "bg-blue-50 border-blue-200", goalLabel: "Followers",
    defaultGoal: { current: 2000, target: 4000, months: 6 },
    defaultPillars: ["Industry News", "Community Engagement", "Video Content", "Team Highlights"],
    defaultSlots: [
      { day: "Mon", time: "10:00", type: "Text Post", description: "Industry news or opinion", frequency: "3x/week" },
      { day: "Wed", time: "10:00", type: "Video", description: "Native video or link share", frequency: "2x/week" },
      { day: "Fri", time: "10:00", type: "Photo Post", description: "Team photo or product image", frequency: "2x/week" },
    ],
  },
  {
    id: "x", name: "X (Twitter)", icon: "MessageCircle", color: "text-gray-900",
    bgColor: "bg-gray-50 border-gray-200", goalLabel: "Followers",
    defaultGoal: { current: 8000, target: 15000, months: 6 },
    defaultPillars: ["Quick Takes", "Threads", "Engagement", "Industry Commentary"],
    defaultSlots: [
      { day: "Mon", time: "08:00", type: "Thread", description: "5-7 tweet thread on industry topic", frequency: "2x/week" },
      { day: "Tue", time: "12:00", type: "Tweet", description: "Quick insight or hot take", frequency: "daily" },
      { day: "Wed", time: "08:00", type: "Tweet", description: "Engagement tweet (question/poll)", frequency: "daily" },
      { day: "Thu", time: "12:00", type: "Thread", description: "How-to or case study thread", frequency: "2x/week" },
      { day: "Fri", time: "08:00", type: "Tweet", description: "Weekend motivation or recap", frequency: "daily" },
    ],
  },
]

function getIcon(name: string) {
  const icons: Record<string, typeof Briefcase> = { Play, Camera, Globe, Briefcase, MessageCircle }
  return icons[name] || MessageCircle
}

function initSchedule(p: typeof PLATFORMS[0]): PlatformSchedule {
  return {
    platform: p.id,
    icon: p.icon,
    color: p.color,
    bgColor: p.bgColor,
    strategy: {
      platform: p.id,
      goal: { ...p.defaultGoal },
      goalLabel: p.goalLabel,
      pillars: [...p.defaultPillars],
      tone: "Professional",
      targetAudience: "",
    },
    slots: p.defaultSlots.map((s, i) => ({ ...s, id: `${p.id}-${i}` })),
    posts_per_week: p.defaultSlots.length,
  }
}

export default function SchedulingPage() {
  const [activePlatform, setActivePlatform] = useState("linkedin")
  const [schedules, setSchedules] = useState<Record<string, PlatformSchedule>>(() => {
    const initial: Record<string, PlatformSchedule> = {}
    for (const p of PLATFORMS) initial[p.id] = initSchedule(p)
    return initial
  })
  const [view, setView] = useState<"daily" | "weekly" | "monthly">("weekly")
  const [saved, setSaved] = useState(false)
  const [showStrategyForm, setShowStrategyForm] = useState(false)
  const [newPillar, setNewPillar] = useState("")
  const [newSlot, setNewSlot] = useState<{ show: boolean; day: string; time: string; type: string; description: string; mediaId: string; mediaName: string }>({ show: false, day: "Mon", time: "09:00", type: "Text Post", description: "", mediaId: "", mediaName: "" })
  const [mediaAssets, setMediaAssets] = useState<Array<{ id: string; name: string; platform: string; content_type: string; type: string }>>([])
  const [showMediaPicker, setShowMediaPicker] = useState(false)
  const [currentDate, setCurrentDate] = useState(new Date())
  const [editingSlot, setEditingSlot] = useState<string | null>(null)
  const [editSlotData, setEditSlotData] = useState<{ day: string; time: string; type: string; description: string }>({ day: "", time: "", type: "", description: "" })
  const [showResearchModal, setShowResearchModal] = useState(false)
  const [researchItems, setResearchItems] = useState<Array<{ id: string; topic: string; category: string; video_seo_score?: number; trend_velocity?: number; platform?: string }>>([])
  const [selectedResearch, setSelectedResearch] = useState<Set<string>>(new Set())
  const [researchLoading, setResearchLoading] = useState(false)


  useEffect(() => {
    if (showMediaPicker) {
      fetch(`${API_URL}/media/assets?platform=${activePlatform}`)
        .then(r => r.json()).then(d => setMediaAssets(d.assets || [])).catch(() => setMediaAssets([]))
    }
  }, [showMediaPicker, activePlatform])

  const current = schedules[activePlatform]
  const platformConfig = PLATFORMS.find(p => p.id === activePlatform)!

  function updateGoal(field: "current" | "target" | "months", value: number) {
    setSchedules(prev => ({ ...prev, [activePlatform]: { ...prev[activePlatform], strategy: { ...prev[activePlatform].strategy, goal: { ...prev[activePlatform].strategy.goal, [field]: value } } } }))
  }
  function updateStrategy(field: keyof ContentStrategy, value: string | string[]) {
    setSchedules(prev => ({ ...prev, [activePlatform]: { ...prev[activePlatform], strategy: { ...prev[activePlatform].strategy, [field]: value } } }))
  }
  function addPillar() {
    if (!newPillar.trim()) return
    updateStrategy("pillars", [...current.strategy.pillars, newPillar.trim()])
    setNewPillar("")
  }
  function removePillar(i: number) {
    updateStrategy("pillars", current.strategy.pillars.filter((_, idx) => idx !== i))
  }
  function addSlot() {
    if (!newSlot.description) return
    setSchedules(prev => ({
      ...prev, [activePlatform]: {
        ...prev[activePlatform],
        slots: [...prev[activePlatform].slots, { id: `${activePlatform}-${Date.now()}`, day: newSlot.day, time: newSlot.time, type: newSlot.type, description: newSlot.description, frequency: "custom", mediaId: newSlot.mediaId, mediaName: newSlot.mediaName }],
        posts_per_week: prev[activePlatform].posts_per_week + 1,
      },
    }))
    setNewSlot({ show: false, day: "Mon", time: "09:00", type: "Text Post", description: "", mediaId: "", mediaName: "" })
  }
  function removeSlot(id: string) {
    setSchedules(prev => ({ ...prev, [activePlatform]: { ...prev[activePlatform], slots: prev[activePlatform].slots.filter(s => s.id !== id), posts_per_week: Math.max(0, prev[activePlatform].posts_per_week - 1) } }))
  }
  function startEditSlot(slot: ContentSlot) {
    setEditingSlot(slot.id)
    setEditSlotData({ day: slot.day, time: slot.time, type: slot.type, description: slot.description })
  }
  function saveEditSlot() {
    if (!editingSlot) return
    setSchedules(prev => ({
      ...prev, [activePlatform]: {
        ...prev[activePlatform],
        slots: prev[activePlatform].slots.map(s => s.id === editingSlot ? { ...s, ...editSlotData } : s),
      },
    }))
    setEditingSlot(null)
  }
  function saveSchedule() { setSaved(true); setTimeout(() => setSaved(false), 2000) }

  async function loadResearchTopics() {
    setResearchLoading(true)
    try {
      const token = localStorage.getItem("token")
      const [risingRes, topRes] = await Promise.all([
        fetch(`${API_URL}/research/rising?platform=${activePlatform}&limit=5`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_URL}/research/top-scoring?limit=5`, { headers: { Authorization: `Bearer ${token}` } }),
      ])
      const rising = risingRes.ok ? (await risingRes.json()).items || [] : []
      const top = topRes.ok ? (await topRes.json()).items || [] : []
      const all = [...rising, ...top]
      // Dedupe by topic
      const seen = new Set<string>()
      const deduped = all.filter((item: { topic: string }) => { if (seen.has(item.topic)) return false; seen.add(item.topic); return true })
      setResearchItems(deduped)
      setSelectedResearch(new Set(deduped.map((i: { id: string }) => i.id)))
    } catch { setResearchItems([]) }
    setResearchLoading(false)
    setShowResearchModal(true)
  }

  function applyResearchSlots() {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    const selected = researchItems.filter(i => selectedResearch.has(i.id))
    const newSlots = selected.map((item, idx) => ({
      id: `research-${item.id}-${Date.now()}`,
      day: days[idx % days.length],
      time: "10:00",
      type: "Text Post",
      description: `${item.topic}${item.video_seo_score ? ` (SEO: ${item.video_seo_score})` : ""}`,
      frequency: "research",
    }))
    setSchedules(prev => ({
      ...prev, [activePlatform]: {
        ...prev[activePlatform],
        slots: [...prev[activePlatform].slots, ...newSlots],
        posts_per_week: prev[activePlatform].posts_per_week + newSlots.length,
      },
    }))
    setShowResearchModal(false)
  }

  const goal = current?.strategy.goal
  const perMonth = goal ? Math.round((goal.target - goal.current) / (goal.months || 6)) : 0

  // Build daily schedule for a given date
  function getSlotsForDay(dayName: string) { return current?.slots.filter(s => s.day === dayName) || [] }
  function getSlotsForWeek() { return current?.slots || [] }
  function getSlotsForMonth() { return current?.slots || [] }

  // Calendar days for monthly view
  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDay = new Date(year, month, 1).getDay()
  const monthDays: (number | null)[] = []
  for (let i = 0; i < firstDay; i++) monthDays.push(null)
  for (let i = 1; i <= daysInMonth; i++) monthDays.push(i)

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Content Scheduling</h1>
            <p className="text-muted-foreground">Plan platform-specific content strategies based on your growth targets.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={loadResearchTopics} className="gap-2">
              <TrendingUp className="h-4 w-4" /> Use Researched Topics
            </Button>
            <Button onClick={saveSchedule} className="gap-2">
              {saved ? <Check className="h-4 w-4" /> : <Save className="h-4 w-4" />}
              {saved ? "Saved!" : "Save All"}
            </Button>
          </div>
        </div>

        <Tabs value={activePlatform} onValueChange={setActivePlatform}>
          <TabsList>
            {PLATFORMS.map(p => { const Ic = getIcon(p.icon); return (
              <TabsTrigger key={p.id} value={p.id} className="gap-2"><Ic className={`h-4 w-4 ${p.color}`} />{p.name}</TabsTrigger>
            ) })}
          </TabsList>

          {PLATFORMS.map(p => (
            <TabsContent key={p.id} value={p.id}>
              {schedules[p.id] && (
                <div className="space-y-6">
                  {/* Content Strategy */}
                  <Card className={p.bgColor}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="flex items-center gap-2"><Target className="h-5 w-5" /> Content Strategy — {p.name}</CardTitle>
                          <CardDescription>Define your growth goals, content pillars, and audience.</CardDescription>
                        </div>
                        <Button variant="outline" size="sm" onClick={() => setShowStrategyForm(!showStrategyForm)} className="gap-1">
                          <Plus className="h-4 w-4" /> {showStrategyForm ? "Close" : "Create Strategy"}
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {showStrategyForm ? (
                        <div className="grid gap-4 md:grid-cols-2">
                          <div><label className="mb-1 block text-xs font-medium">Current {schedules[p.id].strategy.goalLabel}</label><Input type="number" value={goal.current} onChange={(e) => updateGoal("current", Number(e.target.value))} className="font-mono" /></div>
                          <div><label className="mb-1 block text-xs font-medium">Target {schedules[p.id].strategy.goalLabel}</label><Input type="number" value={goal.target} onChange={(e) => updateGoal("target", Number(e.target.value))} className="font-mono" /></div>
                          <div><label className="mb-1 block text-xs font-medium">Timeline (months)</label><Input type="number" value={goal.months} onChange={(e) => updateGoal("months", Number(e.target.value))} className="font-mono" /></div>
                          <div><label className="mb-1 block text-xs font-medium">Tone</label><select className="w-full rounded-lg border bg-background p-2 text-sm" value={current.strategy.tone} onChange={(e) => updateStrategy("tone", e.target.value)}>{["Professional", "Casual", "Humorous", "Inspirational", "Educational"].map(t => <option key={t} value={t}>{t}</option>)}</select></div>
                          <div className="md:col-span-2"><label className="mb-1 block text-xs font-medium">Target Audience</label><Input placeholder="e.g. SaaS founders, marketing managers" value={current.strategy.targetAudience} onChange={(e) => updateStrategy("targetAudience", e.target.value)} /></div>
                          <div className="md:col-span-2">
                            <label className="mb-1 block text-xs font-medium">Content Pillars</label>
                            <div className="flex flex-wrap gap-2 mb-2">{current.strategy.pillars.map((pill, i) => (
                              <span key={i} className="flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">{pill}<button onClick={() => removePillar(i)} className="hover:text-destructive">×</button></span>
                            ))}</div>
                            <div className="flex gap-2"><Input placeholder="Add content pillar" value={newPillar} onChange={(e) => setNewPillar(e.target.value)} onKeyDown={(e) => e.key === "Enter" && addPillar()} className="text-sm" /><Button size="sm" onClick={addPillar}>Add</Button></div>
                          </div>
                        </div>
                      ) : (
                        <div className="grid gap-4 md:grid-cols-4">
                          <div className="rounded-lg bg-white/80 p-3"><p className="text-xs text-muted-foreground">Current</p><p className="text-lg font-bold">{goal.current.toLocaleString()}</p><p className="text-xs text-muted-foreground">{schedules[p.id].strategy.goalLabel}</p></div>
                          <div className="rounded-lg bg-white/80 p-3"><p className="text-xs text-muted-foreground">Target</p><p className="text-lg font-bold">{goal.target.toLocaleString()}</p><p className="text-xs text-muted-foreground">in {goal.months} months</p></div>
                          <div className="rounded-lg bg-white/80 p-3"><p className="text-xs text-muted-foreground">Needed/Month</p><p className="text-lg font-bold text-green-600">+{perMonth.toLocaleString()}</p><p className="text-xs text-muted-foreground">{current.posts_per_week} posts/week</p></div>
                          <div className="rounded-lg bg-white/80 p-3"><p className="text-xs text-muted-foreground">Pillars</p><p className="text-sm font-medium">{current.strategy.pillars.join(", ") || "Not set"}</p><p className="text-xs text-muted-foreground">Tone: {current.strategy.tone}</p></div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* View Toggle */}
                  <div className="flex items-center justify-between">
                    <div className="flex rounded-lg border overflow-hidden">
                      {(["daily", "weekly", "monthly"] as const).map(v => (
                        <button key={v} onClick={() => setView(v)} className={`px-4 py-2 text-sm font-medium capitalize ${view === v ? "bg-primary text-primary-foreground" : "bg-background text-muted-foreground hover:bg-muted"}`}>{v}</button>
                      ))}
                    </div>
                    <Button variant="outline" size="sm" onClick={() => setNewSlot({ ...newSlot, show: !newSlot.show })} className="gap-1">
                      <Plus className="h-4 w-4" /> Add Slot
                    </Button>
                  </div>

                  {/* New Slot Form */}
                  {newSlot.show && (
                    <Card><CardContent className="pt-4 space-y-3">
                      <div className="grid grid-cols-4 gap-2">
                        <select value={newSlot.day} onChange={(e) => setNewSlot({ ...newSlot, day: e.target.value })} className="rounded-lg border bg-background p-2 text-sm">{DAYS.map(d => <option key={d} value={d}>{d}</option>)}</select>
                        <Input type="time" value={newSlot.time} onChange={(e) => setNewSlot({ ...newSlot, time: e.target.value })} className="text-sm" />
                        <select value={newSlot.type} onChange={(e) => setNewSlot({ ...newSlot, type: e.target.value })} className="rounded-lg border bg-background p-2 text-sm">{["Text Post", "Carousel", "Reel", "Video", "Story", "Thread", "Poll", "Newsletter", "Single Post", "Long Video", "Short"].map(t => <option key={t} value={t}>{t}</option>)}</select>
                        <Button size="sm" onClick={addSlot}>Add</Button>
                      </div>
                      <Input placeholder="Description" value={newSlot.description} onChange={(e) => setNewSlot({ ...newSlot, description: e.target.value })} className="text-sm" />
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" onClick={() => setShowMediaPicker(true)} className="gap-1 text-xs"><Image className="h-3 w-3" /> Select Media</Button>
                        {newSlot.mediaName && <span className="flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary"><Film className="h-3 w-3" /> {newSlot.mediaName}<button onClick={() => setNewSlot({ ...newSlot, mediaId: "", mediaName: "" })} className="ml-1 hover:text-destructive">×</button></span>}
                      </div>
                    </CardContent></Card>
                  )}

                  {/* Media Picker Modal */}
                  {showMediaPicker && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                      <Card className="w-full max-w-lg mx-4 max-h-[70vh] flex flex-col">
                        <CardHeader className="pb-3"><div className="flex items-center justify-between"><CardTitle className="text-base">Select Media — {platformConfig.name}</CardTitle><button onClick={() => setShowMediaPicker(false)} className="text-muted-foreground hover:text-foreground">×</button></div></CardHeader>
                        <CardContent className="overflow-y-auto flex-1">
                          {mediaAssets.length === 0 ? (
                            <div className="py-8 text-center text-sm text-muted-foreground"><Image className="mx-auto mb-2 h-8 w-8 opacity-30" /><p>No media in {platformConfig.name} directory.</p></div>
                          ) : (
                            <div className="space-y-2">{mediaAssets.map(asset => (
                              <button key={asset.id} onClick={() => { setNewSlot({ ...newSlot, mediaId: asset.id, mediaName: asset.name }); setShowMediaPicker(false) }} className="flex w-full items-center gap-3 rounded-lg border p-3 text-left hover:bg-muted/50">
                                <div className="flex h-8 w-8 items-center justify-center rounded bg-muted">{asset.type === "video" ? <Video className="h-4 w-4" /> : <Image className="h-4 w-4" />}</div>
                                <div className="flex-1"><p className="text-sm font-medium">{asset.name}</p><p className="text-xs text-muted-foreground">{asset.content_type || asset.type}</p></div>
                              </button>
                            ))}</div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  )}

                  {/* Schedule Views */}
                  {view === "daily" && (
                    <Card>
                      <CardHeader><CardTitle className="flex items-center gap-2"><Clock className="h-5 w-5 text-primary" /> Daily Schedule — {DAYS[currentDate.getDay() === 0 ? 6 : currentDate.getDay() - 1]}</CardTitle><CardDescription>Click a slot to edit its details.</CardDescription></CardHeader>
                      <CardContent>
                        <div className="space-y-1">
                          {HOURS.map(hour => {
                            const daySlots = getSlotsForDay(DAYS[new Date().getDay() === 0 ? 6 : new Date().getDay() - 1]).filter(s => s.time === hour)
                            return (
                              <div key={hour} className="flex items-center gap-3 min-h-[40px]">
                                <span className="w-14 text-xs text-muted-foreground font-mono">{hour}</span>
                                <div className="flex-1 border-l-2 border-muted pl-3">
                                  {daySlots.map(slot => (
                                    editingSlot === slot.id ? (
                                      <div key={slot.id} className="flex items-center gap-2 rounded-lg border border-primary bg-primary/5 px-3 py-2 mb-1">
                                        <select value={editSlotData.day} onChange={(e) => setEditSlotData({ ...editSlotData, day: e.target.value })} className="rounded border bg-background p-1 text-xs">{DAYS.map(d => <option key={d} value={d}>{d}</option>)}</select>
                                        <input type="time" value={editSlotData.time} onChange={(e) => setEditSlotData({ ...editSlotData, time: e.target.value })} className="rounded border bg-background p-1 text-xs" />
                                        <select value={editSlotData.type} onChange={(e) => setEditSlotData({ ...editSlotData, type: e.target.value })} className="rounded border bg-background p-1 text-xs">{["Text Post", "Carousel", "Reel", "Video", "Story", "Thread", "Poll", "Long Video", "Short"].map(t => <option key={t} value={t}>{t}</option>)}</select>
                                        <input value={editSlotData.description} onChange={(e) => setEditSlotData({ ...editSlotData, description: e.target.value })} className="flex-1 rounded border bg-background p-1 text-xs" placeholder="Description" />
                                        <button onClick={saveEditSlot} className="rounded bg-primary px-2 py-1 text-xs text-primary-foreground">Save</button>
                                        <button onClick={() => setEditingSlot(null)} className="rounded bg-muted px-2 py-1 text-xs">Cancel</button>
                                      </div>
                                    ) : (
                                      <div key={slot.id} className="group flex items-center gap-2 rounded-lg bg-primary/5 border border-primary/20 px-3 py-1.5 mb-1 cursor-pointer hover:bg-primary/10 transition-colors" onClick={() => startEditSlot(slot)}>
                                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">{slot.type}</span>
                                        <span className="text-sm flex-1">{slot.description}</span>
                                        {slot.mediaName && <span className="text-xs text-muted-foreground flex items-center gap-1"><Film className="h-3 w-3" />{slot.mediaName}</span>}
                                        <button onClick={(e) => { e.stopPropagation(); removeSlot(slot.id) }} className="opacity-0 group-hover:opacity-100 text-destructive hover:text-destructive"><Trash2 className="h-3 w-3" /></button>
                                      </div>
                                    )
                                  ))}
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {view === "weekly" && (
                    <Card>
                      <CardHeader><CardTitle className="flex items-center gap-2"><Calendar className="h-5 w-5 text-primary" /> Weekly Schedule</CardTitle><CardDescription>{current.posts_per_week} posts across {current.slots.length} slots. Click a slot to edit.</CardDescription></CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-7 gap-2">
                          {DAYS.map(day => (
                            <div key={day} className="rounded-lg border p-2 min-h-[150px]">
                              <p className="text-xs font-medium text-muted-foreground mb-2">{day}</p>
                              <div className="space-y-1">
                                {getSlotsForDay(day).map(slot => (
                                  editingSlot === slot.id ? (
                                    <div key={slot.id} className="rounded border border-primary bg-primary/5 p-2 space-y-1">
                                      <select value={editSlotData.day} onChange={(e) => setEditSlotData({ ...editSlotData, day: e.target.value })} className="w-full rounded border bg-background p-1 text-[10px]">{DAYS.map(d => <option key={d} value={d}>{d}</option>)}</select>
                                      <input type="time" value={editSlotData.time} onChange={(e) => setEditSlotData({ ...editSlotData, time: e.target.value })} className="w-full rounded border bg-background p-1 text-[10px]" />
                                      <select value={editSlotData.type} onChange={(e) => setEditSlotData({ ...editSlotData, type: e.target.value })} className="w-full rounded border bg-background p-1 text-[10px]">{["Text Post", "Carousel", "Reel", "Video", "Story", "Thread", "Poll", "Long Video", "Short"].map(t => <option key={t} value={t}>{t}</option>)}</select>
                                      <input value={editSlotData.description} onChange={(e) => setEditSlotData({ ...editSlotData, description: e.target.value })} className="w-full rounded border bg-background p-1 text-[10px]" placeholder="Description" />
                                      <div className="flex gap-1"><button onClick={saveEditSlot} className="rounded bg-primary px-2 py-0.5 text-[10px] text-primary-foreground">Save</button><button onClick={() => setEditingSlot(null)} className="rounded bg-muted px-2 py-0.5 text-[10px]">Cancel</button></div>
                                    </div>
                                  ) : (
                                    <div key={slot.id} className="group rounded bg-primary/5 border border-primary/20 px-2 py-1 cursor-pointer hover:bg-primary/10 transition-colors" onClick={() => startEditSlot(slot)}>
                                      <div className="flex items-center justify-between">
                                        <p className="text-[10px] font-medium text-primary">{slot.type}</p>
                                        <button onClick={(e) => { e.stopPropagation(); removeSlot(slot.id) }} className="opacity-0 group-hover:opacity-100 text-destructive hover:text-destructive text-[10px]">×</button>
                                      </div>
                                      <p className="text-[10px] text-muted-foreground truncate">{slot.description}</p>
                                      <p className="text-[10px] text-muted-foreground font-mono">{slot.time}</p>
                                    </div>
                                  )
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {view === "monthly" && (
                    <Card>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center gap-2"><Calendar className="h-5 w-5 text-primary" /> Monthly View</CardTitle>
                          <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date(year, month - 1))}><ChevronLeft className="h-4 w-4" /></Button>
                            <span className="text-sm font-medium">{currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" })}</span>
                            <Button variant="outline" size="sm" onClick={() => setCurrentDate(new Date(year, month + 1))}><ChevronRight className="h-4 w-4" /></Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-7 gap-px bg-border rounded-lg overflow-hidden">
                          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d => <div key={d} className="bg-muted p-2 text-center text-xs font-medium">{d}</div>)}
                          {monthDays.map((day, i) => {
                            if (day === null) return <div key={`e-${i}`} className="bg-background p-2 min-h-[80px]" />
                            const dayName = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][new Date(year, month, day).getDay()]
                            const daySlots = getSlotsForDay(dayName)
                            const isToday = new Date().getDate() === day && new Date().getMonth() === month
                            return (
                              <div key={day} className={`bg-background p-2 min-h-[80px] ${isToday ? "ring-2 ring-primary ring-inset" : ""}`}>
                                <p className={`text-xs font-medium mb-1 ${isToday ? "text-primary font-bold" : "text-muted-foreground"}`}>{day}</p>
                                {daySlots.slice(0, 2).map(slot => (
                                  <div key={slot.id} className="rounded bg-primary/5 px-1 py-0.5 text-[9px] truncate mb-0.5">{slot.type}</div>
                                ))}
                                {daySlots.length > 2 && <p className="text-[9px] text-muted-foreground">+{daySlots.length - 2} more</p>}
                              </div>
                            )
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Strategy Summary */}
                  <Card>
                    <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5 text-primary" /> Content Mix — {p.name}</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid gap-4 md:grid-cols-3">
                        <div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Posts/Week</p><p className="text-2xl font-bold">{current.posts_per_week}</p></div>
                        <div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Projected Growth/Month</p><p className="text-2xl font-bold text-green-600">+{perMonth.toLocaleString()}</p></div>
                        <div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Content Types</p><p className="text-sm font-medium">{(() => { const t: Record<string, number> = {}; current.slots.forEach(s => { t[s.type] = (t[s.type] || 0) + 1 }); return Object.entries(t).map(([k, v]) => `${k}(${v})`).join(", ") })()}</p></div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>
          ))}
        </Tabs>

        {/* Research Topics Modal */}
        {showResearchModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <Card className="w-full max-w-lg mx-4 max-h-[70vh] flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2"><TrendingUp className="h-4 w-4" /> Use Researched Topics</CardTitle>
                  <button onClick={() => setShowResearchModal(false)} className="text-muted-foreground hover:text-foreground">×</button>
                </div>
                <CardDescription>Select research items to add as calendar slots on {PLATFORMS.find(p => p.id === activePlatform)?.name}.</CardDescription>
              </CardHeader>
              <CardContent className="overflow-y-auto flex-1 space-y-3">
                {researchLoading ? (
                  <div className="py-8 text-center text-sm text-muted-foreground">Loading research items...</div>
                ) : researchItems.length === 0 ? (
                  <div className="py-8 text-center text-sm text-muted-foreground"><p>No research items found.</p><p className="mt-1">Run keyword or trend research first, then come back.</p></div>
                ) : (
                  <>
                    <div className="space-y-2">
                      {researchItems.map(item => (
                        <label key={item.id} className="flex items-center gap-3 rounded-lg border p-3 cursor-pointer hover:bg-muted/50 transition-colors">
                          <input type="checkbox" checked={selectedResearch.has(item.id)} onChange={() => setSelectedResearch(prev => { const next = new Set(prev); next.has(item.id) ? next.delete(item.id) : next.add(item.id); return next })} className="rounded" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{item.topic}</p>
                            <div className="flex gap-2 mt-0.5">
                              <span className="text-[10px] text-muted-foreground">{item.category}</span>
                              {item.video_seo_score && <span className="text-[10px] text-green-600">SEO: {item.video_seo_score}</span>}
                              {item.trend_velocity && <span className="text-[10px] text-blue-600">Vel: {item.trend_velocity}</span>}
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                    <Button onClick={applyResearchSlots} disabled={selectedResearch.size === 0} className="w-full gap-2">
                      <Plus className="h-4 w-4" /> Add {selectedResearch.size} Topic{selectedResearch.size !== 1 ? "s" : ""} to Calendar
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
