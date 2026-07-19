"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import {
  FlaskConical,
  Plus,
  Trash2,
  Trophy,
  TrendingUp,
  Loader2,
  BarChart3,
} from "lucide-react"
import type { Platform } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

interface Variant {
  label: string
  caption: string
}

interface ABTestResult {
  test_id: string
  platform: string
  variants: {
    variant_id: string
    label: string
    status: string
    engagement: number
    impressions: number
    engagement_rate: number
    data_points: number
  }[]
  winner: {
    label: string
    engagement_rate: number
  } | null
  recommendation: string
}

interface ABTestingProps {
  postId?: string
  platform?: Platform
}

export function ABTesting({ postId, platform = "linkedin" }: ABTestingProps) {
  const [variants, setVariants] = useState<Variant[]>([
    { label: "Variant A", caption: "" },
    { label: "Variant B", caption: "" },
  ])
  const [testDuration, setTestDuration] = useState(24)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>(platform)
  const [testId, setTestId] = useState<string | null>(null)
  const [results, setResults] = useState<ABTestResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [resultsLoading, setResultsLoading] = useState(false)

  const addVariant = () => {
    if (variants.length >= 5) return
    const label = `Variant ${String.fromCharCode(65 + variants.length)}`
    setVariants([...variants, { label, caption: "" }])
  }

  const removeVariant = (index: number) => {
    if (variants.length <= 2) return
    setVariants(variants.filter((_, i) => i !== index))
  }

  const updateVariant = (index: number, field: keyof Variant, value: string) => {
    const updated = [...variants]
    updated[index] = { ...updated[index], [field]: value }
    setVariants(updated)
  }

  const createTest = async () => {
    if (!postId || variants.some((v) => !v.caption.trim())) return

    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/ab-test/create`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          post_id: postId,
          platform: selectedPlatform,
          variants: variants.map((v) => ({ caption: v.caption, label: v.label })),
          test_duration_hours: testDuration,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setTestId(data.test_id)
      }
    } finally {
      setLoading(false)
    }
  }

  const fetchResults = async () => {
    if (!testId) return

    setResultsLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = {}
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/ab-test/${testId}/results`, { headers })
      if (response.ok) {
        setResults(await response.json())
      }
    } finally {
      setResultsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <FlaskConical className="h-4 w-4" />
          A/B Content Testing
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Platform selector */}
        <div>
          <label className="text-xs font-medium text-muted-foreground mb-1 block">
            Test Platform
          </label>
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value as Platform)}
            className="rounded-md border border-border bg-background px-2 py-1 text-sm w-full"
          >
            <option value="linkedin">LinkedIn</option>
            <option value="x">X (Twitter)</option>
            <option value="instagram">Instagram</option>
            <option value="facebook">Facebook</option>
            <option value="youtube">YouTube</option>
          </select>
        </div>

        {/* Variants */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">
            Caption Variants ({variants.length}/5)
          </label>
          {variants.map((variant, i) => (
            <div key={i} className="rounded-lg border p-3 space-y-2">
              <div className="flex items-center gap-2">
                <Input
                  value={variant.label}
                  onChange={(e) => updateVariant(i, "label", e.target.value)}
                  className="h-7 text-xs flex-1"
                  placeholder="Variant name"
                />
                {variants.length > 2 && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 text-red-500"
                    onClick={() => removeVariant(i)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                )}
              </div>
              <Textarea
                value={variant.caption}
                onChange={(e) => updateVariant(i, "caption", e.target.value)}
                placeholder={`Write variant ${variant.label} caption...`}
                className="min-h-[60px] text-sm"
              />
              <div className="text-[10px] text-muted-foreground text-right">
                {variant.caption.length} chars
              </div>
            </div>
          ))}
          {variants.length < 5 && (
            <Button variant="outline" size="sm" onClick={addVariant} className="w-full gap-1">
              <Plus className="h-3.5 w-3.5" />
              Add Variant
            </Button>
          )}
        </div>

        {/* Duration */}
        <div>
          <label className="text-xs font-medium text-muted-foreground mb-1 block">
            Test Duration (hours)
          </label>
          <Input
            type="number"
            value={testDuration}
            onChange={(e) => setTestDuration(Number(e.target.value))}
            min={1}
            max={168}
            className="text-sm"
          />
        </div>

        {/* Create test */}
        {!testId ? (
          <Button
            onClick={createTest}
            disabled={loading || !postId || variants.some((v) => !v.caption.trim())}
            className="w-full gap-1.5"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FlaskConical className="h-4 w-4" />
            )}
            {loading ? "Creating Test..." : "Create A/B Test"}
          </Button>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm">
              <Badge variant="default">Test Active</Badge>
              <span className="text-muted-foreground text-xs">
                ID: {testId.slice(0, 8)}...
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchResults}
              disabled={resultsLoading}
              className="gap-1.5 w-full"
            >
              {resultsLoading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <BarChart3 className="h-3.5 w-3.5" />
              )}
              Check Results
            </Button>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="border-t pt-4 space-y-3">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <Trophy className="h-4 w-4 text-yellow-500" />
              Results
            </h4>
            <p className="text-xs text-muted-foreground">{results.recommendation}</p>

            <div className="space-y-2">
              {results.variants.map((v) => (
                <div
                  key={v.variant_id}
                  className={`flex items-center justify-between p-2 rounded-lg border ${
                    results.winner?.label === v.label ? "border-green-500 bg-green-50" : ""
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {results.winner?.label === v.label && (
                      <Trophy className="h-3.5 w-3.5 text-yellow-500" />
                    )}
                    <span className="text-sm font-medium">{v.label}</span>
                    <span className="text-xs text-muted-foreground">
                      {v.data_points} data points
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">
                      {v.impressions.toLocaleString()} impressions
                    </span>
                    <span className="text-sm font-bold">
                      {v.engagement_rate}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
