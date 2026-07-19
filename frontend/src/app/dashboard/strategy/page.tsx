"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Zap, Target, BarChart3, Clock, Loader2 } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Strategy {
  id: string
  name: string
  status: string
  computed_stats: {
    total_posts_per_week: number
    total_posts_per_month: number
    platforms_active: string[]
    pillar_balance: Record<string, number>
  }
  created_at: string
  updated_at: string
}

const statusColors: Record<string, string> = {
  draft: "bg-gray-100 text-gray-800",
  active: "bg-green-100 text-green-800",
  paused: "bg-yellow-100 text-yellow-800",
  archived: "bg-red-100 text-red-800",
}

export default function StrategyPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)

  async function fetchStrategies() {
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/strategies/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        setStrategies(await res.json())
      }
    } catch (e) {
      console.error("Failed to fetch strategies")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void (async () => { await fetchStrategies() })() }, [])

  async function handleQuickStart() {
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`${API_URL}/strategies/quick-start`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        window.location.href = `/dashboard/strategy/${data.id}`
      }
    } catch (e) {
      console.error("Quick start failed")
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Content Strategy</h1>
            <p className="text-muted-foreground mt-1">Define your growth strategy and auto-generate content</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleQuickStart}>
              <Zap className="h-4 w-4 mr-2" />
              Quick Start
            </Button>
            <Link href="/dashboard/strategy/wizard">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Strategy
              </Button>
            </Link>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : strategies.length === 0 ? (
          <Card>
            <CardContent className="py-16 text-center">
              <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No strategies yet</h3>
              <p className="text-muted-foreground mb-6">Create your first content strategy to start auto-generating posts</p>
              <div className="flex gap-3 justify-center">
                <Button variant="outline" onClick={handleQuickStart}>
                  <Zap className="h-4 w-4 mr-2" />
                  Quick Start
                </Button>
                <Link href="/dashboard/strategy/wizard">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Strategy
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {strategies.map((s) => (
              <Link key={s.id} href={`/dashboard/strategy/${s.id}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-lg">{s.name}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[s.status] || ""}`}>
                            {s.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <BarChart3 className="h-4 w-4" />
                            {s.computed_stats.total_posts_per_week} posts/week
                          </span>
                          <span className="flex items-center gap-1">
                            <Target className="h-4 w-4" />
                            {Object.keys(s.computed_stats.pillar_balance).length} pillars
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {new Date(s.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-1">
                        {s.computed_stats.platforms_active.map((p) => (
                          <span key={p} className="px-2 py-1 bg-muted rounded text-xs capitalize">
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
