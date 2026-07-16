"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  BookOpen,
  Plus,
  X,
  Loader2,
  Check,
  Globe,
  FileText,
  Mail,
  Link2,
  Upload,
  Brain,
  Sparkles,
  Save,
} from "lucide-react"

interface BrandVoiceSource {
  id: string
  type: "url" | "pdf" | "document" | "website" | "posts" | "newsletter"
  value: string
  label: string
  status: "pending" | "processing" | "completed" | "failed"
}

interface BrandVoiceProfile {
  tone: string
  writingStyle: string
  ctaStyle: string
  emojiUsage: string
  formatting: string
  vocabulary: string
  technicalDepth: string
  samplePosts: string[]
}

const SOURCE_TYPES: {
  value: BrandVoiceSource["type"]
  label: string
  icon: React.ElementType
  placeholder: string
}[] = [
  { value: "website", label: "Website", icon: Globe, placeholder: "https://yourcompany.com/blog" },
  { value: "url", label: "Blog URL", icon: Link2, placeholder: "https://blog.example.com/post" },
  { value: "posts", label: "Previous Posts", icon: FileText, placeholder: "Paste your previous posts..." },
  { value: "newsletter", label: "Newsletter", icon: Mail, placeholder: "Paste newsletter content..." },
  { value: "pdf", label: "PDF", icon: Upload, placeholder: "Upload or paste PDF content..." },
  { value: "document", label: "Word Doc", icon: FileText, placeholder: "Paste document content..." },
]

export function BrandVoiceConfig() {
  const [sources, setSources] = useState<BrandVoiceSource[]>([])
  const [sourceType, setSourceType] = useState<BrandVoiceSource["type"]>("website")
  const [sourceValue, setSourceValue] = useState("")
  const [sourceLabel, setSourceLabel] = useState("")

  const [profile, setProfile] = useState<BrandVoiceProfile>({
    tone: "",
    writingStyle: "",
    ctaStyle: "",
    emojiUsage: "",
    formatting: "",
    vocabulary: "",
    technicalDepth: "",
    samplePosts: [],
  })

  const [newSamplePost, setNewSamplePost] = useState("")
  const [analyzing, setAnalyzing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const addSource = () => {
    if (!sourceValue.trim()) return
    const newSource: BrandVoiceSource = {
      id: `src-${Date.now()}`,
      type: sourceType,
      value: sourceValue.trim(),
      label: sourceLabel.trim() || sourceValue.trim().slice(0, 50),
      status: "pending",
    }
    setSources([...sources, newSource])
    setSourceValue("")
    setSourceLabel("")
  }

  const removeSource = (id: string) => {
    setSources(sources.filter((s) => s.id !== id))
  }

  const analyzeSources = async () => {
    if (sources.length === 0) return
    setAnalyzing(true)
    try {
      // Mark sources as processing
      setSources((prev) =>
        prev.map((s) => ({ ...s, status: "processing" as const }))
      )

      // Simulate analysis (in real app, would call API)
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Generate placeholder profile based on sources
      const websiteSource = sources.find((s) => s.type === "website" || s.type === "url")
      const brandName = websiteSource
        ? new URL(websiteSource.value).hostname.replace("www.", "").split(".")[0]
        : "your brand"

      setProfile({
        tone: `Professional yet approachable. Confident without being arrogant. Uses a ${brandName} voice that speaks directly to the reader.`,
        writingStyle: "Conversational and clear. Uses short paragraphs, bullet points, and clear headers. Mixes storytelling with data-driven insights.",
        ctaStyle: "Direct and value-focused. Uses questions to engage, creates urgency without being pushy, and offers clear next steps.",
        emojiUsage: "Strategic and minimal. Uses 1-3 emojis per post maximum. Emojis serve a purpose (emphasis, section breaks) rather than decoration.",
        formatting: "Short paragraphs (2-3 sentences). Bullet points for lists. Bold for emphasis. Clear section headers. White space for readability.",
        vocabulary: "Industry-specific terms with accessible explanations. Avoids jargon without context. Uses active voice predominantly.",
        technicalDepth: "Medium — explains complex concepts in simple terms. Provides enough depth for experts while remaining accessible to newcomers.",
        samplePosts: profile.samplePosts,
      })

      // Mark sources as completed
      setSources((prev) =>
        prev.map((s) => ({ ...s, status: "completed" as const }))
      )
    } catch {
      setSources((prev) =>
        prev.map((s) => ({ ...s, status: "failed" as const }))
      )
    } finally {
      setAnalyzing(false)
    }
  }

  const addSamplePost = () => {
    if (newSamplePost.trim()) {
      setProfile((prev) => ({
        ...prev,
        samplePosts: [...prev.samplePosts, newSamplePost.trim()],
      }))
      setNewSamplePost("")
    }
  }

  const saveProfile = async () => {
    setSaving(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  const statusColors = {
    pending: "bg-yellow-100 text-yellow-700",
    processing: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  }

  return (
    <div className="space-y-6">
      {/* Training Sources */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-accent" />
            Brand Voice Training
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Upload sources to train AI on your brand voice. Add websites, posts, newsletters, or documents.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Add Source Form */}
          <div className="rounded-lg border p-4 space-y-3">
            <div className="flex gap-2 flex-wrap">
              {SOURCE_TYPES.map((st) => {
                const Icon = st.icon
                return (
                  <button
                    key={st.value}
                    onClick={() => {
                      setSourceType(st.value)
                      setSourceValue("")
                      setSourceLabel("")
                    }}
                    className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                      sourceType === st.value
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {st.label}
                  </button>
                )
              })}
            </div>

            <Input
              placeholder={SOURCE_TYPES.find((s) => s.value === sourceType)?.placeholder}
              value={sourceValue}
              onChange={(e) => setSourceValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  addSource()
                }
              }}
            />

            <div className="flex gap-2">
              <Input
                placeholder="Label (optional)"
                value={sourceLabel}
                onChange={(e) => setSourceLabel(e.target.value)}
                className="flex-1"
              />
              <Button onClick={addSource} disabled={!sourceValue.trim()} size="sm" className="gap-1.5">
                <Plus className="h-3.5 w-3.5" />
                Add Source
              </Button>
            </div>
          </div>

          {/* Source List */}
          {sources.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium">{sources.length} Training Sources</h4>
                <Button
                  onClick={analyzeSources}
                  disabled={analyzing}
                  size="sm"
                  className="gap-1.5"
                  variant="secondary"
                >
                  {analyzing ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Brain className="h-3.5 w-3.5" />
                  )}
                  {analyzing ? "Analyzing..." : "Analyze Sources"}
                </Button>
              </div>

              {sources.map((source) => {
                const sourceTypeConfig = SOURCE_TYPES.find((s) => s.value === source.type)
                const Icon = sourceTypeConfig?.icon || Globe
                return (
                  <div
                    key={source.id}
                    className="flex items-center gap-3 rounded-lg border p-3"
                  >
                    <Icon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{source.label}</p>
                      <p className="text-xs text-muted-foreground truncate">{source.value}</p>
                    </div>
                    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${statusColors[source.status]}`}>
                      {source.status}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => removeSource(source.id)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                )
              })}
            </div>
          )}

          {/* Sample Posts */}
          <div>
            <label className="text-sm font-medium mb-2 block">Sample Posts (Optional)</label>
            <p className="text-xs text-muted-foreground mb-2">
              Add examples of your best-performing content to help AI learn your style.
            </p>
            <div className="flex gap-2">
              <textarea
                className="flex min-h-[80px] flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Paste a sample post..."
                value={newSamplePost}
                onChange={(e) => setNewSamplePost(e.target.value)}
              />
              <Button
                onClick={addSamplePost}
                disabled={!newSamplePost.trim()}
                variant="outline"
                size="icon"
                className="self-end"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {profile.samplePosts.length > 0 && (
              <div className="space-y-2 mt-3">
                {profile.samplePosts.map((post, i) => (
                  <div key={i} className="flex items-start gap-2 rounded-lg bg-muted/50 p-3">
                    <p className="text-xs text-muted-foreground flex-1 whitespace-pre-wrap">{post}</p>
                    <button
                      onClick={() =>
                        setProfile((prev) => ({
                          ...prev,
                          samplePosts: prev.samplePosts.filter((_, idx) => idx !== i),
                        }))
                      }
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Brand Voice Profile */}
      {(profile.tone || sources.some((s) => s.status === "completed")) && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-primary" />
                Brand Voice Profile
              </CardTitle>
              <Button onClick={saveProfile} disabled={saving} size="sm" className="gap-1.5">
                {saving ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : saved ? (
                  <Check className="h-3.5 w-3.5" />
                ) : (
                  <Save className="h-3.5 w-3.5" />
                )}
                {saved ? "Saved!" : "Save Profile"}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { key: "tone", label: "Tone", value: profile.tone },
              { key: "writingStyle", label: "Writing Style", value: profile.writingStyle },
              { key: "ctaStyle", label: "CTA Style", value: profile.ctaStyle },
              { key: "emojiUsage", label: "Emoji Usage", value: profile.emojiUsage },
              { key: "formatting", label: "Formatting", value: profile.formatting },
              { key: "vocabulary", label: "Vocabulary", value: profile.vocabulary },
              { key: "technicalDepth", label: "Technical Depth", value: profile.technicalDepth },
            ].map((field) => (
              <div key={field.key}>
                <label className="text-xs font-medium text-muted-foreground mb-1 block">
                  {field.label}
                </label>
                <textarea
                  className="flex min-h-[60px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={field.value}
                  onChange={(e) =>
                    setProfile((prev) => ({
                      ...prev,
                      [field.key]: e.target.value,
                    }))
                  }
                  placeholder={`Describe your ${field.label.toLowerCase()}...`}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
