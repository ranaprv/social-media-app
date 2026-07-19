"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Search, TrendingUp, Users, Key, Loader2, Cpu, BarChart3, Target, Lightbulb,
} from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

type Tab = "trends" | "competitors" | "keywords"

export default function ResearchPage() {
  const [tab, setTab] = useState<Tab>("trends")
  const [topic, setTopic] = useState("")
  const [competitors, setCompetitors] = useState("")
  const [loading, setLoading] = useState(false)
  const [provider, setProvider] = useState("openai")
  const [result, setResult] = useState<Record<string, unknown> | null>(null)

  const search = async () => {
    if (!topic.trim() && tab !== "competitors") return
    if (tab === "competitors" && !competitors.trim() && !topic.trim()) return
    setLoading(true)
    try {
      const endpoint = tab === "trends" ? "/research/trends" : tab === "competitors" ? "/research/competitors" : "/research/keywords"
      const body = tab === "competitors"
        ? { competitors: competitors.split(",").map((c) => c.trim()).filter(Boolean), niche: topic, provider }
        : { topic, niche: topic, provider }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
      setResult(await res.json())
    } catch {
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Research</h1>
          <p className="text-muted-foreground">Discover trends, analyze competitors, and research keywords for your niche.</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          {([["trends", "Trends", TrendingUp], ["competitors", "Competitors", Users], ["keywords", "Keywords", Key]] as const).map(([id, label, Icon]) => (
            <Button key={id} variant={tab === id ? "default" : "outline"} size="sm" className="gap-2" onClick={() => { setTab(id); setResult(null) }}>
              <Icon className="h-4 w-4" /> {label}
            </Button>
          ))}
        </div>

        {/* Input */}
        <Card>
          <CardContent className="pt-6 space-y-3">
            {tab === "trends" || tab === "keywords" ? (
              <div>
                <label className="mb-1 block text-sm font-medium">Topic / Niche *</label>
                <Input placeholder="e.g. sustainable fashion, keto recipes, SaaS growth" value={topic} onChange={(e) => setTopic(e.target.value)} />
              </div>
            ) : (
              <>
                <div>
                  <label className="mb-1 block text-sm font-medium">Niche</label>
                  <Input placeholder="Your niche for context" value={topic} onChange={(e) => setTopic(e.target.value)} />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium">Competitors (comma-separated)</label>
                  <Input placeholder="e.g. Buffer, Hootsuite, Sprout Social" value={competitors} onChange={(e) => setCompetitors(e.target.value)} />
                </div>
              </>
            )}
            <div className="flex items-end gap-3">
              <div className="w-40">
                <label className="mb-1 block text-xs text-muted-foreground">Model</label>
                <select className="w-full rounded-lg border bg-background p-2 text-sm" value={provider} onChange={(e) => setProvider(e.target.value)}>
                  <option value="openrouter">OpenRouter (200+ models)</option>
                  <option value="omniroute">OmniRoute (Smart Routing)</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="gemini">Gemini</option>
                  <option value="deepseek">DeepSeek</option>
                </select>
              </div>
              <Button onClick={search} disabled={loading} className="gap-2">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Research
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Trends */}
            {tab === "trends" && result && "trends" in result && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-primary" /> Trending Topics</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {(result.trends as Array<Record<string, unknown>>).map((trend, i) => (
                      <div key={i} className="rounded-lg border p-4">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-medium">{String(trend.topic)}</h4>
                          <div className="flex items-center gap-2">
                            <span className={`rounded-full px-2 py-0.5 text-xs ${
                              String(trend.trend_direction) === "rising" ? "bg-green-100 text-green-700" :
                              String(trend.trend_direction) === "declining" ? "bg-red-100 text-red-700" :
                              "bg-gray-100 text-gray-700"
                            }`}>{String(trend.trend_direction)}</span>
                            <span className="text-xs text-muted-foreground">Popularity: {String(trend.popularity || trend.热度 || "N/A")}</span>
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground">{String(trend.description)}</p>
                        {Boolean(trend.content_opportunity) && (
                          <p className="mt-1 text-xs text-primary">💡 {String(trend.content_opportunity)}</p>
                        )}
                      </div>
                    ))}
                  </div>
                  {Boolean(result.related_topics) && (
                    <div className="mt-4">
                      <p className="text-sm font-medium mb-2">Related Topics</p>
                      <div className="flex flex-wrap gap-2">
                        {(result.related_topics as string[]).map((t, i) => (
                          <span key={i} className="rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">{t}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Competitors */}
            {tab === "competitors" && result && "competitors" in result && (
              <div className="space-y-4">
                <Card>
                  <CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-5 w-5 text-primary" /> Competitor Analysis</CardTitle></CardHeader>
                  <CardContent>
                    <div className="grid gap-4 md:grid-cols-2">
                      {(result.competitors as Array<Record<string, unknown>>).map((comp, i) => (
                        <div key={i} className="rounded-lg border p-4 space-y-2">
                          <h4 className="font-medium">{String(comp.name)}</h4>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div><span className="text-muted-foreground">Strengths:</span> {String(comp.strengths)}</div>
                            <div><span className="text-muted-foreground">Weaknesses:</span> {String(comp.weaknesses)}</div>
                            <div><span className="text-muted-foreground">Strategy:</span> {String(comp.content_strategy)}</div>
                            <div><span className="text-muted-foreground">Frequency:</span> {String(comp.posting_frequency)}</div>
                          </div>
                          {Boolean(comp.opportunities_to_differentiate) && (
                            <p className="text-xs text-primary">🎯 {String(comp.opportunities_to_differentiate)}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
                {result && "market_gaps" in result && (
                  <Card>
                    <CardHeader><CardTitle className="flex items-center gap-2"><Target className="h-5 w-5 text-primary" /> Market Gaps</CardTitle></CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {(result.market_gaps as string[]).map((gap, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <Lightbulb className="mt-0.5 h-4 w-4 text-yellow-500 flex-shrink-0" />
                            {gap}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
                {result && "recommendations" in result && (
                  <Card>
                    <CardHeader><CardTitle>Recommendations</CardTitle></CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {(result.recommendations as string[]).map((rec, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CheckIcon className="mt-0.5 h-4 w-4 text-green-500 flex-shrink-0" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Keywords */}
            {tab === "keywords" && result && "keywords" in result && (
              <Card>
                <CardHeader><CardTitle className="flex items-center gap-2"><Key className="h-5 w-5 text-primary" /> Keyword Research</CardTitle></CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-left text-muted-foreground">
                          <th className="pb-2 font-medium">Keyword</th>
                          <th className="pb-2 font-medium">Volume</th>
                          <th className="pb-2 font-medium">Difficulty</th>
                          <th className="pb-2 font-medium">Intent</th>
                          <th className="pb-2 font-medium">Content Type</th>
                          <th className="pb-2 font-medium">Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(result.keywords as Array<Record<string, unknown>>).map((kw, i) => (
                          <tr key={i} className="border-b last:border-0">
                            <td className="py-2 font-medium">{String(kw.keyword)}</td>
                            <td className="py-2">
                              <span className={`rounded-full px-2 py-0.5 text-xs ${
                                String(kw.estimated_volume) === "high" ? "bg-green-100 text-green-700" :
                                String(kw.estimated_volume) === "medium" ? "bg-yellow-100 text-yellow-700" :
                                "bg-gray-100 text-gray-700"
                              }`}>{String(kw.estimated_volume)}</span>
                            </td>
                            <td className="py-2">{String(kw.difficulty)}</td>
                            <td className="py-2 capitalize">{String(kw.intent)}</td>
                            <td className="py-2">{String(kw.content_type)}</td>
                            <td className="py-2 font-medium">{String(kw.score)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {result && "long_tail" in result && (
                    <div className="mt-4">
                      <p className="text-sm font-medium mb-2">Long-tail Keywords</p>
                      <div className="flex flex-wrap gap-2">
                        {(result.long_tail as string[]).map((kw, i) => (
                          <span key={i} className="rounded-full bg-muted px-3 py-1 text-xs">{kw}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

function CheckIcon({ className }: { className?: string }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
}
