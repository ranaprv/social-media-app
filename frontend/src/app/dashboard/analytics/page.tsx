"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import {
  TrendingUp,
  TrendingDown,
  Eye,
  Users,
  Heart,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Briefcase,
  MessageCircle,
  Camera,
  Globe,
  Play,
  Loader2,
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

const PLATFORMS = [
  { id: "linkedin", name: "LinkedIn", icon: Briefcase, color: "#0A66C2" },
  { id: "x", name: "X (Twitter)", icon: MessageCircle, color: "#000000" },
  { id: "instagram", name: "Instagram", icon: Camera, color: "#E4405F" },
  { id: "facebook", name: "Facebook", icon: Globe, color: "#1877F2" },
  { id: "youtube", name: "YouTube", icon: Play, color: "#FF0000" },
]

interface KPI {
  value: number
  change: number
  trend: "up" | "down"
  label: string
  suffix?: string
}

interface PlatformData {
  platform: string
  name: string
  color: string
  icon: string
  kpis: Record<string, KPI>
  charts: {
    engagementTrend?: Array<{ date: string; impressions: number; engagement: number }>
    impressionsTrend?: Array<{ date: string; impressions: number; retweets: number }>
    reachTrend?: Array<{ date: string; reach: number; saves?: number; reactions?: number }>
    watchTimeTrend?: Array<{ date: string; views: number; watchTime: number }>
    subscriberGrowth?: Array<{ date: string; subscribers: number }>
    contentTypePerformance?: Array<{ type: string; count: number; avgEngagement: number }>
    bestPostingTimes?: Array<{ day: string; hour: number; score: number }>
    reactionsBreakdown?: Array<{ type: string; count: number; percentage: number }>
  }
  topPosts: Array<{
    id: string
    title: string
    impressions?: number
    views?: number
    engagement: number
    engagementRate: number
    clicks?: number
    retweets?: number
    saves?: number
    reactions?: number
    subscribers?: number
  }>
}

function formatNum(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + "M"
  if (n >= 1000) return (n / 1000).toFixed(1) + "K"
  return n.toString()
}

function KPICard({ kpi }: { kpi: KPI }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {kpi.label}
        </CardTitle>
        {kpi.trend === "up" ? (
          <ArrowUpRight className="h-4 w-4 text-green-500" />
        ) : (
          <ArrowDownRight className="h-4 w-4 text-red-500" />
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {formatNum(kpi.value)}
          {kpi.suffix || ""}
        </div>
        <p className="text-xs text-muted-foreground">
          <span className={kpi.trend === "up" ? "text-green-500" : "text-red-500"}>
            {kpi.change > 0 ? "+" : ""}{kpi.change}%
          </span>{" "}
          from last period
        </p>
      </CardContent>
    </Card>
  )
}

function EngagementTrendChart({ data }: { data: Array<{ date: string; impressions: number; engagement: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Impressions & Engagement Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="impressions" stroke="#3b82f6" strokeWidth={2} dot={false} name="Impressions" />
              <Line type="monotone" dataKey="engagement" stroke="#8b5cf6" strokeWidth={2} dot={false} name="Engagement" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function ImpressionsRetweetChart({ data }: { data: Array<{ date: string; impressions: number; retweets: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Impressions & Retweets Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="impressions" stroke="#000000" strokeWidth={2} dot={false} name="Impressions" />
              <Line type="monotone" dataKey="retweets" stroke="#1d9bf0" strokeWidth={2} dot={false} name="Retweets" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function ReachSavesChart({ data }: { data: Array<{ date: string; reach: number; saves?: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Reach & Saves Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="reach" stroke="#E4405F" strokeWidth={2} dot={false} name="Reach" />
              {data[0]?.saves !== undefined && (
                <Line type="monotone" dataKey="saves" stroke="#833AB4" strokeWidth={2} dot={false} name="Saves" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function WatchTimeChart({ data }: { data: Array<{ date: string; views: number; watchTime: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Views & Watch Time Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="views" stroke="#FF0000" strokeWidth={2} dot={false} name="Views" />
              <Line type="monotone" dataKey="watchTime" stroke="#282828" strokeWidth={2} dot={false} name="Watch Time (hrs)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function SubscriberGrowthChart({ data }: { data: Array<{ date: string; subscribers: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Subscriber Growth</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Line type="monotone" dataKey="subscribers" stroke="#FF0000" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function ContentTypeChart({ data }: { data: Array<{ type: string; count: number; avgEngagement: number }> }) {
  const COLORS = ["#3b82f6", "#8b5cf6", "#06b6d4", "#22c55e", "#f59e0b"]
  return (
    <Card>
      <CardHeader>
        <CardTitle>Content Type Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="type" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Posts" />
              <Bar dataKey="avgEngagement" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Avg Engagement %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

function ReactionsBreakdownChart({ data }: { data: Array<{ type: string; count: number; percentage: number }> }) {
  const COLORS = ["#1877F2", "#F33E58", "#F7B928", "#45BD62", "#E07038", "#E8453C"]
  return (
    <Card>
      <CardHeader>
        <CardTitle>Reactions Breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="count"
                nameKey="type"
              >
                {data.map((_, index) => (
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
  )
}

function BestTimesHeatmap({ data }: { data: Array<{ day: string; hour: number; score: number }> }) {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  const hours = Array.from({ length: 17 }, (_, i) => i + 6)

  return (
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
                    const entry = data.find(d => d.day === day && d.hour === hour)
                    const score = entry?.score || 0.3
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
  )
}

function TopPostsTable({ posts, platform }: { posts: PlatformData["topPosts"]; platform: string }) {
  return (
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
                <th className="pb-3 font-medium">
                  {platform === "youtube" ? "Views" : "Impressions"}
                </th>
                <th className="pb-3 font-medium">Engagement</th>
                <th className="pb-3 font-medium">Eng. Rate</th>
                {platform === "linkedin" && <th className="pb-3 font-medium">Clicks</th>}
                {platform === "x" && <th className="pb-3 font-medium">Retweets</th>}
                {platform === "instagram" && <th className="pb-3 font-medium">Saves</th>}
                {platform === "facebook" && <th className="pb-3 font-medium">Reactions</th>}
                {platform === "youtube" && <th className="pb-3 font-medium">Subscribers</th>}
              </tr>
            </thead>
            <tbody>
              {posts.map((post) => (
                <tr key={post.id} className="border-b last:border-0">
                  <td className="py-3 font-medium">{post.title}</td>
                  <td className="py-3">{formatNum(post.impressions || post.views || 0)}</td>
                  <td className="py-3">{formatNum(post.engagement)}</td>
                  <td className="py-3">{post.engagementRate}%</td>
                  {platform === "linkedin" && <td className="py-3">{formatNum(post.clicks || 0)}</td>}
                  {platform === "x" && <td className="py-3">{formatNum(post.retweets || 0)}</td>}
                  {platform === "instagram" && <td className="py-3">{formatNum(post.saves || 0)}</td>}
                  {platform === "facebook" && <td className="py-3">{formatNum(post.reactions || 0)}</td>}
                  {platform === "youtube" && <td className="py-3">{formatNum(post.subscribers || 0)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

export default function AnalyticsPage() {
  const [activePlatform, setActivePlatform] = useState("linkedin")
  const [platformData, setPlatformData] = useState<PlatformData | null>(null)
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState("30d")

  useEffect(() => {
    async function fetchPlatformData() {
      setLoading(true)
      try {
        const res = await fetch(`${API_URL}/analytics/platform/${activePlatform}?period=${period}`)
        if (res.ok) {
          const data = await res.json()
          setPlatformData(data)
        }
      } catch {
        // Use fallback mock data
      } finally {
        setLoading(false)
      }
    }
    fetchPlatformData()
  }, [activePlatform, period])

  const platformConfig = PLATFORMS.find(p => p.id === activePlatform)!

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-muted-foreground">
              Platform-specific insights for your content performance.
            </p>
          </div>
          <div className="flex gap-2">
            {["7d", "30d", "90d"].map((p) => (
              <Button
                key={p}
                variant={period === p ? "default" : "outline"}
                size="sm"
                onClick={() => setPeriod(p)}
              >
                {p === "7d" ? "7 Days" : p === "30d" ? "30 Days" : "90 Days"}
              </Button>
            ))}
          </div>
        </div>

        {/* Platform Tabs */}
        <Tabs value={activePlatform} onValueChange={setActivePlatform}>
          <TabsList className="h-auto flex-wrap">
            {PLATFORMS.map((platform) => {
              const Icon = platform.icon
              return (
                <TabsTrigger
                  key={platform.id}
                  value={platform.id}
                  className="gap-2"
                  style={{
                    color: activePlatform === platform.id ? platform.color : undefined,
                  }}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{platform.name}</span>
                </TabsTrigger>
              )
            })}
          </TabsList>

          {/* Loading State */}
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : platformData ? (
            <>
              {/* KPI Cards */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {Object.values(platformData.kpis).map((kpi) => (
                  <KPICard key={kpi.label} kpi={kpi} />
                ))}
              </div>

              {/* Platform-Specific Charts */}
              <div className="grid gap-6 lg:grid-cols-2">
                {/* LinkedIn Charts */}
                {activePlatform === "linkedin" && platformData.charts.engagementTrend && (
                  <>
                    <EngagementTrendChart data={platformData.charts.engagementTrend} />
                    {platformData.charts.contentTypePerformance && (
                      <ContentTypeChart data={platformData.charts.contentTypePerformance} />
                    )}
                  </>
                )}

                {/* X Charts */}
                {activePlatform === "x" && platformData.charts.impressionsTrend && (
                  <>
                    <ImpressionsRetweetChart data={platformData.charts.impressionsTrend} />
                    {platformData.charts.bestPostingTimes && (
                      <BestTimesHeatmap data={platformData.charts.bestPostingTimes} />
                    )}
                  </>
                )}

                {/* Instagram Charts */}
                {activePlatform === "instagram" && platformData.charts.reachTrend && (
                  <>
                    <ReachSavesChart data={platformData.charts.reachTrend} />
                    {platformData.charts.contentTypePerformance && (
                      <ContentTypeChart data={platformData.charts.contentTypePerformance} />
                    )}
                  </>
                )}

                {/* Facebook Charts */}
                {activePlatform === "facebook" && platformData.charts.reachTrend && (
                  <>
                    <ReachSavesChart data={platformData.charts.reachTrend} />
                    {platformData.charts.reactionsBreakdown && (
                      <ReactionsBreakdownChart data={platformData.charts.reactionsBreakdown} />
                    )}
                  </>
                )}

                {/* YouTube Charts */}
                {activePlatform === "youtube" && (
                  <>
                    {platformData.charts.watchTimeTrend && (
                      <WatchTimeChart data={platformData.charts.watchTimeTrend} />
                    )}
                    {platformData.charts.subscriberGrowth && (
                      <SubscriberGrowthChart data={platformData.charts.subscriberGrowth} />
                    )}
                  </>
                )}
              </div>

              {/* Top Posts */}
              {platformData.topPosts.length > 0 && (
                <TopPostsTable posts={platformData.topPosts} platform={activePlatform} />
              )}
            </>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-16">
                <BarChart3 className="h-10 w-10 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold">No data yet</h3>
                <p className="text-sm text-muted-foreground">
                  Start posting to see analytics for {platformConfig.name}.
                </p>
              </CardContent>
            </Card>
          )}
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
