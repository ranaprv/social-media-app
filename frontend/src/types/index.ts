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

// ── AI Content Studio Types ──────────────────────────────────────────

export type IdeaCategory =
  | "educational"
  | "tutorials"
  | "stories"
  | "case-studies"
  | "product-updates"
  | "industry-news"
  | "personal-branding"
  | "tips"
  | "mistakes"
  | "comparisons"
  | "myths"

export interface IdeaGeneratorRequest {
  industry: string
  keywords: string[]
  audience: string
  competitors: string[]
  products: string[]
  websiteUrl?: string
  count?: number
  categories?: IdeaCategory[]
}

export interface GeneratedIdea {
  id: string
  title: string
  description: string
  category: IdeaCategory
  platforms: Platform[]
  estimatedEngagement: "high" | "medium" | "low"
  tags: string[]
}

export interface IdeaGeneratorResponse {
  ideas: GeneratedIdea[]
}

// Content Generator
export type LinkedInContentType = "post" | "carousel" | "poll" | "article"
export type XContentType = "tweet" | "thread"
export type InstagramContentType = "reel" | "carousel-copy" | "caption"
export type FacebookContentType = "post" | "story"
export type YouTubeContentType = "short-script" | "long-script" | "title" | "description" | "chapter" | "tags"

export type ContentType =
  | LinkedInContentType
  | XContentType
  | InstagramContentType
  | FacebookContentType
  | YouTubeContentType

export interface ContentGeneratorRequest {
  platform: Platform
  contentType: ContentType
  topic: string
  keywords?: string[]
  tone?: string
  length?: "short" | "medium" | "long"
  additionalContext?: string
}

export interface ContentGeneratorResponse {
  content: string
  hashtags: string[]
  suggestions: string[]
  engagementScore: number
  variations?: string[]
}

// Writing Tools
export type WritingTool =
  | "rewrite"
  | "expand"
  | "summarize"
  | "translate"
  | "improve-grammar"
  | "generate-hooks"
  | "generate-ctas"
  | "generate-hashtags"
  | "seo-optimize"
  | "tone-adjust"

export interface WritingToolRequest {
  tool: WritingTool
  content: string
  platform?: Platform
  targetLanguage?: string
  targetTone?: string
  keywords?: string[]
}

export interface WritingToolResponse {
  result: string
  tool: WritingTool
  suggestions?: string[]
}

// Brand Voice
export interface BrandVoiceConfig {
  id: string
  workspaceId: string
  tone: string
  writingStyle: string
  ctaStyle: string
  emojiUsage: string
  formatting: string
  vocabulary: string
  technicalDepth: string
  samplePosts: string[]
  trainingSources: BrandVoiceSource[]
  approvalHistory: BrandVoiceApproval[]
  createdAt: Date
  updatedAt: Date
}

export interface BrandVoiceSource {
  id: string
  type: "url" | "pdf" | "document" | "website" | "posts" | "newsletter"
  value: string
  label: string
  status: "pending" | "processing" | "completed" | "failed"
}

export interface BrandVoiceApproval {
  id: string
  originalContent: string
  approvedContent: string
  edits: string
  timestamp: Date
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

// ── AI Repurposing Engine ─────────────────────────────────────────────

export type RepurposeInputType =
  | "blog-url"
  | "website"
  | "youtube-video"
  | "podcast"
  | "webinar"
  | "pdf"
  | "docx"
  | "markdown"
  | "github-readme"

export type RepurposeOutputType =
  | "linkedin-post"
  | "twitter-thread"
  | "facebook-post"
  | "instagram-caption"
  | "carousel-copy"
  | "newsletter"
  | "youtube-shorts-script"
  | "reel-script"
  | "email"

export interface RepurposeRequest {
  inputType: RepurposeInputType
  inputContent: string
  inputUrl?: string
  outputTypes: RepurposeOutputType[]
  tone?: string
  brandVoice?: string
}

export interface RepurposeResult {
  id: string
  outputType: RepurposeOutputType
  content: string
  hashtags: string[]
  platform: Platform
  estimatedEngagement: "high" | "medium" | "low"
}

export interface RepurposeResponse {
  results: RepurposeResult[]
  summary: string
}

// ── Content Calendar ──────────────────────────────────────────────────

export type CalendarView = "daily" | "weekly" | "monthly"

export interface CalendarEvent {
  id: string
  postId: string
  title: string
  content: string
  platform: Platform
  status: PostStatus
  date: string // ISO date
  timeSlot?: string
  campaignId?: string
  isRecurring: boolean
  recurringPattern?: "daily" | "weekly" | "monthly"
  authorId: string
  authorName: string
  mediaUrls: string[]
}

export interface Campaign {
  id: string
  name: string
  description: string
  color: string
  startDate: string
  endDate: string
  eventCount: number
}

export interface CalendarState {
  view: CalendarView
  currentDate: Date
  events: CalendarEvent[]
  campaigns: Campaign[]
  selectedEvent: CalendarEvent | null
}

// ── Scheduler ─────────────────────────────────────────────────────────

export interface SchedulerQueueItem {
  id: string
  postId: string
  title: string
  platform: Platform
  scheduledAt: string
  status: "queued" | "publishing" | "published" | "failed"
  retries: number
  maxRetries: number
}

export interface BestPostingTime {
  platform: Platform
  dayOfWeek: number // 0-6
  hour: number // 0-23
  score: number // 0-1
  label: string
}

export interface SchedulerConfig {
  timezone: string
  autoPublish: boolean
  queueEnabled: boolean
  maxDailyPosts: number
  preferredPostingTimes: BestPostingTime[]
}

export interface PlatformScheduleSettings {
  platform: Platform
  connected: boolean
  username?: string
  autoPublish: boolean
  queueEnabled: boolean
}

// ── Team Collaboration ────────────────────────────────────────────────

export type ReviewStatus = "pending" | "approved" | "changes-requested" | "rejected"

export interface TeamMember {
  id: string
  userId: string
  name: string
  email: string
  avatar?: string
  role: "owner" | "admin" | "editor" | "viewer"
  joinedAt: string
}

export interface Comment {
  id: string
  postId: string
  authorId: string
  authorName: string
  authorAvatar?: string
  content: string
  createdAt: string
  updatedAt?: string
  parentId?: string
  replies?: Comment[]
}

export interface Review {
  id: string
  postId: string
  postTitle: string
  requestedBy: string
  requestedByName: string
  assignedTo: string
  assignedToName: string
  status: ReviewStatus
  feedback?: string
  requestedAt: string
  completedAt?: string
}

export interface VersionHistory {
  id: string
  postId: string
  postTitle: string
  version: number
  content: string
  authorId: string
  authorName: string
  createdAt: string
  changeNote?: string
}

export interface Notification {
  id: string
  type: "comment" | "review-request" | "review-complete" | "approval" | "mention" | "assignment"
  title: string
  message: string
  read: boolean
  postId?: string
  createdAt: string
  actorName: string
}

// ── Media Library ─────────────────────────────────────────────────────

export type MediaType = "image" | "video" | "pdf" | "brand-asset" | "logo" | "template"

export interface MediaAsset {
  id: string
  name: string
  type: MediaType
  url: string
  thumbnailUrl?: string
  size: number // bytes
  mimeType: string
  tags: string[]
  folder?: string
  uploadedBy: string
  uploadedByName: string
  createdAt: string
  metadata: Record<string, unknown>
}

export interface MediaFolder {
  id: string
  name: string
  parentId?: string
  assetCount: number
  createdAt: string
}

export interface MediaSearchParams {
  query?: string
  type?: MediaType | "all"
  tags?: string[]
  folder?: string
  sortBy?: "name" | "date" | "size"
  sortOrder?: "asc" | "desc"
}
