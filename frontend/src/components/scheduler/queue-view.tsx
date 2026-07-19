"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Clock,
  XCircle,
  RotateCcw,
  Trash2,
  Loader2,
  Filter,
} from "lucide-react"
import type { PostPlatform, Platform, PostStatus, QueueFilters } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const PLATFORM_ICONS: Record<Platform, { label: string; color: string }> = {
  linkedin: { label: "LinkedIn", color: "text-blue-600" },
  x: { label: "X", color: "text-black" },
  instagram: { label: "Instagram", color: "text-pink-500" },
  facebook: { label: "Facebook", color: "text-blue-500" },
  youtube: { label: "YouTube", color: "text-red-600" },
}

const STATUS_CONFIG: Record<string, { icon: typeof Clock; color: string; label: string }> = {
  draft: { icon: Clock, color: "bg-gray-100 text-gray-700", label: "Draft" },
  scheduled: { icon: Clock, color: "bg-blue-100 text-blue-700", label: "Scheduled" },
  publishing: { icon: Loader2, color: "bg-orange-100 text-orange-700", label: "Publishing" },
  published: { icon: CheckCircle2, color: "bg-green-100 text-green-700", label: "Published" },
  failed: { icon: AlertCircle, color: "bg-red-100 text-red-700", label: "Failed" },
  cancelled: { icon: XCircle, color: "bg-gray-100 text-gray-500", label: "Cancelled" },
}

interface QueueViewProps {
  workspaceId?: string
}

export function QueueView({ workspaceId }: QueueViewProps) {
  const [items, setItems] = useState<PostPlatform[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<QueueFilters>({
    status: "all",
    platform: "all",
    offset: 0,
    limit: 20,
  })
  const [retryingId, setRetryingId] = useState<string | null>(null)

  const fetchQueue = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (filters.status && filters.status !== "all") params.set("status", filters.status)
      if (filters.platform && filters.platform !== "all") params.set("platform", filters.platform)
      params.set("offset", String(filters.offset || 0))
      params.set("limit", String(filters.limit || 20))

      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/queue?${params}`, { headers })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const data = await response.json()
      setItems(data.queue || [])
      setTotal(data.total || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load queue")
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchQueue()
  }, [fetchQueue])

  const handleRetry = async (itemId: string) => {
    setRetryingId(itemId)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/queue/${itemId}/retry`, {
        method: "POST",
        headers,
      })

      if (response.ok) {
        await fetchQueue()
      }
    } finally {
      setRetryingId(null)
    }
  }

  const handleCancel = async (itemId: string) => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
    const headers: Record<string, string> = {}
    if (token) headers["Authorization"] = `Bearer ${token}`

    const response = await fetch(`${API_BASE}/scheduler/queue/${itemId}`, {
      method: "DELETE",
      headers,
    })

    if (response.ok) {
      await fetchQueue()
    }
  }

  const formatDateTime = (iso: string | null): string => {
    if (!iso) return "—"
    const d = new Date(iso)
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    })
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Publishing Queue</CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={fetchQueue}
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mt-2">
          <select
            value={filters.status || "all"}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                status: e.target.value as PostStatus | "all",
                offset: 0,
              }))
            }
            className="rounded-md border border-border bg-background px-2 py-1 text-xs"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="publishing">Publishing</option>
            <option value="published">Published</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select
            value={filters.platform || "all"}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                platform: e.target.value as Platform | "all",
                offset: 0,
              }))
            }
            className="rounded-md border border-border bg-background px-2 py-1 text-xs"
          >
            <option value="all">All Platforms</option>
            <option value="linkedin">LinkedIn</option>
            <option value="x">X (Twitter)</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="youtube">YouTube</option>
          </select>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="text-sm text-red-500 bg-red-50 rounded-md p-3 mb-3">
            {error}
          </div>
        )}

        {loading && items.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
            <p className="text-sm">Loading queue...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No items in queue</p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item) => {
              const statusConf = STATUS_CONFIG[item.status] || STATUS_CONFIG.draft
              const platformConf = PLATFORM_ICONS[item.platform]
              const StatusIcon = statusConf.icon
              const isRetrying = retryingId === item.id

              return (
                <div
                  key={item.id}
                  className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50 transition-colors"
                >
                  {/* Status icon */}
                  <div
                    className={`rounded-full p-1 ${statusConf.color}`}
                  >
                    <StatusIcon
                      className={`h-3.5 w-3.5 ${
                        item.status === "publishing" ? "animate-spin" : ""
                      }`}
                    />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium truncate">
                        {item.title || "Untitled"}
                      </span>
                      <span
                        className={`text-xs font-medium ${platformConf?.color}`}
                      >
                        {platformConf?.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-0.5 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDateTime(item.scheduled_at)}
                      </span>
                      {item.retry_count > 0 && (
                        <span className="text-orange-600">
                          {item.retry_count}/{item.max_retries} retries
                        </span>
                      )}
                      {item.error_message && (
                        <span className="text-red-500 truncate max-w-[200px]">
                          {item.error_message}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Status badge */}
                  <Badge
                    variant="secondary"
                    className={`text-[10px] px-1.5 py-0 ${statusConf.color}`}
                  >
                    {statusConf.label}
                  </Badge>

                  {/* Actions */}
                  <div className="flex items-center gap-1">
                    {item.status === "failed" && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() => handleRetry(item.id)}
                        disabled={isRetrying}
                      >
                        <RotateCcw
                          className={`h-3.5 w-3.5 ${
                            isRetrying ? "animate-spin" : ""
                          }`}
                        />
                      </Button>
                    )}
                    {(item.status === "scheduled" || item.status === "draft") && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-red-500 hover:text-red-700"
                        onClick={() => handleCancel(item.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}

            {/* Pagination */}
            {total > (filters.limit || 20) && (
              <div className="flex items-center justify-between pt-3 text-xs text-muted-foreground">
                <span>
                  Showing {(filters.offset || 0) + 1}–
                  {Math.min((filters.offset || 0) + (filters.limit || 20), total)} of{" "}
                  {total}
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={(filters.offset || 0) === 0}
                    onClick={() =>
                      setFilters((prev) => ({
                        ...prev,
                        offset: Math.max(0, (prev.offset || 0) - (prev.limit || 20)),
                      }))
                    }
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={(filters.offset || 0) + (filters.limit || 20) >= total}
                    onClick={() =>
                      setFilters((prev) => ({
                        ...prev,
                        offset: (prev.offset || 0) + (prev.limit || 20),
                      }))
                    }
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
