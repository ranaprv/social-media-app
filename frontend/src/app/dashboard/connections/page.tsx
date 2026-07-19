"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Link2, Plus, Check, ExternalLink, Loader2, Trash2, Circle,
  Briefcase, Camera, Globe, Play, MessageCircle, Eye, EyeOff,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface ConnectedAccount {
  id: string
  platform: string
  username: string
  client_id: string
  client_secret_preview: string
  connected_at: string
}

const PLATFORMS = [
  { id: "linkedin", name: "LinkedIn", icon: "Briefcase", color: "text-blue-600", description: "Share articles, carousels, and professional updates", url: "https://www.linkedin.com/developers/" },
  { id: "instagram", name: "Instagram", icon: "Camera", color: "text-pink-500", description: "Post reels, stories, carousels, and images", url: "https://developers.facebook.com/" },
  { id: "x", name: "X (Twitter)", icon: "MessageCircle", color: "text-gray-900", description: "Tweet threads, polls, and quick updates", url: "https://developer.x.com/" },
  { id: "facebook", name: "Facebook", icon: "Globe", color: "text-blue-500", description: "Share posts, videos, and community updates", url: "https://developers.facebook.com/" },
  { id: "youtube", name: "YouTube", icon: "Play", color: "text-red-600", description: "Upload videos, shorts, and manage your channel", url: "https://console.cloud.google.com/" },
]

function getIcon(name: string) {
  const icons: Record<string, typeof Briefcase> = { Briefcase, Camera, Globe, Play, MessageCircle }
  return icons[name] || Globe
}

export default function ConnectionsPage() {
  const [connected, setConnected] = useState<ConnectedAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState<string | null>(null)
  const [showForm, setShowForm] = useState<string | null>(null)
  const [credentials, setCredentials] = useState<{ client_id: string; client_secret: string; username: string }>({ client_id: "", client_secret: "", username: "" })
  const [showSecret, setShowSecret] = useState(false)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/connections/`)
      .then(r => r.ok ? r.json() : [])
      .then(d => setConnected(Array.isArray(d) ? d : []))
      .catch(() => setConnected([]))
      .finally(() => setLoading(false))
  }, [])

  async function connectAccount(platformId: string) {
    if (!credentials.client_id.trim() || !credentials.client_secret.trim()) {
      setMessage({ type: "error", text: "Client ID and Client Secret are required." })
      setTimeout(() => setMessage(null), 3000)
      return
    }
    setConnecting(platformId)
    try {
      const res = await fetch(`${API_URL}/connections/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform: platformId,
          client_id: credentials.client_id,
          client_secret: credentials.client_secret,
          username: credentials.username || `user-${platformId}`,
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setConnected(prev => [...prev, {
          id: data.id,
          platform: platformId,
          username: data.username,
          client_id: data.client_id,
          client_secret_preview: data.client_secret_preview,
          connected_at: data.connected_at,
        }])
        setMessage({ type: "success", text: `${PLATFORMS.find(p => p.id === platformId)?.name} connected successfully!` })
      } else {
        const err = await res.json().catch(() => ({ detail: "Connection failed" }))
        setMessage({ type: "error", text: err.detail || "Connection failed" })
      }
    } catch {
      setMessage({ type: "error", text: "Network error. Is the backend running?" })
    }
    setConnecting(null)
    setShowForm(null)
    setCredentials({ client_id: "", client_secret: "", username: "" })
    setShowSecret(false)
    setTimeout(() => setMessage(null), 3000)
  }

  async function disconnectAccount(id: string) {
    try {
      const res = await fetch(`${API_URL}/connections/${id}`, { method: "DELETE" })
      if (res.ok) {
        setConnected(prev => prev.filter(c => c.id !== id))
        setMessage({ type: "success", text: "Account disconnected." })
        setTimeout(() => setMessage(null), 3000)
      }
    } catch { /* ignore */ }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Connected Accounts</h1>
          <p className="text-muted-foreground">Connect your social media accounts to publish and schedule content directly.</p>
        </div>

        {message && (
          <div className={`rounded-lg p-3 text-sm ${message.type === "success" ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-700 border border-red-200"}`}>
            {message.text}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {PLATFORMS.map(p => {
              const Ic = getIcon(p.icon)
              const conn = connected.find(c => c.platform === p.id)
              const isConnecting = connecting === p.id
              const showCredentialForm = showForm === p.id

              return (
                <Card key={p.id} className={conn ? "border-green-200" : ""}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${conn ? "bg-green-100" : "bg-muted"}`}>
                          <Ic className={`h-5 w-5 ${conn ? "text-green-600" : p.color}`} />
                        </div>
                        <div>
                          <CardTitle className="text-base">{p.name}</CardTitle>
                          <p className="text-xs text-muted-foreground">{p.description}</p>
                        </div>
                      </div>
                      {conn ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                          <Check className="h-3 w-3" /> Connected
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-500">
                          <Circle className="h-1.5 w-1.5 fill-current" /> Not connected
                        </span>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {conn ? (
                      <div className="space-y-2">
                        <div className="text-sm space-y-1">
                          <p className="text-muted-foreground">@{conn.username}</p>
                          {conn.client_id && <p className="text-xs text-muted-foreground font-mono">ID: {conn.client_id.slice(0, 12)}...{conn.client_id.slice(-4)}</p>}
                          {conn.client_secret_preview && <p className="text-xs text-muted-foreground font-mono">Secret: {conn.client_secret_preview}</p>}
                        </div>
                        <div className="flex gap-2">
                          <a href={p.url} target="_blank" rel="noopener noreferrer" className="flex-1">
                            <Button variant="outline" size="sm" className="w-full gap-1"><ExternalLink className="h-3 w-3" /> Dashboard</Button>
                          </a>
                          <Button variant="ghost" size="sm" onClick={() => disconnectAccount(conn.id)}><Trash2 className="h-4 w-4 text-red-500" /></Button>
                        </div>
                      </div>
                    ) : showCredentialForm ? (
                      <div className="space-y-2">
                        <Input placeholder="Client ID / App ID" value={credentials.client_id} onChange={(e) => setCredentials({ ...credentials, client_id: e.target.value })} className="text-sm font-mono" />
                        <div className="relative">
                          <Input type={showSecret ? "text" : "password"} placeholder="Client Secret / App Secret" value={credentials.client_secret} onChange={(e) => setCredentials({ ...credentials, client_secret: e.target.value })} className="text-sm font-mono pr-8" />
                          <button type="button" onClick={() => setShowSecret(!showSecret)} className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                            {showSecret ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                        <Input placeholder="Username / Handle" value={credentials.username} onChange={(e) => setCredentials({ ...credentials, username: e.target.value })} className="text-sm" />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => connectAccount(p.id)} disabled={isConnecting || !credentials.client_id.trim() || !credentials.client_secret.trim()} className="flex-1 gap-1">
                            {isConnecting ? <Loader2 className="h-3 w-3 animate-spin" /> : <Link2 className="h-3 w-3" />}
                            {isConnecting ? "Connecting..." : "Connect"}
                          </Button>
                          <Button size="sm" variant="ghost" onClick={() => { setShowForm(null); setCredentials({ client_id: "", client_secret: "", username: "" }); setShowSecret(false) }}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <Button size="sm" className="w-full gap-1" onClick={() => { setShowForm(p.id); setCredentials({ client_id: "", client_secret: "", username: "" }) }}>
                        <Plus className="h-3 w-3" /> Connect {p.name}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
