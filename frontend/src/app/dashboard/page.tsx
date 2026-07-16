"use client"

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
  AlertCircle,
  Plus,
} from "lucide-react"

const stats = [
  {
    title: "Total Posts",
    value: "127",
    change: "+12%",
    icon: PenTool,
    color: "text-blue-500",
  },
  {
    title: "Scheduled",
    value: "23",
    change: "+5",
    icon: Clock,
    color: "text-orange-500",
  },
  {
    title: "Published",
    value: "89",
    change: "+18%",
    icon: CheckCircle,
    color: "text-green-500",
  },
  {
    title: "Total Reach",
    value: "45.2K",
    change: "+24%",
    icon: TrendingUp,
    color: "text-purple-500",
  },
]

const recentPosts = [
  {
    id: "1",
    title: "10 Tips for Building a SaaS Product",
    platform: "LinkedIn",
    status: "published",
    date: "2026-07-15",
  },
  {
    id: "2",
    title: "How I Grew My Twitter Following to 50K",
    platform: "X",
    status: "scheduled",
    date: "2026-07-16",
  },
  {
    id: "3",
    title: "Behind the Scenes: Our Product Launch",
    platform: "Instagram",
    status: "draft",
    date: "2026-07-17",
  },
  {
    id: "4",
    title: "DevOps Best Practices for Startups",
    platform: "YouTube",
    status: "review",
    date: "2026-07-18",
  },
]

const statusColors: Record<string, string> = {
  published: "bg-green-100 text-green-800",
  scheduled: "bg-blue-100 text-blue-800",
  draft: "bg-gray-100 text-gray-800",
  review: "bg-yellow-100 text-yellow-800",
  failed: "bg-red-100 text-red-800",
}

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back! Here&apos;s what&apos;s happening with your content.
            </p>
          </div>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Post
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.change} from last month
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Posts */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Posts</CardTitle>
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentPosts.map((post) => (
                <div
                  key={post.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-4">
                    <div>
                      <p className="font-medium">{post.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {post.platform} • {post.date}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${statusColors[post.status]}`}
                  >
                    {post.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

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
                  <p className="text-sm text-muted-foreground">
                    Generate AI-powered posts
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>

          <Card className="cursor-pointer transition-all hover:shadow-lg">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="rounded-lg bg-secondary/10 p-3">
                <Calendar className="h-6 w-6 text-secondary" />
              </div>
              <div>
                <h3 className="font-semibold">Schedule Posts</h3>
                <p className="text-sm text-muted-foreground">
                  Plan your content calendar
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer transition-all hover:shadow-lg">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="rounded-lg bg-accent/10 p-3">
                <BarChart3 className="h-6 w-6 text-accent" />
              </div>
              <div>
                <h3 className="font-semibold">View Analytics</h3>
                <p className="text-sm text-muted-foreground">
                  Track your performance
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
