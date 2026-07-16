"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Image,
  Video,
  FileText,
  Search,
  Grid,
  List,
  Upload,
  FolderOpen,
  X,
  Tag,
  MoreHorizontal,
  Download,
  Trash2,
  Eye,
  Youtube,
  Instagram,
  Linkedin,
  Facebook,
} from "lucide-react"
import type { MediaType, MediaAsset } from "@/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

// ── Platform definitions ──────────────────────────────────────────────────

interface PlatformContentType {
  id: string
  label: string
  icon: React.ElementType
}

interface PlatformDef {
  id: string
  name: string
  icon: React.ElementType
  color: string
  contentTypes: PlatformContentType[]
}

const PLATFORMS: PlatformDef[] = [
  {
    id: "youtube",
    name: "YouTube",
    icon: Youtube,
    color: "text-red-500",
    contentTypes: [
      { id: "image", label: "Thumbnails & Images", icon: Image },
      { id: "video", label: "Videos", icon: Video },
    ],
  },
  {
    id: "instagram",
    name: "Instagram",
    icon: Instagram,
    color: "text-pink-500",
    contentTypes: [
      { id: "reel", label: "Reels", icon: Video },
      { id: "carousel", label: "Carousels", icon: FileText },
      { id: "vertical_video", label: "Vertical Videos", icon: Video },
      { id: "image", label: "Images", icon: Image },
    ],
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    icon: Linkedin,
    color: "text-blue-600",
    contentTypes: [
      { id: "post", label: "Posts", icon: FileText },
      { id: "carousel", label: "Carousels", icon: FileText },
      { id: "video", label: "Videos", icon: Video },
      { id: "document", label: "Documents", icon: FileText },
    ],
  },
  {
    id: "facebook",
    name: "Facebook",
    icon: Facebook,
    color: "text-blue-500",
    contentTypes: [
      { id: "image", label: "Images", icon: Image },
      { id: "video", label: "Videos", icon: Video },
    ],
  },
]

// ── Component ─────────────────────────────────────────────────────────────

export function MediaLibrary() {
  const [assets, setAssets] = useState<MediaAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null)
  const [selectedContentType, setSelectedContentType] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [selectedAsset, setSelectedAsset] = useState<MediaAsset | null>(null)

  // Fetch assets
  useEffect(() => {
    async function fetchAssets() {
      try {
        const params = new URLSearchParams()
        if (selectedPlatform) params.set("platform", selectedPlatform)
        if (selectedContentType) params.set("content_type", selectedContentType)
        if (searchQuery) params.set("search", searchQuery)

        const res = await fetch(`${API_URL}/media/assets?${params}`)
        if (res.ok) {
          const data = await res.json()
          setAssets(data.assets || [])
        }
      } catch {
        // Fallback to empty
        setAssets([])
      } finally {
        setLoading(false)
      }
    }
    fetchAssets()
  }, [selectedPlatform, selectedContentType, searchQuery])

  // Filtered assets
  const displayAssets = useMemo(() => {
    if (!searchQuery) return assets
    const q = searchQuery.toLowerCase()
    return assets.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        (a.tags || []).some((t) => t.toLowerCase().includes(q))
    )
  }, [assets, searchQuery])

  // Asset counts per platform
  const platformCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    assets.forEach((a) => {
      if (a.platform) {
        counts[a.platform] = (counts[a.platform] || 0) + 1
      }
    })
    return counts
  }, [assets])

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "—"
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getAssetIcon = (asset: MediaAsset) => {
    if (asset.type === "video" || asset.content_type === "reel" || asset.content_type === "vertical_video") return Video
    if (asset.type === "pdf" || asset.content_type === "document") return FileText
    return Image
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Media Library</h2>
          <p className="text-muted-foreground">
            Organize content by platform for automatic scheduling.
          </p>
        </div>
        <Button className="gap-2">
          <Upload className="h-4 w-4" />
          Upload
        </Button>
      </div>

      {/* Platform Tabs */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => { setSelectedPlatform(null); setSelectedContentType(null) }}
          className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
            !selectedPlatform
              ? "bg-primary text-primary-foreground shadow-md"
              : "bg-card text-muted-foreground hover:bg-muted border"
          }`}
        >
          <Grid className="h-4 w-4" />
          All
        </button>
        {PLATFORMS.map((p) => {
          const Icon = p.icon
          const isActive = selectedPlatform === p.id
          const count = platformCounts[p.id] || 0
          return (
            <button
              key={p.id}
              onClick={() => {
                setSelectedPlatform(isActive ? null : p.id)
                setSelectedContentType(null)
              }}
              className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                isActive
                  ? "bg-primary text-primary-foreground shadow-md"
                  : "bg-card text-muted-foreground hover:bg-muted border"
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? "" : p.color}`} />
              <span className="hidden sm:inline">{p.name}</span>
              {count > 0 && (
                <span className="ml-1 rounded-full bg-muted px-2 py-0.5 text-xs">
                  {count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Content Type Sub-Directories (when platform selected) */}
      {selectedPlatform && (
        <div className="flex gap-2 flex-wrap">
          {PLATFORMS.find((p) => p.id === selectedPlatform)?.contentTypes.map((ct) => {
            const Icon = ct.icon
            const isActive = selectedContentType === ct.id
            return (
              <button
                key={ct.id}
                onClick={() => setSelectedContentType(isActive ? null : ct.id)}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/30"
                    : "bg-muted text-muted-foreground hover:bg-muted/80 border"
                }`}
              >
                <Icon className="h-3 w-3" />
                {ct.label}
              </button>
            )
          })}
        </div>
      )}

      {/* Search & View Toggle */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search media..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <div className="flex border rounded-lg">
          <button
            onClick={() => setViewMode("grid")}
            className={`p-2 ${viewMode === "grid" ? "bg-muted" : ""}`}
          >
            <Grid className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`p-2 ${viewMode === "list" ? "bg-muted" : ""}`}
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Breadcrumb */}
      {(selectedPlatform || selectedContentType) && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <FolderOpen className="h-4 w-4" />
          <span>Media</span>
          {selectedPlatform && (
            <>
              <span>/</span>
              <span className="font-medium text-foreground">
                {PLATFORMS.find((p) => p.id === selectedPlatform)?.name}
              </span>
            </>
          )}
          {selectedContentType && (
            <>
              <span>/</span>
              <span className="font-medium text-foreground">
                {PLATFORMS.find((p) => p.id === selectedPlatform)
                  ?.contentTypes.find((ct) => ct.id === selectedContentType)
                  ?.label}
              </span>
            </>
          )}
        </div>
      )}

      {/* Assets Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : displayAssets.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {selectedPlatform ? "No content yet" : "No media uploaded"}
            </h3>
            <p className="text-sm text-muted-foreground max-w-md mb-4">
              {selectedPlatform
                ? `Upload content to the ${PLATFORMS.find((p) => p.id === selectedPlatform)?.name} directory to get started.`
                : "Upload images, videos, and documents to organize by platform."}
            </p>
            <Button className="gap-2">
              <Upload className="h-4 w-4" />
              Upload Content
            </Button>
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {displayAssets.map((asset) => {
            const Icon = getAssetIcon(asset)
            const platform = PLATFORMS.find((p) => p.id === asset.platform)
            return (
              <Card
                key={asset.id}
                className="cursor-pointer hover:shadow-md transition-shadow group"
                onClick={() => setSelectedAsset(asset)}
              >
                <div className="aspect-square bg-muted flex items-center justify-center rounded-t-lg relative">
                  <Icon className="h-10 w-10 text-muted-foreground" />
                  {platform && (
                    <span className={`absolute top-2 right-2 rounded px-1.5 py-0.5 text-[10px] font-medium bg-background/80 ${platform.color}`}>
                      {platform.name}
                    </span>
                  )}
                  {asset.content_type && (
                    <span className="absolute bottom-2 left-2 rounded bg-background/80 px-1.5 py-0.5 text-[10px] font-medium">
                      {asset.content_type}
                    </span>
                  )}
                </div>
                <CardContent className="p-3">
                  <p className="text-sm font-medium truncate">{asset.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatSize(asset.size)}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : (
        <Card>
          <div className="divide-y">
            {displayAssets.map((asset) => {
              const Icon = getAssetIcon(asset)
              const platform = PLATFORMS.find((p) => p.id === asset.platform)
              return (
                <div
                  key={asset.id}
                  className="flex items-center gap-4 p-4 cursor-pointer hover:bg-muted/50"
                  onClick={() => setSelectedAsset(asset)}
                >
                  <Icon className="h-8 w-8 text-muted-foreground shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{asset.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatSize(asset.size)}
                      {asset.platform && ` · ${platform?.name}`}
                      {asset.content_type && ` · ${asset.content_type}`}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}
