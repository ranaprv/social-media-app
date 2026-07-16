"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Repeat,
  Loader2,
  Copy,
  Check,
  Globe,
  FileText,
  Video,
  Mic,
  Presentation,
  FileDown,
  FileCode,
  BookOpen,
  Plus,
  X,
  ChevronDown,
} from "lucide-react"
import type { RepurposeInputType, RepurposeOutputType, Platform } from "@/types"

const INPUT_TYPES: { id: RepurposeInputType; label: string; icon: React.ElementType; needsUrl: boolean }[] = [
  { id: "blog-url", label: "Blog URL", icon: Globe, needsUrl: true },
  { id: "website", label: "Website", icon: Globe, needsUrl: true },
  { id: "youtube-video", label: "YouTube Video", icon: Video, needsUrl: true },
  { id: "podcast", label: "Podcast", icon: Mic, needsUrl: true },
  { id: "webinar", label: "Webinar", icon: Presentation, needsUrl: true },
  { id: "pdf", label: "PDF", icon: FileDown, needsUrl: false },
  { id: "docx", label: "DOCX", icon: FileText, needsUrl: false },
  { id: "markdown", label: "Markdown", icon: FileCode, needsUrl: false },
  { id: "github-readme", label: "GitHub README", icon: BookOpen, needsUrl: true },
]

const OUTPUT_TYPES: { id: RepurposeOutputType; label: string; platform: Platform; color: string }[] = [
  { id: "linkedin-post", label: "LinkedIn Post", platform: "linkedin", color: "bg-blue-600" },
  { id: "twitter-thread", label: "X/Twitter Thread", platform: "x", color: "bg-black" },
  { id: "facebook-post", label: "Facebook Post", platform: "facebook", color: "bg-blue-500" },
  { id: "instagram-caption", label: "Instagram Caption", platform: "instagram", color: "bg-gradient-to-r from-purple-500 to-pink-500" },
  { id: "carousel-copy", label: "Carousel Copy", platform: "linkedin", color: "bg-indigo-600" },
  { id: "newsletter", label: "Newsletter", platform: "linkedin", color: "bg-teal-600" },
  { id: "youtube-shorts-script", label: "YouTube Shorts Script", platform: "youtube", color: "bg-red-600" },
  { id: "reel-script", label: "Reel Script", platform: "instagram", color: "bg-pink-600" },
  { id: "email", label: "Email", platform: "linkedin", color: "bg-amber-600" },
]

const TONES = ["Professional", "Casual", "Humorous", "Inspirational", "Educational", "Provocative"]

export function RepurposeEngine() {
  const [inputType, setInputType] = useState<RepurposeInputType>("markdown")
  const [inputUrl, setInputUrl] = useState("")
  const [inputContent, setInputContent] = useState("")
  const [outputTypes, setOutputTypes] = useState<RepurposeOutputType[]>([
    "linkedin-post", "twitter-thread", "instagram-caption",
  ])
  const [tone, setTone] = useState("Professional")
  const [results, setResults] = useState<{ id: string; outputType: RepurposeOutputType; content: string; platform: Platform }[]>([])
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const currentInputConfig = INPUT_TYPES.find((t) => t.id === inputType)

  const toggleOutputType = (id: RepurposeOutputType) => {
    setOutputTypes((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    )
  }

  const generate = async () => {
    if ((!inputContent.trim() && !inputUrl.trim()) || outputTypes.length === 0) return
    setLoading(true)
    try {
      const res = await fetch("/api/ai/repurpose/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_type: inputType,
          input_content: inputContent,
          input_url: inputUrl || undefined,
          output_types: outputTypes,
          tone,
        }),
      })
      const data = await res.json()
      setResults(data.results || [])
    } catch {
      setResults(
        outputTypes.map((ot, i) => ({
          id: `res-${i}`,
          outputType: ot,
          content: generatePlaceholder(ot),
          platform: OUTPUT_TYPES.find((o) => o.id === ot)?.platform || "linkedin",
        }))
      )
    } finally {
      setLoading(false)
    }
  }

  const generatePlaceholder = (ot: RepurposeOutputType): string => {
    const topic = inputContent.slice(0, 100) || "this content"
    const placeholders: Record<string, string> = {
      "linkedin-post": `🚀 Repurposed LinkedIn Post\n\nKey insights from: ${topic}\n\n1. Always lead with value\n2. Back claims with data\n3. End with a question\n\nWhat's your experience? 👇\n\n#ContentCreation #GrowthHacking`,
      "twitter-thread": `🧵 Thread: Key takeaways\n\n${topic}\n\n1/4 The first insight is about consistency...\n\n2/4 Second, data beats opinions...\n\n3/4 Third, your audience tells you what they want...\n\n4/4 The takeaway: focus on what works and double down.`,
      "facebook-post": `Hey! 👋\n\nJust analyzed: ${topic}\n\nHere's what stood out:\n💡 Key insight #1\n📊 Data point #2\n🎯 Actionable tip #3\n\nWhat do you think? Let's discuss! 💬`,
      "instagram-caption": `✨ Key Takeaways ✨\n\nFrom analyzing: ${topic}\n\n📌 Save this for later!\n\n1️⃣ Insight one\n2️⃣ Insight two\n3️⃣ Insight three\n\nDouble tap if you agree! ❤️\n\n#ContentCreator #SocialMediaTips`,
      "carousel-copy": `Slide 1: Title Slide\nSlide 2: The Problem\nSlide 3: Key Insight from ${topic}\nSlide 4: The Solution\nSlide 5: Action Steps\nSlide 6: CTA — Save & Share`,
      "newsletter": `Subject: This Week's Key Insight\n\nHi [Name],\n\nThis week I analyzed: ${topic}\n\nThe biggest takeaway:\n[Key insight here]\n\nTry this framework this week.\n\nBest,\n[Your Name]`,
      "youtube-shorts-script": `[HOOK] Stop scrolling!\nHere's what I learned from ${topic}\n\n[CONTENT]\nTip 1...\nTip 2...\nTip 3...\n\n[CTA] Follow for more!`,
      "reel-script": `[Scene 1] Text: "POV: Analyzing ${topic}"\n[Scene 2] Quick tips flying in\n[Scene 3] CTA: Save this! 📌`,
      "email": `Subject: Quick insight on ${topic}\n\nHi [Name],\n\nWanted to share: ${topic.slice(0, 50)}...\n\nKey takeaway: [Insight]\n\nBest,\n[Your Name]`,
    }
    return placeholders[ot] || `Repurposed content for ${ot}`
  }

  const copyResult = (id: string, content: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Repeat className="h-5 w-5 text-primary" />
            AI Repurposing Engine
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Transform one piece of content into multiple platform-specific formats.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Input Type */}
          <div>
            <label className="text-sm font-medium mb-2 block">Input Source</label>
            <div className="flex gap-2 flex-wrap">
              {INPUT_TYPES.map((t) => {
                const Icon = t.icon
                return (
                  <button
                    key={t.id}
                    onClick={() => setInputType(t.id)}
                    className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                      inputType === t.id
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {t.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* URL or Content Input */}
          {currentInputConfig?.needsUrl ? (
            <div>
              <label className="text-sm font-medium mb-1.5 block">URL</label>
              <Input
                placeholder={`Enter ${currentInputConfig.label.toLowerCase()} URL...`}
                value={inputUrl}
                onChange={(e) => setInputUrl(e.target.value)}
                type="url"
              />
            </div>
          ) : (
            <div>
              <label className="text-sm font-medium mb-1.5 block">Paste Content</label>
              <textarea
                className="flex min-h-[120px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Paste your content here..."
                value={inputContent}
                onChange={(e) => setInputContent(e.target.value)}
              />
            </div>
          )}

          {/* Output Types */}
          <div>
            <label className="text-sm font-medium mb-2 block">
              Output Formats ({outputTypes.length} selected)
            </label>
            <div className="grid grid-cols-3 gap-2">
              {OUTPUT_TYPES.map((ot) => (
                <button
                  key={ot.id}
                  onClick={() => toggleOutputType(ot.id)}
                  className={`flex items-center gap-2 rounded-lg border p-2.5 text-xs font-medium transition-all ${
                    outputTypes.includes(ot.id)
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-transparent bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  <span className={`w-2.5 h-2.5 rounded-full ${ot.color}`} />
                  {ot.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tone */}
          <div>
            <label className="text-sm font-medium mb-2 block">Tone</label>
            <div className="flex gap-1.5 flex-wrap">
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

          <Button
            onClick={generate}
            disabled={loading || ((!inputContent.trim() && !inputUrl.trim()) || outputTypes.length === 0)}
            className="w-full gap-2"
            size="lg"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Repeat className="h-4 w-4" />}
            {loading ? "Repurposing..." : `Repurpose into ${outputTypes.length} Formats`}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">{results.length} Formats Generated</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                const all = results.map((r) => {
                  const label = OUTPUT_TYPES.find((o) => o.id === r.outputType)?.label || r.outputType
                  return `=== ${label} ===\n\n${r.content}`
                }).join("\n\n---\n\n")
                navigator.clipboard.writeText(all)
              }}
            >
              <Copy className="h-4 w-4 mr-1.5" />
              Copy All
            </Button>
          </div>

          <div className="grid gap-3">
            {results.map((result) => {
              const config = OUTPUT_TYPES.find((o) => o.id === result.outputType)
              const isExpanded = expandedId === result.id

              return (
                <Card
                  key={result.id}
                  className="cursor-pointer transition-all hover:shadow-md"
                  onClick={() => setExpandedId(isExpanded ? null : result.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className={`inline-block w-2.5 h-2.5 rounded-full ${config?.color || "bg-gray-400"}`} />
                          <span className="text-xs font-medium text-muted-foreground">
                            {config?.label || result.outputType}
                          </span>
                        </div>
                        <div className={`whitespace-pre-wrap text-sm leading-relaxed ${isExpanded ? "" : "line-clamp-3"}`}>
                          {result.content}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 flex-shrink-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          copyResult(result.id, result.content)
                        }}
                      >
                        {copiedId === result.id ? (
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
