export interface User {
  id: string
  email: string
  name: string | null
  image: string | null
  createdAt: Date
  updatedAt: Date
}

export interface Workspace {
  id: string
  name: string
  slug: string
  ownerId: string
  createdAt: Date
  updatedAt: Date
}

export interface Post {
  id: string
  workspaceId: string
  authorId: string
  title: string | null
  content: string
  mediaUrls: string[]
  platform: Platform
  status: PostStatus
  scheduledAt: Date | null
  publishedAt: Date | null
  platformPostId: string | null
  metadata: Record<string, unknown>
  createdAt: Date
  updatedAt: Date
}

export type Platform = "youtube" | "instagram" | "facebook" | "linkedin" | "x"

export type PostStatus = "draft" | "review" | "scheduled" | "publishing" | "published" | "failed"

export interface PlatformConnection {
  id: string
  workspaceId: string
  platform: Platform
  platformUserId: string
  platformUsername: string
  accessToken: string
  refreshToken: string | null
  expiresAt: Date | null
  metadata: Record<string, unknown>
  createdAt: Date
  updatedAt: Date
}

export interface ContentCalendar {
  id: string
  workspaceId: string
  postId: string
  date: Date
  timeSlot: string | null
  createdAt: Date
}

export interface AnalyticsMetric {
  id: string
  postId: string
  platform: Platform
  impressions: number
  reach: number
  engagement: number
  likes: number
  comments: number
  shares: number
  clicks: number
  watchTime: number | null
  subscribers: number | null
  recordedAt: Date
  createdAt: Date
}

export interface AIContentRequest {
  platform: Platform
  contentType: string
  topic: string
  brandVoice?: string
  keywords?: string[]
  competitorPosts?: string[]
  tone?: string
  length?: "short" | "medium" | "long"
}

export interface AIContentResponse {
  content: string
  hashtags: string[]
  suggestions: string[]
  engagementScore: number
}

export interface DashboardStats {
  totalPosts: number
  scheduledPosts: number
  publishedPosts: number
  totalImpressions: number
  totalEngagement: number
  followersGrowth: number
  topPerformingPost: Post | null
  recentActivity: Activity[]
}

export interface Activity {
  id: string
  type: "post_created" | "post_published" | "post_failed" | "connection_added" | "comment_added"
  description: string
  timestamp: Date
  userId: string
}
