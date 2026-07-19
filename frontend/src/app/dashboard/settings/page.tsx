"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { User, Bell, Palette, Shield, Key, Eye, EyeOff, Check, Trash2, ExternalLink, Cpu } from "lucide-react"
import Link from "next/link"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface KeyStatus {
  provider: string
  configured: boolean
  fingerprint: string
}

const PROVIDER_INFO: Record<string, { name: string; setup_url: string; description: string }> = {
  openrouter: { name: "OpenRouter", setup_url: "https://openrouter.ai/keys", description: "200+ models from all providers" },
  openai: { name: "OpenAI", setup_url: "https://platform.openai.com/api-keys", description: "GPT-4o, DALL-E, TTS" },
  anthropic: { name: "Anthropic", setup_url: "https://console.anthropic.com/", description: "Claude Sonnet 4, Haiku" },
  gemini: { name: "Google Gemini", setup_url: "https://aistudio.google.com/", description: "Gemini 2.5 Flash, Pro" },
  deepseek: { name: "DeepSeek", setup_url: "https://platform.deepseek.com/", description: "DeepSeek V3, R1 reasoning" },
  omniroute: { name: "OmniRoute", setup_url: "https://openrouter.ai/keys", description: "Smart multi-provider routing (uses OpenRouter key)" },
}

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences.
          </p>
        </div>

        <Tabs defaultValue="general">
          <TabsList>
            <TabsTrigger value="general" className="gap-2">
              <User className="h-4 w-4" /> General
            </TabsTrigger>
            <TabsTrigger value="api-keys" className="gap-2">
              <Key className="h-4 w-4" /> API Keys
            </TabsTrigger>
            <TabsTrigger value="notifications" className="gap-2">
              <Bell className="h-4 w-4" /> Notifications
            </TabsTrigger>
            <TabsTrigger value="appearance" className="gap-2">
              <Palette className="h-4 w-4" /> Appearance
            </TabsTrigger>
            <TabsTrigger value="security" className="gap-2">
              <Shield className="h-4 w-4" /> Security
            </TabsTrigger>
          </TabsList>

          <TabsContent value="general">
            <Card>
              <CardHeader><CardTitle>General Settings</CardTitle><CardDescription>Update your profile information and preferences.</CardDescription></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">General settings coming soon. Configure your display name, email, and timezone here.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api-keys">
            <APIKeysPanel />
          </TabsContent>

          <TabsContent value="notifications">
            <Card>
              <CardHeader><CardTitle>Notification Settings</CardTitle><CardDescription>Choose how and when you want to be notified.</CardDescription></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Notification settings coming soon. Manage email alerts, in-app notifications, and digest preferences.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appearance">
            <Card>
              <CardHeader><CardTitle>Appearance Settings</CardTitle><CardDescription>Customize the look and feel of your dashboard.</CardDescription></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Theme settings are available in the header theme toggle. More customization options coming soon.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="security">
            <Card>
              <CardHeader><CardTitle>Security Settings</CardTitle><CardDescription>Manage your password, MFA, and session settings.</CardDescription></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Security settings coming soon. Configure MFA, manage active sessions, and update your password here.</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function APIKeysPanel() {
  const [keys, setKeys] = useState<KeyStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [editingProvider, setEditingProvider] = useState<string | null>(null)
  const [newKey, setNewKey] = useState("")
  const [showKey, setShowKey] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  useEffect(() => {
    fetchKeys()
  }, [])

  function fetchKeys() {
    fetch(`${API_URL}/ai/keys/`)
      .then(r => r.json())
      .then(d => setKeys(d.keys || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  async function saveKey() {
    if (!editingProvider || !newKey.trim()) return
    setSaving(true)
    try {
      const res = await fetch(`${API_URL}/ai/keys/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: editingProvider, api_key: newKey }),
      })
      if (res.ok) {
        setMessage({ type: "success", text: `API key saved for ${PROVIDER_INFO[editingProvider]?.name || editingProvider}` })
        setEditingProvider(null)
        setNewKey("")
        fetchKeys()
      } else {
        const err = await res.json()
        setMessage({ type: "error", text: err.detail || "Failed to save key" })
      }
    } catch {
      setMessage({ type: "error", text: "Network error" })
    }
    setSaving(false)
    setTimeout(() => setMessage(null), 3000)
  }

  async function deleteKey(provider: string) {
    await fetch(`${API_URL}/ai/keys/${provider}`, { method: "DELETE" })
    fetchKeys()
  }

  const configuredCount = keys.filter(k => k.configured).length

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5 text-primary" />
            API Keys
          </CardTitle>
          <CardDescription>
            Configure API keys for AI providers. Keys are stored securely and used for content generation.
            {configuredCount > 0 && (
              <span className="ml-2 text-green-600 font-medium">{configuredCount} provider{configuredCount !== 1 ? "s" : ""} connected</span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8 text-muted-foreground"><Cpu className="mr-2 h-4 w-4 animate-pulse" /> Loading...</div>
          ) : (
            <div className="space-y-3">
              {keys.map(key => {
                const info = PROVIDER_INFO[key.provider]
                const isEditing = editingProvider === key.provider
                return (
                  <div key={key.provider} className={`rounded-xl border p-4 ${key.configured ? "border-green-200 bg-green-50/50" : ""}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${key.configured ? "bg-green-100" : "bg-muted"}`}>
                          <Key className={`h-5 w-5 ${key.configured ? "text-green-600" : "text-muted-foreground"}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{info?.name || key.provider}</p>
                            {key.configured ? (
                              <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                                <Check className="h-3 w-3" /> Active
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-500">
                                Not configured
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">{info?.description}</p>
                          {key.configured && <p className="text-xs text-muted-foreground font-mono mt-0.5">sha256:{key.fingerprint}</p>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {key.configured && (
                          <Button variant="ghost" size="sm" onClick={() => deleteKey(key.provider)}>
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        )}
                        <a href={info?.setup_url} target="_blank" rel="noopener noreferrer">
                          <Button variant="ghost" size="sm"><ExternalLink className="h-4 w-4" /></Button>
                        </a>
                        <Button
                          variant={key.configured ? "outline" : "default"}
                          size="sm"
                          onClick={() => { setEditingProvider(isEditing ? null : key.provider); setNewKey("") }}
                        >
                          {isEditing ? "Cancel" : key.configured ? "Update" : "Add Key"}
                        </Button>
                      </div>
                    </div>
                    {isEditing && (
                      <div className="mt-3 flex gap-2">
                        <div className="relative flex-1">
                          <Input
                            type={showKey ? "text" : "password"}
                            placeholder={`Enter ${info?.name || key.provider} API key`}
                            value={newKey}
                            onChange={(e) => setNewKey(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && saveKey()}
                            className="pr-10 font-mono"
                          />
                          <button
                            type="button"
                            onClick={() => setShowKey(!showKey)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                          >
                            {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </button>
                        </div>
                        <Button onClick={saveKey} disabled={!newKey.trim() || saving}>
                          {saving ? "Saving..." : "Save"}
                        </Button>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}

          {message && (
            <div className={`mt-3 rounded-lg p-3 text-sm ${message.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
              {message.text}
            </div>
          )}

          <div className="mt-4 rounded-lg border border-dashed p-4">
            <p className="text-sm text-muted-foreground">
              <strong>Recommended:</strong> Add an OpenRouter API key for instant access to 200+ models from all providers.
              {" "}
              <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                Get a key →
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
