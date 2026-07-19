"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  CheckCircle2,
  XCircle,
  Clock,
  MessageSquare,
  RefreshCw,
  Loader2,
  Send,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ApprovalItem {
  post_id: string
  title: string
  content_preview: string
  platforms: { platform: Platform; status: string }[]
  requested_at: string | null
  author_id: string
}

export function ApprovalWorkflow() {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [rejectReason, setRejectReason] = useState<Record<string, string>>({})

  const fetchApprovals = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/approval/pending`, { headers })
      if (response.ok) {
        const data = await response.json()
        setApprovals(data.approvals || [])
      }
    } catch (err) {
      console.error("Failed to load approvals:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchApprovals() }, [fetchApprovals])

  const handleApprove = async (postId: string) => {
    setActionLoading(postId)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      await fetch(`${API_BASE}/scheduler/approval/approve/${postId}`, {
        method: "POST",
        headers,
        body: JSON.stringify({ comment: "" }),
      })
      await fetchApprovals()
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (postId: string) => {
    setActionLoading(postId)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      await fetch(`${API_BASE}/scheduler/approval/reject/${postId}`, {
        method: "POST",
        headers,
        body: JSON.stringify({ reason: rejectReason[postId] || "" }),
      })
      setRejectReason((prev) => { const n = { ...prev }; delete n[postId]; return n })
      await fetchApprovals()
    } finally {
      setActionLoading(null)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Loading approvals...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Send className="h-4 w-4" />
            Pending Approvals
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant={approvals.length > 0 ? "destructive" : "secondary"}>
              {approvals.length} pending
            </Badge>
            <Button variant="ghost" size="icon" onClick={fetchApprovals}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {approvals.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <CheckCircle2 className="h-10 w-10 mx-auto mb-2 text-green-500 opacity-50" />
            <p className="text-sm">All caught up! No pending approvals.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {approvals.map((item) => (
              <div key={item.post_id} className="rounded-lg border p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium">{item.title}</h4>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                      {item.content_preview}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      {item.platforms.map((p) => (
                        <Badge key={p.platform} variant="outline" className="text-[10px] capitalize">
                          {p.platform}
                        </Badge>
                      ))}
                      {item.requested_at && (
                        <span className="text-[10px] text-muted-foreground">
                          {new Date(item.requested_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Reject reason input */}
                {rejectReason[item.post_id] !== undefined && (
                  <div className="mt-3">
                    <Textarea
                      value={rejectReason[item.post_id]}
                      onChange={(e) => setRejectReason((prev) => ({ ...prev, [item.post_id]: e.target.value }))}
                      placeholder="Reason for rejection..."
                      className="min-h-[60px] text-sm"
                    />
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2 mt-3">
                  <Button
                    size="sm"
                    onClick={() => handleApprove(item.post_id)}
                    disabled={actionLoading === item.post_id}
                    className="gap-1.5 bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Approve
                  </Button>
                  {rejectReason[item.post_id] !== undefined ? (
                    <>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleReject(item.post_id)}
                        disabled={actionLoading === item.post_id}
                      >
                        Confirm Reject
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setRejectReason((prev) => { const n = { ...prev }; delete n[item.post_id]; return n })}
                      >
                        Cancel
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setRejectReason((prev) => ({ ...prev, [item.post_id]: "" }))}
                    >
                      <XCircle className="h-3.5 w-3.5 mr-1" />
                      Reject
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
