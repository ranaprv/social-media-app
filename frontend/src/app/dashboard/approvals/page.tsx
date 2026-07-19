"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckCircle, XCircle, Clock, Loader2, MessageSquare } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Approval { id: string; post_title: string; workflow_name: string; current_stage: number; total_stages: number; stage_name: string; requested_by: string; requested_at: string }

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/approvals/pending`).then(r => r.json()).then(d => setApprovals(d.approvals || [])).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const approve = async (id: string) => { await fetch(`${API_URL}/approvals/approve/${id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: "Approved" }) }); setApprovals((p) => p.filter((a) => a.id !== id)) }
  const reject = async (id: string) => { await fetch(`${API_URL}/approvals/reject/${id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reason: "Needs revision" }) }); setApprovals((p) => p.filter((a) => a.id !== id)) }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div><h1 className="text-3xl font-bold">Approval Workflows</h1><p className="text-muted-foreground">Review and approve content before publishing.</p></div>
        {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : approvals.length === 0 ? (
          <Card><CardContent className="flex flex-col items-center py-16 text-center"><CheckCircle className="mb-3 h-10 w-10 text-green-500" /><p className="font-medium">All caught up!</p><p className="text-sm text-muted-foreground">No content pending approval.</p></CardContent></Card>
        ) : (
          <div className="space-y-4">
            {approvals.map((a) => (
              <Card key={a.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium">{a.post_title}</h4>
                      <p className="text-sm text-muted-foreground">Workflow: {a.workflow_name} • Requested by {a.requested_by}</p>
                      <div className="mt-2 flex items-center gap-2">
                        {Array.from({ length: a.total_stages }).map((_, i) => (
                          <div key={i} className={`h-2 w-8 rounded-full ${i < a.current_stage ? "bg-green-500" : i === a.current_stage - 1 ? "bg-yellow-500" : "bg-gray-200 dark:bg-gray-700"}`} />
                        ))}
                        <span className="text-xs text-muted-foreground">Stage {a.current_stage}/{a.total_stages} — {a.stage_name}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" className="gap-1" onClick={() => approve(a.id)}><CheckCircle className="h-3 w-3" /> Approve</Button>
                      <Button size="sm" variant="outline" className="gap-1" onClick={() => reject(a.id)}><XCircle className="h-3 w-3" /> Reject</Button>
                    </div>
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
