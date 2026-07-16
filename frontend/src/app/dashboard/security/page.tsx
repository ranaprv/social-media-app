"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Shield,
  Lock,
  Key,
  Users,
  Eye,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Globe,
  RefreshCw,
  FileText,
  ExternalLink,
  ChevronDown,
  Loader2,
  Filter,
  Clock,
  Ban,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const roleColors: Record<string, string> = {
  owner: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
  admin: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  editor: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  viewer: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
}

const actionColors: Record<string, string> = {
  post_created: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  post_published: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  connection_added: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  member_invited: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  settings_updated: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  brand_voice_updated: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
  media_uploaded: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400",
  subscription_changed: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
  comment_added: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400",
  review_approved: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
}

const fallbackRoles = {
  owner: { level: 4, permissions: ["*"] },
  admin: { level: 3, permissions: ["manage_team", "manage_billing", "manage_content", "manage_settings", "view_analytics"] },
  editor: { level: 2, permissions: ["create_content", "edit_content", "schedule_content", "view_analytics", "comment"] },
  viewer: { level: 1, permissions: ["view_content", "view_analytics"] },
}

const fallbackConnections = [
  { provider: "google", connected: true, username: "user@gmail.com", scopes: ["email", "profile"] },
  { provider: "github", connected: true, username: "socialmediamanager", scopes: ["repo", "user"] },
  { provider: "linkedin", connected: true, username: "Social Media Manager", scopes: ["w_member_social", "r_liteprofile"] },
  { provider: "twitter", connected: false, username: null as string | null, scopes: [] as string[] },
  { provider: "facebook", connected: true, username: "Social Media Manager Page", scopes: ["pages_manage_posts"] },
  { provider: "youtube", connected: false, username: null as string | null, scopes: [] as string[] },
]

export default function SecurityPage() {
  const [auditLogs, setAuditLogs] = useState<Array<Record<string, unknown>>>([])
  const [roles, setRoles] = useState(fallbackRoles)
  const [connections, setConnections] = useState(fallbackConnections)
  const [rateLimit, setRateLimit] = useState({ remaining: 87, limit: 100, window_seconds: 60, reset_at: "" })
  const [encryption, setEncryption] = useState({ api_keys_encrypted: true, oauth_tokens_encrypted: true, encryption_algorithm: "AES-256-GCM", key_rotation_enabled: true, last_key_rotation: "" })
  const [gdpr, setGdpr] = useState({ data_processing_agreement: true, consent_recorded: true, data_retention_days: 365, right_to_erasure: true, data_portability: true, privacy_policy_url: "/legal/privacy", terms_of_service_url: "/legal/terms", last_audit: "", dpo_contact: "privacy@socialmediamanager.ai" })
  const [actionFilter, setActionFilter] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const [logsRes, rolesRes, rlRes, encRes, gdprRes, connRes] = await Promise.allSettled([
          fetch(`${API_URL}/security/audit-logs?limit=50`),
          fetch(`${API_URL}/security/roles`),
          fetch(`${API_URL}/security/rate-limit/status`),
          fetch(`${API_URL}/security/encryption/status`),
          fetch(`${API_URL}/security/gdpr/status`),
          fetch(`${API_URL}/security/oauth/connections`),
        ])
        if (logsRes.status === "fulfilled" && logsRes.value.ok) {
          const data = await logsRes.value.json()
          if (data.logs) setAuditLogs(data.logs)
        }
        if (rolesRes.status === "fulfilled" && rolesRes.value.ok) {
          const data = await rolesRes.value.json()
          if (data.roles) setRoles(data.roles)
        }
        if (rlRes.status === "fulfilled" && rlRes.value.ok) {
          const data = await rlRes.value.json()
          setRateLimit(data)
        }
        if (encRes.status === "fulfilled" && encRes.value.ok) {
          const data = await encRes.value.json()
          setEncryption(data)
        }
        if (gdprRes.status === "fulfilled" && gdprRes.value.ok) {
          const data = await gdprRes.value.json()
          setGdpr(data)
        }
        if (connRes.status === "fulfilled" && connRes.value.ok) {
          const data = await connRes.value.json()
          if (data.connections) setConnections(data.connections)
        }
      } catch {
        // use fallbacks
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const filteredLogs = actionFilter
    ? auditLogs.filter((l) => l.action === actionFilter)
    : auditLogs

  const connectedCount = connections.filter((c) => c.connected).length
  const rlPct = rateLimit.limit > 0 ? ((rateLimit.limit - rateLimit.remaining) / rateLimit.limit) * 100 : 0

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Security & Access</h1>
            <p className="text-muted-foreground">Manage roles, audit logs, rate limits, and compliance settings.</p>
          </div>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => window.location.reload()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>

        {/* Overview Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Audit Logs</CardTitle>
              <Activity className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{auditLogs.length}</div>
              <p className="text-xs text-muted-foreground">Total entries</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Roles</CardTitle>
              <Users className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Object.keys(roles).length}</div>
              <p className="text-xs text-muted-foreground">Role definitions</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Rate Limit</CardTitle>
              <Shield className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{rateLimit.remaining}/{rateLimit.limit}</div>
              <p className="text-xs text-muted-foreground">Remaining / {rateLimit.window_seconds}s window</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">OAuth Connections</CardTitle>
              <Globe className="h-4 w-4 text-cyan-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{connectedCount}/{connections.length}</div>
              <p className="text-xs text-muted-foreground">Connected providers</p>
            </CardContent>
          </Card>
        </div>

        {/* RBAC Roles */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5 text-primary" />
              Roles & Permissions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(roles).map(([role, config]) => (
                <div key={role} className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <span className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${roleColors[role] || ""}`}>
                      {role}
                    </span>
                    <span className="text-xs text-muted-foreground">Level {config.level}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {config.permissions.map((p: string) => (
                      <span key={p} className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Rate Limiting */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Rate Limiting
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="font-medium">Requests Used</span>
                  <span className="text-muted-foreground">{rateLimit.limit - rateLimit.remaining} / {rateLimit.limit}</span>
                </div>
                <div className="h-3 rounded-full bg-muted">
                  <div
                    className={`h-3 rounded-full transition-all ${rlPct >= 90 ? "bg-red-500" : rlPct >= 70 ? "bg-yellow-500" : "bg-green-500"}`}
                    style={{ width: `${rlPct}%` }}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="rounded-lg bg-muted p-3">
                  <p className="text-muted-foreground">Window</p>
                  <p className="font-medium">{rateLimit.window_seconds}s</p>
                </div>
                <div className="rounded-lg bg-muted p-3">
                  <p className="text-muted-foreground">Remaining</p>
                  <p className="font-medium">{rateLimit.remaining}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Encryption & GDPR */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5 text-primary" />
                Encryption & Compliance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between rounded-lg border p-3">
                <div className="flex items-center gap-2">
                  {encryption.api_keys_encrypted ? <CheckCircle className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                  <span className="text-sm">API Keys Encrypted</span>
                </div>
                <span className="text-xs text-muted-foreground">{encryption.encryption_algorithm}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border p-3">
                <div className="flex items-center gap-2">
                  {encryption.oauth_tokens_encrypted ? <CheckCircle className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />}
                  <span className="text-sm">OAuth Tokens Encrypted</span>
                </div>
              </div>
              <div className="flex items-center justify-between rounded-lg border p-3">
                <div className="flex items-center gap-2">
                  {encryption.key_rotation_enabled ? <CheckCircle className="h-4 w-4 text-green-500" /> : <AlertTriangle className="h-4 w-4 text-yellow-500" />}
                  <span className="text-sm">Key Rotation</span>
                </div>
                <span className="text-xs text-muted-foreground">{encryption.key_rotation_enabled ? "Enabled" : "Disabled"}</span>
              </div>
              <div className="mt-2 border-t pt-3">
                <p className="mb-2 text-xs font-medium text-muted-foreground">GDPR</p>
                <div className="space-y-1.5">
                  {[["Data Processing Agreement", gdpr.data_processing_agreement], ["Consent Recorded", gdpr.consent_recorded], ["Right to Erasure", gdpr.right_to_erasure], ["Data Portability", gdpr.data_portability]].map(([label, ok]) => (
                    <div key={label as string} className="flex items-center gap-2 text-sm">
                      {ok ? <CheckCircle className="h-3.5 w-3.5 text-green-500" /> : <XCircle className="h-3.5 w-3.5 text-red-500" />}
                      <span>{label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* OAuth Connections */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-primary" />
              OAuth Connections
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {connections.map((conn) => (
                <div key={conn.provider} className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center gap-3">
                    {conn.connected ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-400" />
                    )}
                    <div>
                      <p className="text-sm font-medium capitalize">{conn.provider}</p>
                      <p className="text-xs text-muted-foreground">{conn.connected ? conn.username : "Not connected"}</p>
                    </div>
                  </div>
                  <Button variant={conn.connected ? "outline" : "default"} size="sm">
                    {conn.connected ? "Disconnect" : "Connect"}
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Audit Logs */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Audit Logs
              </CardTitle>
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <select
                  className="rounded-lg border bg-background p-1.5 text-sm"
                  value={actionFilter}
                  onChange={(e) => setActionFilter(e.target.value)}
                >
                  <option value="">All Actions</option>
                  <option value="post_created">Post Created</option>
                  <option value="post_published">Post Published</option>
                  <option value="connection_added">Connection Added</option>
                  <option value="member_invited">Member Invited</option>
                  <option value="settings_updated">Settings Updated</option>
                  <option value="subscription_changed">Subscription Changed</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-3 font-medium">Timestamp</th>
                    <th className="pb-3 font-medium">Action</th>
                    <th className="pb-3 font-medium">Resource</th>
                    <th className="pb-3 font-medium">Details</th>
                    <th className="pb-3 font-medium">IP</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map((log, i) => (
                    <tr key={String(log.id || i)} className="border-b last:border-0">
                      <td className="py-3">
                        <div className="flex items-center gap-1 text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {new Date(String(log.timestamp)).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                        </div>
                      </td>
                      <td className="py-3">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${actionColors[String(log.action)] || "bg-gray-100 text-gray-800"}`}>
                          {String(log.action).replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="py-3 capitalize">{String(log.resource)}</td>
                      <td className="py-3 text-muted-foreground">
                        {typeof log.details === "object" && log.details !== null ? String((log.details as Record<string, unknown>).description || "") : ""}
                      </td>
                      <td className="py-3 font-mono text-xs text-muted-foreground">{String(log.ip_address)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
