"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  BarChart3,
  TrendingUp,
  Users,
  Globe,
  RefreshCw,
  Loader2,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface WorkspaceMetrics {
  posts: { total: number; last_7_days: number }
  queue: {
    total_entries: number
    by_status: Record<string, number>
    success_rate: number
  }
  connections: { count: number; platforms: string[] }
  analytics: {
    total_impressions: number
    total_engagement: number
    total_reach: number
    total_clicks: number
    impressions_7d: number
    engagement_7d: number
    engagement_rate: number
  }
}

interface SystemHealth {
  timestamp: string
  workspaces: number
  total_posts: number
  last_24h: { published: number; failed: number; success_rate: number }
  queue_depth: number
}

export function AdminMetricsDashboard() {
  const [metrics, setMetrics] = useState<WorkspaceMetrics | null>(null)
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const [metricsRes, healthRes] = await Promise.all([
        fetch(`${API_BASE}/scheduler/admin/metrics`, { headers }),
        fetch(`${API_BASE}/scheduler/admin/system-health`, { headers }),
      ])

      if (metricsRes.ok) setMetrics(await metricsRes.json())
      if (healthRes.ok) setSystemHealth(await healthRes.json())
    } catch (err) {
      console.error("Failed to load admin metrics:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  const formatNumber = (n: number) => {
    if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
    if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
    return n.toString()
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Loading metrics...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Admin Dashboard
        </h3>
        <Button variant="ghost" size="icon" onClick={fetchData}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* System Health */}
      {systemHealth && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="text-center">
                <div className="text-lg font-bold">{systemHealth.workspaces}</div>
                <div className="text-[10px] text-muted-foreground">Workspaces</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold">{systemHealth.total_posts}</div>
                <div className="text-[10px] text-muted-foreground">Total Posts</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">{systemHealth.last_24h.published}</div>
                <div className="text-[10px] text-muted-foreground">Published (24h)</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-red-600">{systemHealth.last_24h.failed}</div>
                <div className="text-[10px] text-muted-foreground">Failed (24h)</div>
              </div>
            </div>
            <div className="flex items-center justify-center gap-2 mt-3">
              <Badge variant={systemHealth.last_24h.success_rate >= 90 ? "default" : "destructive"}>
                {systemHealth.last_24h.success_rate}% success (24h)
              </Badge>
              <Badge variant="outline">{systemHealth.queue_depth} in queue</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Workspace Metrics */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-xl font-bold">{formatNumber(metrics.analytics.total_impressions)}</div>
              <div className="text-[10px] text-muted-foreground">Total Impressions</div>
              <div className="text-[10px] text-green-600 mt-0.5">
                {formatNumber(metrics.analytics.impressions_7d)} this week
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-xl font-bold">{metrics.analytics.engagement_rate}%</div>
              <div className="text-[10px] text-muted-foreground">Engagement Rate</div>
              <div className="text-[10px] text-green-600 mt-0.5">
                {formatNumber(metrics.analytics.total_engagement)} total
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-xl font-bold">{metrics.connections.count}</div>
              <div className="text-[10px] text-muted-foreground">Connected Platforms</div>
              <div className="text-[10px] text-muted-foreground mt-0.5">
                {metrics.connections.platforms.join(", ") || "None"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className={`text-xl font-bold ${metrics.queue.success_rate >= 90 ? "text-green-600" : "text-red-600"}`}>
                {metrics.queue.success_rate}%
              </div>
              <div className="text-[10px] text-muted-foreground">Publish Success Rate</div>
              <div className="text-[10px] text-muted-foreground mt-0.5">
                {metrics.queue.total_entries} total entries
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Queue Breakdown */}
      {metrics && Object.keys(metrics.queue.by_status).length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Queue Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {Object.entries(metrics.queue.by_status).map(([status, count]) => (
                <div key={status} className="flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5">
                  {status === "published" && <CheckCircle2 className="h-3 w-3 text-green-500" />}
                  {status === "failed" && <XCircle className="h-3 w-3 text-red-500" />}
                  {status === "scheduled" && <Clock className="h-3 w-3 text-blue-500" />}
                  {status === "publishing" && <Activity className="h-3 w-3 text-orange-500" />}
                  <span className="text-xs font-medium capitalize">{status}</span>
                  <span className="text-xs text-muted-foreground">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
