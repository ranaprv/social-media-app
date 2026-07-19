"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Upload,
  Download,
  FileText,
  Loader2,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface ImportResult {
  total_rows: number
  created: number
  errors: number
  items: { row: number; post_id: string; platform: string; title: string }[]
  error_details: string[]
}

export function BulkImportExport() {
  const [csvContent, setCsvContent] = useState("")
  const [autoSchedule, setAutoSchedule] = useState(false)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)

  const importCSV = async () => {
    if (!csvContent) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/import/csv`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          csv_content: csvContent,
          auto_schedule: autoSchedule,
          platform: "linkedin",
        }),
      })
      if (response.ok) setImportResult(await response.json())
    } finally {
      setLoading(false)
    }
  }

  const exportCSV = async () => {
    setExporting(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/export/csv`, { headers })
      if (response.ok) {
        const blob = await response.blob()
        const a = document.createElement("a")
        a.href = URL.createObjectURL(blob)
        a.download = "posts_export.csv"
        a.click()
      }
    } finally {
      setExporting(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Bulk Import / Export
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Import */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">
            Paste CSV content (columns: title, content, platform, scheduled_at, tags)
          </label>
          <Textarea
            value={csvContent}
            onChange={(e) => setCsvContent(e.target.value)}
            placeholder='title,content,platform,scheduled_at,tags&#10;"My Post","Hello world","linkedin","2026-07-20T10:00:00","tip,social"'
            className="min-h-[80px] text-[10px] font-mono"
          />
          <label className="flex items-center gap-2 text-xs">
            <input
              type="checkbox"
              checked={autoSchedule}
              onChange={(e) => setAutoSchedule(e.target.checked)}
              className="rounded"
            />
            Auto-schedule imported posts
          </label>
          <Button onClick={importCSV} disabled={loading || !csvContent} size="sm" className="w-full gap-1">
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />}
            Import
          </Button>
        </div>

        {/* Import result */}
        {importResult && (
          <div className="rounded-lg border p-2.5 space-y-1.5 text-xs">
            <div className="flex items-center gap-3">
              <Badge variant="default" className="bg-green-600">{importResult.created} imported</Badge>
              {importResult.errors > 0 && (
                <Badge variant="destructive">{importResult.errors} errors</Badge>
              )}
            </div>
            {importResult.error_details.slice(0, 5).map((err, i) => (
              <p key={i} className="text-red-500 text-[10px]">• {err}</p>
            ))}
          </div>
        )}

        {/* Export */}
        <div className="border-t pt-3">
          <Button onClick={exportCSV} disabled={exporting} variant="outline" size="sm" className="w-full gap-1">
            {exporting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
            Export All Posts to CSV
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
