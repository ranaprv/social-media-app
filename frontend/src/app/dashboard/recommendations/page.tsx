"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Sparkles,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Zap,
  Target,
  Lightbulb,
  Clock,
  Hash,
  BarChart3,
  CheckCircle2,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const mockRecommendations = [
  {
    id: "rec-1",
    type: "better-headlines",
    title: "Improve Headline",
    priority: "high",
    current: "10 Tips for Content Creation",
    suggested: [
      "10 Content Creation Hacks That Tripled Our Engagement",
      "I Tried 10 Content Strategies — Here's What Actually Worked",
      "The Content Creation Framework Nobody Talks About",
    ],
    impact: "+45% more clicks",
    explanation: "Headlines with numbers, personal experience, and curiosity gaps perform 2-3x better than generic titles.",
    icon: Target,
  },
  {
    id: "rec-2",
    type: "better-hooks",
    title: "Strengthen Opening Hook",
    priority: "high",
    current: "Here are some tips for content creation.",
    suggested: [
      "Stop creating content that nobody reads. Here's the fix.",
      "I wasted 6 months creating content before I learned this one thing.",
      "90% of content creators make this exact same mistake.",
    ],
    impact: "+62% retention",
    explanation: "Hooks that create curiosity gaps or emotional responses keep readers engaged 3x longer.",
    icon: Zap,
  },
  {
    id: "rec-3",
    type: "better-cta",
    title: "Add Stronger Call-to-Action",
    priority: "medium",
    current: "Thanks for reading!",
    suggested: [
      "If this helped, share it with one person who needs to see it.",
      "What's your biggest content creation challenge? Reply and I'll help.",
      "Save this post for your next content planning session.",
    ],
    impact: "+38% engagement",
    explanation: "Specific CTAs that ask for a single action convert 2.5x better than generic ones.",
    icon: Lightbulb,
  },
  {
    id: "rec-4",
    type: "better-posting-time",
    title: "Optimize Posting Schedule",
    priority: "medium",
    current: "Posting at 3:00 PM",
    suggested: [
      "Tuesday 8:00 AM — your audience is most active",
      "Wednesday 10:00 AM — highest engagement window",
      "Thursday 9:00 AM — peak professional browsing time",
    ],
    impact: "+28% reach",
    explanation: "Your analytics show 2.3x higher engagement during morning professional hours vs afternoon.",
    icon: Clock,
  },
  {
    id: "rec-5",
    type: "better-hashtags",
    title: "Hashtag Strategy",
    priority: "medium",
    current: "#content #marketing #tips",
    suggested: [
      "#ContentStrategy #CreatorEconomy #GrowthMarketing",
      "#SaaSGrowth #ContentCreation #B2BMarketing",
      "#SocialMediaTips #ContentMarketing #DigitalStrategy",
    ],
    impact: "+34% discoverability",
    explanation: "Niche hashtags (50K-500K posts) outperform broad ones (1M+) for targeted reach.",
    icon: Hash,
  },
]

const mockAnalysis = {
  readabilityScore: 72,
  emotionalImpact: 65,
  specificityScore: 58,
  originalityScore: 81,
  ctaStrength: 45,
  hookPower: 52,
}

const priorityColors: Record<string, string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  low: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
}

function ScoreGauge({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 45
  const offset = circumference - (score / 100) * circumference
  const color = score >= 70 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444"

  return (
    <div className="relative flex items-center justify-center">
      <svg width="120" height="120" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted/30" />
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 50 50)"
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-2xl font-bold">{score}</div>
        <div className="text-xs text-muted-foreground">/100</div>
      </div>
    </div>
  )
}

function AnalysisBar({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? "bg-green-500" : value >= 50 ? "bg-yellow-500" : "bg-red-500"
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div className={`h-2 rounded-full transition-all ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

export default function RecommendationsPage() {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [overallScore, setOverallScore] = useState(78)
  const [analysis, setAnalysis] = useState(mockAnalysis)
  const [recs, setRecs] = useState(mockRecommendations)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchRecs() {
      try {
        const res = await fetch(`${API_URL}/ai/recommendations/analyze`)
        if (res.ok) {
          const data = await res.json()
          setOverallScore(data.overallScore || 78)
          setAnalysis(data.contentAnalysis || mockAnalysis)
          if (data.recommendations?.length) {
            setRecs(
              data.recommendations.map((r: Record<string, unknown>, i: number) => ({
                ...r,
                icon: [Target, Zap, Lightbulb, Clock, Hash, BarChart3, TrendingUp][i % 7],
              }))
            )
          }
        }
      } catch {
        // use mock
      } finally {
        setLoading(false)
      }
    }
    fetchRecs()
  }, [])

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">AI Recommendations</h1>
          <p className="text-muted-foreground">AI-powered insights to improve your content performance.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Score Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Content Score
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-4">
              <ScoreGauge score={overallScore} />
              <p className="text-center text-sm text-muted-foreground">
                {overallScore >= 70
                  ? "Good — your content is well-optimized. Follow recommendations to reach 90+."
                  : "Room for improvement — apply the suggestions below to boost your score."}
              </p>
              <Button className="w-full gap-2">
                <Zap className="h-4 w-4" />
                Apply All Suggestions
              </Button>
            </CardContent>
          </Card>

          {/* Content Analysis */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Content Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <AnalysisBar label="Readability" value={analysis.readabilityScore} />
              <AnalysisBar label="Emotional Impact" value={analysis.emotionalImpact} />
              <AnalysisBar label="Specificity" value={analysis.specificityScore} />
              <AnalysisBar label="Originality" value={analysis.originalityScore} />
              <AnalysisBar label="CTA Strength" value={analysis.ctaStrength} />
              <AnalysisBar label="Hook Power" value={analysis.hookPower} />
            </CardContent>
          </Card>
        </div>

        {/* Recommendations List */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Recommendations ({recs.length})</h2>
          {recs.map((rec) => {
            const isExpanded = expandedId === rec.id
            const Icon = rec.icon
            return (
              <Card key={rec.id} className="transition-all hover:shadow-md">
                <CardHeader
                  className="cursor-pointer"
                  onClick={() => setExpandedId(isExpanded ? null : rec.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="rounded-lg bg-primary/10 p-2">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-base">{rec.title}</CardTitle>
                        <p className="text-sm text-muted-foreground">{rec.explanation}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`rounded-full px-3 py-1 text-xs font-medium ${priorityColors[rec.priority]}`}>
                        {rec.priority}
                      </span>
                      <span className="text-sm font-medium text-green-600">{rec.impact}</span>
                      {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                    </div>
                  </div>
                </CardHeader>
                {isExpanded && (
                  <CardContent className="border-t pt-4">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <h4 className="mb-2 text-sm font-medium text-muted-foreground">Current</h4>
                        <div className="rounded-lg border p-3 text-sm">{rec.current}</div>
                      </div>
                      <div>
                        <h4 className="mb-2 text-sm font-medium text-muted-foreground">Suggested Alternatives</h4>
                        <div className="space-y-2">
                          {rec.suggested.map((s: string, i: number) => (
                            <div key={i} className="flex items-start gap-2 rounded-lg border p-3 text-sm">
                              <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-green-500" />
                              <span>{s}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Button size="sm" className="gap-1">
                        <Zap className="h-3 w-3" />
                        Apply Best Option
                      </Button>
                      <Button size="sm" variant="outline">
                        Dismiss
                      </Button>
                    </div>
                  </CardContent>
                )}
              </Card>
            )
          })}
        </div>
      </div>
    </DashboardLayout>
  )
}
