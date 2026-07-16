"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  PenTool,
  Sparkles,
  Loader2,
  Copy,
  Check,
  RefreshCw,
  Plus,
  X,
} from "lucide-react"
import type { Platform, ContentType } from "@/types"

interface PlatformConfig {
  id: Platform
  name: string
  color: string
  contentTypes: { id: ContentType; label: string }[]
}

const PLATFORMS: PlatformConfig[] = [
  {
    id: "linkedin",
    name: "LinkedIn",
    color: "bg-blue-600",
    contentTypes: [
      { id: "post", label: "Post" },
      { id: "carousel", label: "Carousel" },
      { id: "poll", label: "Poll" },
      { id: "article", label: "Article" },
    ],
  },
  {
    id: "x",
    name: "X (Twitter)",
    color: "bg-black",
    contentTypes: [
      { id: "tweet", label: "Tweet" },
      { id: "thread", label: "Thread" },
    ],
  },
  {
    id: "instagram",
    name: "Instagram",
    color: "bg-gradient-to-r from-purple-500 to-pink-500",
    contentTypes: [
      { id: "reel", label: "Reel Script" },
      { id: "carousel-copy", label: "Carousel Copy" },
      { id: "caption", label: "Caption" },
    ],
  },
  {
    id: "facebook",
    name: "Facebook",
    color: "bg-blue-500",
    contentTypes: [
      { id: "post", label: "Post" },
      { id: "story", label: "Story" },
    ],
  },
  {
    id: "youtube",
    name: "YouTube",
    color: "bg-red-600",
    contentTypes: [
      { id: "short-script", label: "Shorts Script" },
      { id: "long-script", label: "Long Video Script" },
      { id: "title", label: "Title" },
      { id: "description", label: "Description" },
      { id: "chapter", label: "Chapters" },
      { id: "tags", label: "Tags" },
    ],
  },
]

const TONES = [
  "Professional", "Casual", "Humorous", "Inspirational",
  "Educational", "Provocative", "Empathetic", "Authoritative",
  "Friendly", "Urgent",
]

const LENGTHS = [
  { value: "short", label: "Short", desc: "Under 100 words" },
  { value: "medium", label: "Medium", desc: "100-250 words" },
  { value: "long", label: "Long", desc: "250-500 words" },
]

export function ContentGenerator() {
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>("linkedin")
  const [contentType, setContentType] = useState<ContentType>("post")
  const [topic, setTopic] = useState("")
  const [tone, setTone] = useState("Professional")
  const [length, setLength] = useState<"short" | "medium" | "long">("medium")
  const [keywords, setKeywords] = useState<string[]>([])
  const [keywordInput, setKeywordInput] = useState("")
  const [additionalContext, setAdditionalContext] = useState("")

  const [generatedContent, setGeneratedContent] = useState("")
  const [generatedHashtags, setGeneratedHashtags] = useState<string[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [variations, setVariations] = useState<string[]>([])

  const platformConfig = PLATFORMS.find((p) => p.id === selectedPlatform)

  const generateContent = async () => {
    if (!topic.trim()) return
    setLoading(true)
    try {
      const res = await fetch("/api/ai/generate?workspace_id=default", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform: selectedPlatform,
          content_type: contentType,
          topic,
          tone,
          length,
          keywords,
          additional_context: additionalContext,
        }),
      })
      const data = await res.json()
      setGeneratedContent(data.content || "")
      setGeneratedHashtags(data.hashtags || [])
      setSuggestions(data.suggestions || [])
      setVariations(data.variations || [])
    } catch {
      setGeneratedContent(generatePlaceholder())
      setGeneratedHashtags([
        `#${topic.split(" ")[0] || "Content"}`,
        "#SocialMedia",
        "#Marketing",
      ])
      setSuggestions([
        "Add a compelling call-to-action",
        "Include relevant emojis for engagement",
        "Post during peak hours for maximum reach",
      ])
    } finally {
      setLoading(false)
    }
  }

  const generatePlaceholder = (): string => {
    const platformSpecific = {
      linkedin: `🚀 ${topic}\n\nHere's what most people miss about ${topic}:\n\n1. It's not about perfection — it's about consistency\n2. Start with your audience's pain points\n3. Share real results, not theory\n\nThe key insight? ${keywords[0] || topic} works when you focus on providing value first.\n\nWhat's your experience with ${topic}? Drop a comment below 👇\n\n#${(topic.split(" ")[0] || "Topic").replace(/\s/g, "")} #ContentCreation #Growth`,
      x: `Hot take: ${topic}\n\nMost people get this wrong 👇\n\n🧵 Thread on what actually works:`,
      instagram: `✨ ${topic} ✨\n\nSave this for later! 📌\n\nHere's everything you need to know:\n\n💬 Comment your thoughts below!\n\n#${(topic.split(" ")[0] || "Topic").replace(/\s/g, "")} #InstaTips #ContentCreator`,
      facebook: `Hey everyone! 👋\n\nLet's talk about ${topic}.\n\nI've been thinking about this a lot lately, and here's my take:\n\nThe biggest mistake people make is overcomplicating it. Keep it simple, focus on value, and the results will follow.\n\nWhat do you think? Agree or disagree?`,
      youtube: `🎬 ${topic} - Complete Guide\n\n📝 Description:\nIn this video, we break down everything you need to know about ${topic}. Whether you're a beginner or experienced, this guide covers it all.\n\n⏱️ Chapters:\n0:00 - Introduction\n1:00 - What is ${topic}?\n3:00 - Why it matters\n5:00 - How to get started\n8:00 - Pro tips\n10:00 - Common mistakes\n12:00 - Final thoughts`,
    }
    return platformSpecific[selectedPlatform] || `Content about ${topic}`
  }

  const copyContent = () => {
    navigator.clipboard.writeText(generatedContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PenTool className="h-5 w-5 text-primary" />
            AI Content Generator
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Generate platform-optimized content with AI. Pick your platform, content type, and topic.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Platform Selector */}
          <div>
            <label className="text-sm font-medium mb-2 block">Platform</label>
            <div className="flex gap-2 flex-wrap">
              {PLATFORMS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => {
                    setSelectedPlatform(p.id)
                    setContentType(p.contentTypes[0].id)
                  }}
                  className={`inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                    selectedPlatform === p.id
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  <span className={`w-3 h-3 rounded-full ${p.color}`} />
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {/* Content Type */}
          {platformConfig && (
            <div>
              <label className="text-sm font-medium mb-2 block">Content Type</label>
              <div className="flex gap-2 flex-wrap">
                {platformConfig.contentTypes.map((ct) => (
                  <button
                    key={ct.id}
                    onClick={() => setContentType(ct.id)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                      contentType === ct.id
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    {ct.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Topic */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Topic *</label>
            <Input
              placeholder="e.g., 10 Productivity Tips for Remote Teams"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          {/* Tone + Length */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Tone</label>
              <div className="flex flex-wrap gap-1.5">
                {TONES.map((t) => (
                  <button
                    key={t}
                    onClick={() => setTone(t)}
                    className={`rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
                      tone === t
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Length</label>
              <div className="flex gap-2">
                {LENGTHS.map((l) => (
                  <button
                    key={l.value}
                    onClick={() => setLength(l.value as "short" | "medium" | "long")}
                    className={`flex-1 rounded-lg px-3 py-2 text-xs font-medium transition-all text-center ${
                      length === l.value
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    <div>{l.label}</div>
                    <div className="text-[10px] opacity-75">{l.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Keywords */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Keywords</label>
            <div className="flex gap-2">
              <Input
                placeholder="Add keyword and press Enter"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && keywordInput.trim()) {
                    e.preventDefault()
                    if (!keywords.includes(keywordInput.trim())) {
                      setKeywords([...keywords, keywordInput.trim()])
                    }
                    setKeywordInput("")
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => {
                  if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
                    setKeywords([...keywords, keywordInput.trim()])
                    setKeywordInput("")
                  }
                }}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {keywords.map((kw, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                  >
                    {kw}
                    <button onClick={() => setKeywords(keywords.filter((_, idx) => idx !== i))}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Additional Context */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Additional Context</label>
            <textarea
              className="flex min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Any additional context, specific angle, or requirements..."
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
            />
          </div>

          <Button
            onClick={generateContent}
            disabled={!topic.trim() || loading}
            className="w-full gap-2"
            size="lg"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {loading ? "Generating..." : "Generate Content"}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Content */}
      {generatedContent && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Generated Content</CardTitle>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={generateContent}>
                  <RefreshCw className="h-4 w-4 mr-1.5" />
                  Regenerate
                </Button>
                <Button variant="ghost" size="sm" onClick={copyContent}>
                  {copied ? (
                    <Check className="h-4 w-4 mr-1.5 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4 mr-1.5" />
                  )}
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Content Preview */}
            <div className="rounded-lg border bg-muted/50 p-4 whitespace-pre-wrap text-sm leading-relaxed">
              {generatedContent}
            </div>

            {/* Hashtags */}
            {generatedHashtags.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs font-medium text-muted-foreground mb-2">Hashtags</h4>
                <div className="flex flex-wrap gap-1.5">
                  {generatedHashtags.map((tag, i) => (
                    <span
                      key={i}
                      className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {suggestions.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs font-medium text-muted-foreground mb-2">Suggestions</h4>
                <ul className="space-y-1">
                  {suggestions.map((s, i) => (
                    <li key={i} className="text-xs text-muted-foreground flex items-start gap-2">
                      <span className="text-primary mt-0.5">•</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
