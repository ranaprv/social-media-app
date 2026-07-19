"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Search, TrendingUp, TrendingDown, Plus, Loader2, Trash2, Pause, Play,
  BarChart3, MessageSquare, Globe, Filter, ArrowUpRight, ArrowDownRight,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const PLATFORM_COLORS: Record<string, string> = {
  linkedin: "bg-blue-600 text-white",
  x: "bg-gray-900 text-white",
  instagram: "bg-gradient-to-r from-purple-500 to-pink-500 text-white",
  facebook: "bg-blue-500 text-white",
  youtube: "bg-red-600 text-white",
}

const SENTIMENT_COLORS: Record<string, string> = {
  positive: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  neutral: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400",
  negative: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
}

interface Alert {
  id: string
  keyword: string
  platforms: string[]
  check_interval: string
  last_checked: string | null
  is_active: boolean
  mentions_count: number
  sentiment_avg: number
}

interface Mention {
  id: string
  keyword: string
  platform: string
  author: string
  content: string
  sentiment: string
  sentiment_score: number
  url: string
  found_at: string
  engagement: number
}

export default function ListeningPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [mentions, setMentions] = useState<Mention[]>([])
  const [trends, setTrends] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [newKeyword, setNewKeyword] = useState("")
  const [newPlatforms, setNewPlatforms] = useState(["x"])
  const [platformFilter, setPlatformFilter] = useState("")
  const [sentimentFilter, setSentimentFilter] = useState("")
  const [activeTab, setActiveTab] = useState<"alerts" | "mentions" | "trends">("alerts")

  useEffect(() => {
    async function fetchListening() {
      try {
        const [alertsRes, mentionsRes, trendsRes] = await Promise.allSettled([
          fetch(`${API_URL}/listening/alerts`),
          fetch(`${API_URL}/listening/mentions?limit=20`),
          fetch(`${API_URL}/listening/trends`),
        ])
        if (alertsRes.status === "fulfilled" && alertsRes.value.ok) {
          const d = await alertsRes.value.json()
          setAlerts(d.alerts || [])
        }
        if (mentionsRes.status === "fulfilled" && mentionsRes.value.ok) {
          const d = await mentionsRes.value.json()
          setMentions(d.mentions || [])
        }
        if (trendsRes.status === "fulfilled" && trendsRes.value.ok) {
          setTrends(await trendsRes.value.json())
        }
      } catch { /* empty state */ }
      finally { setLoading(false) }
    }
    fetchListening()
  }, [])

  const createAlert = async () => {
    if (!newKeyword.trim()) return
    try {
      const res = await fetch(`${API_URL}/listening/alerts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: newKeyword, platforms: newPlatforms }),
      })
      if (res.ok) {
        const alert = await res.json()
        setAlerts((prev) => [...prev, alert])
        setNewKeyword("")
      }
    } catch { /* ignore */ }
  }

  const deleteAlert = async (id: string) => {
    try {
      await fetch(`${API_URL}/listening/alerts/${id}`, { method: "DELETE" })
      setAlerts((prev) => prev.filter((a) => a.id !== id))
    } catch { /* ignore */ }
  }

  const toggleAlert = async (id: string) => {
    try {
      await fetch(`${API_URL}/listening/alerts/${id}/toggle`, { method: "PUT" })
      setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, is_active: !a.is_active } : a))
    } catch { /* ignore */ }
  }

  const filteredMentions = mentions.filter((m) => {
    if (platformFilter && m.platform !== platformFilter) return false
    if (sentimentFilter && m.sentiment !== sentimentFilter) return false
    return true
  })

  const dailyTrends = (trends?.daily_trends || []) as Array<{ date: string; mentions: number; positive: number; neutral: number; negative: number }>
  const keywordCloud = (trends?.keyword_cloud || []) as Array<{ keyword: string; count: number; sentiment: number }>
  const trendingUp = (trends?.trending_up || []) as Array<{ keyword: string; change: number }>
  const trendingDown = (trends?.trending_down || []) as Array<{ keyword: string; change: number }>

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Social Listening</h1>
            <p className="text-muted-foreground">Monitor keywords, track mentions, discover trends.</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {([["alerts", "Alerts", Bell], ["mentions", "Mentions", MessageSquare], ["trends", "Trends", TrendingUp]] as const).map(([id, label, Icon]) => (
            <Button key={id} variant={activeTab === id ? "default" : "outline"} size="sm" className="gap-2" onClick={() => setActiveTab(id)}>
              <Icon className="h-4 w-4" /> {label}
            </Button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : (
          <>
            {/* Alerts Tab */}
            {activeTab === "alerts" && (
              <>
                {/* Create Alert */}
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex gap-3">
                      <Input
                        placeholder="Enter keyword to monitor..."
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && createAlert()}
                      />
                      <Button onClick={createAlert} className="gap-2" disabled={!newKeyword.trim()}>
                        <Plus className="h-4 w-4" /> Add Alert
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Alert List */}
                <div className="space-y-3">
                  {alerts.map((alert) => (
                    <Card key={alert.id}>
                      <CardContent className="flex items-center justify-between p-4">
                        <div className="flex items-center gap-4">
                          <div className={`rounded-lg p-2 ${alert.is_active ? "bg-green-100 dark:bg-green-900/30" : "bg-gray-100 dark:bg-gray-800"}`}>
                            <Search className={`h-5 w-5 ${alert.is_active ? "text-green-600" : "text-gray-400"}`} />
                          </div>
                          <div>
                            <h4 className="font-medium">{alert.keyword}</h4>
                            <div className="flex items-center gap-2 mt-1">
                              {alert.platforms.map((p) => (
                                <span key={p} className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${PLATFORM_COLORS[p] || "bg-gray-500 text-white"}`}>{p}</span>
                              ))}
                              <span className="text-xs text-muted-foreground">• {alert.check_interval}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-lg font-bold">{alert.mentions_count}</p>
                            <p className="text-xs text-muted-foreground">mentions</p>
                          </div>
                          <div className="text-right">
                            <p className={`text-sm font-medium ${alert.sentiment_avg >= 0.6 ? "text-green-600" : alert.sentiment_avg >= 0.4 ? "text-yellow-600" : "text-red-600"}`}>
                              {alert.sentiment_avg >= 0.6 ? "Positive" : alert.sentiment_avg >= 0.4 ? "Neutral" : "Negative"}
                            </p>
                            <p className="text-xs text-muted-foreground">{(alert.sentiment_avg * 100).toFixed(0)}%</p>
                          </div>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => toggleAlert(alert.id)}>
                              {alert.is_active ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => deleteAlert(alert.id)}>
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </>
            )}

            {/* Mentions Tab */}
            {activeTab === "mentions" && (
              <>
                <div className="flex gap-2">
                  <select className="rounded-lg border bg-background px-3 py-2 text-sm" value={platformFilter} onChange={(e) => setPlatformFilter(e.target.value)}>
                    <option value="">All Platforms</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="x">X (Twitter)</option>
                    <option value="instagram">Instagram</option>
                    <option value="facebook">Facebook</option>
                    <option value="youtube">YouTube</option>
                  </select>
                  <select className="rounded-lg border bg-background px-3 py-2 text-sm" value={sentimentFilter} onChange={(e) => setSentimentFilter(e.target.value)}>
                    <option value="">All Sentiment</option>
                    <option value="positive">Positive</option>
                    <option value="neutral">Neutral</option>
                    <option value="negative">Negative</option>
                  </select>
                </div>

                <div className="space-y-3">
                  {filteredMentions.map((mention) => (
                    <Card key={mention.id}>
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full text-white text-xs font-bold ${PLATFORM_COLORS[mention.platform] || "bg-gray-500"}`}>
                            {mention.author.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-sm">{mention.author}</span>
                                <span className="text-xs text-muted-foreground capitalize">{mention.platform}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${SENTIMENT_COLORS[mention.sentiment]}`}>{mention.sentiment}</span>
                                <span className="text-xs text-muted-foreground">Eng: {mention.engagement}</span>
                              </div>
                            </div>
                            <p className="mt-1 text-sm">{mention.content}</p>
                            <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                              <span>Keyword: {mention.keyword}</span>
                              <span>•</span>
                              <span>{new Date(mention.found_at).toLocaleString()}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </>
            )}

            {/* Trends Tab */}
            {activeTab === "trends" && (
              <div className="grid gap-6 lg:grid-cols-2">
                {/* Mentions Over Time */}
                <Card>
                  <CardHeader><CardTitle className="text-sm flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Mentions Over Time</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {dailyTrends.map((d, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <span className="w-12 text-xs text-muted-foreground">{d.date}</span>
                          <div className="flex-1 flex gap-1">
                            <div className="h-5 rounded bg-green-400" style={{ width: `${(d.positive / 50) * 100}%` }} title={`Positive: ${d.positive}`} />
                            <div className="h-5 rounded bg-gray-300" style={{ width: `${(d.neutral / 50) * 100}%` }} title={`Neutral: ${d.neutral}`} />
                            <div className="h-5 rounded bg-red-400" style={{ width: `${(d.negative / 50) * 100}%` }} title={`Negative: ${d.negative}`} />
                          </div>
                          <span className="w-8 text-right text-xs font-medium">{d.mentions}</span>
                        </div>
                      ))}
                      <div className="flex gap-4 text-xs text-muted-foreground mt-2">
                        <span className="flex items-center gap-1"><span className="h-2 w-2 rounded bg-green-400" /> Positive</span>
                        <span className="flex items-center gap-1"><span className="h-2 w-2 rounded bg-gray-300" /> Neutral</span>
                        <span className="flex items-center gap-1"><span className="h-2 w-2 rounded bg-red-400" /> Negative</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Keyword Cloud */}
                <Card>
                  <CardHeader><CardTitle className="text-sm flex items-center gap-2"><Globe className="h-4 w-4" /> Keyword Cloud</CardTitle></CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {keywordCloud.map((kw, i) => {
                        const size = kw.count > 30 ? "text-base font-bold" : kw.count > 15 ? "text-sm font-medium" : "text-xs"
                        const color = kw.sentiment >= 0.6 ? "text-green-600 bg-green-50 dark:bg-green-900/20" :
                                     kw.sentiment >= 0.4 ? "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20" :
                                     "text-red-600 bg-red-50 dark:bg-red-900/20"
                        return (
                          <span key={i} className={`rounded-full px-3 py-1 ${size} ${color}`}>
                            {kw.keyword} ({kw.count})
                          </span>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>

                {/* Trending */}
                <Card>
                  <CardHeader><CardTitle className="text-sm">Trending Topics</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    {trendingUp.map((t, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-sm">{t.keyword}</span>
                        <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                          <ArrowUpRight className="h-3 w-3" /> +{t.change}%
                        </span>
                      </div>
                    ))}
                    {trendingDown.map((t, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-sm">{t.keyword}</span>
                        <span className="flex items-center gap-1 text-sm font-medium text-red-600">
                          <ArrowDownRight className="h-3 w-3" /> {t.change}%
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Sentiment Summary */}
                <Card>
                  <CardHeader><CardTitle className="text-sm">Sentiment Overview</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Total Mentions</span>
                        <span className="font-bold">{(trends?.total_mentions as number) || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Avg Sentiment</span>
                        <span className={`font-bold ${((trends?.avg_sentiment as number) || 0) >= 0.6 ? "text-green-600" : "text-yellow-600"}`}>
                          {(((trends?.avg_sentiment as number) || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="space-y-2 mt-4">
                        {Object.entries((trends?.sentiment_distribution || {}) as Record<string, number>).map(([s, count]) => (
                          <div key={s} className="flex items-center gap-3">
                            <span className={`w-20 text-xs capitalize ${SENTIMENT_COLORS[s]?.split(" ")[1] || ""}`}>{s}</span>
                            <div className="flex-1 h-3 rounded-full bg-muted">
                              <div className={`h-3 rounded-full ${s === "positive" ? "bg-green-500" : s === "neutral" ? "bg-gray-400" : "bg-red-500"}`} style={{ width: `${((count as number) / 85) * 100}%` }} />
                            </div>
                            <span className="w-8 text-right text-xs font-medium">{String(count)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  )
}

function Bell({ className }: { className?: string }) {
  return <Search className={className} />
}
