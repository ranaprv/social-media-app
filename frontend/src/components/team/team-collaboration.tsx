"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Users,
  MessageSquare,
  CheckCircle,
  Clock,
  AlertCircle,
  Bell,
  History,
  Send,
  Reply,
  MoreHorizontal,
  Eye,
  Edit3,
  Shield,
  UserPlus,
  X,
  Check,
} from "lucide-react"
import type { ReviewStatus } from "@/types"

const TEAM_MEMBERS = [
  { id: "tm-1", name: "You", role: "owner", avatar: "Y", color: "bg-primary" },
  { id: "tm-2", name: "Sarah Chen", role: "admin", avatar: "SC", color: "bg-purple-500" },
  { id: "tm-3", name: "Marcus Johnson", role: "editor", avatar: "MJ", color: "bg-green-500" },
  { id: "tm-4", name: "Priya Patel", role: "editor", avatar: "PP", color: "bg-orange-500" },
  { id: "tm-5", name: "Alex Kim", role: "viewer", avatar: "AK", color: "bg-cyan-500" },
]

const ROLE_ICONS: Record<string, React.ElementType> = {
  owner: Shield,
  admin: Shield,
  editor: Edit3,
  viewer: Eye,
}

const DEMO_COMMENTS = [
  { id: "c-1", author: "Sarah Chen", avatar: "SC", color: "bg-purple-500", content: "Love this angle! Maybe we could add a specific example from our Q2 campaign?", time: "2 hours ago", replies: [
    { id: "c-1-1", author: "You", avatar: "Y", color: "bg-primary", content: "Great idea! I'll add the metrics from the product launch campaign.", time: "1 hour ago" },
  ]},
  { id: "c-2", author: "Marcus Johnson", avatar: "MJ", color: "bg-green-500", content: "The CTA at the end could be stronger. What about asking a specific question instead?", time: "5 hours ago", replies: [] },
  { id: "c-3", author: "Priya Patel", avatar: "PP", color: "bg-orange-500", content: "Approved from my side! Ready for scheduling.", time: "1 hour ago", replies: [] },
]

const DEMO_REVIEWS = [
  { id: "r-1", post: "10 Tips for Content Creation", requester: "Sarah Chen", assignee: "You", status: "pending" as ReviewStatus, time: "3 hours ago" },
  { id: "r-2", post: "Thread: Growth Strategies", requester: "You", assignee: "Marcus Johnson", status: "approved" as ReviewStatus, time: "12 hours ago" },
  { id: "r-3", post: "Behind the Scenes Reel", requester: "Priya Patel", assignee: "You", status: "changes-requested" as ReviewStatus, time: "8 hours ago" },
  { id: "r-4", post: "Weekly Motivation Post", requester: "You", assignee: "Sarah Chen", status: "pending" as ReviewStatus, time: "1 day ago" },
]

const DEMO_VERSIONS = [
  { id: "v-1", post: "10 Tips for Content", version: 3, author: "You", time: "1 hour ago", note: "Improved CTA and added examples" },
  { id: "v-2", post: "10 Tips for Content", version: 2, author: "Sarah Chen", time: "4 hours ago", note: "Added specific metrics from Q2 campaign" },
  { id: "v-3", post: "10 Tips for Content", version: 1, author: "You", time: "8 hours ago", note: "Initial draft" },
]

const DEMO_NOTIFICATIONS = [
  { id: "n-1", type: "review-request", title: "Review Requested", message: "Sarah Chen requested your review on '10 Tips for Content Creation'", read: false, time: "3 hours ago", actor: "Sarah Chen" },
  { id: "n-2", type: "comment", title: "New Comment", message: "Marcus Johnson commented on 'Thread: Growth Strategies'", read: false, time: "5 hours ago", actor: "Marcus Johnson" },
  { id: "n-3", type: "approval", title: "Review Approved", message: "Marcus Johnson approved 'Behind the Scenes Reel'", read: true, time: "12 hours ago", actor: "Marcus Johnson" },
  { id: "n-4", type: "mention", title: "Mentioned", message: "Priya Patel mentioned you in a comment", read: true, time: "1 day ago", actor: "Priya Patel" },
  { id: "n-5", type: "assignment", title: "Assigned for Review", message: "You've been assigned to review 'Product Update: New Features'", read: false, time: "1 hour ago", actor: "Sarah Chen" },
]

const STATUS_CONFIG: Record<ReviewStatus, { icon: React.ElementType; color: string; label: string }> = {
  pending: { icon: Clock, color: "text-yellow-500", label: "Pending" },
  approved: { icon: CheckCircle, color: "text-green-500", label: "Approved" },
  "changes-requested": { icon: AlertCircle, color: "text-orange-500", label: "Changes Requested" },
  rejected: { icon: X, color: "text-red-500", label: "Rejected" },
}

type TeamTab = "members" | "comments" | "reviews" | "history" | "notifications"

export function TeamCollaboration() {
  const [activeTab, setActiveTab] = useState<TeamTab>("comments")
  const [newComment, setNewComment] = useState("")
  const [replyTo, setReplyTo] = useState<string | null>(null)
  const [replyContent, setReplyContent] = useState("")

  const unreadCount = DEMO_NOTIFICATIONS.filter((n) => !n.read).length

  const tabs: { id: TeamTab; label: string; icon: React.ElementType; badge?: number }[] = [
    { id: "members", label: "Members", icon: Users },
    { id: "comments", label: "Comments", icon: MessageSquare },
    { id: "reviews", label: "Reviews", icon: CheckCircle, badge: DEMO_REVIEWS.filter((r) => r.status === "pending").length },
    { id: "history", label: "History", icon: History },
    { id: "notifications", label: "Notifications", icon: Bell, badge: unreadCount },
  ]

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                  {tab.badge && tab.badge > 0 && (
                    <span className="ml-1 bg-red-500 text-white text-[10px] rounded-full w-5 h-5 flex items-center justify-center">
                      {tab.badge}
                    </span>
                  )}
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Members Tab */}
      {activeTab === "members" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Team Members ({TEAM_MEMBERS.length})</CardTitle>
              <Button size="sm" className="gap-1.5">
                <UserPlus className="h-3.5 w-3.5" />
                Invite
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {TEAM_MEMBERS.map((member) => {
                const RoleIcon = ROLE_ICONS[member.role] || Eye
                return (
                  <div key={member.id} className="flex items-center gap-3 rounded-lg border p-3">
                    <div className={`w-10 h-10 rounded-full ${member.color} flex items-center justify-center text-white text-sm font-medium`}>
                      {member.avatar}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-sm">{member.name}</p>
                      <p className="text-xs text-muted-foreground capitalize flex items-center gap-1">
                        <RoleIcon className="h-3 w-3" />
                        {member.role}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comments Tab */}
      {activeTab === "comments" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Comments & Discussion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* New Comment */}
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-medium flex-shrink-0">Y</div>
              <div className="flex-1">
                <Input
                  placeholder="Add a comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
                {newComment && (
                  <Button size="sm" className="mt-2 gap-1.5">
                    <Send className="h-3 w-3" />
                    Post
                  </Button>
                )}
              </div>
            </div>

            {/* Comments List */}
            {DEMO_COMMENTS.map((comment) => (
              <div key={comment.id} className="space-y-3">
                <div className="flex gap-3">
                  <div className={`w-8 h-8 rounded-full ${comment.color} flex items-center justify-center text-white text-xs font-medium flex-shrink-0`}>
                    {comment.avatar}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium">{comment.author}</span>
                      <span className="text-xs text-muted-foreground">{comment.time}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{comment.content}</p>
                    <button
                      onClick={() => setReplyTo(replyTo === comment.id ? null : comment.id)}
                      className="text-xs text-primary mt-1 flex items-center gap-1 hover:underline"
                    >
                      <Reply className="h-3 w-3" />
                      Reply
                    </button>

                    {/* Replies */}
                    {comment.replies.length > 0 && (
                      <div className="mt-3 space-y-2 ml-4 border-l-2 border-muted pl-3">
                        {comment.replies.map((reply) => (
                          <div key={reply.id} className="flex gap-2">
                            <div className={`w-6 h-6 rounded-full ${reply.color} flex items-center justify-center text-white text-[10px] font-medium flex-shrink-0`}>
                              {reply.avatar}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-medium">{reply.author}</span>
                                <span className="text-[10px] text-muted-foreground">{reply.time}</span>
                              </div>
                              <p className="text-xs text-muted-foreground">{reply.content}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Reply Input */}
                    {replyTo === comment.id && (
                      <div className="mt-2 flex gap-2">
                        <Input
                          placeholder="Write a reply..."
                          value={replyContent}
                          onChange={(e) => setReplyContent(e.target.value)}
                          className="text-xs"
                        />
                        <Button size="sm" variant="ghost">Send</Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Reviews Tab */}
      {activeTab === "reviews" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Review Workflow</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {DEMO_REVIEWS.map((review) => {
                const statusConfig = STATUS_CONFIG[review.status]
                const StatusIcon = statusConfig.icon
                return (
                  <div key={review.id} className="flex items-center gap-4 rounded-lg border p-4">
                    <StatusIcon className={`h-5 w-5 ${statusConfig.color} flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{review.post}</p>
                      <p className="text-xs text-muted-foreground">
                        Requested by {review.requester} → Assigned to {review.assignee} • {review.time}
                      </p>
                    </div>
                    <span className={`text-xs font-medium ${statusConfig.color}`}>
                      {statusConfig.label}
                    </span>
                    {review.status === "pending" && review.assignee === "You" && (
                      <div className="flex gap-1.5">
                        <Button size="sm" variant="ghost" className="text-green-600 gap-1">
                          <Check className="h-3 w-3" />
                          Approve
                        </Button>
                        <Button size="sm" variant="ghost" className="text-orange-600 gap-1">
                          <AlertCircle className="h-3 w-3" />
                          Changes
                        </Button>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* History Tab */}
      {activeTab === "history" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Version History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {DEMO_VERSIONS.map((version, i) => (
                <div key={version.id} className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                      i === 0 ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                    }`}>
                      v{version.version}
                    </div>
                    {i < DEMO_VERSIONS.length - 1 && (
                      <div className="w-px h-8 bg-border mt-1" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{version.author}</span>
                      <span className="text-xs text-muted-foreground">{version.time}</span>
                      {i === 0 && (
                        <span className="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-medium">
                          Current
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{version.note}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Notifications Tab */}
      {activeTab === "notifications" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Notifications</CardTitle>
              <Button variant="ghost" size="sm">Mark all read</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {DEMO_NOTIFICATIONS.map((notif) => (
                <div
                  key={notif.id}
                  className={`flex items-start gap-3 rounded-lg p-3 transition-all ${
                    notif.read ? "bg-background" : "bg-primary/5"
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${notif.read ? "bg-transparent" : "bg-primary"}`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{notif.title}</p>
                    <p className="text-xs text-muted-foreground">{notif.message}</p>
                    <p className="text-[10px] text-muted-foreground mt-1">{notif.time}</p>
                  </div>
                  {!notif.read && (
                    <Button variant="ghost" size="sm" className="text-xs">
                      Mark read
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
