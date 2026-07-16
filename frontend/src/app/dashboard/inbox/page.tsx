"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  MessageSquare, Mail, AtSign, Image, Loader2, CheckCircle,
  Reply, Search, Filter, Send, Bookmark,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

const PLATFORM_ICONS: Record<string, string> = {
  linkedin: "bg-blue-600",
  x: "bg-gray-900",
  instagram: "bg-gradient-to-r from-purple-500 to-pink-500",
  facebook: "bg-blue-500",
  youtube: "bg-red-600",
}

const TYPE_ICONS: Record<string, typeof MessageSquare> = {
  dm: Mail,
  comment: MessageSquare,
  mention: AtSign,
  story_reply: Image,
}

const STATUS_COLORS: Record<string, string> = {
  unread: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  read: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  replied: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
}

interface Message {
  id: string
  platform: string
  message_type: string
  sender_name: string
  content: string
  status: string
  received_at: string
}

interface SavedReply {
  id: string
  title: string
  content: string
  category: string
  shortcut: string
}

export default function InboxPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [savedReplies, setSavedReplies] = useState<SavedReply[]>([])
  const [loading, setLoading] = useState(true)
  const [platformFilter, setPlatformFilter] = useState<string>("")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [replyText, setReplyText] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    async function fetchInbox() {
      try {
        const params = new URLSearchParams()
        if (platformFilter) params.set("platform", platformFilter)
        if (statusFilter) params.set("status", statusFilter)

        const [msgRes, replyRes] = await Promise.allSettled([
          fetch(`${API_URL}/inbox/messages?${params}`),
          fetch(`${API_URL}/inbox/saved-replies`),
        ])

        if (msgRes.status === "fulfilled" && msgRes.value.ok) {
          const data = await msgRes.value.json()
          setMessages(data.messages || [])
          setUnreadCount(data.unread_count || 0)
        }
        if (replyRes.status === "fulfilled" && replyRes.value.ok) {
          const data = await replyRes.value.json()
          setSavedReplies(data.replies || [])
        }
      } catch { /* use empty state */ }
      finally { setLoading(false) }
    }
    fetchInbox()
  }, [platformFilter, statusFilter])

  const sendReply = async (messageId: string) => {
    if (!replyText.trim()) return
    try {
      await fetch(`${API_URL}/inbox/messages/${messageId}/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: replyText }),
      })
      setMessages((prev) => prev.map((m) => m.id === messageId ? { ...m, status: "replied" } : m))
      setReplyText("")
      setSelectedMessage(null)
    } catch { /* ignore */ }
  }

  const markRead = async (messageId: string) => {
    try {
      await fetch(`${API_URL}/inbox/messages/${messageId}/read`, { method: "PUT" })
      setMessages((prev) => prev.map((m) => m.id === messageId ? { ...m, status: "read" } : m))
      setUnreadCount((c) => Math.max(0, c - 1))
    } catch { /* ignore */ }
  }

  const filteredMessages = searchQuery
    ? messages.filter((m) => m.content.toLowerCase().includes(searchQuery.toLowerCase()) || m.sender_name.toLowerCase().includes(searchQuery.toLowerCase()))
    : messages

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Inbox</h1>
            <p className="text-muted-foreground">
              Manage messages across all platforms
              {unreadCount > 0 && <span className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">{unreadCount} unread</span>}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              className="w-full rounded-lg border bg-background pl-8 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <select className="rounded-lg border bg-background px-3 py-2 text-sm" value={platformFilter} onChange={(e) => setPlatformFilter(e.target.value)}>
            <option value="">All Platforms</option>
            <option value="linkedin">LinkedIn</option>
            <option value="x">X (Twitter)</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
          </select>
          <select className="rounded-lg border bg-background px-3 py-2 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Status</option>
            <option value="unread">Unread</option>
            <option value="read">Read</option>
            <option value="replied">Replied</option>
          </select>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Message List */}
          <div className="lg:col-span-2 space-y-2">
            {loading ? (
              <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
            ) : filteredMessages.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center py-16 text-center">
                  <Mail className="mb-3 h-10 w-10 text-muted-foreground" />
                  <p className="text-muted-foreground">No messages found</p>
                </CardContent>
              </Card>
            ) : (
              filteredMessages.map((msg) => {
                const TypeIcon = TYPE_ICONS[msg.message_type] || MessageSquare
                const isSelected = selectedMessage?.id === msg.id
                return (
                  <Card
                    key={msg.id}
                    className={`cursor-pointer transition-all hover:shadow-md ${isSelected ? "ring-2 ring-primary" : ""} ${msg.status === "unread" ? "border-l-4 border-l-blue-500" : ""}`}
                    onClick={() => { setSelectedMessage(msg); if (msg.status === "unread") markRead(msg.id) }}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full text-white text-xs font-bold ${PLATFORM_ICONS[msg.platform] || "bg-gray-500"}`}>
                          {msg.sender_name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-sm">{msg.sender_name}</span>
                              <TypeIcon className="h-3 w-3 text-muted-foreground" />
                              <span className="text-xs text-muted-foreground capitalize">{msg.platform}</span>
                            </div>
                            <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${STATUS_COLORS[msg.status]}`}>{msg.status}</span>
                          </div>
                          <p className="mt-1 text-sm text-muted-foreground truncate">{msg.content}</p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {new Date(msg.received_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })
            )}
          </div>

          {/* Thread / Reply Panel */}
          <div className="space-y-4">
            {selectedMessage ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">{selectedMessage.sender_name}</CardTitle>
                    <p className="text-xs text-muted-foreground">
                      {selectedMessage.platform} • {selectedMessage.message_type} • {new Date(selectedMessage.received_at).toLocaleString()}
                    </p>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{selectedMessage.content}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle className="text-sm">Reply</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    <textarea
                      className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      rows={4}
                      placeholder="Type your reply..."
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <Button onClick={() => sendReply(selectedMessage.id)} disabled={!replyText.trim()} className="gap-1 flex-1">
                        <Send className="h-3 w-3" /> Send
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Saved Replies */}
                <Card>
                  <CardHeader><CardTitle className="text-sm flex items-center gap-1"><Bookmark className="h-4 w-4" /> Quick Replies</CardTitle></CardHeader>
                  <CardContent className="space-y-2">
                    {savedReplies.map((sr) => (
                      <button
                        key={sr.id}
                        onClick={() => setReplyText(sr.content)}
                        className="w-full rounded-lg border p-2 text-left text-xs hover:bg-muted transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{sr.title}</span>
                          <span className="text-muted-foreground">{sr.shortcut}</span>
                        </div>
                        <p className="mt-0.5 text-muted-foreground truncate">{sr.content}</p>
                      </button>
                    ))}
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="flex flex-col items-center py-16 text-center text-muted-foreground">
                  <MessageSquare className="mb-3 h-10 w-10" />
                  <p className="text-sm">Select a message to view and reply</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
