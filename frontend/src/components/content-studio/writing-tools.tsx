"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Wand2,
  Loader2,
  Copy,
  Check,
  ArrowRightLeft,
  Maximize2,
  Minimize2,
  Languages,
  SpellCheck,
  Target,
  MousePointerClick,
  Hash,
  Search,
  Palette,
} from "lucide-react"
import type { WritingTool, Platform } from "@/types"

const TOOLS: {
  id: WritingTool
  label: string
  icon: React.ElementType
  description: string
  color: string
  needsPlatform?: boolean
  needsLanguage?: boolean
  needsTone?: boolean
  needsKeywords?: boolean
}[] = [
  {
    id: "rewrite",
    label: "Rewrite",
    icon: ArrowRightLeft,
    description: "Rewrite content for clarity and impact",
    color: "bg-blue-100 text-blue-700 border-blue-200",
    needsPlatform: true,
  },
  {
    id: "expand",
    label: "Expand",
    icon: Maximize2,
    description: "Add detail, examples, and depth",
    color: "bg-green-100 text-green-700 border-green-200",
  },
  {
    id: "summarize",
    label: "Summarize",
    icon: Minimize2,
    description: "Create a concise summary",
    color: "bg-purple-100 text-purple-700 border-purple-200",
  },
  {
    id: "translate",
    label: "Translate",
    icon: Languages,
    description: "Translate to another language",
    color: "bg-orange-100 text-orange-700 border-orange-200",
    needsLanguage: true,
  },
  {
    id: "improve-grammar",
    label: "Grammar",
    icon: SpellCheck,
    description: "Fix grammar and improve readability",
    color: "bg-cyan-100 text-cyan-700 border-cyan-200",
  },
  {
    id: "generate-hooks",
    label: "Hooks",
    icon: Target,
    description: "Generate attention-grabbing hooks",
    color: "bg-red-100 text-red-700 border-red-200",
  },
  {
    id: "generate-ctas",
    label: "CTAs",
    icon: MousePointerClick,
    description: "Generate effective call-to-actions",
    color: "bg-amber-100 text-amber-700 border-amber-200",
  },
  {
    id: "generate-hashtags",
    label: "Hashtags",
    icon: Hash,
    description: "Generate a hashtag strategy",
    color: "bg-pink-100 text-pink-700 border-pink-200",
  },
  {
    id: "seo-optimize",
    label: "SEO",
    icon: Search,
    description: "Optimize for search engines",
    color: "bg-teal-100 text-teal-700 border-teal-200",
    needsKeywords: true,
  },
  {
    id: "tone-adjust",
    label: "Tone",
    icon: Palette,
    description: "Adjust the writing tone",
    color: "bg-indigo-100 text-indigo-700 border-indigo-200",
    needsTone: true,
  },
]

const LANGUAGES = [
  "English", "Spanish", "French", "German", "Portuguese", "Japanese",
  "Chinese (Simplified)", "Korean", "Arabic", "Hindi", "Italian",
  "Dutch", "Russian", "Turkish", "Swedish",
]

const TONES = [
  "Professional", "Casual", "Humorous", "Inspirational", "Educational",
  "Friendly", "Urgent", "Empathetic", "Authoritative", "Playful",
]

const PLATFORMS: { id: Platform; label: string }[] = [
  { id: "linkedin", label: "LinkedIn" },
  { id: "x", label: "X" },
  { id: "instagram", label: "Instagram" },
  { id: "facebook", label: "Facebook" },
  { id: "youtube", label: "YouTube" },
]

export function WritingTools() {
  const [activeTool, setActiveTool] = useState<WritingTool>("rewrite")
  const [content, setContent] = useState("")
  const [platform, setPlatform] = useState<Platform | "">("")
  const [targetLanguage, setTargetLanguage] = useState("Spanish")
  const [targetTone, setTargetTone] = useState("Professional")
  const [keywords, setKeywords] = useState<string[]>([])
  const [keywordInput, setKeywordInput] = useState("")

  const [result, setResult] = useState("")
  const [toolSuggestions, setToolSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  const activeToolConfig = TOOLS.find((t) => t.id === activeTool)

  const useTool = async () => {
    if (!content.trim()) return
    setLoading(true)
    try {
      const res = await fetch("/api/ai/writing-tools?workspace_id=default", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: activeTool,
          content,
          platform: platform || undefined,
          target_language: targetLanguage,
          target_tone: targetTone,
          keywords,
        }),
      })
      const data = await res.json()
      setResult(data.result || "")
      setToolSuggestions(data.suggestions || [])
    } catch {
      setResult(`[${activeTool} result]\n\n${content}`)
      setToolSuggestions([])
    } finally {
      setLoading(false)
    }
  }

  const copyResult = () => {
    navigator.clipboard.writeText(result)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Tool Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="h-5 w-5 text-secondary" />
            AI Writing Tools
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Transform your content with AI-powered writing tools.
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-2">
            {TOOLS.map((tool) => {
              const Icon = tool.icon
              return (
                <button
                  key={tool.id}
                  onClick={() => setActiveTool(tool.id)}
                  className={`flex flex-col items-center gap-1.5 rounded-lg border p-3 text-xs font-medium transition-all ${
                    activeTool === tool.id
                      ? "border-primary bg-primary/5 text-primary shadow-sm"
                      : "border-transparent bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tool.label}
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Active Tool */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            {activeToolConfig && (
              <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${activeToolConfig.color}`}>
                <activeToolConfig.icon className="h-3 w-3" />
                {activeToolConfig.label}
              </span>
            )}
            <CardTitle className="text-base">
              {activeToolConfig?.description}
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Content Input */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Input Content *</label>
            <textarea
              className="flex min-h-[120px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder={
                activeTool === "generate-hooks"
                  ? "Describe your topic to generate hooks..."
                  : activeTool === "generate-ctas"
                  ? "Describe your content to generate CTAs..."
                  : activeTool === "generate-hashtags"
                  ? "Describe your content for hashtag strategy..."
                  : "Paste your content here..."
              }
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>

          {/* Tool-specific options */}
          <div className="flex flex-wrap gap-4">
            {activeToolConfig?.needsPlatform && (
              <div>
                <label className="text-xs font-medium mb-1 block">Target Platform</label>
                <div className="flex gap-1.5">
                  {PLATFORMS.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setPlatform(p.id)}
                      className={`rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
                        platform === p.id
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground hover:bg-muted/80"
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeToolConfig?.needsLanguage && (
              <div>
                <label className="text-xs font-medium mb-1 block">Target Language</label>
                <select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  className="rounded-lg border border-input bg-background px-3 py-1.5 text-xs"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
            )}

            {activeToolConfig?.needsTone && (
              <div>
                <label className="text-xs font-medium mb-1 block">Target Tone</label>
                <div className="flex flex-wrap gap-1.5">
                  {TONES.map((t) => (
                    <button
                      key={t}
                      onClick={() => setTargetTone(t)}
                      className={`rounded-md px-2 py-1 text-xs font-medium transition-all ${
                        targetTone === t
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground hover:bg-muted/80"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeToolConfig?.needsKeywords && (
              <div>
                <label className="text-xs font-medium mb-1 block">Target Keywords</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add keyword"
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
                    className="h-8 text-xs"
                  />
                </div>
                {keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {keywords.map((kw, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary"
                      >
                        {kw}
                        <button onClick={() => setKeywords(keywords.filter((_, idx) => idx !== i))}>
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <Button
            onClick={useTool}
            disabled={!content.trim() || loading}
            className="w-full gap-2"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Wand2 className="h-4 w-4" />
            )}
            {loading ? "Processing..." : `Apply ${activeToolConfig?.label}`}
          </Button>
        </CardContent>
      </Card>

      {/* Result */}
      {result && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Result</CardTitle>
              <Button variant="ghost" size="sm" onClick={copyResult}>
                {copied ? (
                  <Check className="h-4 w-4 mr-1.5 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4 mr-1.5" />
                )}
                {copied ? "Copied!" : "Copy"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border bg-muted/50 p-4 whitespace-pre-wrap text-sm leading-relaxed">
              {result}
            </div>

            {toolSuggestions.length > 0 && (
              <div className="mt-4">
                <h4 className="text-xs font-medium text-muted-foreground mb-2">Tips</h4>
                <ul className="space-y-1">
                  {toolSuggestions.map((s, i) => (
                    <li key={i} className="text-xs text-muted-foreground flex items-start gap-2">
                      <span className="text-primary mt-0.5">•</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Use as input for another tool */}
            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground mb-2">Chain tools — use result as input:</p>
              <div className="flex gap-1.5 flex-wrap">
                {TOOLS.filter((t) => t.id !== activeTool).slice(0, 5).map((tool) => (
                  <button
                    key={tool.id}
                    onClick={() => {
                      setContent(result)
                      setActiveTool(tool.id)
                      setResult("")
                      window.scrollTo({ top: 0, behavior: "smooth" })
                    }}
                    className="rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground hover:bg-muted/80 transition-all"
                  >
                    → {tool.label}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
