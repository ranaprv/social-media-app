"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Eye,
  AlertTriangle,
  CheckCircle2,
  Loader2,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface PreviewResult {
  platform: string
  preview: string
  char_count: number
  max_chars: number
  is_truncated: boolean
  in_optimal_range: boolean
  hashtags: string[]
  has_question: boolean
  has_emoji: boolean
  notes: string[]
}

interface PostPreviewProps {
  initialContent?: string
  platform?: Platform
}

export function PostPreview({ initialContent = "", platform = "linkedin" }: PostPreviewProps) {
  const [content, setContent] = useState(initialContent)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [preview, setPreview] = useState<PreviewResult | null>(null)
  const [loading, setLoading] = useState(false)

  const generatePreview = useCallback(async () => {
    if (!content) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/preview`, {
        method: "POST",
        headers,
        body: JSON.stringify({ content, platform: selectedPlatform }),
      })
      if (response.ok) setPreview(await response.json())
    } finally {
      setLoading(false)
    }
  }, [content, selectedPlatform])

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Eye className="h-4 w-4" />
          Post Preview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Content input */}
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Type or paste your post content..."
          className="min-h-[80px] text-sm"
        />

        {/* Platform selector */}
        <div className="flex items-center gap-2">
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value as Platform)}
            className="rounded-md border border-border bg-background px-2 py-1 text-sm"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="x">X (Twitter)</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="youtube">YouTube</option>
          </select>
          <Button onClick={generatePreview} disabled={loading || !content} size="sm" className="gap-1">
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Eye className="h-3.5 w-3.5" />}
            Preview
          </Button>
        </div>

        {/* Preview result */}
        {preview && (
          <div className="space-y-2 pt-2 border-t">
            {/* Platform card preview */}
            <div className={`rounded-lg border p-3 ${
              preview.platform === "x" ? "bg-gray-50" :
              preview.platform === "instagram" ? "bg-pink-50/50" :
              preview.platform === "linkedin" ? "bg-blue-50/50" :
              preview.platform === "facebook" ? "bg-blue-50/50" :
              "bg-red-50/50"
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-medium capitalize">{preview.platform}</span>
                {preview.is_truncated && (
                  <Badge variant="destructive" className="text-[9px]">Truncated</Badge>
                )}
                {preview.in_optimal_range && (
                  <Badge variant="default" className="text-[9px] bg-green-600">Optimal length</Badge>
                )}
              </div>
              <p className="text-sm whitespace-pre-wrap">{preview.preview}</p>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
              <span>{preview.char_count}/{preview.max_chars} chars</span>
              <span>{preview.hashtags.length} hashtags</span>
              {preview.has_question && <span className="text-green-600">✓ Question</span>}
              {preview.has_emoji && <span className="text-green-600">✓ Emoji</span>}
            </div>

            {/* Notes */}
            {preview.notes.length > 0 && (
              <div className="space-y-1">
                {preview.notes.map((note, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-xs">
                    <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5 shrink-0" />
                    <span className="text-muted-foreground">{note}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
