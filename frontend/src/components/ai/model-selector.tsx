"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Cpu, Zap, DollarSign, Check, Circle, ChevronDown, ExternalLink } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface ModelInfo {
  id: string
  name: string
  max_tokens: number
  cost_tier: string
  context_window?: number
}

interface ProviderInfo {
  name: string
  configured: boolean
  description: string
  models_count: number
  setup_url: string
  benefit: string
}

interface RoutingInfo {
  providers: Record<string, { configured: boolean; models_count: number; note: string }>
  routing: Record<string, { selected_provider: string; recommended_model: string; alternatives: string[] }>
}

interface Props {
  onSelect?: (provider: string, modelId: string, modelName: string) => void
  compact?: boolean
}

const COST_COLORS: Record<string, string> = {
  low: "text-green-600 bg-green-50",
  medium: "text-amber-600 bg-amber-50",
  high: "text-red-600 bg-red-50",
}

const COST_LABELS: Record<string, string> = {
  low: "$",
  medium: "$$",
  high: "$$$",
}

export function ModelSelector({ onSelect, compact = false }: Props) {
  const [providers, setProviders] = useState<Record<string, ProviderInfo>>({})
  const [availableModels, setAvailableModels] = useState<Record<string, { name: string; models: ModelInfo[] }>>({})
  const [routing, setRouting] = useState<RoutingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState<{ provider: string; model: string } | null>(null)

  useEffect(() => {
    Promise.allSettled([
      fetch(`${API_URL}/ai/models/providers`).then(r => r.json()),
      fetch(`${API_URL}/ai/models/available`).then(r => r.json()),
      fetch(`${API_URL}/ai/models/routing`).then(r => r.json()),
    ]).then(([p, m, r]) => {
      if (p.status === "fulfilled") setProviders(p.value.providers || {})
      if (m.status === "fulfilled") setAvailableModels(m.value.providers || {})
      if (r.status === "fulfilled") setRouting(r.value)
    }).finally(() => setLoading(false))
  }, [])

  function handleSelect(provider: string, modelId: string, modelName: string) {
    setSelectedModel({ provider, model: modelId })
    onSelect?.(provider, modelId, modelName)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8 text-muted-foreground">
        <Cpu className="mr-2 h-4 w-4 animate-pulse" /> Loading models...
      </div>
    )
  }

  if (compact) {
    return <CompactSelector providers={providers} models={availableModels} onSelect={handleSelect} selectedModel={selectedModel} />
  }

  return (
    <div className="space-y-4">
      {Object.entries(providers).map(([key, provider]) => {
        const models = availableModels[key]?.models || []
        const isExpanded = expandedProvider === key
        return (
          <Card key={key} className={provider.configured ? "border-green-200" : "opacity-60"}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${provider.configured ? "bg-green-100" : "bg-muted"}`}>
                    <Cpu className={`h-4 w-4 ${provider.configured ? "text-green-600" : "text-muted-foreground"}`} />
                  </div>
                  <div>
                    <CardTitle className="text-base">{provider.name}</CardTitle>
                    <p className="text-xs text-muted-foreground">{provider.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${provider.configured ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    <Circle className={`h-1.5 w-1.5 fill-current ${provider.configured ? "text-green-500" : "text-gray-400"}`} />
                    {provider.configured ? "Connected" : "Not configured"}
                  </span>
                  {models.length > 0 && (
                    <Button variant="ghost" size="sm" onClick={() => setExpandedProvider(isExpanded ? null : key)}>
                      <ChevronDown className={`h-4 w-4 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            {isExpanded && models.length > 0 && (
              <CardContent className="pt-0">
                <div className="space-y-2">
                  {models.map(model => {
                    const isSelected = selectedModel?.provider === key && selectedModel?.model === model.id
                    return (
                      <button
                        key={model.id}
                        onClick={() => handleSelect(key, model.id, model.name)}
                        className={`flex w-full items-center justify-between rounded-lg border p-3 text-left transition-colors ${
                          isSelected ? "border-primary bg-primary/5" : "hover:bg-muted"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`flex h-6 w-6 items-center justify-center rounded ${isSelected ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                            {isSelected ? <Check className="h-3 w-3" /> : <Circle className="h-2 w-2" />}
                          </div>
                          <div>
                            <p className="text-sm font-medium">{model.name}</p>
                            <p className="text-xs text-muted-foreground font-mono">{model.id}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          {model.context_window && (
                            <span className="text-muted-foreground">{(model.context_window / 1000).toFixed(0)}K ctx</span>
                          )}
                          <span className={`rounded-full px-2 py-0.5 font-medium ${COST_COLORS[model.cost_tier] || ""}`}>
                            {COST_LABELS[model.cost_tier] || model.cost_tier}
                          </span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </CardContent>
            )}
            {!provider.configured && (
              <CardContent className="pt-0">
                <a
                  href={provider.setup_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                >
                  Get API key <ExternalLink className="h-3 w-3" />
                </a>
              </CardContent>
            )}
          </Card>
        )
      })}
    </div>
  )
}

function CompactSelector({
  providers,
  models,
  onSelect,
  selectedModel,
}: {
  providers: Record<string, ProviderInfo>
  models: Record<string, { name: string; models: ModelInfo[] }>
  onSelect: (provider: string, modelId: string, modelName: string) => void
  selectedModel: { provider: string; model: string } | null
}) {
  const [open, setOpen] = useState(false)

  const allModels: { provider: string; model: ModelInfo }[] = []
  for (const [key, group] of Object.entries(models)) {
    if (providers[key]?.configured) {
      for (const m of group.models) {
        allModels.push({ provider: key, model: m })
      }
    }
  }

  const current = selectedModel
    ? allModels.find(m => m.provider === selectedModel.provider && m.model.id === selectedModel.model)
    : allModels[0]

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-lg border bg-card px-3 py-2 text-sm transition-colors hover:bg-muted"
      >
        <Cpu className="h-4 w-4 text-primary" />
        <span className="font-medium">{current?.model.name || "Select model"}</span>
        <span className="text-xs text-muted-foreground">{current?.provider}</span>
        <ChevronDown className={`h-3 w-3 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-1 w-80 rounded-xl border bg-card shadow-lg">
          <div className="max-h-80 overflow-y-auto p-2">
            {allModels.map(({ provider, model }) => {
              const isSelected = selectedModel?.provider === provider && selectedModel?.model === model.id
              return (
                <button
                  key={`${provider}/${model.id}`}
                  onClick={() => { onSelect(provider, model.id, model.name); setOpen(false) }}
                  className={`flex w-full items-center gap-3 rounded-lg p-2 text-left text-sm transition-colors ${
                    isSelected ? "bg-primary/10 text-primary" : "hover:bg-muted"
                  }`}
                >
                  <div className="flex-1">
                    <p className="font-medium">{model.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{model.id}</p>
                  </div>
                  <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium ${COST_COLORS[model.cost_tier] || ""}`}>
                    {COST_LABELS[model.cost_tier] || ""}
                  </span>
                </button>
              )
            })}
            {allModels.length === 0 && (
              <p className="py-4 text-center text-sm text-muted-foreground">
                No providers configured. Add an API key to get started.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
