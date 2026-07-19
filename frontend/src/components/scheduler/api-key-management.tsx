"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Key,
  Plus,
  Copy,
  Trash2,
  Shield,
  Loader2,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface APIKeyData {
  key_id: string
  name: string
  api_key: string
  permissions: string[]
  rate_limit: number
  expires_at: string
}

interface APIKeyManagementProps {
  onKeyCreated?: (key: APIKeyData) => void
}

export function APIKeyManagement({ onKeyCreated }: APIKeyManagementProps) {
  const [keyName, setKeyName] = useState("")
  const [permissions, setPermissions] = useState<string[]>(["posts:read"])
  const [createdKey, setCreatedKey] = useState<APIKeyData | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const availableScopes = [
    "posts:read", "posts:write", "posts:publish",
    "analytics:read", "media:read", "media:write",
    "workspace:read", "workspace:write", "team:read", "admin",
  ]

  const createKey = async () => {
    if (!keyName) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/api-keys/create`, {
        method: "POST",
        headers,
        body: JSON.stringify({ name: keyName, permissions, rate_limit: 100 }),
      })
      if (response.ok) {
        const data = await response.json()
        setCreatedKey(data)
        onKeyCreated?.(data)
        setKeyName("")
      }
    } finally {
      setLoading(false)
    }
  }

  const copyKey = async () => {
    if (!createdKey) return
    await navigator.clipboard.writeText(createdKey.api_key)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Key className="h-4 w-4" />
          API Key Management
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={keyName}
          onChange={(e) => setKeyName(e.target.value)}
          placeholder="Key name (e.g. My App)"
          className="text-sm"
        />

        <div className="flex flex-wrap gap-1.5">
          {availableScopes.map((scope) => (
            <button
              key={scope}
              onClick={() =>
                setPermissions((prev) =>
                  prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
                )
              }
              className={`rounded-full px-2 py-0.5 text-[9px] font-medium transition-all ${
                permissions.includes(scope)
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {scope}
            </button>
          ))}
        </div>

        <Button onClick={createKey} disabled={loading || !keyName} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
          Generate API Key
        </Button>

        {createdKey && (
          <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-3 space-y-2">
            <div className="flex items-center gap-2 text-xs font-medium text-yellow-800">
              <Shield className="h-3.5 w-3.5" />
              Save this key — it won&apos;t be shown again
            </div>
            <div className="flex items-center gap-2">
              <code className="text-[10px] bg-white px-1.5 py-0.5 rounded flex-1 truncate border">
                {createdKey.api_key}
              </code>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={copyKey}>
                <Copy className="h-3 w-3" />
              </Button>
            </div>
            {copied && <span className="text-[10px] text-green-600">Copied!</span>}
            <div className="flex gap-2 text-[10px] text-muted-foreground">
              <span>ID: {createdKey.key_id}</span>
              <span>Expires: {new Date(createdKey.expires_at).toLocaleDateString()}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
