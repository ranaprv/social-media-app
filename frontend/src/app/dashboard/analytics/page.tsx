"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  TrendingUp,
  TrendingDown,
  Eye,
  Users,
  Heart,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#ef4444", "#22c55e", "#f59e0b"]

const mockSummary = {
  reach: { value: 142500, change: 23.5, trend: "up" },
  impressions: { value: 287000, change: 18.2, trend: "up" },
  engagement: { value: 12400, change: -5.1, trend: "down" },
  followers: { value: 28400, change: 8.7, trend: "up" },
}

const mockReachTrend = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toISOString().slice(5, 10),
  value: Math.round(4000 + Math.random() * 2000 + i * 50),
}))

const mockImpressionsTrend = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toISOString().slice(5, 10),
  value: Math.round(8000 + Math.random() * 4000 + i * 80),
}))

const mockEngagementTrend = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toISOString().slice(5, 10),
  value: Math.round(300 + Math.random() * 200 + i * 10),
}))

const mockPlatforms = [
  { platform: "LinkedIn", followers: 12400, reach: 67000, engagement: 5200, engagementRate: 3.9, color: "#0A66C2" },
  { platform: "X", followers: 8900, reach: 45000, engagement: 3100, engagementRate: 3.4, color: "#000000" },
  { platform: "Instagram", followers: 4200, reach: 28000, engagement: 2800, engagementRate: 5.0, color: "#E4405F" },
  { platform: "Facebook", followers: 1800, reach: 12000, engagement: 900, engagementRate: 3.8, color: "#1877F2" },
  { platform: "YouTube", followers: 1100, reach: 38000, engagement: 4000, engagementRate: 5.3, color: "#FF0000" },
]

const mockContentTypes = [
  { type: "Educational", count: 34, avgEngagement: 5.2 },
  { type: "Behind-the-Scenes", count: 18, avgEngagement: 4.8 },
  { type: "Case Studies", count: 12, avgEngagement: 6.1 },
  { type: "Tutorials", count: 22, avgEngagement: 4.5 },
  { type: "Product Updates", count: 8, avgEngagement: 3.2 },
]

const mockTopPosts = [
  { id: "p-1", title: "10 SaaS Growth Strategies", platform: "linkedin", impressions: 24500, engagement: 1820, engagementRate: 7.4, clicks: 890, publishedAt: "2026-07-10" },
  { id: "p-2", title: "Thread: How We Grew 300%", platform: "x", impressions: 18900, engagement: 1340, engagementRate: 7.1, clicks: 560, publishedAt: "2026-07-08" },
  { id: "p-3", title: "Content Strategy Guide 2026", platform: "youtube", impressions: 32100, engagement: 2890, engagementRate: 9.0, clicks: 1200, publishedAt: "2026-07-05" },
  { id: "p-4", title: "Behind the Scenes Launch", platform: "instagram", impressions: 15200, engagement: 1120, engagementRate: 7.4, clicks: 340, publishedAt: "2026-07-12" },
  { id: "p-5", title: "Productivity Tips for Creators", platform: "linkedin", impressions: 12800, engagement: 890, engagementRate: 7.0, clicks: 420, publishedAt: "2026-07-14" },
]

const platformColors: Record<string, string> = {
  linkedin: "#0A66C2",
  x: "#000000",
  instagram: "#E4405F",
  facebook: "#1877F2",
  youtube: "#FF0000",
}

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
const hours = Array.from({ length: 17 }, (_, i) => i + 6)

function formatNum(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M"
  if (n >= 1000) return (n / 1000).toFixed(1) + "K"
  return n.toString()
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState("30d")
  const [reachTrend, setReachTrend] = useState(mockReachTrend)
  const [impressionsTrend, setImpressionsTrend] = useState(mockImpressionsTrend)
  const [engagementTrend, setEngagementTrend] = useState(mockEngagementTrend)
  const [summary, setSummary] = useState(mockSummary)

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const [dashRes, trendsRes] = await Promise.all([
          fetch(`${API_URL}/analytics/dashboard?period=${period}`),
          fetch(`${API_URL}/analytics/content-trends?period=${period}`),
        ])
        if (dashRes.ok) {
          const data = await dashRes.json()
          setSummary(data.summary)
          setReachTrend(data.reachTrend)
          setImpressionsTrend(data.impressionsTrend)
          setEngagementTrend(data.engagementTrend)
        }
        if (trendsRes.ok) {
          const data = await trendsRes.json()
          setReachTrend(data.reachTrend || reachTrend)
          setImpressionsTrend(data.engagementTrend || impressionsTrend)
        }
      } catch {
        // Use mock data
      }
    }
    fetchAnalytics()
  }, [period])

  const kpis = [
    { title: "Reach", value: summary.reach.value, change: summary.reach.change, trend: summary.reach.trend, icon: Eye, color: "text-blue-500" },
    { title: "Impressions", value: summary.impressions.value, change: summary.impressions.change, trend: summary.impressions.trend, icon: Users, color: "text-purple-500" },
    { title: "Engagement", value: summary.engagement.value, change: summary.engagement.change, trend: summary.engagement.trend, icon: Heart, color: "text-pink-500" },
    { title: "Followers", value: summary.followers.value, change: summary.followers.change, trend: summary.followers.trend, icon: Users, color: "text-green-500" },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-muted-foreground">Track your content performance across all platforms.</p>
          </div>
          <div className="flex gap-2">
            {["7d", "30d", "90d"].map((p) => (
              <Button key={p} variant={period === p ? "default" : "outline"} size="sm" onClick={() => setPeriod(p)}>
                {p === "7d" ? "7 Days" : p === "30d" ? "30 Days" : "90 Days"}
              </Button>
            ))}
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {kpis.map((kpi) => (
            <Card key={kpi.title}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{kpi.title}</CardTitle>
                <kpi.icon className={`h-4 w-4 ${kpi.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatNum(kpi.value)}</div>
                <p className="flex items-center gap-1 text-xs text-muted-foreground">
                  {kpi.trend === "up" ? (
                    <ArrowUpRight className="h-3 w-3 text-green-500" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-red-500" />
                  )}
                  <span className={kpi.trend === "up" ? "text-green-500" : "text-red-500"}>
                    {Math.abs(kpi.change)}%
                  </span>
                  from last period
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Reach Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Reach Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={reachTrend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="date" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Impressions Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Impressions Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={impressionsTrend}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="date" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Platform Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>Platform Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mockPlatforms}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="platform" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="reach" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="engagement" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Content Type Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Content Type Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={mockContentTypes}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                      dataKey="count"
                      nameKey="type"
                    >
                      {mockContentTypes.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Best Posting Times Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle>Best Posting Times</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <div className="min-w-[700px]">
                <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Less</span>
                  {[0.2, 0.4, 0.6, 0.8, 1.0].map((v) => (
                    <div key={v} className="h-4 w-4 rounded" style={{ backgroundColor: `rgba(59,130,246,${v})` }} />
                  ))}
                  <span>More</span>
                </div>
                <div className="grid gap-1" style={{ gridTemplateColumns: `60px repeat(${hours.length}, 1fr)` }}>
                  {days.map((day) => (
                    <div key={day} className="contents">
                      <div className="flex items-center text-xs text-muted-foreground">{day}</div>
                      {hours.map((hour) => {
                        const score = 0.3 + 0.7 * Math.abs(5 - Math.abs(hour - 10)) / 5
                        return (
                          <div
                            key={`${day}-${hour}`}
                            className="aspect-square rounded-sm transition-colors hover:opacity-80"
                            style={{ backgroundColor: `rgba(59,130,246,${Math.min(score, 1)})` }}
                            title={`${day} ${hour}:00 — Score: ${score.toFixed(2)}`}
                          />
                        )
                      })}
                    </div>
                  ))}
                  <div />
                  {hours.map((h) => (
                    <div key={h} className="text-center text-[10px] text-muted-foreground">{h}</div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Top Performing Posts */}
        <Card>
          <CardHeader>
            <CardTitle>Top Performing Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-3 font-medium">Post</th>
                    <th className="pb-3 font-medium">Platform</th>
                    <th className="pb-3 font-medium">Impressions</th>
                    <th className="pb-3 font-medium">Engagement</th>
                    <th className="pb-3 font-medium">Eng. Rate</th>
                    <th className="pb-3 font-medium">Clicks</th>
                  </tr>
                </thead>
                <tbody>
                  {mockTopPosts.map((post) => (
                    <tr key={post.id} className="border-b last:border-0">
                      <td className="py-3 font-medium">{post.title}</td>
                      <td className="py-3">
                        <span
                          className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
                          style={{
                            backgroundColor: (platformColors[post.platform] || "#666") + "20",
                            color: platformColors[post.platform] || "#666",
                          }}
                        >
                          {post.platform}
                        </span>
                      </td>
                      <td className="py-3">{formatNum(post.impressions)}</td>
                      <td className="py-3">{formatNum(post.engagement)}</td>
                      <td className="py-3">{post.engagementRate}%</td>
                      <td className="py-3">{formatNum(post.clicks)}</td>
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
