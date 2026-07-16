"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  PenTool, Sparkles, Loader2, Copy, Check, Cpu, Save, RefreshCw, Image, Film, FileText,
  Mic, Layout, MessageSquare, Mail, Video,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

const CONTENT_TYPES = [
  { id: "image", label: "Image Prompt", icon: Image, color: "bg-pink-100 text-pink-700" },
  { id: "carousel", label: "Carousel", icon: Layout, color: "bg-purple-100 text-purple-700" },
  { id: "article", label: "Article", icon: FileText, color: "bg-blue-100 text-blue-700" },
  { id: "linkedin_post", label: "LinkedIn Post", icon: MessageSquare, color: "bg-blue-600 text-white" },
  { id: "short_video", label: "Short Video", icon: Video, color: "bg-red-100 text-red-700" },
  { id: "long_video", label: "Long Video", icon: Film, color: "bg-orange-100 text-orange-700" },
  { id: "reel", label: "Reel", icon: Mic, color: "bg-gradient-to-r from-purple-500 to-pink-500 text-white" },
  { id: "tweet_thread", label: "X Thread", icon: MessageSquare, color: "bg-gray-900 text-white" },
]

const PLATFORMS = ["linkedin", "x", "instagram", "facebook", "youtube"]
const TONES = ["professional", "casual", "humorous", "inspirational", "educational", "provocative", "storytelling"]
const LENGTHS = ["short", "medium", "long"]

export function ContentGenerator() {
  const [contentType, setContentType] = useState("linkedin_post")
  const [platform, setPlatform] = useState("linkedin")
  const [topic, setTopic] = useState("")
  const [tone, setTone] = useState("professional")
  const [length, setLength] = useState("medium")
  const [keywords, setKeywords] = useState("")
  const [customPrompt, setCustomPrompt] = useState("")

  // Model selection
  const [availableModels, setAvailableModels] = useState<Record<string, { name: string; models: { id: string; name: string }[] }>>({})
  const [selectedProvider, setSelectedProvider] = useState("openai")
  const [selectedModel, setSelectedModel] = useState("")

  // Result
  const [result, setResult] = useState<{ content: string; hashtags: string[]; drive_url: string | null } | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    async function fetchModels() {
      try {
        const res = await fetch(`${API_URL}/ai/models`)
        if (res.ok) {
          const data = await res.json()
          setAvailableModels(data.models || {})
          const providers = Object.keys(data.models || {})
          if (providers.length > 0) setSelectedProvider(providers[0])
        }
      } catch { /* use defaults */ }
    }
    fetchModels()
  }, [])

  const generate = async () => {
    if (!topic.trim()) return
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/ai/generate-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content_type: contentType,
          topic,
          platform,
          provider: selectedProvider,
          model: selectedModel || undefined,
          custom_prompt: customPrompt,
          tone,
          keywords: keywords.split(",").map((k) => k.trim()).filter(Boolean),
          length,
        }),
      })
      const data = await res.json()
      setResult(data)
    } catch {
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const copyContent = () => {
    if (result?.content) {
      navigator.clipboard.writeText(result.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const providers = Object.keys(availableModels)
  const currentModels = availableModels[selectedProvider]?.models || []

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PenTool className="h-5 w-5 text-primary" />
            Content Engine
          </CardTitle>
          <p className="text-sm text-muted-foreground">Generate content with AI. Choose content type, model, and topic.</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Content Type Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium">Content Type *</label>
            <div className="grid grid-cols-4 gap-2">
              {CONTENT_TYPES.map((ct) => {
                const Icon = ct.icon
                return (
                  <button
                    key={ct.id}
                    onClick={() => setContentType(ct.id)}
                    className={`flex flex-col items-center gap-1 rounded-lg border p-3 text-xs font-medium transition-all ${
                      contentType === ct.id
                        ? "border-primary bg-primary/10 text-primary ring-2 ring-primary/20"
                        : "bg-background hover:bg-muted"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    {ct.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Platform + Tone + Length */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Platform</label>
              <select className="w-full rounded-lg border bg-background p-2 text-sm" value={platform} onChange={(e) => setPlatform(e.target.value)}>
                {PLATFORMS.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Tone</label>
              <select className="w-full rounded-lg border bg-background p-2 text-sm" value={tone} onChange={(e) => setTone(e.target.value)}>
                {TONES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Length</label>
              <div className="flex gap-1">
                {LENGTHS.map((l) => (
                  <button key={l} onClick={() => setLength(l)}
                    className={`flex-1 rounded-lg border px-2 py-1.5 text-xs font-medium ${
                      length === l ? "border-primary bg-primary/10 text-primary" : "bg-background"
                    }`}
                  >{l}</button>
                ))}
              </div>
            </div>
          </div>

          {/* Topic */}
          <div>
            <label className="mb-1 block text-sm font-medium">Topic *</label>
            <Input placeholder="What should the content be about?" value={topic} onChange={(e) => setTopic(e.target.value)} />
          </div>

          {/* Keywords */}
          <div>
            <label className="mb-1 block text-sm font-medium">Keywords (comma-separated)</label>
            <Input placeholder="growth, marketing, strategy" value={keywords} onChange={(e) => setKeywords(e.target.value)} />
          </div>

          {/* Custom Prompt */}
          <div>
            <label className="mb-1 block text-sm font-medium">Custom Instructions (optional)</label>
            <textarea
              className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              rows={3}
              placeholder="Extra context: include a specific example, reference a competitor, target a sub-audience..."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
            />
          </div>

          {/* Model Selection */}
          <div className="rounded-lg border p-4 space-y-3">
            <label className="text-sm font-medium flex items-center gap-2">
              <Cpu className="h-4 w-4" /> AI Model
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs text-muted-foreground">Provider</label>
                <select className="w-full rounded-lg border bg-background p-2 text-sm" value={selectedProvider} onChange={(e) => { setSelectedProvider(e.target.value); setSelectedModel(""); }}>
                  {providers.map((p) => <option key={p} value={p}>{availableModels[p]?.name || p}</option>)}
                  {providers.length === 0 && <option value="openai">OpenAI (configure API key)</option>}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs text-muted-foreground">Model</label>
                <select className="w-full rounded-lg border bg-background p-2 text-sm" value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                  <option value="">Auto (default)</option>
                  {currentModels.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Generate */}
          <Button onClick={generate} disabled={loading || !topic.trim()} className="w-full gap-2">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            Generate Content
          </Button>
        </CardContent>
      </Card>

      {/* Result */}
      {result && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Generated Content
              </CardTitle>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={copyContent} className="gap-1">
                  {copied ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
                  {copied ? "Copied" : "Copy"}
                </Button>
                {result.drive_url && (
                  <a href={result.drive_url} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" size="sm" className="gap-1">
                      <Save className="h-3 w-3" /> View on Drive
                    </Button>
                  </a>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4 bg-muted/30">
              <pre className="whitespace-pre-wrap text-sm font-mono">{result.content}</pre>
            </div>
            {result.hashtags && result.hashtags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {result.hashtags.map((tag, i) => (
                  <span key={i} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">{tag}</span>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
