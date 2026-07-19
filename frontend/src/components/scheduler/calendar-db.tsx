"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  FileJson,
  Loader2,
  RefreshCw,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface CalendarEvent {
  id: string
  post_id: string
  title: string
  platform: Platform
  status: string
  date: string
  time_slot: string | null
  scheduled_at: string | null
}

const PLATFORM_COLORS: Record<Platform, string> = {
  linkedin: "border-l-blue-600 bg-blue-50",
  x: "border-l-black bg-gray-50",
  instagram: "border-l-pink-500 bg-pink-50",
  facebook: "border-l-blue-500 bg-blue-50",
  youtube: "border-l-red-600 bg-red-50",
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  scheduled: "bg-blue-100 text-blue-700",
  publishing: "bg-orange-100 text-orange-700",
  published: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
}

export function CalendarViewDB() {
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [currentDate, setCurrentDate] = useState(new Date())
  const [exporting, setExporting] = useState<string | null>(null)

  const fetchEvents = useCallback(async () => {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
      const end = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)

      const response = await fetch(
        `${API_BASE}/scheduler/calendar/events?start_date=${start.toISOString()}&end_date=${end.toISOString()}`,
        { headers }
      )
      if (response.ok) {
        const data = await response.json()
        setEvents(data.events || [])
      }
    } catch (err) {
      console.error("Failed to load calendar events:", err)
    } finally {
      setLoading(false)
    }
  }, [currentDate])

  useEffect(() => { void (async () => { await fetchEvents() })() }, [fetchEvents])

  const navigate = (direction: number) => {
    setCurrentDate((prev) => {
      const d = new Date(prev)
      d.setMonth(d.getMonth() + direction)
      return d
    })
  }

  const handleExport = async (format: "csv" | "json") => {
    setExporting(format)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const url = format === "csv"
        ? `${API_BASE}/scheduler/export/schedule/csv`
        : `${API_BASE}/scheduler/export/schedule/json`

      const response = await fetch(url, { headers })
      if (response.ok) {
        const blob = await response.blob()
        const a = document.createElement("a")
        a.href = URL.createObjectURL(blob)
        a.download = `schedule.${format}`
        a.click()
      }
    } finally {
      setExporting(null)
    }
  }

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate()
  const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay()

  const monthDays: (number | null)[] = []
  for (let i = 0; i < firstDay; i++) monthDays.push(null)
  for (let i = 1; i <= daysInMonth; i++) monthDays.push(i)

  const getEventsForDay = (day: number) => {
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`
    return events.filter((e) => e.date === dateStr)
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h3 className="text-lg font-semibold min-w-[200px] text-center">
                {currentDate.toLocaleDateString("en-US", { month: "long", year: "numeric" })}
              </h3>
              <Button variant="outline" size="icon" onClick={() => navigate(1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setCurrentDate(new Date())}>
                Today
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => handleExport("csv")} disabled={!!exporting}>
                {exporting === "csv" ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : <FileText className="h-3.5 w-3.5 mr-1" />}
                CSV
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport("json")} disabled={!!exporting}>
                {exporting === "json" ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : <FileJson className="h-3.5 w-3.5 mr-1" />}
                JSON
              </Button>
              <Button variant="ghost" size="icon" onClick={fetchEvents}>
                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Month Grid */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-7 gap-px bg-border rounded-lg overflow-hidden">
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
              <div key={d} className="bg-muted p-2 text-center text-xs font-medium text-muted-foreground">
                {d}
              </div>
            ))}
            {monthDays.map((day, i) => {
              if (day === null) return <div key={`empty-${i}`} className="bg-background p-2 min-h-[80px]" />
              const dayEvents = getEventsForDay(day)
              const isToday = new Date().getDate() === day && new Date().getMonth() === currentDate.getMonth()

              return (
                <div
                  key={day}
                  className={`bg-background p-1.5 min-h-[80px] ${isToday ? "ring-2 ring-primary ring-inset" : ""}`}
                >
                  <div className={`text-xs font-medium mb-1 ${isToday ? "text-primary font-bold" : "text-muted-foreground"}`}>
                    {day}
                  </div>
                  <div className="space-y-0.5">
                    {dayEvents.slice(0, 3).map((evt) => (
                      <div
                        key={evt.id}
                        className={`border-l-2 rounded-r px-1 py-0.5 text-[9px] truncate ${PLATFORM_COLORS[evt.platform] || "border-l-gray-300 bg-gray-50"}`}
                      >
                        <span className="font-medium">{evt.title || "Post"}</span>
                      </div>
                    ))}
                    {dayEvents.length > 3 && (
                      <div className="text-[9px] text-muted-foreground pl-1">
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

      {/* Legend */}
      <div className="flex flex-wrap gap-2 text-xs">
        {(["linkedin", "x", "instagram", "facebook", "youtube"] as Platform[]).map((p) => (
          <div key={p} className={`border-l-2 pl-2 ${PLATFORM_COLORS[p] || ""}`}>
            <span className="capitalize">{p}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
