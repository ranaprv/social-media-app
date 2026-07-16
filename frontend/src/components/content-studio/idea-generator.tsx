"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Lightbulb,
  Sparkles,
  Plus,
  X,
  Loader2,
  Copy,
  Check,
  BookOpen,
  GraduationCap,
  Newspaper,
  Megaphone,
  AlertTriangle,
  GitCompare,
  TrendingUp,
  Target,
  PenTool,
  RefreshCw,
} from "lucide-react"
import type { GeneratedIdea, IdeaCategory, Platform } from "@/types"

const CATEGORIES: { value: IdeaCategory; label: string; icon: React.ElementType; color: string }[] = [
  { value: "educational", label: "Educational", icon: GraduationCap, color: "bg-blue-100 text-blue-700" },
  { value: "tutorials", label: "Tutorials", icon: BookOpen, color: "bg-green-100 text-green-700" },
  { value: "stories", label: "Stories", icon: PenTool, color: "bg-purple-100 text-purple-700" },
  { value: "case-studies", label: "Case Studies", icon: Target, color: "bg-orange-100 text-orange-700" },
  { value: "product-updates", label: "Product Updates", icon: Megaphone, color: "bg-cyan-100 text-cyan-700" },
  { value: "industry-news", label: "Industry News", icon: Newspaper, color: "bg-yellow-100 text-yellow-700" },
  { value: "personal-branding", label: "Personal Branding", icon: TrendingUp, color: "bg-pink-100 text-pink-700" },
  { value: "tips", label: "Tips", icon: Lightbulb, color: "bg-amber-100 text-amber-700" },
  { value: "mistakes", label: "Mistakes", icon: AlertTriangle, color: "bg-red-100 text-red-700" },
  { value: "comparisons", label: "Comparisons", icon: GitCompare, color: "bg-indigo-100 text-indigo-700" },
  { value: "myths", label: "Myths", icon: RefreshCw, color: "bg-teal-100 text-teal-700" },
]

const PLATFORM_COLORS: Record<Platform, string> = {
  linkedin: "bg-blue-600",
  x: "bg-black",
  instagram: "bg-gradient-to-r from-purple-500 to-pink-500",
  facebook: "bg-blue-500",
  youtube: "bg-red-600",
}

export function IdeaGenerator() {
  const [industry, setIndustry] = useState("")
  const [keywords, setKeywords] = useState<string[]>([])
  const [keywordInput, setKeywordInput] = useState("")
  const [audience, setAudience] = useState("")
  const [competitors, setCompetitors] = useState<string[]>([])
  const [competitorInput, setCompetitorInput] = useState("")
  const [products, setProducts] = useState<string[]>([])
  const [productInput, setProductInput] = useState("")
  const [websiteUrl, setWebsiteUrl] = useState("")
  const [selectedCategories, setSelectedCategories] = useState<IdeaCategory[]>([])
  const [ideas, setIdeas] = useState<GeneratedIdea[]>([])
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [expandedIdea, setExpandedIdea] = useState<string | null>(null)

  const addToList = (
    value: string,
    list: string[],
    setter: (v: string[]) => void,
    inputSetter: (v: string) => void,
  ) => {
    if (value.trim() && !list.includes(value.trim())) {
      setter([...list, value.trim()])
      inputSetter("")
    }
  }

  const removeFromList = (
    index: number,
    list: string[],
    setter: (v: string[]) => void,
  ) => {
    setter(list.filter((_, i) => i !== index))
  }

  const toggleCategory = (cat: IdeaCategory) => {
    setSelectedCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    )
  }

  const generateIdeas = async () => {
    if (!industry.trim()) return
    setLoading(true)
    try {
      const res = await fetch("/api/ai/ideas/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          industry,
          keywords,
          audience,
          competitors,
          products,
          website_url: websiteUrl || null,
          count: 10,
          categories: selectedCategories.length > 0 ? selectedCategories : undefined,
        }),
      })
      const data = await res.json()
      setIdeas(data.ideas || [])
    } catch {
      // Generate client-side placeholder
      setIdeas(generatePlaceholderIdeas())
    } finally {
      setLoading(false)
    }
  }

  const generatePlaceholderIdeas = (): GeneratedIdea[] => {
    const templates = [
      { title: `How ${industry} is Changing in 2026`, category: "educational" as IdeaCategory, engagement: "high" as const },
      { title: `Top 5 Mistakes in ${industry}`, category: "mistakes" as IdeaCategory, engagement: "high" as const },
      { title: `${keywords[0] || "Topic"}: Everything You Need to Know`, category: "tutorials" as IdeaCategory, engagement: "medium" as const },
      { title: `Case Study: How We Grew with ${keywords[0] || "Strategy"}`, category: "case-studies" as IdeaCategory, engagement: "high" as const },
      { title: `Myths About ${keywords[0] || industry} Debunked`, category: "myths" as IdeaCategory, engagement: "medium" as const },
      { title: `Quick Tips for ${keywords[0] || "Beginners"} in ${industry}`, category: "tips" as IdeaCategory, engagement: "medium" as const },
      { title: `${keywords[0] || "Tool A"} vs ${keywords[1] || "Tool B"}: Which is Better?`, category: "comparisons" as IdeaCategory, engagement: "medium" as const },
      { title: `Behind the Scenes: Our ${industry} Journey`, category: "stories" as IdeaCategory, engagement: "low" as const },
      { title: `What's New in ${industry} This Month`, category: "industry-news" as IdeaCategory, engagement: "low" as const },
      { title: `Building Your Personal Brand in ${industry}`, category: "personal-branding" as IdeaCategory, engagement: "medium" as const },
    ]

    return templates.map((t, i) => ({
      id: `idea-${i}`,
      title: t.title,
      description: `Create engaging ${t.category} content about ${keywords[0] || industry} targeting ${audience || "professionals"}.`,
      category: t.category,
      platforms: ["linkedin", "x"] as Platform[],
      estimatedEngagement: t.engagement,
      tags: [keywords[0] || industry, t.category],
    }))
  }

  const copyIdea = (idea: GeneratedIdea) => {
    navigator.clipboard.writeText(`${idea.title}\n\n${idea.description}`)
    setCopiedId(idea.id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-amber-500" />
            AI Idea Generator
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Generate content ideas tailored to your industry, audience, and goals.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Industry */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Industry *</label>
            <Input
              placeholder="e.g., SaaS, E-commerce, Health Tech, Finance"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            />
          </div>

          {/* Keywords */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Keywords</label>
            <div className="flex gap-2">
              <Input
                placeholder="Add a keyword and press Enter"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    addToList(keywordInput, keywords, setKeywords, setKeywordInput)
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => addToList(keywordInput, keywords, setKeywords, setKeywordInput)}
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
                    <button onClick={() => removeFromList(i, keywords, setKeywords)}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Audience */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Target Audience</label>
            <Input
              placeholder="e.g., CTOs, Marketing Managers, Startup Founders"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
            />
          </div>

          {/* Competitors */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Competitors</label>
            <div className="flex gap-2">
              <Input
                placeholder="Add competitor name"
                value={competitorInput}
                onChange={(e) => setCompetitorInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    addToList(competitorInput, competitors, setCompetitors, setCompetitorInput)
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => addToList(competitorInput, competitors, setCompetitors, setCompetitorInput)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {competitors.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {competitors.map((c, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-full bg-secondary/10 px-2.5 py-0.5 text-xs font-medium text-secondary"
                  >
                    {c}
                    <button onClick={() => removeFromList(i, competitors, setCompetitors)}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Products */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Products / Services</label>
            <div className="flex gap-2">
              <Input
                placeholder="Add product or service"
                value={productInput}
                onChange={(e) => setProductInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    addToList(productInput, products, setProducts, setProductInput)
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => addToList(productInput, products, setProducts, setProductInput)}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {products.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {products.map((p, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-full bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent"
                  >
                    {p}
                    <button onClick={() => removeFromList(i, products, setProducts)}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Website URL */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Website URL</label>
            <Input
              placeholder="https://yourcompany.com"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              type="url"
            />
          </div>

          {/* Category Filter */}
          <div>
            <label className="text-sm font-medium mb-2 block">Filter by Categories</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon
                const isSelected = selectedCategories.includes(cat.value)
                return (
                  <button
                    key={cat.value}
                    onClick={() => toggleCategory(cat.value)}
                    className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                      isSelected
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {cat.label}
                  </button>
                )
              })}
            </div>
          </div>

          <Button
            onClick={generateIdeas}
            disabled={!industry.trim() || loading}
            className="w-full gap-2"
            size="lg"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {loading ? "Generating Ideas..." : "Generate Ideas"}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {ideas.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">{ideas.length} Ideas Generated</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                const all = ideas.map((i) => `${i.title}\n${i.description}`).join("\n\n---\n\n")
                navigator.clipboard.writeText(all)
              }}
            >
              <Copy className="h-4 w-4 mr-1.5" />
              Copy All
            </Button>
          </div>

          <div className="grid gap-3">
            {ideas.map((idea) => {
              const catInfo = CATEGORIES.find((c) => c.value === idea.category)
              const CatIcon = catInfo?.icon || Lightbulb
              const isExpanded = expandedIdea === idea.id

              return (
                <Card
                  key={idea.id}
                  className="cursor-pointer transition-all hover:shadow-md"
                  onClick={() => setExpandedIdea(isExpanded ? null : idea.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${catInfo?.color || "bg-gray-100 text-gray-700"}`}>
                            <CatIcon className="h-3 w-3" />
                            {catInfo?.label || idea.category}
                          </span>
                          <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                            idea.estimatedEngagement === "high"
                              ? "bg-green-100 text-green-700"
                              : idea.estimatedEngagement === "medium"
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-gray-100 text-gray-600"
                          }`}>
                            {idea.estimatedEngagement} engagement
                          </span>
                        </div>
                        <h4 className="font-medium text-sm">{idea.title}</h4>
                        {isExpanded && (
                          <p className="text-sm text-muted-foreground mt-2">{idea.description}</p>
                        )}
                        {isExpanded && idea.platforms.length > 0 && (
                          <div className="flex gap-1.5 mt-2">
                            {idea.platforms.map((p) => (
                              <span
                                key={p}
                                className={`inline-block w-5 h-5 rounded-full ${PLATFORM_COLORS[p]} opacity-80`}
                                title={p}
                              />
                            ))}
                          </div>
                        )}
                        {isExpanded && idea.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {idea.tags.map((tag, i) => (
                              <span key={i} className="text-xs text-muted-foreground bg-muted rounded px-1.5 py-0.5">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 flex-shrink-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          copyIdea(idea)
                        }}
                      >
                        {copiedId === idea.id ? (
                          <Check className="h-4 w-4 text-green-500" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
