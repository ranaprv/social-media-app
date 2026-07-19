"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import {
  CheckCircle2,
  Circle,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Calendar,
  FileText,
  Image,
} from "lucide-react"
import type { Platform, PostPlatform, MediaAsset } from "@/types"

interface PlatformConfig {
  key: Platform
  name: string
  icon: string
  color: string
  bgColor: string
  limits: {
    maxCaption: number
    mediaTypes: string[]
  }
}

const PLATFORMS: PlatformConfig[] = [
  {
    key: "linkedin",
    name: "LinkedIn",
    icon: "LinkedIn",
    color: "text-blue-600",
    bgColor: "bg-blue-50 border-blue-200",
    limits: { maxCaption: 3000, mediaTypes: ["image", "video", "document"] },
  },
  {
    key: "x",
    name: "X (Twitter)",
    icon: "X",
    color: "text-black",
    bgColor: "bg-gray-50 border-gray-200",
    limits: { maxCaption: 280, mediaTypes: ["image", "video", "gif"] },
  },
  {
    key: "instagram",
    name: "Instagram",
    icon: "IG",
    color: "text-pink-500",
    bgColor: "bg-pink-50 border-pink-200",
    limits: { maxCaption: 2200, mediaTypes: ["image", "video", "carousel"] },
  },
  {
    key: "facebook",
    name: "Facebook",
    icon: "FB",
    color: "text-blue-500",
    bgColor: "bg-blue-50 border-blue-200",
    limits: { maxCaption: 63206, mediaTypes: ["image", "video"] },
  },
  {
    key: "youtube",
    name: "YouTube",
    icon: "YT",
    color: "text-red-600",
    bgColor: "bg-red-50 border-red-200",
    limits: { maxCaption: 5000, mediaTypes: ["video", "image"] },
  },
]

interface PlatformOverride {
  platform: Platform
  enabled: boolean
  caption: string
  mediaAssetIds: string[]
  scheduledAt: string
}

interface MultiPlatformSelectorProps {
  postId: string
  defaultCaption: string
  defaultMediaIds?: string[]
  connectedPlatforms?: Platform[]
  onSchedule: (platforms: PlatformOverride[]) => Promise<void>
}

export function MultiPlatformSelector({
  postId,
  defaultCaption,
  defaultMediaIds = [],
  connectedPlatforms = ["linkedin", "x", "facebook", "instagram", "youtube"],
  onSchedule,
}: MultiPlatformSelectorProps) {
  const [overrides, setOverrides] = useState<Record<Platform, PlatformOverride>>(
    () => {
      const initial = {} as Record<Platform, PlatformOverride>
      for (const p of PLATFORMS) {
        initial[p.key] = {
          platform: p.key,
          enabled: false,
          caption: "",
          mediaAssetIds: [],
          scheduledAt: "",
        }
      }
      return initial
    }
  )
  const [expandedPlatform, setExpandedPlatform] = useState<Platform | null>(null)
  const [isScheduling, setIsScheduling] = useState(false)

  const togglePlatform = useCallback((platform: Platform) => {
    setOverrides((prev) => ({
      ...prev,
      [platform]: { ...prev[platform], enabled: !prev[platform].enabled },
    }))
  }, [])

  const updateOverride = useCallback(
    (platform: Platform, field: keyof PlatformOverride, value: string | string[]) => {
      setOverrides((prev) => ({
        ...prev,
        [platform]: { ...prev[platform], [field]: value },
      }))
    },
    []
  )

  const enabledCount = Object.values(overrides).filter((o) => o.enabled).length

  const getEffectiveCaption = (platform: Platform): string => {
    const override = overrides[platform]
    return override.caption || defaultCaption
  }

  const getCaptionLength = (platform: Platform): number => {
    return getEffectiveCaption(platform).length
  }

  const isOverLimit = (platform: Platform): boolean => {
    const config = PLATFORMS.find((p) => p.key === platform)
    return config ? getCaptionLength(platform) > config.limits.maxCaption : false
  }

  const handleSchedule = async () => {
    setIsScheduling(true)
    try {
      const enabled = Object.values(overrides).filter((o) => o.enabled)
      await onSchedule(enabled)
    } finally {
      setIsScheduling(false)
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Publish to Platforms</CardTitle>
          <Badge variant={enabledCount > 0 ? "default" : "secondary"}>
            {enabledCount} selected
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {PLATFORMS.map((config) => {
          const override = overrides[config.key]
          const isConnected = connectedPlatforms.includes(config.key)
          const isExpanded = expandedPlatform === config.key
          const captionLen = getCaptionLength(config.key)
          const overLimit = isOverLimit(config.key)

          return (
            <div
              key={config.key}
              className={`rounded-lg border transition-colors ${
                override.enabled ? config.bgColor : "border-border"
              } ${!isConnected ? "opacity-50" : ""}`}
            >
              {/* Platform row */}
              <div className="flex items-center gap-3 px-3 py-2.5">
                <Checkbox
                  checked={override.enabled}
                  onCheckedChange={() => togglePlatform(config.key)}
                  disabled={!isConnected}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${config.color}`}>
                      {config.name}
                    </span>
                    {!isConnected && (
                      <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                        Not connected
                      </Badge>
                    )}
                    {override.enabled && !override.caption && (
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                        Uses default caption
                      </Badge>
                    )}
                    {override.enabled && override.caption && (
                      <Badge variant="default" className="text-[10px] px-1.5 py-0">
                        Custom caption
                      </Badge>
                    )}
                  </div>
                  {override.enabled && (
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[11px] text-muted-foreground">
                        {captionLen}/{config.limits.maxCaption} chars
                      </span>
                      {overLimit && (
                        <span className="text-[11px] text-red-500 flex items-center gap-0.5">
                          <AlertCircle className="h-3 w-3" />
                          Over limit
                        </span>
                      )}
                    </div>
                  )}
                </div>
                {override.enabled && isConnected && (
                  <button
                    onClick={() =>
                      setExpandedPlatform(isExpanded ? null : config.key)
                    }
                    className="text-muted-foreground hover:text-foreground"
                  >
                    {isExpanded ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </button>
                )}
              </div>

              {/* Expanded settings */}
              {isExpanded && override.enabled && (
                <div className="px-3 pb-3 space-y-3 border-t border-border/50">
                  {/* Custom caption */}
                  <div className="pt-2">
                    <label className="text-xs font-medium text-muted-foreground mb-1 block">
                      Platform-specific caption
                    </label>
                    <Textarea
                      value={override.caption}
                      onChange={(e) =>
                        updateOverride(config.key, "caption", e.target.value)
                      }
                      placeholder={`Leave empty to use default caption (${defaultCaption.length} chars)`}
                      className="min-h-[60px] text-sm"
                      maxLength={config.limits.maxCaption}
                    />
                  </div>

                  {/* Schedule time */}
                  <div>
                    <label className="text-xs font-medium text-muted-foreground mb-1 block">
                      Schedule time (optional)
                    </label>
                    <Input
                      type="datetime-local"
                      value={override.scheduledAt}
                      onChange={(e) =>
                        updateOverride(config.key, "scheduledAt", e.target.value)
                      }
                      className="text-sm"
                    />
                  </div>
                </div>
              )}
            </div>
          )
        })}

        {/* Schedule button */}
        <div className="pt-2 flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            {enabledCount === 0
              ? "Select platforms above to schedule"
              : `Will publish to ${enabledCount} platform${enabledCount > 1 ? "s" : ""}`}
          </p>
          <Button
            onClick={handleSchedule}
            disabled={enabledCount === 0 || isScheduling}
            size="sm"
            className="gap-1.5"
          >
            <Calendar className="h-3.5 w-3.5" />
            {isScheduling ? "Scheduling..." : "Schedule"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
