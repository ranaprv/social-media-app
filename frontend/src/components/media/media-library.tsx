"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Image,
  Video,
  FileText,
  Palette,
  Stamp,
  Layout,
  Search,
  Grid,
  List,
  Upload,
  FolderPlus,
  X,
  Tag,
  MoreHorizontal,
  Download,
  Trash2,
  Eye,
  Pencil,
  Calendar,
  HardDrive,
} from "lucide-react"
import type { MediaType, MediaAsset } from "@/types"

const TYPE_FILTERS: { value: MediaType | "all"; label: string; icon: React.ElementType }[] = [
  { value: "all", label: "All", icon: Grid },
  { value: "image", label: "Images", icon: Image },
  { value: "video", label: "Videos", icon: Video },
  { value: "pdf", label: "PDFs", icon: FileText },
  { value: "brand-asset", label: "Brand Assets", icon: Palette },
  { value: "logo", label: "Logos", icon: Stamp },
  { value: "template", label: "Templates", icon: Layout },
]

const TYPE_COLORS: Record<MediaType, string> = {
  image: "bg-blue-100 text-blue-700",
  video: "bg-purple-100 text-purple-700",
  pdf: "bg-red-100 text-red-700",
  "brand-asset": "bg-amber-100 text-amber-700",
  logo: "bg-green-100 text-green-700",
  template: "bg-cyan-100 text-cyan-700",
}

const TYPE_ICONS: Record<MediaType, React.ElementType> = {
  image: Image,
  video: Video,
  pdf: FileText,
  "brand-asset": Palette,
  logo: Stamp,
  template: Layout,
}

const DEMO_ASSETS: MediaAsset[] = [
  { id: "ma-1", name: "hero-banner.png", type: "image", url: "/assets/hero-banner.png", size: 245000, mimeType: "image/png", tags: ["banner", "hero", "marketing"], folder: "campaigns", uploadedBy: "user-1", uploadedByName: "You", createdAt: "2026-07-11", metadata: { width: 1200, height: 630 } },
  { id: "ma-2", name: "product-demo.mp4", type: "video", url: "/assets/product-demo.mp4", size: 15400000, mimeType: "video/mp4", tags: ["demo", "product", "tutorial"], folder: "videos", uploadedBy: "user-2", uploadedByName: "Sarah Chen", createdAt: "2026-07-13", metadata: { duration: "2:00", resolution: "1080p" } },
  { id: "ma-3", name: "brand-guidelines.pdf", type: "pdf", url: "/assets/brand-guidelines.pdf", size: 890000, mimeType: "application/pdf", tags: ["brand", "guidelines", "design"], folder: "brand", uploadedBy: "user-1", uploadedByName: "You", createdAt: "2026-06-16", metadata: { pages: 24 } },
  { id: "ma-4", name: "company-logo.svg", type: "logo", url: "/assets/company-logo.svg", size: 12000, mimeType: "image/svg+xml", tags: ["logo", "brand"], folder: "brand", uploadedBy: "user-1", uploadedByName: "You", createdAt: "2026-05-17", metadata: {} },
  { id: "ma-5", name: "post-template-linkedin.psd", type: "template", url: "/assets/templates/linkedin-post.psd", size: 3400000, mimeType: "application/octet-stream", tags: ["template", "linkedin", "design"], folder: "templates", uploadedBy: "user-3", uploadedByName: "Marcus Johnson", createdAt: "2026-07-02", metadata: { dimensions: "1200x627" } },
  { id: "ma-6", name: "infographic-q2.png", type: "image", url: "/assets/infographic-q2.png", size: 520000, mimeType: "image/png", tags: ["infographic", "data", "q2"], folder: "campaigns", uploadedBy: "user-4", uploadedByName: "Priya Patel", createdAt: "2026-07-09", metadata: { width: 1080, height: 1920 } },
  { id: "ma-7", name: "webinar-recording.mp4", type: "video", url: "/assets/webinar-recording.mp4", size: 89000000, mimeType: "video/mp4", tags: ["webinar", "recording", "education"], folder: "videos", uploadedBy: "user-1", uploadedByName: "You", createdAt: "2026-07-06", metadata: { duration: "40:00", resolution: "1080p" } },
  { id: "ma-8", name: "social-templates-bundle.zip", type: "template", url: "/assets/templates/social-bundle.zip", size: 12000000, mimeType: "application/zip", tags: ["template", "bundle", "social"], folder: "templates", uploadedBy: "user-2", uploadedByName: "Sarah Chen", createdAt: "2026-06-26", metadata: { count: 15 } },
  { id: "ma-9", name: "icon-set-brand.svg", type: "brand-asset", url: "/assets/brand/icon-set.svg", size: 45000, mimeType: "image/svg+xml", tags: ["icons", "brand", "ui"], folder: "brand", uploadedBy: "user-1", uploadedByName: "You", createdAt: "2026-06-01", metadata: { icons: 50 } },
  { id: "ma-10", name: "quote-card-template.png", type: "template", url: "/assets/templates/quote-card.png", size: 180000, mimeType: "image/png", tags: ["template", "quote", "social"], folder: "templates", uploadedBy: "user-3", uploadedByName: "Marcus Johnson", createdAt: "2026-07-08", metadata: { dimensions: "1080x1080" } },
]

const FOLDERS = [
  { id: "campaigns", name: "Campaigns", count: 2 },
  { id: "videos", name: "Videos", count: 2 },
  { id: "brand", name: "Brand", count: 3 },
  { id: "templates", name: "Templates", count: 3 },
]

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function MediaLibrary() {
  const [searchQuery, setSearchQuery] = useState("")
  const [typeFilter, setTypeFilter] = useState<MediaType | "all">("all")
  const [folderFilter, setFolderFilter] = useState<string | "all">("all")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [selectedAsset, setSelectedAsset] = useState<MediaAsset | null>(null)
  const [showUpload, setShowUpload] = useState(false)
  const [allTags, setAllTags] = useState<string[]>([])
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  const filteredAssets = useMemo(() => {
    let assets = DEMO_ASSETS

    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      assets = assets.filter(
        (a) => a.name.toLowerCase().includes(q) || a.tags.some((t) => t.includes(q))
      )
    }

    if (typeFilter !== "all") {
      assets = assets.filter((a) => a.type === typeFilter)
    }

    if (folderFilter !== "all") {
      assets = assets.filter((a) => a.folder === folderFilter)
    }

    if (selectedTags.length > 0) {
      assets = assets.filter((a) => selectedTags.some((t) => a.tags.includes(t)))
    }

    return assets
  }, [searchQuery, typeFilter, folderFilter, selectedTags])

  const uniqueTags = useMemo(() => {
    const tags = new Set<string>()
    DEMO_ASSETS.forEach((a) => a.tags.forEach((t) => tags.add(t)))
    return Array.from(tags).sort()
  }, [])

  const totalSize = useMemo(() => DEMO_ASSETS.reduce((sum, a) => sum + a.size, 0), [])

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Total Assets", value: DEMO_ASSETS.length.toString(), icon: HardDrive, color: "text-blue-500" },
          { label: "Total Size", value: formatSize(totalSize), icon: HardDrive, color: "text-purple-500" },
          { label: "Folders", value: FOLDERS.length.toString(), icon: FolderPlus, color: "text-green-500" },
          { label: "Tags", value: uniqueTags.length.toString(), icon: Tag, color: "text-orange-500" },
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4 flex items-center gap-3">
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
              <div>
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search assets by name or tag..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="flex rounded-lg border overflow-hidden">
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 ${viewMode === "grid" ? "bg-primary text-primary-foreground" : "bg-background"}`}
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 ${viewMode === "list" ? "bg-primary text-primary-foreground" : "bg-background"}`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
            <Button className="gap-1.5" onClick={() => setShowUpload(true)}>
              <Upload className="h-4 w-4" />
              Upload
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-56 flex-shrink-0 space-y-4">
          {/* Type Filters */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium text-muted-foreground uppercase">Type</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {TYPE_FILTERS.map((tf) => {
                const Icon = tf.icon
                return (
                  <button
                    key={tf.value}
                    onClick={() => setTypeFilter(tf.value)}
                    className={`w-full flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm transition-all ${
                      typeFilter === tf.value
                        ? "bg-primary/10 text-primary font-medium"
                        : "text-muted-foreground hover:bg-muted"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {tf.label}
                  </button>
                )
              })}
            </CardContent>
          </Card>

          {/* Folders */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium text-muted-foreground uppercase">Folders</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              <button
                onClick={() => setFolderFilter("all")}
                className={`w-full flex items-center justify-between rounded-lg px-3 py-1.5 text-sm transition-all ${
                  folderFilter === "all"
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-muted-foreground hover:bg-muted"
                }`}
              >
                <span>All Folders</span>
                <span className="text-xs">{DEMO_ASSETS.length}</span>
              </button>
              {FOLDERS.map((f) => (
                <button
                  key={f.id}
                  onClick={() => setFolderFilter(f.id)}
                  className={`w-full flex items-center justify-between rounded-lg px-3 py-1.5 text-sm transition-all ${
                    folderFilter === f.id
                      ? "bg-primary/10 text-primary font-medium"
                      : "text-muted-foreground hover:bg-muted"
                  }`}
                >
                  <span>{f.name}</span>
                  <span className="text-xs">{f.count}</span>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Tags */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-medium text-muted-foreground uppercase">Tags</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-1.5">
                {uniqueTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() =>
                      setSelectedTags((prev) =>
                        prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
                      )
                    }
                    className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
                      selectedTags.includes(tag)
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:bg-muted/80"
                    }`}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Asset Grid/List */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-muted-foreground">
              {filteredAssets.length} asset{filteredAssets.length !== 1 ? "s" : ""}
            </p>
          </div>

          {viewMode === "grid" ? (
            <div className="grid grid-cols-3 gap-3">
              {filteredAssets.map((asset) => {
                const Icon = TYPE_ICONS[asset.type]
                return (
                  <Card
                    key={asset.id}
                    className="cursor-pointer transition-all hover:shadow-md"
                    onClick={() => setSelectedAsset(asset)}
                  >
                    <div className="aspect-square bg-muted/50 flex items-center justify-center rounded-t-xl">
                      <Icon className="h-12 w-12 text-muted-foreground/30" />
                    </div>
                    <CardContent className="p-3">
                      <p className="text-sm font-medium truncate">{asset.name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_COLORS[asset.type]}`}>
                          {asset.type}
                        </span>
                        <span className="text-[10px] text-muted-foreground">{formatSize(asset.size)}</span>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            <Card>
              <CardContent className="p-0">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left p-3 font-medium text-muted-foreground">Name</th>
                      <th className="text-left p-3 font-medium text-muted-foreground">Type</th>
                      <th className="text-left p-3 font-medium text-muted-foreground">Size</th>
                      <th className="text-left p-3 font-medium text-muted-foreground">Tags</th>
                      <th className="text-left p-3 font-medium text-muted-foreground">Date</th>
                      <th className="p-3"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAssets.map((asset) => {
                      const Icon = TYPE_ICONS[asset.type]
                      return (
                        <tr
                          key={asset.id}
                          className="border-b last:border-0 hover:bg-muted/30 cursor-pointer"
                          onClick={() => setSelectedAsset(asset)}
                        >
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              <Icon className="h-4 w-4 text-muted-foreground" />
                              <span className="font-medium">{asset.name}</span>
                            </div>
                          </td>
                          <td className="p-3">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_COLORS[asset.type]}`}>
                              {asset.type}
                            </span>
                          </td>
                          <td className="p-3 text-muted-foreground">{formatSize(asset.size)}</td>
                          <td className="p-3">
                            <div className="flex gap-1">
                              {asset.tags.slice(0, 2).map((t) => (
                                <span key={t} className="text-[10px] bg-muted rounded px-1.5 py-0.5">#{t}</span>
                              ))}
                              {asset.tags.length > 2 && (
                                <span className="text-[10px] text-muted-foreground">+{asset.tags.length - 2}</span>
                              )}
                            </div>
                          </td>
                          <td className="p-3 text-muted-foreground text-xs">{asset.createdAt}</td>
                          <td className="p-3">
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={() => setSelectedAsset(null)}>
          <Card className="max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{selectedAsset.name}</CardTitle>
                <Button variant="ghost" size="icon" onClick={() => setSelectedAsset(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                {(() => {
                  const Icon = TYPE_ICONS[selectedAsset.type]
                  return <Icon className="h-16 w-16 text-muted-foreground/30" />
                })()}
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Type:</span>{" "}
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_COLORS[selectedAsset.type]}`}>
                    {selectedAsset.type}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Size:</span> {formatSize(selectedAsset.size)}
                </div>
                <div>
                  <span className="text-muted-foreground">Folder:</span> {selectedAsset.folder || "Root"}
                </div>
                <div>
                  <span className="text-muted-foreground">Uploaded:</span> {selectedAsset.uploadedByName}
                </div>
              </div>
              <div>
                <span className="text-muted-foreground text-sm">Tags:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {selectedAsset.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex gap-2 pt-2">
                <Button variant="outline" className="flex-1 gap-1.5">
                  <Download className="h-4 w-4" />
                  Download
                </Button>
                  <Button variant="outline" className="gap-1.5">
                    <Pencil className="h-4 w-4" />
                    Edit
                  </Button>
                <Button variant="destructive" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" onClick={() => setShowUpload(false)}>
          <Card className="max-w-md w-full" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Upload Assets</CardTitle>
                <Button variant="ghost" size="icon" onClick={() => setShowUpload(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-12 w-12 mx-auto mb-3 text-muted-foreground/30" />
                <p className="text-sm font-medium">Drop files here or click to browse</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Images, Videos, PDFs, and more
                </p>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1 block">Folder</label>
                <select className="w-full rounded-lg border bg-background px-3 py-2 text-sm">
                  <option value="">Root</option>
                  {FOLDERS.map((f) => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1 block">Tags</label>
                <Input placeholder="Add tags (comma separated)" />
              </div>
              <Button className="w-full gap-1.5">
                <Upload className="h-4 w-4" />
                Upload
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
