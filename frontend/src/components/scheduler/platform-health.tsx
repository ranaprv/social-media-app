"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Activity,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Loader2,
  Wifi,
  WifiOff,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const PLATFORM_CONFIG: Record<Platform, { name: string; color: string }> = {
  linkedin: { name: "LinkedIn", color: "text-blue-600" },
  x: { name: "X (Twitter)", color: "text-black" },
  instagram: { name: "Instagram", color: "text-pink-500" },
  facebook: { name: "Facebook", color: "text-blue-500" },
  youtube: { name: "YouTube", color: "text-red-600" },
}

interface HealthStatus {
  platform: string
  status: "healthy" | "token_expired" | "rate_limited" | "timeout" | "error" | "no_token" | "unknown"
  message: string
  latency_ms?: number
  checked_at?: string
}

export function PlatformHealthMonitor() {
  const [health, setHealth] = useState<Record<string, HealthStatus>>({})
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(false)

  const fetchHealth = useCallback(async (checkAll = false) => {
    if (checkAll) setChecking(true)
    else setLoading(true)

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const url = checkAll ? `${API_BASE}/scheduler/health` : `${API_BASE}/scheduler/health`
      const response = await fetch(url, { headers })
      if (response.ok) {
        const data = await response.json()
        setHealth(data)
      }
    } catch (err) {
      console.error("Failed to check health:", err)
    } finally {
      setLoading(false)
      setChecking(false)
    }
  }, [])

  useEffect(() => { fetchHealth() }, [fetchHealth])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy": return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case "token_expired": return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "rate_limited": return <Clock className="h-4 w-4 text-orange-500" />
      case "timeout": return <WifiOff className="h-4 w-4 text-red-500" />
      case "error": return <XCircle className="h-4 w-4 text-red-500" />
      case "no_token": return <Wifi className="h-4 w-4 text-gray-400" />
      default: return <Activity className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    const configs: Record<string, { color: string; label: string }> = {
      healthy: { color: "bg-green-100 text-green-700", label: "Healthy" },
      token_expired: { color: "bg-yellow-100 text-yellow-700", label: "Token Expired" },
      rate_limited: { color: "bg-orange-100 text-orange-700", label: "Rate Limited" },
      timeout: { color: "bg-red-100 text-red-700", label: "Timeout" },
      error: { color: "bg-red-100 text-red-700", label: "Error" },
      no_token: { color: "bg-gray-100 text-gray-600", label: "Not Connected" },
      unknown: { color: "bg-gray-100 text-gray-600", label: "Unknown" },
    }
    const c = configs[status] || configs.unknown
    return <Badge className={`text-[10px] px-1.5 py-0 ${c.color}`}>{c.label}</Badge>
  }

  const platforms = Object.keys(PLATFORM_CONFIG) as Platform[]
  const healthyCount = Object.values(health).filter((h) => h.status === "healthy").length

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Checking platform health...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Platform Health
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant={healthyCount === platforms.length ? "default" : "secondary"}>
              {healthyCount}/{platforms.length} healthy
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => fetchHealth(true)}
              disabled={checking}
            >
              <RefreshCw className={`h-4 w-4 ${checking ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {platforms.map((platform) => {
            const status = health[platform]
            const config = PLATFORM_CONFIG[platform]

            return (
              <div
                key={platform}
                className="flex items-center gap-3 rounded-lg border p-3"
              >
                {getStatusIcon(status?.status || "unknown")}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${config.color}`}>
                      {config.name}
                    </span>
                    {getStatusBadge(status?.status || "unknown")}
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5 truncate">
                    {status?.message || "Not checked"}
                  </p>
                </div>
                {status?.latency_ms !== undefined && (
                  <span className="text-[10px] text-muted-foreground">
                    {status.latency_ms}ms
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
