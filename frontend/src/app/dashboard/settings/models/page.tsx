"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ModelSelector } from "@/components/ai/model-selector"
import { Cpu, Zap, Settings, Route, Check, Circle, ExternalLink, Sparkles } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface ProviderStatus {
  name: string
  configured: boolean
  description: string
  models_count: number
  setup_url: string
  benefit: string
}

interface RoutingRecommendation {
  selected_provider: string
  recommended_model: string
  alternatives: string[]
}

const TASK_LABELS: Record<string, string> = {
  social_copy: "Social Media Copy",
  long_form: "Long-Form Content",
  short_form: "Short-Form Posts",
  brainstorm: "Brainstorming / Ideas",
  media_prompts: "Image / Video Prompts",
  caption: "Caption Generation",
}

export default function AIModelsPage() {
  const [providers, setProviders] = useState<Record<string, ProviderStatus>>({})
  const [routing, setRouting] = useState<Record<string, RoutingRecommendation>>({})
  const [totalModels, setTotalModels] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetch(`${API_URL}/ai/models/providers`).then(r => r.json()),
      fetch(`${API_URL}/ai/models/routing`).then(r => r.json()),
    ]).then(([p, r]) => {
      if (p.status === "fulfilled") {
        setProviders(p.value.providers || {})
        setTotalModels(p.value.total_available_models || 0)
      }
      if (r.status === "fulfilled") setRouting(r.value.routing || {})
    }).finally(() => setLoading(false))
  }, [])

  const configuredCount = Object.values(providers).filter(p => p.configured).length

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Model Configuration</h1>
          <p className="text-muted-foreground">
            Configure AI providers and select models for content generation.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                <Cpu className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{configuredCount}</p>
                <p className="text-xs text-muted-foreground">Providers Connected</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-green-500/10">
                <Sparkles className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalModels}</p>
                <p className="text-xs text-muted-foreground">Models Available</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
                <Route className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">OmniRoute</p>
                <p className="text-xs text-muted-foreground">Smart Routing Active</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="providers">
          <TabsList>
            <TabsTrigger value="providers" className="gap-2">
              <Cpu className="h-4 w-4" /> Providers
            </TabsTrigger>
            <TabsTrigger value="models" className="gap-2">
              <Zap className="h-4 w-4" /> Models
            </TabsTrigger>
            <TabsTrigger value="routing" className="gap-2">
              <Route className="h-4 w-4" /> Routing
            </TabsTrigger>
          </TabsList>

          {/* Providers Tab */}
          <TabsContent value="providers">
            <div className="space-y-4">
              {/* OpenRouter Quick Setup */}
              {!providers.openrouter?.configured && (
                <Card className="border-primary/30 bg-primary/5">
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                        <Sparkles className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">Recommended: OpenRouter</p>
                        <p className="text-sm text-muted-foreground">
                          One API key gives you access to Claude, GPT-4o, Gemini, Llama, and 200+ more models.
                        </p>
                      </div>
                    </div>
                    <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer">
                      <Button className="gap-2">
                        Get API Key <ExternalLink className="h-4 w-4" />
                      </Button>
                    </a>
                  </CardContent>
                </Card>
              )}

              {loading ? (
                <div className="flex justify-center py-12 text-muted-foreground">
                  <Cpu className="mr-2 h-4 w-4 animate-pulse" /> Loading providers...
                </div>
              ) : (
                Object.entries(providers).map(([key, provider]) => (
                  <Card key={key}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${provider.configured ? "bg-green-100" : "bg-muted"}`}>
                            <Cpu className={`h-5 w-5 ${provider.configured ? "text-green-600" : "text-muted-foreground"}`} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium">{provider.name}</p>
                              <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${provider.configured ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                                <Circle className={`h-1.5 w-1.5 fill-current ${provider.configured ? "text-green-500" : "text-gray-400"}`} />
                                {provider.configured ? "Connected" : "Not configured"}
                              </span>
                            </div>
                            <p className="text-sm text-muted-foreground">{provider.description}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">{provider.models_count} models</p>
                          <p className="text-xs text-muted-foreground">{provider.benefit}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Models Tab */}
          <TabsContent value="models">
            <Card>
              <CardHeader>
                <CardTitle>Available Models</CardTitle>
                <CardDescription>
                  Select models for each provider. Connected providers show their available models.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ModelSelector compact={false} />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Routing Tab */}
          <TabsContent value="routing">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Route className="h-5 w-5 text-primary" />
                  OmniRoute Smart Routing
                </CardTitle>
                <CardDescription>
                  OmniRoute automatically selects the best provider and model for each task type based on availability, cost, and capability.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex justify-center py-12 text-muted-foreground">
                    <Cpu className="mr-2 h-4 w-4 animate-pulse" /> Loading routing info...
                  </div>
                ) : (
                  <div className="space-y-3">
                    {Object.entries(TASK_LABELS).map(([taskKey, label]) => {
                      const rec = routing[taskKey]
                      if (!rec) return null
                      return (
                        <div key={taskKey} className="flex items-center justify-between rounded-lg border p-3">
                          <div>
                            <p className="text-sm font-medium">{label}</p>
                            <p className="text-xs text-muted-foreground">
                              Recommended: <span className="font-mono text-primary">{rec.recommended_model}</span>
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                              rec.selected_provider !== "none" ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"
                            }`}>
                              {rec.selected_provider !== "none" ? rec.selected_provider : "no provider"}
                            </span>
                            {rec.alternatives.length > 0 && (
                              <span className="text-xs text-muted-foreground">
                                +{rec.alternatives.length} alt
                              </span>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
