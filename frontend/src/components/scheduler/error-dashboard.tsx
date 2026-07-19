"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RotateCcw,
  BarChart3,
  RefreshCw,
  Loader2,
  Filter,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ErrorSummary {
  period_days: number
  total_attempts: number
  total_failures: number
  failure_rate: number
  by_platform: Record<string, { attempts: number; failures: number; rate: number }>
  by_error_type: { error: string; count: number; platforms: string[] }[]
  recent_failures: {
    id: string
    post_id: string
    platform: string
    error: string | null
    retry_count: number
    max_retries: number
    created_at: string | null
    scheduled_at: string | null
  }[]
  retry_stats: { retried: number; recovered: number; permanently_failed: number }
}

interface PublishStats {
  period_days: number
  total: number
  by_status: Record<string, number>
  success_rate: number
  published: number
  failed: number
  scheduled: number
  publishing: number
}

export function ErrorDashboard() {
  const [errors, setErrors] = useState<ErrorSummary | null>(null)
  const [stats, setStats] = useState<PublishStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState(30)
  const [retryingAll, setRetryingAll] = useState(false)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const [errorsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/scheduler/errors/summary?days=${period}`, { headers }),
        fetch(`${API_BASE}/scheduler/errors/stats?days=${period}`, { headers }),
      ])

      if (errorsRes.ok) setErrors(await errorsRes.json())
      if (statsRes.ok) setStats(await statsRes.json())
    } catch (err) {
      console.error("Failed to load error data:", err)
    } finally {
      setLoading(false)
    }
  }, [period])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRetryAll = async (platform?: string) => {
    setRetryingAll(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const url = platform
        ? `${API_BASE}/scheduler/errors/retry-all?platform=${platform}`
        : `${API_BASE}/scheduler/errors/retry-all`

      await fetch(url, { method: "POST", headers })
      await fetchData()
    } finally {
      setRetryingAll(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Loading error data...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {[7, 30, 90].map((d) => (
            <Button
              key={d}
              variant={period === d ? "default" : "outline"}
              size="sm"
              onClick={() => setPeriod(d)}
            >
              {d}d
            </Button>
          ))}
        </div>
        <Button variant="ghost" size="icon" onClick={fetchData}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Overview Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold">{stats.total}</div>
              <div className="text-xs text-muted-foreground">Total Posts</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{stats.published}</div>
              <div className="text-xs text-muted-foreground">Published</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
              <div className="text-xs text-muted-foreground">Failed</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-3 text-center">
              <div className={`text-2xl font-bold ${stats.success_rate >= 90 ? "text-green-600" : stats.success_rate >= 70 ? "text-yellow-600" : "text-red-600"}`}>
                {stats.success_rate}%
              </div>
              <div className="text-xs text-muted-foreground">Success Rate</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error Details */}
      {errors && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* By Platform */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Failures by Platform
              </CardTitle>
            </CardHeader>
            <CardContent>
              {Object.entries(errors.by_platform).map(([platform, data]) => (
                <div key={platform} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium capitalize">{platform}</span>
                    <span className="text-xs text-muted-foreground">
                      {data.attempts} attempts
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${data.rate > 20 ? "text-red-600" : data.rate > 10 ? "text-yellow-600" : "text-green-600"}`}>
                      {data.rate}%
                    </span>
                    {data.failures > 0 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 text-xs"
                        onClick={() => handleRetryAll(platform)}
                        disabled={retryingAll}
                      >
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              {Object.keys(errors.by_platform).length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No publish attempts in this period.
                </p>
              )}
            </CardContent>
          </Card>

          {/* By Error Type */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Error Categories
              </CardTitle>
            </CardHeader>
            <CardContent>
              {errors.by_error_type.map((errorType, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <span className="text-sm">{errorType.error}</span>
                    <div className="flex gap-1 mt-0.5">
                      {errorType.platforms.map((p) => (
                        <Badge key={p} variant="outline" className="text-[10px] px-1 py-0 capitalize">
                          {p}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <Badge variant="secondary">{errorType.count}</Badge>
                </div>
              ))}
              {errors.by_error_type.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No errors in this period.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Retry Stats + Bulk Retry */}
      {errors && errors.retry_stats.retried > 0 && (
        <Card>
          <CardContent className="p-3 flex items-center justify-between">
            <div className="flex items-center gap-4 text-sm">
              <span className="flex items-center gap-1">
                <RotateCcw className="h-3.5 w-3.5" />
                {errors.retry_stats.retried} retried
              </span>
              <span className="flex items-center gap-1 text-green-600">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {errors.retry_stats.recovered} recovered
              </span>
              <span className="flex items-center gap-1 text-red-600">
                <XCircle className="h-3.5 w-3.5" />
                {errors.retry_stats.permanently_failed} permanently failed
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRetryAll()}
              disabled={retryingAll || errors.total_failures === 0}
              className="gap-1.5"
            >
              <RotateCcw className={`h-3.5 w-3.5 ${retryingAll ? "animate-spin" : ""}`} />
              Retry All Failed
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Recent Failures */}
      {errors && errors.recent_failures.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Recent Failures</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {errors.recent_failures.map((failure) => (
                <div
                  key={failure.id}
                  className="flex items-start gap-3 rounded-lg border p-2.5 text-sm"
                >
                  <XCircle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium capitalize">{failure.platform}</span>
                      <span className="text-xs text-muted-foreground">
                        {failure.retry_count}/{failure.max_retries} retries
                      </span>
                      {failure.scheduled_at && (
                        <span className="text-xs text-muted-foreground">
                          {new Date(failure.scheduled_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-red-600 truncate mt-0.5">
                      {failure.error || "Unknown error"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
