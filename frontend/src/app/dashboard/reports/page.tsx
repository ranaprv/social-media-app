"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Plus, Download, Loader2, Calendar } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export default function ReportsPage() {
  const [reports, setReports] = useState<Array<{ id: string; name: string; metrics: string[]; schedule: string; last_generated: string }>>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/reports`).then(r => r.json()).then(d => setReports(d.reports || [])).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const generate = async (id: string) => { setGenerating(id); await fetch(`${API_URL}/reports/${id}/generate`, { method: "POST" }); setGenerating(null) }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div><h1 className="text-3xl font-bold">Reports</h1><p className="text-muted-foreground">Build custom analytics reports and export data.</p></div>
          <Button className="gap-2"><Plus className="h-4 w-4" /> New Report</Button>
        </div>
        {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : (
          <div className="space-y-4">
            {reports.map((r) => (
              <Card key={r.id}>
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <h4 className="font-medium">{r.name}</h4>
                      <p className="text-sm text-muted-foreground">Metrics: {r.metrics.join(", ")} • Schedule: {r.schedule}</p>
                      <p className="text-xs text-muted-foreground">Last generated: {r.last_generated}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => generate(r.id)} disabled={generating === r.id}>
                      {generating === r.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Download className="h-3 w-3" />}
                      Generate
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
