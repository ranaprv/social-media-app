"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  CheckSquare,
  XSquare,
  Calendar,
  Type,
  Loader2,
  RefreshCw,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface BulkOperationsToolbarProps {
  selectedIds: string[]
  onClearSelection: () => void
  onComplete: () => void
}

export function BulkOperationsToolbar({
  selectedIds,
  onClearSelection,
  onComplete,
}: BulkOperationsToolbarProps) {
  const [action, setAction] = useState<string | null>(null)
  const [rescheduleDate, setRescheduleDate] = useState("")
  const [captionTemplate, setCaptionTemplate] = useState("")

  const handleBulkAction = async (actionType: string) => {
    setAction(actionType)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      let url = ""
      let body: Record<string, unknown> = {}

      switch (actionType) {
        case "cancel":
          url = `${API_BASE}/scheduler/bulk/cancel`
          body = { item_ids: selectedIds }
          break
        case "reschedule":
          url = `${API_BASE}/scheduler/bulk/reschedule`
          body = { item_ids: selectedIds, new_start: rescheduleDate, interval_minutes: 15 }
          break
        case "caption":
          url = `${API_BASE}/scheduler/bulk/caption`
          body = { item_ids: selectedIds, caption_template: captionTemplate }
          break
      }

      if (url) {
        const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) })
        if (response.ok) {
          onComplete()
          onClearSelection()
          setRescheduleDate("")
          setCaptionTemplate("")
        }
      }
    } finally {
      setAction(null)
    }
  }

  if (selectedIds.length === 0) return null

  return (
    <Card className="border-primary">
      <CardContent className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Badge variant="default">{selectedIds.length} selected</Badge>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="destructive"
                onClick={() => handleBulkAction("cancel")}
                disabled={!!action}
                className="gap-1"
              >
                {action === "cancel" ? <Loader2 className="h-3 w-3 animate-spin" /> : <XSquare className="h-3 w-3" />}
                Cancel
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleBulkAction("reschedule")}
                disabled={!!action || !rescheduleDate}
                className="gap-1"
              >
                <Calendar className="h-3 w-3" />
                Reschedule
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleBulkAction("caption")}
                disabled={!!action || !captionTemplate}
                className="gap-1"
              >
                <Type className="h-3 w-3" />
                Update Caption
              </Button>
            </div>
          </div>
          <Button size="sm" variant="ghost" onClick={onClearSelection}>
            Clear
          </Button>
        </div>

        {/* Inline inputs */}
        <div className="flex gap-2 mt-2">
          <Input
            type="datetime-local"
            value={rescheduleDate}
            onChange={(e) => setRescheduleDate(e.target.value)}
            placeholder="New time"
            className="h-7 text-xs flex-1"
          />
          <Input
            value={captionTemplate}
            onChange={(e) => setCaptionTemplate(e.target.value)}
            placeholder="Caption template ({platform}, {date})"
            className="h-7 text-xs flex-1"
          />
        </div>
      </CardContent>
    </Card>
  )
}
