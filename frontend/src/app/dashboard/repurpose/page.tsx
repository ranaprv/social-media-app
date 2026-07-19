"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Repeat, Loader2, Copy, Check, Globe, FileText, Video, Mic,
  Image, Scissors, Type, BarChart3, BookOpen, ArrowRight, Save,
  ChevronDown, X,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

type RepurposeMode = "micro-content" | "text-to-carousel" | "visual-to-text" | "audio-to-written"

interface ModeConfig {
  id: RepurposeMode
  label: string
  description: string
  icon: React.ElementType
  inputLabel: string
  inputPlaceholder: string
  outputs: string[]
  color: string
}

const MODES: ModeConfig[] = [
  {
    id: "micro-content",
    label: "Micro-Content from Long-Form",
    description: "Slice long videos/podcasts into 30-60s clips for Reels, Shorts, and Stories",
    icon: Scissors,
    inputLabel: "Video/Podcast URL or Description",
    inputPlaceholder: "Paste YouTube URL or describe the long-form content...",
    outputs: ["Instagram Reel Script", "YouTube Short Script", "TikTok Script", "Story Script"],
    color: "bg-purple-50 border-purple-200",
  },
  {
    id: "text-to-carousel",
    label: "Text to Carousels",
    description: "Convert threads, blog posts, or text into swipeable image carousels",
    icon: Image,
    inputLabel: "Text Content (thread, blog, or notes)",
    inputPlaceholder: "Paste a Twitter thread, blog paragraph, or notes...",
    outputs: ["Instagram Carousel (10 slides)", "LinkedIn Carousel (8 slides)", "Twitter Thread", "Blog Summary"],
    color: "bg-blue-50 border-blue-200",
  },
  {
    id: "visual-to-text",
    label: "Visual Data to Text",
    description: "Turn statistics into infographics, case studies into compelling posts",
    icon: BarChart3,
    inputLabel: "Data, Stats, or Case Study",
    inputPlaceholder: "Paste statistics, data points, or case study details...",
    outputs: ["LinkedIn Thought Leadership", "Instagram Infographic Copy", "Blog Post", "Newsletter Section"],
    color: "bg-green-50 border-green-200",
  },
  {
    id: "audio-to-written",
    label: "Audio to Written",
    description: "Transcribe podcasts/streams into newsletters, blog posts, and threads",
    icon: BookOpen,
    inputLabel: "Podcast/Stream Transcript or URL",
    inputPlaceholder: "Paste transcript or describe the audio content...",
    outputs: ["Email Newsletter", "Blog Post", "LinkedIn Article", "Twitter Thread", "Key Takeaways List"],
    color: "bg-amber-50 border-amber-200",
  },
]

const PLATFORMS = [
  { id: "linkedin", name: "LinkedIn", color: "text-blue-600" },
  { id: "instagram", name: "Instagram", color: "text-pink-500" },
  { id: "youtube", name: "YouTube", color: "text-red-600" },
  { id: "x", name: "X (Twitter)", color: "text-gray-900" },
  { id: "facebook", name: "Facebook", color: "text-blue-500" },
]

export default function RepurposePage() {
  const [mode, setMode] = useState<RepurposeMode | null>(null)
  const [input, setInput] = useState("")
  const [tone, setTone] = useState("Professional")
  const [selectedOutputs, setSelectedOutputs] = useState<string[]>([])
  const [results, setResults] = useState<Array<{ title: string; content: string; platform: string }>>([])
  const [loading, setLoading] = useState(false)
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null)
  const [savedToMedia, setSavedToMedia] = useState<number | null>(null)
  const [targetPlatform, setTargetPlatform] = useState("linkedin")

  const currentMode = MODES.find(m => m.id === mode)

  function toggleOutput(output: string) {
    setSelectedOutputs(prev => prev.includes(output) ? prev.filter(o => o !== output) : [...prev, output])
  }

  async function generate() {
    if (!mode || !input.trim() || selectedOutputs.length === 0) return
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/ai/repurpose/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, input, outputs: selectedOutputs, tone, platform: targetPlatform }),
      })
      if (res.ok) {
        const data = await res.json()
        setResults(data.results || [])
      } else {
        setResults(selectedOutputs.map((o, i) => ({ title: o, content: generatePlaceholder(mode, o, input), platform: targetPlatform })))
      }
    } catch {
      setResults(selectedOutputs.map((o, i) => ({ title: o, content: generatePlaceholder(mode, o, input), platform: targetPlatform })))
    }
    setLoading(false)
  }

  function generatePlaceholder(m: RepurposeMode, output: string, inp: string): string {
    const topic = inp.slice(0, 120) || "this content"
    const placeholders: Record<string, Record<string, string>> = {
      "micro-content": {
        "Instagram Reel Script": `[HOOK] Stop scrolling!\nHere's what I learned from ${topic}\n\n[SCENE 1] Text overlay: "The #1 mistake"\n[SCENE 2] Quick tip with b-roll\n[SCENE 3] Key insight reveal\n[SCENE 4] CTA: "Save this!" 📌\n\nDuration: 30-45s | Audio: Trending sound`,
        "YouTube Short Script": `[HOOK - 0:00-0:03] "You NEED to know this about ${topic.slice(0, 50)}"\n\n[TIP 1 - 0:03-0:15] First key insight\n[TIP 2 - 0:15-0:30] Second key insight\n[TIP 3 - 0:30-0:45] Third key insight\n\n[CTA - 0:45-0:60] "Follow for more tips!"`,
        "TikTok Script": `Scene 1: [POV text] "When someone asks about ${topic.slice(0, 40)}"\nScene 2: Quick-fire tips with transitions\nScene 3: "But here's what they don't tell you..."\nScene 4: The real insight\nOutro: "Follow for part 2!"`,
        "Story Script": `Story Slide 1: "Did you know?" + hook\nStory Slide 2: Key stat or insight\nStory Slide 3: "Here's why it matters"\nStory Slide 4: CTA with poll sticker`,
      },
      "text-to-carousel": {
        "Instagram Carousel (10 slides)": `Slide 1: "${topic.slice(0, 40)} — A Thread" (hook)\nSlide 2: The Problem\nSlide 3: Why Most People Get It Wrong\nSlide 4: Key Insight #1\nSlide 5: Key Insight #2\nSlide 6: Key Insight #3\nSlide 7: The Framework\nSlide 8: Action Steps\nSlide 9: Common Mistakes\nSlide 10: CTA — "Save & Share!"`,
        "LinkedIn Carousel (8 slides)": `Slide 1: Bold title slide — "${topic.slice(0, 50)}"\nSlide 2: Context — why this matters now\nSlide 3: Data point or statistic\nSlide 4: The framework breakdown\nSlide 5: Step-by-step process\nSlide 6: Real-world example\nSlide 7: Key takeaways\nSlide 8: "What's your experience? Comment below"`,
        "Twitter Thread": `🧵 Thread: ${topic.slice(0, 60)}\n\n1/8 The hook — why this matters\n2/8 Background context\n3/8 The problem most people face\n4/8 Key insight #1\n5/8 Key insight #2\n6/8 The framework\n7/8 Action steps\n8/8 TL;DR + CTA`,
        "Blog Summary": `# ${topic.slice(0, 60)}\n\n## Key Takeaways\n- Insight 1 from the content\n- Insight 2 with supporting data\n- Insight 3 with actionable advice\n\n## The Deep Dive\n[Expanded analysis of each point]\n\n## What You Can Do Today\n1. Action item 1\n2. Action item 2\n3. Action item 3`,
      },
      "visual-to-text": {
        "LinkedIn Thought Leadership": `I've been analyzing ${topic.slice(0, 60)} and here's what the data shows:\n\n📊 The numbers tell a clear story:\n→ Key stat 1\n→ Key stat 2\n→ Key stat 3\n\nMost people focus on [common approach], but the real opportunity is in [contrarian insight].\n\nHere's my framework for thinking about this:\n1. [Step 1]\n2. [Step 2]\n3. [Step 3]\n\nWhat's your take? I'd love to hear how you approach this.\n\n#${topic.split(" ")[0]} #DataInsights #ThoughtLeadership`,
        "Instagram Infographic Copy": `📊 ${topic.slice(0, 40)} — By The Numbers\n\n✅ Stat 1: [Number]\n✅ Stat 2: [Number]\n✅ Stat 3: [Number]\n\n💡 Key insight: [One-line takeaway]\n\nSave this for your next strategy session! 📌\n\n#${topic.split(" ")[0]} #Infographics #DataVisualization`,
        "Blog Post": `# ${topic.slice(0, 60)}: What The Data Actually Shows\n\nWhen we look at the numbers behind ${topic.slice(0, 40)}, a clear pattern emerges.\n\n## The Stats That Matter\n\nHere are the three most important data points...\n\n## What This Means For You\n\n[Analysis and implications]\n\n## The Action Plan\n\nBased on this data, here's what you should do:\n1. [Step 1]\n2. [Step 2]\n3. [Step 3]`,
        "Newsletter Section": `📊 Data Spotlight: ${topic.slice(0, 40)}\n\nThis week I dug into the numbers and found something interesting.\n\nThe key stat: [Number]\nWhy it matters: [One sentence]\nWhat to do about it: [Action]\n\nWant the full breakdown? [Link]\n\n— [Your Name]`,
      },
      "audio-to-written": {
        "Email Newsletter": `Subject: Key insights from ${topic.slice(0, 40)}\n\nHi [Name],\n\nI just finished analyzing ${topic.slice(0, 50)} and wanted to share the biggest takeaways.\n\n🔑 Key Insight 1: [Summary]\n🔑 Key Insight 2: [Summary]\n🔑 Key Insight 3: [Summary]\n\n💡 My favorite quote: "[Memorable quote from content]"\n\n🎯 Action item: Try [specific thing] this week.\n\nBest,\n[Your Name]`,
        "Blog Post": `# ${topic.slice(0, 60)}: Key Takeaways\n\nI spent time analyzing ${topic.slice(0, 40)} and here are the most valuable insights.\n\n## The Big Ideas\n\n1. **[Insight 1]** — [Explanation]\n2. **[Insight 2]** — [Explanation]\n3. **[Insight 3]** — [Explanation]\n\n## My Take\n\n[Your analysis and opinion]\n\n## What To Do Next\n\n- [Action 1]\n- [Action 2]\n- [Action 3]`,
        "LinkedIn Article": `I just analyzed ${topic.slice(0, 50)} and here are 5 things that stood out:\n\n1/ [First insight with context]\n\n2/ [Second insight with data]\n\n3/ [Third insight with example]\n\n4/ [Fourth insight with contrarian view]\n\n5/ [Fifth insight with action item]\n\nThe biggest lesson: [One-liner takeaway]\n\nAgree or disagree? Let me know in the comments 👇`,
        "Twitter Thread": `🧵 Just analyzed ${topic.slice(0, 40)} — here are the best insights:\n\n1/6 [Hook — why this matters]\n2/6 [First key insight]\n3/6 [Second key insight]\n4/6 [Third key insight]\n5/6 [My contrarian take]\n6/6 [TL;DR + follow for more]`,
        "Key Takeaways List": `📌 Key Takeaways from ${topic.slice(0, 40)}:\n\n1. [Takeaway 1]\n2. [Takeaway 2]\n3. [Takeaway 3]\n4. [Takeaway 4]\n5. [Takeaway 5]\n\n💡 Bonus: [Unexpected insight]\n\nWhich one resonates most?`,
      },
    }
    return placeholders[m]?.[output] || `Repurposed content for ${output} from ${topic}`
  }

  async function saveToMedia(result: { title: string; content: string }, idx: number) {
    try {
      await fetch(`${API_URL}/media/assets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: `${result.title} — repurposed`,
          type: "document",
          url: "",
          platform: targetPlatform,
          content_type: "post",
          tags: ["repurposed", mode],
          size: result.content.length,
        }),
      })
      setSavedToMedia(idx)
      setTimeout(() => setSavedToMedia(null), 2000)
    } catch { /* ignore */ }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Repurposing Engine</h1>
          <p className="text-muted-foreground">Fetch content from the web, enhance and rebrand it, then repurpose into multiple formats.</p>
        </div>

        {/* Mode Selection */}
        {!mode ? (
          <div className="grid gap-4 md:grid-cols-2">
            {MODES.map(m => {
              const Icon = m.icon
              return (
                <Card key={m.id} className={`cursor-pointer transition-all hover:shadow-md ${m.color}`} onClick={() => { setMode(m.id); setSelectedOutputs(m.outputs.slice(0, 3)) }}>
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/80"><Icon className="h-6 w-6 text-primary" /></div>
                      <div>
                        <h3 className="font-semibold text-lg">{m.label}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{m.description}</p>
                        <div className="flex flex-wrap gap-1 mt-3">{m.outputs.map(o => <span key={o} className="rounded-full bg-background/80 px-2 py-0.5 text-[10px] font-medium">{o}</span>)}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        ) : (
          <>
            <Button variant="ghost" size="sm" onClick={() => { setMode(null); setResults([]) }} className="gap-1 self-start">
              ← Back to modes
            </Button>

            {/* Input Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {currentMode && <currentMode.icon className="h-5 w-5 text-primary" />}
                  {currentMode?.label}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium">{currentMode?.inputLabel}</label>
                  {mode === "micro-content" || mode === "audio-to-written" ? (
                    <Input placeholder={currentMode?.inputPlaceholder} value={input} onChange={(e) => setInput(e.target.value)} />
                  ) : (
                    <textarea className="w-full rounded-lg border bg-background p-3 text-sm min-h-[120px]" placeholder={currentMode?.inputPlaceholder} value={input} onChange={(e) => setInput(e.target.value)} />
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="mb-1 block text-xs font-medium">Target Platform</label>
                    <select className="w-full rounded-lg border bg-background p-2 text-sm" value={targetPlatform} onChange={(e) => setTargetPlatform(e.target.value)}>
                      {PLATFORMS.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-medium">Tone</label>
                    <select className="w-full rounded-lg border bg-background p-2 text-sm" value={tone} onChange={(e) => setTone(e.target.value)}>
                      {["Professional", "Casual", "Humorous", "Inspirational", "Educational"].map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="mb-2 block text-xs font-medium">Output Formats ({selectedOutputs.length} selected)</label>
                  <div className="flex flex-wrap gap-2">
                    {currentMode?.outputs.map(o => (
                      <button key={o} onClick={() => toggleOutput(o)} className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${selectedOutputs.includes(o) ? "bg-primary text-primary-foreground" : "border bg-background text-muted-foreground hover:bg-muted"}`}>{o}</button>
                    ))}
                  </div>
                </div>

                <Button onClick={generate} disabled={loading || !input.trim() || selectedOutputs.length === 0} className="w-full gap-2" size="lg">
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Repeat className="h-4 w-4" />}
                  {loading ? "Repurposing..." : `Generate ${selectedOutputs.length} Formats`}
                </Button>
              </CardContent>
            </Card>

            {/* Results */}
            {results.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">{results.length} Formats Generated</h3>
                  <Button variant="ghost" size="sm" onClick={() => navigator.clipboard.writeText(results.map(r => `=== ${r.title} ===\n\n${r.content}`).join("\n\n---\n\n"))}><Copy className="h-4 w-4 mr-1" />Copy All</Button>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  {results.map((r, i) => (
                    <Card key={i}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">{r.title}</span>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => { navigator.clipboard.writeText(r.content); setCopiedIdx(i); setTimeout(() => setCopiedIdx(null), 2000) }}>
                              {copiedIdx === i ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => saveToMedia(r, i)}>
                              {savedToMedia === i ? <Check className="h-4 w-4 text-green-500" /> : <Save className="h-4 w-4" />}
                            </Button>
                          </div>
                        </div>
                        <pre className="whitespace-pre-wrap text-sm text-muted-foreground bg-muted/30 rounded-lg p-3 max-h-[300px] overflow-y-auto font-sans">{r.content}</pre>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  )
}
