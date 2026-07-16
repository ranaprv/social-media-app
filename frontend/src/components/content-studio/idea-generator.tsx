"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Lightbulb, Sparkles, Plus, X, Loader2, Copy, Check, RefreshCw,
  GraduationCap, BookOpen, Newspaper, Megaphone, AlertTriangle,
  GitCompare, TrendingUp, Target, PenTool, Cpu, Vote, Users,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

const CATEGORIES = [
  { value: "educational", label: "Educational", icon: GraduationCap, color: "bg-blue-100 text-blue-700" },
  { value: "tutorials", label: "Tutorials", icon: BookOpen, color: "bg-green-100 text-green-700" },
  { value: "stories", label: "Stories", icon: PenTool, color: "bg-purple-100 text-purple-700" },
  { value: "case-studies", label: "Case Studies", icon: Target, color: "bg-orange-100 text-orange-700" },
  { value: "tips", label: "Tips", icon: Lightbulb, color: "bg-amber-100 text-amber-700" },
  { value: "mistakes", label: "Mistakes", icon: AlertTriangle, color: "bg-red-100 text-red-700" },
  { value: "comparisons", label: "Comparisons", icon: GitCompare, color: "bg-indigo-100 text-indigo-700" },
  { value: "myths", label: "Myths", icon: RefreshCw, color: "bg-teal-100 text-teal-700" },
]

interface Idea {
  id: string
  title: string
  description: string
  category: string
  content_type: string
  platforms: string[]
  estimated_engagement: string
  tags: string[]
  angles: string[]
  vote_count?: number
  voted_by?: string[]
}

interface ModelInfo {
  name: string
  models: { id: string; name: string; cost_tier: string }[]
}

export function IdeaGenerator() {
  const [niche, setNiche] = useState("")
  const [topic, setTopic] = useState("")
  const [customPrompt, setCustomPrompt] = useState("")
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [count, setCount] = useState(10)

  // Model selection
  const [availableModels, setAvailableModels] = useState<Record<string, ModelInfo>>({})
  const [selectedProvider, setSelectedProvider] = useState("openai")
  const [selectedModel, setSelectedModel] = useState("")
  const [selectedProviders, setSelectedProviders] = useState<string[]>([])
  const [useVoting, setUseVoting] = useState(false)

  const [ideas, setIdeas] = useState<Idea[]>([])
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [expandedIdea, setExpandedIdea] = useState<string | null>(null)
  const [method, setMethod] = useState("")
  const [providersUsed, setProvidersUsed] = useState<string[]>([])

  useEffect(() => {
    async function fetchModels() {
      try {
        const res = await fetch(`${API_URL}/ai/ideas/models`)
        if (res.ok) {
          const data = await res.json()
          setAvailableModels(data.models || {})
          // Set default provider
          const providers = Object.keys(data.models || {})
          if (providers.length > 0) setSelectedProvider(providers[0])
        }
      } catch { /* use defaults */ }
    }
    fetchModels()
  }, [])

  const toggleProvider = (p: string) => {
    setSelectedProviders((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    )
  }

  const generateIdeas = async () => {
    if (!niche.trim() && !topic.trim()) return
    setLoading(true)
    try {
      const body: Record<string, unknown> = {
        niche: niche || topic,
        topic,
        count,
        custom_prompt: customPrompt,
      }

      if (useVoting && selectedProviders.length > 1) {
        body.providers = selectedProviders
        body.use_voting = true
      } else {
        body.provider = selectedProvider
        body.model = selectedModel || undefined
      }

      if (selectedCategories.length > 0) {
        body.categories = selectedCategories
      }

      const res = await fetch(`${API_URL}/ai/ideas/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      const data = await res.json()
      setIdeas(data.ideas || [])
      setMethod(data.method || "")
      setProvidersUsed(data.providers_used || data.provider ? [data.provider] : [])
    } catch {
      setIdeas([])
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const providers = Object.keys(availableModels)
  const currentModels = availableModels[selectedProvider]?.models || []

  return (
    <div className="space-y-6">
      {/* Input Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-primary" />
            Niche Idea Generator
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Brainstorm niche-specific content ideas. Focus on a topic, not a broad industry.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Niche/Topic Input */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Niche *</label>
              <Input
                placeholder="e.g. sustainable fashion, keto recipes, indie game dev"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Specific Topic</label>
              <Input
                placeholder="e.g. summer capsule wardrobe on a budget"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Custom Instructions (optional)</label>
            <textarea
              className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              rows={2}
              placeholder="Additional context: trending angle, audience detail, content goal..."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
            />
          </div>

          {/* Model Selection */}
          <div className="rounded-lg border p-4 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                AI Model Selection
              </label>
              {providers.length > 1 && (
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={useVoting}
                    onChange={(e) => {
                      setUseVoting(e.target.checked)
                      if (e.target.checked && selectedProviders.length === 0) {
                        setSelectedProviders(providers.slice(0, 2))
                      }
                    }}
                    className="rounded"
                  />
                  <Vote className="h-3 w-3" />
                  Multi-model voting
                </label>
              )}
            </div>

            {!useVoting ? (
              /* Single model selection */
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs text-muted-foreground">Provider</label>
                  <select
                    className="w-full rounded-lg border bg-background p-2 text-sm"
                    value={selectedProvider}
                    onChange={(e) => {
                      setSelectedProvider(e.target.value)
                      setSelectedModel("")
                    }}
                  >
                    {providers.map((p) => (
                      <option key={p} value={p}>{availableModels[p]?.name || p}</option>
                    ))}
                    {providers.length === 0 && <option value="openai">OpenAI (configure API key)</option>}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs text-muted-foreground">Model</label>
                  <select
                    className="w-full rounded-lg border bg-background p-2 text-sm"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                  >
                    <option value="">Auto (default)</option>
                    {currentModels.map((m) => (
                      <option key={m.id} value={m.id}>{m.name} ({m.cost_tier})</option>
                    ))}
                  </select>
                </div>
              </div>
            ) : (
              /* Multi-model voting */
              <div>
                <label className="mb-2 block text-xs text-muted-foreground">
                  Select 2+ providers to brainstorm and vote
                </label>
                <div className="flex flex-wrap gap-2">
                  {providers.map((p) => (
                    <button
                      key={p}
                      onClick={() => toggleProvider(p)}
                      className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                        selectedProviders.includes(p)
                          ? "bg-primary text-primary-foreground"
                          : "border bg-background hover:bg-muted"
                      }`}
                    >
                      {availableModels[p]?.name || p}
                      {selectedProviders.includes(p) && <Check className="ml-1 inline h-3 w-3" />}
                    </button>
                  ))}
                </div>
                {selectedProviders.length >= 2 && (
                  <p className="mt-2 text-xs text-muted-foreground flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {selectedProviders.length} models will brainstorm. Ideas agreed by multiple models rank higher.
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Categories */}
          <div>
            <label className="mb-2 block text-sm font-medium">Categories</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon
                const active = selectedCategories.includes(cat.value)
                return (
                  <button
                    key={cat.value}
                    onClick={() => setSelectedCategories((prev) =>
                      active ? prev.filter((c) => c !== cat.value) : [...prev, cat.value]
                    )}
                    className={`flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
                      active ? cat.color : "border bg-background text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    <Icon className="h-3 w-3" />
                    {cat.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Count + Generate */}
          <div className="flex items-end gap-4">
            <div className="w-24">
              <label className="mb-1 block text-xs text-muted-foreground">Count</label>
              <Input
                type="number"
                min={1}
                max={20}
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
              />
            </div>
            <Button onClick={generateIdeas} disabled={loading || (!niche && !topic)} className="gap-2">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              Generate Ideas
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {ideas.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-500" />
                Generated Ideas ({ideas.length})
              </CardTitle>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {method === "multi_model_voting" && (
                  <span className="rounded-full bg-primary/10 px-2 py-1 text-primary">
                    <Vote className="mr-1 inline h-3 w-3" />
                    {providersUsed.join(" + ")} voting
                  </span>
                )}
                {method === "single_model" && (
                  <span className="rounded-full bg-muted px-2 py-1">
                    <Cpu className="mr-1 inline h-3 w-3" />
                    {providersUsed[0] || "AI"}
                  </span>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {ideas.map((idea, i) => {
                const isExpanded = expandedIdea === idea.id
                return (
                  <div key={idea.id} className="rounded-lg border p-4 transition-all hover:shadow-sm">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-muted-foreground">#{i + 1}</span>
                          {idea.vote_count !== undefined && idea.vote_count > 0 && (
                            <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                              {idea.vote_count} vote{idea.vote_count > 1 ? "s" : ""}
                              {idea.voted_by && ` (${idea.voted_by.join(", ")})`}
                            </span>
                          )}
                          <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{idea.category}</span>
                          {idea.content_type && (
                            <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">{idea.content_type}</span>
                          )}
                          <span className={`rounded-full px-2 py-0.5 text-xs ${
                            idea.estimated_engagement === "high" ? "bg-green-100 text-green-700" :
                            idea.estimated_engagement === "medium" ? "bg-yellow-100 text-yellow-700" :
                            "bg-gray-100 text-gray-700"
                          }`}>{idea.estimated_engagement}</span>
                        </div>
                        <h4 className="font-medium">{idea.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{idea.description}</p>
                      </div>
                      <div className="flex items-center gap-1 ml-2">
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => copyToClipboard(idea.title, idea.id)}
                        >
                          {copiedId === idea.id ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                        </Button>
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => setExpandedIdea(isExpanded ? null : idea.id)}
                        >
                          {isExpanded ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-3 border-t pt-3 space-y-2">
                        {idea.angles && idea.angles.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-muted-foreground mb-1">Angles:</p>
                            {idea.angles.map((angle, j) => (
                              <p key={j} className="text-sm ml-2">• {angle}</p>
                            ))}
                          </div>
                        )}
                        {idea.platforms && (
                          <div className="flex gap-1">
                            {idea.platforms.map((p) => (
                              <span key={p} className="rounded bg-muted px-2 py-0.5 text-xs capitalize">{p}</span>
                            ))}
                          </div>
                        )}
                        {idea.tags && (
                          <div className="flex flex-wrap gap-1">
                            {idea.tags.map((t, j) => (
                              <span key={j} className="rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">#{t}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
