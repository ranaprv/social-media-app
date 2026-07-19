"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import {
  Zap,
  RefreshCw,
  Loader2,
  Clock,
  Bell,
  RotateCcw,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface AutomationRule {
  id: string
  name: string
  description: string
  trigger: { type: string }
  action: { type: string }
  enabled: boolean
}

const ACTION_ICONS: Record<string, typeof Clock> = {
  recycle: RotateCcw,
  notify: Bell,
  transition: Clock,
  report: RotateCcw,
}

export function AutomationRules() {
  const [rules, setRules] = useState<AutomationRule[]>([])
  const [loading, setLoading] = useState(true)
  const [toggling, setToggling] = useState<string | null>(null)

  const fetchRules = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/automation/rules`, { headers })
      if (response.ok) {
        const data = await response.json()
        setRules(data.rules || [])
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchRules() }, [fetchRules])

  const toggleRule = async (ruleId: string, enabled: boolean) => {
    setToggling(ruleId)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      await fetch(`${API_BASE}/scheduler/automation/rules/${ruleId}`, {
        method: "PUT",
        headers,
        body: JSON.stringify({ enabled }),
      })
      setRules((prev) =>
        prev.map((r) => (r.id === ruleId ? { ...r, enabled } : r))
      )
    } finally {
      setToggling(null)
    }
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

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Automation Rules
          </CardTitle>
          <Badge variant="outline">{rules.filter((r) => r.enabled).length} active</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {rules.map((rule) => {
          const Icon = ACTION_ICONS[rule.action.type] || Zap
          return (
            <div
              key={rule.id}
              className={`flex items-center gap-3 rounded-lg border p-3 transition-colors ${
                rule.enabled ? "bg-primary/5" : ""
              }`}
            >
              <Icon className={`h-4 w-4 ${rule.enabled ? "text-primary" : "text-muted-foreground"}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium">{rule.name}</span>
                  <Badge variant={rule.enabled ? "default" : "secondary"} className="text-[8px] px-1 py-0">
                    {rule.trigger.type}
                  </Badge>
                </div>
                <p className="text-[10px] text-muted-foreground mt-0.5">{rule.description}</p>
              </div>
              <Switch
                checked={rule.enabled}
                onCheckedChange={(checked) => toggleRule(rule.id, checked)}
                disabled={toggling === rule.id}
              />
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
