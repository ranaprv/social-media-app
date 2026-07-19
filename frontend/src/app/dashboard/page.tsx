"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  PenTool,
  Calendar,
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  Plus,
  FileText,
  Loader2,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const statusColors: Record<string, string> = {
  published: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  scheduled: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  draft: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
  review: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  failed: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  publishing: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
}

interface DashboardStats {
  total_posts: number
  scheduled_posts: number
  published_posts: number
  total_impressions: number
  total_engagement: number
  followers_growth: number
}

interface Post {
  id: string
  title: string | null
  platform: string
  status: string
  created_at: string
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const sessionRes = await fetch("/api/auth/session")
        const session = await sessionRes.json()
        const token = session?.accessToken

        if (!token) {
          setLoading(false)
          return
        }

        const headers = { Authorization: `Bearer ${token}` }

        // Try to get workspace ID from session or use first workspace
        const wsRes = await fetch(`${API_URL}/workspaces/`, { headers })
        if (wsRes.ok) {
          const workspaces = await wsRes.json()
          if (workspaces.length > 0) {
            const wsId = workspaces[0].id

            const [statsRes, postsRes] = await Promise.allSettled([
              fetch(`${API_URL}/dashboard/${wsId}/stats`, { headers }),
              fetch(`${API_URL}/posts/${wsId}?limit=5`, { headers }),
            ])

            if (statsRes.status === "fulfilled" && statsRes.value.ok) {
              setStats(await statsRes.value.json())
            }
            if (postsRes.status === "fulfilled" && postsRes.value.ok) {
              const data = await postsRes.value.json()
              setPosts(data.items || data || [])
            }
          }
        }
      } catch {
        // API not reachable — show empty state
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  const hasData = stats && (stats.total_posts > 0 || posts.length > 0)

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              {loading
                ? "Loading your content..."
                : hasData
                  ? "Here's what's happening with your content."
                  : "Get started by creating your first post."}
            </p>
          </div>
          <Link href="/dashboard/content-studio">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Post
            </Button>
          </Link>
        </div>

        {loading ? (
          /* Loading State */
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : !hasData ? (
          /* Empty State */
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="mb-4 rounded-full bg-primary/10 p-4">
                <FileText className="h-10 w-10 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">No content yet</h3>
              <p className="mb-6 max-w-md text-sm text-muted-foreground">
                You haven&apos;t created any posts. Start by generating AI-powered content
                or scheduling your first post.
              </p>
              <div className="flex gap-3">
                <Link href="/dashboard/content-studio">
                  <Button className="gap-2">
                    <PenTool className="h-4 w-4" />
                    Create Content
                  </Button>
                </Link>
                <Link href="/dashboard/calendar">
                  <Button variant="outline" className="gap-2">
                    <Calendar className="h-4 w-4" />
                    Open Calendar
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Total Posts</CardTitle>
                  <PenTool className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_posts ?? 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Scheduled</CardTitle>
                  <Clock className="h-4 w-4 text-orange-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.scheduled_posts ?? 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Published</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.published_posts ?? 0}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Total Reach</CardTitle>
                  <TrendingUp className="h-4 w-4 text-purple-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{(stats?.total_impressions ?? 0).toLocaleString()}</div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Posts */}
            {posts.length > 0 && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Recent Posts</CardTitle>
                    <Link href="/dashboard/content-studio">
                      <Button variant="ghost" size="sm">View All</Button>
                    </Link>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {posts.map((post) => (
                      <div key={post.id} className="flex items-center justify-between rounded-lg border p-4">
                        <div>
                          <p className="font-medium">{post.title || "Untitled post"}</p>
                          <p className="text-sm text-muted-foreground">
                            {post.platform} • {new Date(post.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusColors[post.status] || statusColors.draft}`}>
                          {post.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quick Actions */}
            <div className="grid gap-4 md:grid-cols-3">
              <Link href="/dashboard/content-studio">
                <Card className="cursor-pointer transition-all hover:shadow-lg">
                  <CardContent className="flex items-center gap-4 p-6">
                    <div className="rounded-lg bg-primary/10 p-3">
                      <PenTool className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Create Content</h3>
                      <p className="text-sm text-muted-foreground">Generate AI-powered posts</p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard/calendar">
                <Card className="cursor-pointer transition-all hover:shadow-lg">
                  <CardContent className="flex items-center gap-4 p-6">
                    <div className="rounded-lg bg-secondary/10 p-3">
                      <Calendar className="h-6 w-6 text-secondary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Schedule Posts</h3>
                      <p className="text-sm text-muted-foreground">Plan your content calendar</p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard/analytics">
                <Card className="cursor-pointer transition-all hover:shadow-lg">
                  <CardContent className="flex items-center gap-4 p-6">
                    <div className="rounded-lg bg-accent/10 p-3">
                      <BarChart3 className="h-6 w-6 text-accent" />
                    </div>
                    <div>
                      <h3 className="font-semibold">View Analytics</h3>
                      <p className="text-sm text-muted-foreground">Track your performance</p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
