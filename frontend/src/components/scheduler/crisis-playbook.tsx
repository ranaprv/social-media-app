"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Shield,
  RefreshCw,
  Loader2,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface CrisisScenario {
  name: string
  severity: string
  response_framework: string
  templates: { name: string; template: string; timing: string }[]
  do: string[]
  dont: string[]
}

export function CrisisPlaybook() {
  const [playbook, setPlaybook] = useState<Record<string, CrisisScenario>>({})
  const [checklist, setChecklist] = useState<{ step: string; priority: string }[]>([])
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const [playbookRes, checklistRes] = await Promise.all([
        fetch(`${API_BASE}/scheduler/crisis/playbook`, { headers }),
        fetch(`${API_BASE}/scheduler/crisis/checklist`, { headers }),
      ])

      if (playbookRes.ok) {
        const data = await playbookRes.json()
        setPlaybook(data.playbooks || {})
      }
      if (checklistRes.ok) {
        const data = await checklistRes.json()
        setChecklist(data.checklist || [])
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void (async () => { await fetchData() })() }, [fetchData])

  const severityColor = (s: string) => {
    if (s === "high") return "bg-red-100 text-red-700"
    if (s === "medium") return "bg-yellow-100 text-yellow-700"
    return "bg-gray-100 text-gray-600"
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Loader2 className="h-5 w-5 animate-spin mx-auto" />
        </CardContent>
      </Card>
    )
  }

  const activeScenario = selectedScenario ? playbook[selectedScenario] : null

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Crisis Playbook
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={fetchData}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Scenario selector */}
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(playbook).map(([key, scenario]) => (
            <button
              key={key}
              onClick={() => setSelectedScenario(selectedScenario === key ? null : key)}
              className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium transition-all ${
                selectedScenario === key
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {scenario.name}
            </button>
          ))}
        </div>

        {/* Active scenario */}
        {activeScenario && (
          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center gap-2">
              <Badge className={`text-[9px] ${severityColor(activeScenario.severity)}`}>
                {activeScenario.severity}
              </Badge>
              <span className="text-xs font-medium">{activeScenario.response_framework}</span>
            </div>

            {/* Templates */}
            {activeScenario.templates.map((t, i) => (
              <div key={i} className="rounded border p-2 text-[10px]">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium">{t.name}</span>
                  <Badge variant="outline" className="text-[8px]">{t.timing}</Badge>
                </div>
                <p className="text-muted-foreground">{t.template}</p>
              </div>
            ))}

            {/* Do / Don't */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <h4 className="text-[10px] font-medium text-green-600 mb-1">✓ Do</h4>
                {activeScenario.do.map((item, i) => (
                  <p key={i} className="text-[10px] text-muted-foreground">• {item}</p>
                ))}
              </div>
              <div>
                <h4 className="text-[10px] font-medium text-red-600 mb-1">✗ Don&apos;t</h4>
                {activeScenario.dont.map((item, i) => (
                  <p key={i} className="text-[10px] text-muted-foreground">• {item}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Checklist */}
        {checklist.length > 0 && !selectedScenario && (
          <div className="pt-2 border-t">
            <h4 className="text-xs font-medium mb-2">General Crisis Checklist</h4>
            <div className="space-y-1">
              {checklist.map((item, i) => (
                <div key={i} className="flex items-center gap-2 text-[10px]">
                  <Badge variant={item.priority === "immediate" ? "destructive" : "secondary"} className="text-[8px] px-1 py-0">
                    {item.priority}
                  </Badge>
                  <span>{item.step}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
