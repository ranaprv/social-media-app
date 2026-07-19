"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  PenTool, Sparkles, Loader2, Copy, Check, Cpu, Save, Image, Film, FileText,
  Mic, Layout, MessageSquare, Video, Lightbulb, X, Mail,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

const CONTENT_TYPES = [
  { id: "linkedin_post", label: "LinkedIn Post", icon: MessageSquare, color: "bg-blue-600 text-white" },
  { id: "tweet_thread", label: "X Thread", icon: MessageSquare, color: "bg-gray-900 text-white" },
  { id: "article", label: "Article", icon: FileText, color: "bg-blue-100 text-blue-700" },
  { id: "carousel", label: "Carousel", icon: Layout, color: "bg-purple-100 text-purple-700" },
  { id: "reel", label: "Reel", icon: Mic, color: "bg-gradient-to-r from-purple-500 to-pink-500 text-white" },
  { id: "short_video", label: "Short Video", icon: Video, color: "bg-red-100 text-red-700" },
  { id: "image", label: "Image Prompt", icon: Image, color: "bg-pink-100 text-pink-700" },
  { id: "email", label: "Newsletter", icon: Mail, color: "bg-amber-100 text-amber-700" },
]

const PLATFORMS = ["linkedin", "x", "instagram", "facebook", "youtube"]
const TONES = ["professional", "casual", "humorous", "inspirational", "educational", "provocative", "storytelling"]
const LENGTHS = ["short", "medium", "long"]

interface SavedIdea {
  title: string
  description: string
  platforms: string[]
  content_type: string
}

interface Props {
  savedIdea?: SavedIdea | null
  onClearIdea?: () => void
}

export function ContentGenerator({ savedIdea, onClearIdea }: Props) {
  const [contentType, setContentType] = useState("linkedin_post")
  const [platform, setPlatform] = useState("linkedin")
  const [topic, setTopic] = useState("")
  const [tone, setTone] = useState("professional")
  const [length, setLength] = useState("medium")
  const [keywords, setKeywords] = useState("")
  const [customPrompt, setCustomPrompt] = useState("")

  // Model selection
  const [allModels, setAllModels] = useState<Record<string, { name: string; models: { id: string; name: string; cost_tier: string }[] }>>({})
  const [selectedProvider, setSelectedProvider] = useState("openrouter")
  const [selectedModel, setSelectedModel] = useState("")

  // Result
  const [result, setResult] = useState<{ content: string; hashtags: string[] } | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  // Pre-fill from saved idea
  useEffect(() => {
    if (savedIdea) {
      queueMicrotask(() => {
        setTopic(savedIdea.title)
        setCustomPrompt(savedIdea.description)
        if (savedIdea.content_type) setContentType(savedIdea.content_type)
        if (savedIdea.platforms && savedIdea.platforms.length > 0) setPlatform(savedIdea.platforms[0])
      })
    }
  }, [savedIdea])

  useEffect(() => {
    async function fetchModels() {
      try {
        const res = await fetch(`${API_URL}/ai/ideas/models`)
        if (res.ok) {
          const data = await res.json()
          setAllModels(data.all || data.models || {})
          const providers = Object.keys(data.all || data.models || {})
          if (providers.length > 0 && !providers.includes(selectedProvider)) setSelectedProvider(providers[0])
        }
      } catch { /* use defaults */ }
    }
    fetchModels()
  }, [])

  const generate = async () => {
    if (!topic.trim()) return
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
      if (res.ok) {
        const data = await res.json()
        setResult(data)
      } else {
        // Fallback: generate placeholder
        setResult({
          content: generatePlaceholder(contentType, topic, tone),
          hashtags: [`#${topic.replace(/\s+/g, "").slice(0, 20)}`, "#ContentCreator", "#SocialMediaTips"],
        })
      }
    } catch {
      setResult({
        content: generatePlaceholder(contentType, topic, tone),
        hashtags: [`#${topic.replace(/\s+/g, "").slice(0, 20)}`, "#ContentCreator"],
      })
    } finally {
      setLoading(false)
    }
  }

  function generatePlaceholder(type: string, t: string, tn: string): string {
    const topic = t || "your topic"
    const placeholders: Record<string, string> = {
      linkedin_post: `🚀 ${topic}\n\nHere's what most people get wrong about ${topic}:\n\n1. Start with value, not promotion\n2. Share real experiences, not theory\n3. Engage with your community\n\nThe key insight? Consistency beats perfection every time.\n\nWhat's your take? Drop a comment below 👇\n\n#ContentMarketing #GrowthHacking`,
      tweet_thread: `🧵 Thread: ${topic}\n\nMost people get this wrong. Here's what actually works 👇\n\n1/5 The first thing to understand is that this isn't about luck.\n\n2/5 When you focus on the fundamentals, everything else falls into place.\n\n3/5 The biggest mistake? Trying to do everything at once.\n\n4/5 Start small, measure, iterate. That's the playbook.\n\n5/5 If this was helpful, RT and follow for more.`,
      article: `# ${topic}: The Complete Guide\n\n## Introduction\nHere's everything you need to know about ${topic}...\n\n## Key Insights\n1. Understanding the basics\n2. Advanced strategies\n3. Common pitfalls to avoid\n\n## Conclusion\nStart implementing these strategies today.`,
      carousel: `Slide 1: ${topic} — A Complete Guide\nSlide 2: Why This Matters\nSlide 3: The Problem\nSlide 4: The Solution\nSlide 5: Key Takeaways\nSlide 6: CTA — Save & Share`,
      reel: `[Scene 1] Text: "POV: You finally understand ${topic}"\n[Scene 2] Quick tips flying in\n[Scene 3] CTA: Save this! 📌`,
      short_video: `[HOOK] Stop scrolling!\nHere's what I learned about ${topic}\n[CONTENT] Tip 1...\nTip 2...\nTip 3...\n[CTA] Follow for more!`,
      image: `Create a bold, modern social media graphic about "${topic}". Style: clean typography, vibrant gradient background, minimal design. Include the headline text prominently.`,
      email: `Subject: The ${topic} Playbook\n\nHi [Name],\n\nThis week I want to share something about ${topic} that changed how I think.\n\nThe core insight: [Key insight]\n\nHere's the 3-step framework:\nStep 1: Foundation\nStep 2: Execution\nStep 3: Optimization\n\nTry this out and let me know how it goes.\n\nBest,\n[Your Name]`,
    }
    return placeholders[type] || `Generated ${type} content about ${topic} with ${tn} tone.`
  }

  const copyContent = () => {
    if (result?.content) {
      navigator.clipboard.writeText(result.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const providers = Object.keys(allModels)
  const currentModels = allModels[selectedProvider]?.models || []

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
          {/* Saved Idea Banner */}
          {savedIdea && (
            <div className="rounded-lg border border-green-200 bg-green-50 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-green-800">Idea loaded: {savedIdea.title}</p>
                  <p className="text-xs text-green-600 truncate max-w-md">{savedIdea.description}</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={onClearIdea}><X className="h-4 w-4" /></Button>
            </div>
          )}

          {/* Content Type Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium">Content Type *</label>
            <div className="grid grid-cols-4 gap-2">
              {CONTENT_TYPES.map((ct) => {
                const Icon = ct.icon
                return (
                  <button key={ct.id} onClick={() => setContentType(ct.id)}
                    className={`flex flex-col items-center gap-1 rounded-lg border p-3 text-xs font-medium transition-all ${contentType === ct.id ? "border-primary bg-primary/10 text-primary ring-2 ring-primary/20" : "bg-background hover:bg-muted"}`}>
                    <Icon className="h-5 w-5" /> {ct.label}
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
                    className={`flex-1 rounded-lg border px-2 py-1.5 text-xs font-medium ${length === l ? "border-primary bg-primary/10 text-primary" : "bg-background"}`}>
                    {l}
                  </button>
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
            <textarea className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring" rows={3}
              placeholder="Extra context: include a specific example, reference a competitor, target a sub-audience..." value={customPrompt} onChange={(e) => setCustomPrompt(e.target.value)} />
          </div>

          {/* Model Selection */}
          <div className="rounded-lg border p-4 space-y-3">
            <label className="text-sm font-medium flex items-center gap-2"><Cpu className="h-4 w-4" /> AI Model</label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs text-muted-foreground">Provider</label>
                <select className="w-full rounded-lg border bg-background p-2 text-sm" value={selectedProvider}
                  onChange={(e) => { setSelectedProvider(e.target.value); setSelectedModel("") }}>
                  {providers.map((p) => <option key={p} value={p}>{allModels[p]?.name || p}</option>)}
                  {providers.length === 0 && <option value="openrouter">OpenRouter (configure API key)</option>}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs text-muted-foreground">Model</label>
                <select className="w-full rounded-lg border bg-background p-2 text-sm" value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}>
                  <option value="">Auto (default)</option>
                  {currentModels.map((m) => <option key={m.id} value={m.id}>{m.name} ({m.cost_tier})</option>)}
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
              <CardTitle className="flex items-center gap-2"><Sparkles className="h-5 w-5 text-primary" /> Generated Content</CardTitle>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={copyContent} className="gap-1">
                  {copied ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
                  {copied ? "Copied" : "Copy"}
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border p-4 bg-muted/30">
              <pre className="whitespace-pre-wrap text-sm font-mono">{result.content}</pre>
            </div>
            {result.hashtags && result.hashtags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {result.hashtags.map((tag, i) => <span key={i} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">{tag}</span>)}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
