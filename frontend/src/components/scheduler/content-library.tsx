"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  BookOpen,
  Search,
  Tag,
  Trash2,
  Copy,
  Loader2,
  FolderOpen,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface LibraryItem {
  id: string
  title: string
  content_preview: string
  platform: string
  category: string
  tags: string[]
  saved_at: string | null
}

export function ContentLibrary() {
  const [items, setItems] = useState<LibraryItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [categories, setCategories] = useState<string[]>([])

  const fetchLibrary = useCallback(async () => {
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const params = new URLSearchParams()
      if (searchQuery) params.set("query", searchQuery)
      if (selectedCategory) params.set("category", selectedCategory)

      const response = await fetch(`${API_BASE}/scheduler/library/search?${params}`, { headers })
      if (response.ok) {
        const data = await response.json()
        setItems(data.items || [])
        setTotal(data.total || 0)
        setCategories(data.categories || [])
      }
    } catch (err) {
      console.error("Failed to load library:", err)
    } finally {
      setLoading(false)
    }
  }, [searchQuery, selectedCategory])

  useEffect(() => { fetchLibrary() }, [fetchLibrary])

  const handleRemove = async (postId: string) => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
    const headers: Record<string, string> = {}
    if (token) headers["Authorization"] = `Bearer ${token}`

    await fetch(`${API_BASE}/scheduler/library/${postId}`, { method: "DELETE", headers })
    fetchLibrary()
  }

  const handleCopy = async (content: string) => {
    await navigator.clipboard.writeText(content)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Content Library
          </CardTitle>
          <Badge variant="outline">{total} items</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Search */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search library..."
              className="pl-8 text-sm"
            />
          </div>
        </div>

        {/* Categories */}
        {categories.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${!selectedCategory ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
                className={`rounded-full px-2 py-0.5 text-[10px] font-medium capitalize ${selectedCategory === cat ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {/* Items */}
        {loading ? (
          <div className="text-center py-6">
            <Loader2 className="h-5 w-5 animate-spin mx-auto mb-2 text-muted-foreground" />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <FolderOpen className="h-8 w-8 mx-auto mb-2 opacity-30" />
            <p className="text-xs">No library items found</p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item) => (
              <div key={item.id} className="rounded-lg border p-2.5 space-y-1.5">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-medium truncate">{item.title || "Untitled"}</h4>
                    <p className="text-[10px] text-muted-foreground line-clamp-2 mt-0.5">
                      {item.content_preview}
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1 flex-wrap">
                    <Badge variant="outline" className="text-[9px] capitalize">{item.platform}</Badge>
                    <Badge variant="secondary" className="text-[9px] capitalize">{item.category}</Badge>
                    {item.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-[9px]">
                        <Tag className="h-2 w-2 mr-0.5" />{tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => handleCopy(item.content_preview)}>
                      <Copy className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-6 w-6 text-red-500" onClick={() => handleRemove(item.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
