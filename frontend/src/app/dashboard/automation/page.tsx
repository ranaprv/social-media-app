"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Zap, Plus, Trash2, Play, Pause, Loader2 } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface Rule { id: string; trigger_type: string; trigger_value: string; action_type: string; response_text: string; platforms: string[]; is_active: boolean; trigger_count: number }

export default function AutomationPage() {
  const [rules, setRules] = useState<Rule[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newTrigger, setNewTrigger] = useState("")
  const [newResponse, setNewResponse] = useState("")

  useEffect(() => {
    fetch(`${API_URL}/automation/rules`).then(r => r.json()).then(d => setRules(d.rules || [])).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const createRule = async () => {
    if (!newTrigger.trim() || !newResponse.trim()) return
    const res = await fetch(`${API_URL}/automation/rules`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ trigger_type: "keyword", trigger_value: newTrigger, action_type: "reply", response_text: newResponse, platforms: ["x", "linkedin"] }) })
    if (res.ok) { const data = await res.json(); setRules((p) => [...p, data]); setNewTrigger(""); setNewResponse(""); setShowForm(false) }
  }

  const toggleRule = async (id: string) => {
    await fetch(`${API_URL}/automation/rules/${id}/toggle`, { method: "PUT" })
    setRules((p) => p.map((r) => r.id === id ? { ...r, is_active: !r.is_active } : r))
  }

  const deleteRule = async (id: string) => {
    await fetch(`${API_URL}/automation/rules/${id}`, { method: "DELETE" })
    setRules((p) => p.filter((r) => r.id !== id))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div><h1 className="text-3xl font-bold">Message Automation</h1><p className="text-muted-foreground">Auto-reply rules, keyword triggers, and saved replies.</p></div>
          <Button className="gap-2" onClick={() => setShowForm(!showForm)}><Plus className="h-4 w-4" /> New Rule</Button>
        </div>

        {showForm && (
          <Card><CardContent className="pt-6 space-y-3">
            <div><label className="mb-1 block text-sm font-medium">Trigger Keyword</label><input className="w-full rounded-lg border bg-background p-2 text-sm" placeholder="e.g. pricing, demo, help" value={newTrigger} onChange={(e) => setNewTrigger(e.target.value)} /></div>
            <div><label className="mb-1 block text-sm font-medium">Auto-Reply Message</label><textarea className="w-full rounded-lg border bg-background p-3 text-sm" rows={3} placeholder="Response message..." value={newResponse} onChange={(e) => setNewResponse(e.target.value)} /></div>
            <div className="flex gap-2">
              <Button onClick={createRule} disabled={!newTrigger.trim() || !newResponse.trim()}>Create Rule</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent></Card>
        )}

        <div className="space-y-3">
          {loading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div> : rules.map((rule) => (
            <Card key={rule.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <Zap className={`h-5 w-5 ${rule.is_active ? "text-green-500" : "text-gray-400"}`} />
                  <div>
                    <h4 className="font-medium">&quot;{rule.trigger_value}&quot; → Auto-reply</h4>
                    <p className="text-sm text-muted-foreground truncate max-w-md">{rule.response_text}</p>
                    <div className="flex gap-1 mt-1">{rule.platforms.map((p) => <span key={p} className="rounded bg-muted px-1.5 py-0.5 text-[10px] capitalize">{p}</span>)}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">{rule.trigger_count} triggers</span>
                  <Button variant="ghost" size="sm" onClick={() => toggleRule(rule.id)}>{rule.is_active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}</Button>
                  <Button variant="ghost" size="sm" onClick={() => deleteRule(rule.id)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  )
}
