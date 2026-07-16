"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Plus,
  GripVertical,
  Clock,
  Repeat,
  Tag,
} from "lucide-react"
import type { CalendarEvent, CalendarView, Platform, PostStatus, Campaign } from "@/types"

const PLATFORM_COLORS: Record<Platform, string> = {
  linkedin: "border-l-blue-600 bg-blue-50",
  x: "border-l-black bg-gray-50",
  instagram: "border-l-pink-500 bg-pink-50",
  facebook: "border-l-blue-500 bg-blue-50",
  youtube: "border-l-red-600 bg-red-50",
}

const STATUS_COLORS: Record<PostStatus, string> = {
  draft: "bg-gray-100 text-gray-700",
  review: "bg-yellow-100 text-yellow-700",
  scheduled: "bg-blue-100 text-blue-700",
  publishing: "bg-orange-100 text-orange-700",
  published: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
}

const DEMO_CAMPAIGNS: Campaign[] = [
  { id: "camp-0", name: "Product Launch Q3", description: "", color: "#3b82f6", startDate: "2026-07-01", endDate: "2026-09-30", eventCount: 24 },
  { id: "camp-1", name: "Thought Leadership", description: "", color: "#8b5cf6", startDate: "2026-07-01", endDate: "2026-12-31", eventCount: 52 },
  { id: "camp-2", name: "Summer Engagement", description: "", color: "#06b6d4", startDate: "2026-06-01", endDate: "2026-08-31", eventCount: 18 },
]

function generateDemoEvents(year: number, month: number): CalendarEvent[] {
  const events: CalendarEvent[] = []
  const titles = [
    "10 Tips for Content", "Behind the Scenes", "Industry Insights",
    "Growth Case Study", "Product Update", "Motivation Monday",
    "Tutorial Guide", "Client Success", "FAQ Session", "Community Spotlight",
  ]
  const platforms: Platform[] = ["linkedin", "x", "instagram", "facebook", "youtube"]
  const statuses: PostStatus[] = ["draft", "review", "scheduled", "published", "failed"]

  for (let i = 0; i < 20; i++) {
    const day = (i % 28) + 1
    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`
    events.push({
      id: `evt-${i}`,
      postId: `post-${i}`,
      title: titles[i % titles.length],
      content: `Content for ${titles[i % titles.length]}`,
      platform: platforms[i % platforms.length],
      status: statuses[i % statuses.length],
      date: dateStr,
      timeSlot: `${9 + (i % 10)}:00`,
      campaignId: i % 5 === 0 ? DEMO_CAMPAIGNS[i % 3].id : undefined,
      isRecurring: i % 6 === 0,
      recurringPattern: i % 6 === 0 ? "weekly" : undefined,
      authorId: "user-1",
      authorName: "You",
      mediaUrls: [],
    })
  }
  return events
}

export function CalendarViewComponent() {
  const [view, setView] = useState<CalendarView>("weekly")
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedCampaign, setSelectedCampaign] = useState<string | "all">("all")
  const [draggedEvent, setDraggedEvent] = useState<string | null>(null)

  const events = useMemo(
    () => generateDemoEvents(currentDate.getFullYear(), currentDate.getMonth()),
    [currentDate]
  )

  const filteredEvents = useMemo(() => {
    if (selectedCampaign === "all") return events
    return events.filter((e) => e.campaignId === selectedCampaign)
  }, [events, selectedCampaign])

  const navigate = (direction: number) => {
    setCurrentDate((prev) => {
      const d = new Date(prev)
      if (view === "daily") d.setDate(d.getDate() + direction)
      else if (view === "weekly") d.setDate(d.getDate() + direction * 7)
      else d.setMonth(d.getMonth() + direction)
      return d
    })
  }

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate()
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay()

  const monthDays = useMemo(() => {
    const days: (number | null)[] = []
    for (let i = 0; i < firstDayOfMonth; i++) days.push(null)
    for (let i = 1; i <= daysInMonth; i++) days.push(i)
    return days
  }, [firstDayOfMonth, daysInMonth])

  const weekDays = useMemo(() => {
    const start = new Date(currentDate)
    start.setDate(start.getDate() - start.getDay())
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(start)
      d.setDate(d.getDate() + i)
      return d
    })
  }, [currentDate])

  const getEventsForDay = (dateStr: string) =>
    filteredEvents.filter((e) => e.date === dateStr)

  const handleDragStart = (eventId: string) => setDraggedEvent(eventId)
  const handleDragOver = (e: React.DragEvent) => e.preventDefault()
  const handleDrop = (date: string) => {
    if (draggedEvent) {
      setDraggedEvent(null)
    }
  }

  const formatDate = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`

  return (
    <div className="space-y-6">
      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h3 className="text-lg font-semibold min-w-[200px] text-center">
                {view === "daily" && currentDate.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}
                {view === "weekly" && `Week of ${weekDays[0].toLocaleDateString("en-US", { month: "short", day: "numeric" })}`}
                {view === "monthly" && currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
              </h3>
              <Button variant="outline" size="icon" onClick={() => navigate(1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setCurrentDate(new Date())}>
                Today
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex rounded-lg border overflow-hidden">
                {(["daily", "weekly", "monthly"] as CalendarView[]).map((v) => (
                  <button
                    key={v}
                    onClick={() => setView(v)}
                    className={`px-3 py-1.5 text-xs font-medium capitalize ${
                      view === v ? "bg-primary text-primary-foreground" : "bg-background text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    {v}
                  </button>
                ))}
              </div>
              <Button size="sm" className="gap-1.5">
                <Plus className="h-3.5 w-3.5" />
                New Post
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Campaign Filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setSelectedCampaign("all")}
          className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
            selectedCampaign === "all"
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-muted/80"
          }`}
        >
          All Campaigns
        </button>
        {DEMO_CAMPAIGNS.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedCampaign(c.id)}
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
              selectedCampaign === c.id
                ? "text-white"
                : "text-muted-foreground hover:bg-muted/80"
            }`}
            style={{ backgroundColor: selectedCampaign === c.id ? c.color : undefined }}
          >
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.color }} />
            {c.name}
            <span className="opacity-75">({c.eventCount})</span>
          </button>
        ))}
      </div>

      {/* Monthly View */}
      {view === "monthly" && (
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-7 gap-px bg-border rounded-lg overflow-hidden">
              {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
                <div key={d} className="bg-muted p-2 text-center text-xs font-medium text-muted-foreground">
                  {d}
                </div>
              ))}
              {monthDays.map((day, i) => {
                if (day === null) return <div key={`empty-${i}`} className="bg-background p-2 min-h-[100px]" />
                const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`
                const dayEvents = getEventsForDay(dateStr)
                const isToday = formatDate(new Date()) === dateStr

                return (
                  <div
                    key={day}
                    className={`bg-background p-2 min-h-[100px] ${isToday ? "ring-2 ring-primary ring-inset" : ""}`}
                    onDragOver={handleDragOver}
                    onDrop={() => handleDrop(dateStr)}
                  >
                    <div className={`text-xs font-medium mb-1 ${isToday ? "text-primary font-bold" : "text-muted-foreground"}`}>
                      {day}
                    </div>
                    <div className="space-y-1">
                      {dayEvents.slice(0, 3).map((evt) => (
                        <div
                          key={evt.id}
                          draggable
                          onDragStart={() => handleDragStart(evt.id)}
                          className={`border-l-2 rounded-r px-1.5 py-0.5 text-[10px] cursor-grab active:cursor-grabbing truncate ${PLATFORM_COLORS[evt.platform]}`}
                        >
                          <div className="flex items-center gap-1">
                            <GripVertical className="h-2.5 w-2.5 opacity-40" />
                            <span className="truncate font-medium">{evt.title}</span>
                          </div>
                        </div>
                      ))}
                      {dayEvents.length > 3 && (
                        <div className="text-[10px] text-muted-foreground pl-1">
                          +{dayEvents.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Weekly View */}
      {view === "weekly" && (
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-7 gap-3">
              {weekDays.map((day) => {
                const dateStr = formatDate(day)
                const dayEvents = getEventsForDay(dateStr)
                const isToday = formatDate(new Date()) === dateStr

                return (
                  <div key={dateStr} className={`rounded-lg border p-3 min-h-[200px] ${isToday ? "border-primary bg-primary/5" : ""}`}>
                    <div className={`text-sm font-medium mb-2 ${isToday ? "text-primary" : ""}`}>
                      {day.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}
                    </div>
                    <div className="space-y-2">
                      {dayEvents.map((evt) => (
                        <div
                          key={evt.id}
                          draggable
                          onDragStart={() => handleDragStart(evt.id)}
                          className={`border-l-2 rounded-r px-2 py-1.5 text-xs cursor-grab active:cursor-grabbing ${PLATFORM_COLORS[evt.platform]}`}
                        >
                          <div className="font-medium truncate">{evt.title}</div>
                          <div className="flex items-center gap-1 mt-0.5">
                            <Clock className="h-2.5 w-2.5 opacity-50" />
                            <span className="opacity-60">{evt.timeSlot}</span>
                            <span className={`ml-auto text-[10px] px-1 py-0 rounded ${STATUS_COLORS[evt.status]}`}>
                              {evt.status}
                            </span>
                          </div>
                          {evt.isRecurring && (
                            <Repeat className="h-2.5 w-2.5 opacity-40 mt-0.5" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Daily View */}
      {view === "daily" && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-3">
              {getEventsForDay(formatDate(currentDate)).map((evt) => (
                <div
                  key={evt.id}
                  draggable
                  onDragStart={() => handleDragStart(evt.id)}
                  className={`flex items-center gap-4 rounded-lg border-l-4 p-4 ${PLATFORM_COLORS[evt.platform]}`}
                >
                  <GripVertical className="h-5 w-5 text-muted-foreground cursor-grab" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{evt.title}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[evt.status]}`}>
                        {evt.status}
                      </span>
                      {evt.isRecurring && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Repeat className="h-3 w-3" /> {evt.recurringPattern}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {evt.timeSlot}
                      </span>
                      <span className="capitalize">{evt.platform}</span>
                      {evt.campaignId && (
                        <span className="flex items-center gap-1">
                          <Tag className="h-3 w-3" />
                          {DEMO_CAMPAIGNS.find((c) => c.id === evt.campaignId)?.name}
                        </span>
                      )}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">Edit</Button>
                </div>
              ))}
              {getEventsForDay(formatDate(currentDate)).length === 0 && (
                <div className="text-center py-12 text-muted-foreground">
                  <CalendarIcon className="h-12 w-12 mx-auto mb-3 opacity-30" />
                  <p className="text-sm">No posts scheduled for this day</p>
                  <Button variant="outline" size="sm" className="mt-3 gap-1.5">
                    <Plus className="h-3.5 w-3.5" />
                    Schedule a Post
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
