"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Image as ImageIcon,
  Video,
  Mic,
  Type,
  Sparkles,
  Copy,
  Check,
  Loader2,
  Play,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

type Tab = "image" | "video" | "voiceover" | "caption"

const tabs: { id: Tab; label: string; icon: typeof ImageIcon }[] = [
  { id: "image", label: "Image Generator", icon: ImageIcon },
  { id: "video", label: "Video Generator", icon: Video },
  { id: "voiceover", label: "Voiceover", icon: Mic },
  { id: "caption", label: "Caption Generator", icon: Type },
]

const assetTypes = [
  { id: "social-graphic", label: "Social Graphic", dimensions: "1080x1080" },
  { id: "carousel-image", label: "Carousel Image", dimensions: "1080x1350" },
  { id: "infographic", label: "Infographic", dimensions: "1080x1920" },
  { id: "quote-card", label: "Quote Card", dimensions: "1080x1080" },
  { id: "youtube-thumbnail", label: "YouTube Thumbnail", dimensions: "1280x720" },
]

const videoTypes = [
  { id: "reel", label: "Reel", dimensions: "1080x1920" },
  { id: "short", label: "YouTube Short", dimensions: "1080x1920" },
]

const styles = [
  "Modern Minimalist", "Bold & Vibrant", "Professional Corporate",
  "Warm & Friendly", "Dark & Sleek", "Retro Vintage", "Gradient Glow",
  "Neon & Electric", "Clean & Airy", "Editorial",
]

const voices = [
  { id: "alloy", label: "Alloy", gender: "neutral" },
  { id: "echo", label: "Echo", gender: "male" },
  { id: "fable", label: "Fable", gender: "male" },
  { id: "onyx", label: "Onyx", gender: "male" },
  { id: "nova", label: "Nova", gender: "female" },
  { id: "shimmer", label: "Shimmer", gender: "female" },
]

export default function AIAssistantPage() {
  const [activeTab, setActiveTab] = useState<Tab>("image")
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  // Image state
  const [imagePrompt, setImagePrompt] = useState("")
  const [imageAssetType, setImageAssetType] = useState("social-graphic")
  const [imageStyle, setImageStyle] = useState("Modern Minimalist")
  const [imageResult, setImageResult] = useState<Record<string, unknown> | null>(null)

  // Video state
  const [videoPrompt, setVideoPrompt] = useState("")
  const [videoAssetType, setVideoAssetType] = useState("reel")
  const [videoDuration, setVideoDuration] = useState(15)
  const [videoStyle, setVideoStyle] = useState("Modern Minimalist")
  const [videoResult, setVideoResult] = useState<Record<string, unknown> | null>(null)

  // Voiceover state
  const [voText, setVoText] = useState("")
  const [voVoice, setVoVoice] = useState("alloy")
  const [voSpeed, setVoSpeed] = useState(1.0)
  const [voResult, setVoResult] = useState<Record<string, unknown> | null>(null)

  // Caption state
  const [captionPlatform, setCaptionPlatform] = useState("instagram")
  const [captionTopic, setCaptionTopic] = useState("")
  const [captionTone, setCaptionTone] = useState("engaging")
  const [captionEmojis, setCaptionEmojis] = useState(true)
  const [captionHashtags, setCaptionHashtags] = useState(true)
  const [captionResult, setCaptionResult] = useState<Record<string, unknown> | null>(null)

  async function generateImage() {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/ai/media/generate-image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          asset_type: imageAssetType,
          prompt: imagePrompt,
          style: imageStyle,
        }),
      })
      const data = await res.json()
      setImageResult(data)
    } catch {
      setImageResult({ status: "generated", url: "/placeholder.png", message: "Placeholder — connect API for real generation." })
    } finally {
      setLoading(false)
    }
  }

  async function generateVideo() {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/ai/media/generate-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          asset_type: videoAssetType,
          prompt: videoPrompt,
          duration: videoDuration,
          style: videoStyle,
        }),
      })
      const data = await res.json()
      setVideoResult(data)
    } catch {
      setVideoResult({ status: "queued", message: "Placeholder — connect API for real generation." })
    } finally {
      setLoading(false)
    }
  }

  async function generateVoiceover() {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/ai/media/generate-voiceover`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: voText, voice: voVoice, speed: voSpeed }),
      })
      const data = await res.json()
      setVoResult(data)
    } catch {
      setVoResult({ status: "generated", message: "Placeholder — add OPENAI_API_KEY for real TTS." })
    } finally {
      setLoading(false)
    }
  }

  async function generateCaption() {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/ai/media/generate-caption`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform: captionPlatform,
          topic: captionTopic,
          tone: captionTone,
          include_emojis: captionEmojis,
          include_hashtags: captionHashtags,
        }),
      })
      const data = await res.json()
      setCaptionResult(data)
    } catch {
      setCaptionResult({
        caption: "✨ Placeholder caption — add OPENAI_API_KEY for AI generation.",
        hashtags: ["#Placeholder", "#AIContent"],
      })
    } finally {
      setLoading(false)
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">AI Assistant</h1>
          <p className="text-muted-foreground">Generate images, videos, voiceovers, and captions with AI.</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 overflow-x-auto">
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "outline"}
              size="sm"
              className="gap-2 whitespace-nowrap"
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </Button>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Configure & Generate
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {activeTab === "image" && (
                <>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Prompt</label>
                    <textarea
                      className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      rows={4}
                      placeholder="Describe the image you want to create..."
                      value={imagePrompt}
                      onChange={(e) => setImagePrompt(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Asset Type</label>
                    <select
                      className="w-full rounded-lg border bg-background p-2 text-sm"
                      value={imageAssetType}
                      onChange={(e) => setImageAssetType(e.target.value)}
                    >
                      {assetTypes.map((t) => (
                        <option key={t.id} value={t.id}>{t.label} ({t.dimensions})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Style</label>
                    <select
                      className="w-full rounded-lg border bg-background p-2 text-sm"
                      value={imageStyle}
                      onChange={(e) => setImageStyle(e.target.value)}
                    >
                      {styles.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                  <Button onClick={generateImage} disabled={!imagePrompt || loading} className="w-full gap-2">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                    Generate Image
                  </Button>
                </>
              )}

              {activeTab === "video" && (
                <>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Prompt</label>
                    <textarea
                      className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      rows={4}
                      placeholder="Describe the video you want to create..."
                      value={videoPrompt}
                      onChange={(e) => setVideoPrompt(e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="mb-1 block text-sm font-medium">Asset Type</label>
                      <select
                        className="w-full rounded-lg border bg-background p-2 text-sm"
                        value={videoAssetType}
                        onChange={(e) => setVideoAssetType(e.target.value)}
                      >
                        {videoTypes.map((t) => (
                          <option key={t.id} value={t.id}>{t.label}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium">Style</label>
                      <select
                        className="w-full rounded-lg border bg-background p-2 text-sm"
                        value={videoStyle}
                        onChange={(e) => setVideoStyle(e.target.value)}
                      >
                        {styles.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Duration: {videoDuration}s</label>
                    <input
                      type="range"
                      min={5}
                      max={60}
                      value={videoDuration}
                      onChange={(e) => setVideoDuration(Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <Button onClick={generateVideo} disabled={!videoPrompt || loading} className="w-full gap-2">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Video className="h-4 w-4" />}
                    Generate Video
                  </Button>
                </>
              )}

              {activeTab === "voiceover" && (
                <>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Script</label>
                    <textarea
                      className="w-full rounded-lg border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                      rows={6}
                      placeholder="Enter the script for voiceover..."
                      value={voText}
                      onChange={(e) => setVoText(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Voice</label>
                    <div className="grid grid-cols-3 gap-2">
                      {voices.map((v) => (
                        <button
                          key={v.id}
                          className={`rounded-lg border p-2 text-center text-sm transition-colors ${
                            voVoice === v.id
                              ? "border-primary bg-primary/10 text-primary"
                              : "hover:bg-muted"
                          }`}
                          onClick={() => setVoVoice(v.id)}
                        >
                          {v.label}
                          <span className="block text-xs text-muted-foreground">{v.gender}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Speed: {voSpeed.toFixed(1)}x</label>
                    <input
                      type="range"
                      min={0.5}
                      max={2.0}
                      step={0.1}
                      value={voSpeed}
                      onChange={(e) => setVoSpeed(Number(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <Button onClick={generateVoiceover} disabled={!voText || loading} className="w-full gap-2">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mic className="h-4 w-4" />}
                    Generate Voiceover
                  </Button>
                </>
              )}

              {activeTab === "caption" && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="mb-1 block text-sm font-medium">Platform</label>
                      <select
                        className="w-full rounded-lg border bg-background p-2 text-sm"
                        value={captionPlatform}
                        onChange={(e) => setCaptionPlatform(e.target.value)}
                      >
                        {["instagram", "linkedin", "x", "facebook", "youtube"].map((p) => (
                          <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block text-sm font-medium">Tone</label>
                      <Input
                        placeholder="engaging, professional, casual..."
                        value={captionTone}
                        onChange={(e) => setCaptionTone(e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium">Topic</label>
                    <Input
                      placeholder="What is the caption about?"
                      value={captionTopic}
                      onChange={(e) => setCaptionTopic(e.target.value)}
                    />
                  </div>
                  <div className="flex gap-6">
                    <label className="flex items-center gap-2 text-sm">
                      <input type="checkbox" checked={captionEmojis} onChange={(e) => setCaptionEmojis(e.target.checked)} className="rounded" />
                      Include Emojis
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input type="checkbox" checked={captionHashtags} onChange={(e) => setCaptionHashtags(e.target.checked)} className="rounded" />
                      Include Hashtags
                    </label>
                  </div>
                  <Button onClick={generateCaption} disabled={!captionTopic || loading} className="w-full gap-2">
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Type className="h-4 w-4" />}
                    Generate Caption
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          {/* Result Panel */}
          <Card>
            <CardHeader>
              <CardTitle>Result</CardTitle>
            </CardHeader>
            <CardContent>
              {activeTab === "image" && imageResult && (
                <div className="space-y-4">
                  <div className="flex aspect-square items-center justify-center rounded-lg border-2 border-dashed bg-muted/50">
                    <div className="text-center text-muted-foreground">
                      <ImageIcon className="mx-auto mb-2 h-12 w-12" />
                      <p className="text-sm">{imageResult.status === "generated" ? "Image Generated" : "Generating..."}</p>
                      {Boolean(imageResult.dimensions) && <p className="text-xs">{String(imageResult.dimensions)}</p>}
                    </div>
                  </div>
                  {Boolean(imageResult.message) && (
                    <p className="rounded-lg bg-muted p-3 text-sm">{String(imageResult.message)}</p>
                  )}
                </div>
              )}

              {activeTab === "video" && videoResult && (
                <div className="space-y-4">
                  <div className="flex aspect-[9/16] items-center justify-center rounded-lg border-2 border-dashed bg-muted/50">
                    <div className="text-center text-muted-foreground">
                      <Video className="mx-auto mb-2 h-12 w-12" />
                      <p className="text-sm">{videoResult.status === "queued" ? "Video Queued" : "Video Generated"}</p>
                      {Boolean(videoResult.duration) && <p className="text-xs">{String(videoResult.duration)}s</p>}
                    </div>
                  </div>
                  {Boolean(videoResult.message) && (
                    <p className="rounded-lg bg-muted p-3 text-sm">{String(videoResult.message)}</p>
                  )}
                </div>
              )}

              {activeTab === "voiceover" && voResult && (
                <div className="space-y-4">
                  <div className="rounded-lg border p-6 text-center">
                    <Mic className="mx-auto mb-3 h-12 w-12 text-primary" />
                    <p className="mb-2 text-sm font-medium">Voiceover Generated</p>
                    <p className="mb-4 text-xs text-muted-foreground">
                      Voice: {String(voResult.voice)} • Speed: {String(voResult.speed)}x
                    </p>
                    <div className="flex items-center justify-center gap-3">
                      <Button size="sm" variant="outline" className="gap-1">
                        <Play className="h-3 w-3" />
                        Play
                      </Button>
                    </div>
                  </div>
                  {Boolean(voResult.message) && (
                    <p className="rounded-lg bg-muted p-3 text-sm">{String(voResult.message)}</p>
                  )}
                </div>
              )}

              {activeTab === "caption" && captionResult && (
                <div className="space-y-4">
                  <div className="relative rounded-lg border p-4">
                    <p className="whitespace-pre-wrap text-sm">{String(captionResult.caption || "")}</p>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="absolute right-2 top-2"
                      onClick={() => copyToClipboard(String(captionResult.caption || ""))}
                    >
                      {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                  {Boolean(captionResult.hashtags) && (
                    <div className="flex flex-wrap gap-2">
                      {(captionResult.hashtags as string[]).map((tag: string, i: number) => (
                        <span key={i} className="rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  {Boolean(captionResult.character_count) && (
                    <p className="text-xs text-muted-foreground">
                      {String(captionResult.character_count)} characters
                      {captionResult.platform_optimized ? " • Platform optimized" : ""}
                    </p>
                  )}
                  {Boolean(captionResult.message) && (
                    <p className="rounded-lg bg-muted p-3 text-sm">{String(captionResult.message)}</p>
                  )}
                </div>
              )}

              {!imageResult && !videoResult && !voResult && !captionResult && (
                <div className="flex flex-col items-center justify-center py-16 text-center text-muted-foreground">
                  <Sparkles className="mb-3 h-12 w-12" />
                  <p className="text-sm">Configure your request and click Generate to see results here.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
