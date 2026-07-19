"use client"

import { useState, useEffect, useMemo, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Image, Video, FileText, Search, Grid, List, Upload, FolderOpen,
  X, Globe, Camera, Share2, Tv, Eye, Download, Trash2, Loader2,
  Play, ExternalLink, Plus, CheckSquare, Square, Check, Type,
} from "lucide-react"
import type { MediaType, MediaAsset } from "@/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api"

interface PlatformContentType { id: string; label: string; icon: React.ElementType }
interface PlatformDef { id: string; name: string; icon: React.ElementType; color: string; contentTypes: PlatformContentType[] }

const PLATFORMS: PlatformDef[] = [
  { id: "youtube", name: "YouTube", icon: Tv, color: "text-red-500", contentTypes: [
    { id: "video", label: "Videos", icon: Video }, { id: "short", label: "Shorts", icon: Video }, { id: "image", label: "Thumbnails", icon: Image },
  ]},
  { id: "instagram", name: "Instagram", icon: Camera, color: "text-pink-500", contentTypes: [
    { id: "reel", label: "Reels", icon: Video }, { id: "carousel", label: "Carousels", icon: FileText }, { id: "vertical_video", label: "Vertical Videos", icon: Video }, { id: "image", label: "Images", icon: Image },
  ]},
  { id: "linkedin", name: "LinkedIn", icon: Share2, color: "text-blue-600", contentTypes: [
    { id: "post", label: "Posts", icon: FileText }, { id: "carousel", label: "Carousels", icon: FileText }, { id: "video", label: "Videos", icon: Video }, { id: "document", label: "Documents", icon: FileText },
  ]},
  { id: "facebook", name: "Facebook", icon: Globe, color: "text-blue-500", contentTypes: [
    { id: "image", label: "Images", icon: Image }, { id: "video", label: "Videos", icon: Video },
  ]},
]

type AddMediaTab = "image" | "video" | "text" | "pdf"

export function MediaLibrary() {
  const [assets, setAssets] = useState<MediaAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null)
  const [selectedContentType, setSelectedContentType] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [selectedAsset, setSelectedAsset] = useState<MediaAsset | null>(null)
  const [selectMode, setSelectMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Upload modal
  const [showUpload, setShowUpload] = useState(false)
  const [uploadPlatform, setUploadPlatform] = useState<string>("")
  const [uploadContentType, setUploadContentType] = useState<string>("")
  const [uploading, setUploading] = useState(false)
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null)
  const [uploadTags, setUploadTags] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Add Media modal
  const [showAddMedia, setShowAddMedia] = useState(false)
  const [addTab, setAddTab] = useState<AddMediaTab>("image")
  const [addPlatform, setAddPlatform] = useState<string>("")
  const [addContentType, setAddContentType] = useState<string>("")
  const [addTags, setAddTags] = useState("")
  const [addForm, setAddForm] = useState({ name: "", url: "", content: "", title: "" })
  const [adding, setAdding] = useState(false)

  // Fetch assets
  useEffect(() => {
    async function fetchAssets() {
      try {
        const params = new URLSearchParams()
        if (selectedPlatform) params.set("platform", selectedPlatform)
        if (selectedContentType) params.set("content_type", selectedContentType)
        if (searchQuery) params.set("search", searchQuery)
        const res = await fetch(`${API_URL}/media/assets?${params}`)
        if (res.ok) { const data = await res.json(); setAssets(data.assets || []) }
      } catch { setAssets([]) }
      finally { setLoading(false) }
    }
    fetchAssets()
  }, [selectedPlatform, selectedContentType, searchQuery])

  const displayAssets = useMemo(() => {
    if (!searchQuery) return assets
    const q = searchQuery.toLowerCase()
    return assets.filter(a => a.name.toLowerCase().includes(q) || (a.tags || []).some(t => t.toLowerCase().includes(q)))
  }, [assets, searchQuery])

  const platformCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    assets.forEach(a => { if (a.platform) counts[a.platform] = (counts[a.platform] || 0) + 1 })
    return counts
  }, [assets])

  const formatSize = (bytes: number) => {
    if (bytes === 0) return "—"
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getAssetIcon = (asset: MediaAsset) => {
    if (asset.type === "video" || ["reel", "short", "vertical_video"].includes(asset.content_type || "")) return Video
    if (asset.type === "pdf" || asset.content_type === "document") return FileText
    return Image
  }

  const isVideo = (a: MediaAsset) => a.type === "video" || ["reel", "short", "vertical_video"].includes(a.content_type || "")
  const isImage = (a: MediaAsset) => a.type === "image" || a.mime_type?.startsWith("image/")
  const isPdf = (a: MediaAsset) => a.type === "pdf" || a.mime_type?.includes("pdf")
  const isText = (a: MediaAsset) => a.content_type === "post" || a.content_type === "text" || a.mime_type?.startsWith("text/")
  const isEditable = (a: MediaAsset) => isText(a) || isPdf(a)

  // ── Select / Multi-select ────────────────────────────────────────────
  function toggleSelectMode() { setSelectMode(!selectMode); setSelectedIds(new Set()) }
  function toggleSelect(id: string) {
    setSelectedIds(prev => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next })
  }
  function selectAll() { setSelectedIds(new Set(displayAssets.map(a => a.id))) }

  // ── Delete ───────────────────────────────────────────────────────────
  async function deleteAsset(id: string) {
    try { await fetch(`${API_URL}/media/assets/${id}`, { method: "DELETE" }); setAssets(prev => prev.filter(a => a.id !== id)); setSelectedAsset(null) } catch {}
  }
  async function deleteSelected() {
    const ids = Array.from(selectedIds)
    for (const id of ids) { try { await fetch(`${API_URL}/media/assets/${id}`, { method: "DELETE" }) } catch {} }
    setAssets(prev => prev.filter(a => !selectedIds.has(a.id)))
    setSelectedIds(new Set()); setSelectMode(false)
  }

  // ── Upload files ─────────────────────────────────────────────────────
  async function handleUpload() {
    if (!uploadFiles || uploadFiles.length === 0) return
    setUploading(true)
    const tags = uploadTags.split(",").map(t => t.trim()).filter(Boolean)
    for (let i = 0; i < uploadFiles.length; i++) {
      const file = uploadFiles[i]
      const ext = file.name.split(".").pop()?.toLowerCase() || ""
      const isVid = ["mp4", "mov", "avi", "webm"].includes(ext)
      const isImg = ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(ext)
      const isPdfF = ext === "pdf"
      const assetType = isVid ? "video" : isPdfF ? "pdf" : isImg ? "image" : "document"
      try {
        await fetch(`${API_URL}/media/assets`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: file.name, type: assetType, url: `/uploads/${file.name}`, platform: uploadPlatform || null, content_type: uploadContentType || null, size: file.size, mime_type: file.type, tags }),
        })
      } catch {}
    }
    setUploading(false); setShowUpload(false); setUploadFiles(null); setUploadTags("")
    refreshAssets()
  }

  // ── Add Media (manual) ──────────────────────────────────────────────
  async function handleAddMedia() {
    if (!addForm.name.trim()) return
    setAdding(true)
    const tags = addTags.split(",").map(t => t.trim()).filter(Boolean)
    let assetType: MediaType = "image"
    let url = addForm.url || ""
    let content = ""

    if (addTab === "image") { assetType = "image"; url = addForm.url || "https://picsum.photos/seed/media-placeholder/800/600" }
    else if (addTab === "video") { assetType = "video"; url = addForm.url || "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" }
    else if (addTab === "text") { assetType = "pdf" as MediaType; content = addForm.content; url = `data:text/plain;base64,${btoa(addForm.content || addForm.title || "New text content")}` }
    else if (addTab === "pdf") { assetType = "pdf"; url = addForm.url || "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" }

    try {
      await fetch(`${API_URL}/media/assets`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: addForm.name, type: assetType, url, platform: addPlatform || null, content_type: addContentType || null, size: (content || url).length, mime_type: addTab === "text" ? "text/plain" : addTab === "pdf" ? "application/pdf" : addTab === "video" ? "video/mp4" : "image/jpeg", tags, content }),
      })
    } catch {}
    setAdding(false); setShowAddMedia(false); setAddForm({ name: "", url: "", content: "", title: "" }); setAddTags("")
    refreshAssets()
  }

  async function refreshAssets() {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedPlatform) params.set("platform", selectedPlatform)
      if (selectedContentType) params.set("content_type", selectedContentType)
      const res = await fetch(`${API_URL}/media/assets?${params}`)
      if (res.ok) { const data = await res.json(); setAssets(data.assets || []) }
    } catch {}
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Media Library</h2>
          <p className="text-muted-foreground">Organize content by platform for automatic scheduling.</p>
        </div>
        <div className="flex items-center gap-2">
          {selectMode && selectedIds.size > 0 && (
            <Button variant="destructive" size="sm" onClick={deleteSelected} className="gap-1">
              <Trash2 className="h-4 w-4" /> Delete ({selectedIds.size})
            </Button>
          )}
          <Button variant={selectMode ? "default" : "outline"} size="sm" onClick={toggleSelectMode} className="gap-1">
            {selectMode ? <CheckSquare className="h-4 w-4" /> : <Square className="h-4 w-4" />}
            {selectMode ? "Cancel" : "Select"}
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowAddMedia(true)} className="gap-1">
            <Plus className="h-4 w-4" /> Add Media
          </Button>
          <Button size="sm" onClick={() => setShowUpload(true)} className="gap-1">
            <Upload className="h-4 w-4" /> Upload
          </Button>
        </div>
      </div>

      {/* Platform Tabs */}
      <div className="flex gap-2 flex-wrap">
        <button onClick={() => { setSelectedPlatform(null); setSelectedContentType(null) }}
          className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${!selectedPlatform ? "bg-primary text-primary-foreground shadow-md" : "bg-card text-muted-foreground hover:bg-muted border"}`}>
          <Grid className="h-4 w-4" /> All
        </button>
        {PLATFORMS.map(p => {
          const Icon = p.icon; const isActive = selectedPlatform === p.id; const count = platformCounts[p.id] || 0
          return (
            <button key={p.id} onClick={() => { setSelectedPlatform(isActive ? null : p.id); setSelectedContentType(null) }}
              className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${isActive ? "bg-primary text-primary-foreground shadow-md" : "bg-card text-muted-foreground hover:bg-muted border"}`}>
              <Icon className={`h-4 w-4 ${isActive ? "" : p.color}`} />
              <span className="hidden sm:inline">{p.name}</span>
              {count > 0 && <span className="ml-1 rounded-full bg-muted px-2 py-0.5 text-xs">{count}</span>}
            </button>
          )
        })}
      </div>

      {/* Content Type Sub-Directories */}
      {selectedPlatform && (
        <div className="flex gap-2 flex-wrap">
          {PLATFORMS.find(p => p.id === selectedPlatform)?.contentTypes.map(ct => {
            const Icon = ct.icon; const isActive = selectedContentType === ct.id
            return (
              <button key={ct.id} onClick={() => setSelectedContentType(isActive ? null : ct.id)}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-all ${isActive ? "bg-primary/10 text-primary border border-primary/30" : "bg-muted text-muted-foreground hover:bg-muted/80 border"}`}>
                <Icon className="h-3 w-3" /> {ct.label}
              </button>
            )
          })}
        </div>
      )}

      {/* Search & View Toggle */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search media..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="pl-9" />
          {searchQuery && <button onClick={() => setSearchQuery("")} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></button>}
        </div>
        <div className="flex border rounded-lg">
          <button onClick={() => setViewMode("grid")} className={`p-2 ${viewMode === "grid" ? "bg-muted" : ""}`}><Grid className="h-4 w-4" /></button>
          <button onClick={() => setViewMode("list")} className={`p-2 ${viewMode === "list" ? "bg-muted" : ""}`}><List className="h-4 w-4" /></button>
        </div>
      </div>

      {/* Breadcrumb */}
      {(selectedPlatform || selectedContentType) && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <FolderOpen className="h-4 w-4" /><span>Media</span>
          {selectedPlatform && <><span>/</span><span className="font-medium text-foreground">{PLATFORMS.find(p => p.id === selectedPlatform)?.name}</span></>}
          {selectedContentType && <><span>/</span><span className="font-medium text-foreground">{PLATFORMS.find(p => p.id === selectedPlatform)?.contentTypes.find(ct => ct.id === selectedContentType)?.label}</span></>}
        </div>
      )}

      {/* Assets */}
      {loading ? (
        <div className="flex items-center justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
      ) : displayAssets.length === 0 ? (
        <Card><CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">{selectedPlatform ? "No content yet" : "No media uploaded"}</h3>
          <p className="text-sm text-muted-foreground max-w-md mb-4">Upload images, videos, and documents to organize by platform.</p>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setShowAddMedia(true)} className="gap-2"><Plus className="h-4 w-4" /> Add Media</Button>
            <Button onClick={() => setShowUpload(true)} className="gap-2"><Upload className="h-4 w-4" /> Upload</Button>
          </div>
        </CardContent></Card>
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {displayAssets.map(asset => {
            const Icon = getAssetIcon(asset); const platform = PLATFORMS.find(p => p.id === asset.platform); const isSelected = selectedIds.has(asset.id)
            return (
              <Card key={asset.id} className={`cursor-pointer hover:shadow-md transition-shadow group ${isSelected ? "ring-2 ring-primary" : ""}`}
                onClick={() => selectMode ? toggleSelect(asset.id) : setSelectedAsset(asset)}>
                <div className="aspect-square bg-muted flex items-center justify-center rounded-t-lg relative">
                  {selectMode && (
                    <div className="absolute top-2 left-2 z-10">
                      {isSelected ? <CheckSquare className="h-5 w-5 text-primary fill-primary/20" /> : <Square className="h-5 w-5 text-muted-foreground" />}
                    </div>
                  )}
                  {isVideo(asset) ? (
                    <div className="flex flex-col items-center justify-center gap-1">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 group-hover:bg-primary/30 transition-colors">
                        <Play className="h-6 w-6 text-primary fill-primary" />
                      </div>
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                  ) : isImage(asset) ? (
                    <img src={asset.url} alt={asset.name} className="w-full h-full object-cover rounded-t-lg" loading="lazy" />
                  ) : isText(asset) ? (
                    <div className="flex flex-col items-center justify-center gap-1 p-3">
                      <Type className="h-8 w-8 text-blue-500" />
                      <p className="text-[10px] text-muted-foreground text-center line-clamp-3">{asset.name}</p>
                    </div>
                  ) : (
                    <Icon className="h-10 w-10 text-muted-foreground" />
                  )}
                  {platform && <span className={`absolute top-2 right-2 rounded px-1.5 py-0.5 text-[10px] font-medium bg-background/80 ${platform.color}`}>{platform.name}</span>}
                  {asset.content_type && <span className="absolute bottom-2 left-2 rounded bg-background/80 px-1.5 py-0.5 text-[10px] font-medium">{asset.content_type}</span>}
                </div>
                <CardContent className="p-3">
                  <p className="text-sm font-medium truncate">{asset.name}</p>
                  <p className="text-xs text-muted-foreground">{formatSize(asset.size)}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : (
        <Card><div className="divide-y">
          {displayAssets.map(asset => {
            const Icon = getAssetIcon(asset); const platform = PLATFORMS.find(p => p.id === asset.platform); const isSelected = selectedIds.has(asset.id)
            return (
              <div key={asset.id} className={`flex items-center gap-4 p-4 cursor-pointer hover:bg-muted/50 ${isSelected ? "bg-primary/5" : ""}`}
                onClick={() => selectMode ? toggleSelect(asset.id) : setSelectedAsset(asset)}>
                {selectMode && <div className="shrink-0">{isSelected ? <CheckSquare className="h-5 w-5 text-primary fill-primary/20" /> : <Square className="h-5 w-5 text-muted-foreground" />}</div>}
                <Icon className="h-8 w-8 text-muted-foreground shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{asset.name}</p>
                  <p className="text-xs text-muted-foreground">{formatSize(asset.size)}{asset.platform && ` · ${platform?.name}`}{asset.content_type && ` · ${asset.content_type}`}</p>
                </div>
                {!selectMode && (
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-8 w-8" onClick={e => { e.stopPropagation(); setSelectedAsset(asset) }}><Eye className="h-4 w-4" /></Button>
                    <a href={asset.url} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-8 w-8"><Download className="h-4 w-4" /></Button>
                    </a>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={e => { e.stopPropagation(); deleteAsset(asset.id) }}><Trash2 className="h-4 w-4" /></Button>
                  </div>
                )}
              </div>
            )
          })}
        </div></Card>
      )}

      {/* ── Viewer/Player Modal ─────────────────────────────────────── */}
      {selectedAsset && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={() => setSelectedAsset(null)}>
          <div className="relative w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between bg-background rounded-t-xl px-4 py-3 border-b">
              <div className="flex items-center gap-3 min-w-0">
                {isVideo(selectedAsset) ? <Video className="h-5 w-5 text-red-500 shrink-0" /> :
                 isImage(selectedAsset) ? <Image className="h-5 w-5 text-blue-500 shrink-0" /> :
                 isText(selectedAsset) ? <Type className="h-5 w-5 text-blue-500 shrink-0" /> :
                 <FileText className="h-5 w-5 text-muted-foreground shrink-0" />}
                <div className="min-w-0">
                  <p className="font-medium truncate">{selectedAsset.name}</p>
                  <p className="text-xs text-muted-foreground">{formatSize(selectedAsset.size)}{selectedAsset.platform && ` · ${PLATFORMS.find(p => p.id === selectedAsset.platform)?.name}`}{selectedAsset.content_type && ` · ${selectedAsset.content_type}`}</p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <a href={selectedAsset.url} target="_blank" rel="noopener noreferrer">
                  <Button variant="ghost" size="sm" className="gap-1"><ExternalLink className="h-4 w-4" /> Open</Button>
                </a>
                <a href={selectedAsset.url} download={selectedAsset.name}>
                  <Button variant="ghost" size="sm" className="gap-1"><Download className="h-4 w-4" /> Download</Button>
                </a>
                <Button variant="ghost" size="sm" className="gap-1 text-destructive" onClick={() => deleteAsset(selectedAsset.id)}><Trash2 className="h-4 w-4" /> Delete</Button>
                <Button variant="ghost" size="icon" onClick={() => setSelectedAsset(null)}><X className="h-5 w-5" /></Button>
              </div>
            </div>
            <div className="bg-black rounded-b-xl flex-1 flex items-center justify-center overflow-auto min-h-[300px]">
              {isVideo(selectedAsset) ? (
                <video src={selectedAsset.url} controls autoPlay className="max-w-full max-h-[70vh] rounded-b-xl" poster={selectedAsset.thumbnail_url || selectedAsset.thumbnailUrl}>Your browser does not support video.</video>
              ) : isImage(selectedAsset) ? (
                <img src={selectedAsset.url} alt={selectedAsset.name} className="max-w-full max-h-[70vh] object-contain rounded-b-xl" />
              ) : isPdf(selectedAsset) ? (
                <iframe src={selectedAsset.url} className="w-full h-[70vh] rounded-b-xl border-0" title={selectedAsset.name} />
              ) : isText(selectedAsset) ? (
                <div className="w-full h-[70vh] bg-white rounded-b-xl overflow-auto p-8">
                  <div className="max-w-2xl mx-auto">
                    <h2 className="text-xl font-bold mb-4 text-gray-900">{selectedAsset.name}</h2>
                    <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap leading-relaxed">
                      {"content" in selectedAsset ? String((selectedAsset as Record<string, unknown>).content || "Text content — click Open to view in your default text editor, or Download to save locally.") : "Text content — click Open to view in your default text editor, or Download to save locally."}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-white/60 py-16">
                  <FileText className="mx-auto h-16 w-16 mb-4 opacity-30" />
                  <p className="text-lg font-medium">{selectedAsset.name}</p>
                  <p className="text-sm mt-1">{selectedAsset.mime_type || "Document"}</p>
                  <a href={selectedAsset.url} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" className="mt-4 text-white border-white/30 hover:bg-white/10"><ExternalLink className="h-4 w-4 mr-2" /> Open File</Button>
                  </a>
                </div>
              )}
            </div>
            {selectedAsset.tags && selectedAsset.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2 px-1">{selectedAsset.tags.map((tag, i) => <span key={i} className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-white/70">{tag}</span>)}</div>
            )}
          </div>
        </div>
      )}

      {/* ── Add Media Modal ────────────────────────────────────────── */}
      {showAddMedia && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowAddMedia(false)}>
          <Card className="w-full max-w-lg mx-4" onClick={e => e.stopPropagation()}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2"><Plus className="h-5 w-5 text-primary" /> Add Media</span>
                <button onClick={() => setShowAddMedia(false)} className="text-muted-foreground hover:text-foreground"><X className="h-5 w-5" /></button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Content type tabs */}
              <div className="flex gap-2">
                {([["image", "Image", Image], ["video", "Video", Video], ["text", "Text", Type], ["pdf", "PDF", FileText]] as const).map(([id, label, Icon]) => (
                  <button key={id} onClick={() => setAddTab(id as AddMediaTab)}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium transition-all ${addTab === id ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80"}`}>
                    <Icon className="h-3 w-3" /> {label}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs font-medium">Platform</label>
                  <select className="w-full rounded-lg border bg-background p-2 text-sm" value={addPlatform} onChange={e => { setAddPlatform(e.target.value); setAddContentType("") }}>
                    <option value="">No platform</option>
                    {PLATFORMS.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium">Content Type</label>
                  <select className="w-full rounded-lg border bg-background p-2 text-sm" value={addContentType} onChange={e => setAddContentType(e.target.value)}>
                    <option value="">Auto-detect</option>
                    {addPlatform ? PLATFORMS.find(p => p.id === addPlatform)?.contentTypes.map(ct => <option key={ct.id} value={ct.id}>{ct.label}</option>) : ["image", "video", "document"].map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>

              <div><label className="mb-1 block text-xs font-medium">Name *</label><Input placeholder="e.g. Summer Campaign Banner" value={addForm.name} onChange={e => setAddForm({ ...addForm, name: e.target.value })} /></div>

              {(addTab === "image" || addTab === "video" || addTab === "pdf") && (
                <div><label className="mb-1 block text-xs font-medium">URL</label><Input placeholder={addTab === "image" ? "https://example.com/image.jpg" : addTab === "video" ? "https://example.com/video.mp4" : "https://example.com/document.pdf"} value={addForm.url} onChange={e => setAddForm({ ...addForm, url: e.target.value })} /></div>
              )}
              {addTab === "text" && (
                <div><label className="mb-1 block text-xs font-medium">Content</label><textarea className="w-full rounded-lg border bg-background p-3 text-sm min-h-[120px]" placeholder="Write or paste your text content..." value={addForm.content} onChange={e => setAddForm({ ...addForm, content: e.target.value })} /></div>
              )}

              <div><label className="mb-1 block text-xs font-medium">Tags</label><Input placeholder="e.g. campaign, evergreen, product" value={addTags} onChange={e => setAddTags(e.target.value)} /></div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowAddMedia(false)}>Cancel</Button>
                <Button onClick={handleAddMedia} disabled={!addForm.name.trim() || adding} className="gap-2">
                  {adding ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                  {adding ? "Adding..." : "Add to Library"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Upload Modal ───────────────────────────────────────────── */}
      {showUpload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowUpload(false)}>
          <Card className="w-full max-w-lg mx-4" onClick={e => e.stopPropagation()}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2"><Upload className="h-5 w-5 text-primary" /> Upload Files</span>
                <button onClick={() => setShowUpload(false)} className="text-muted-foreground hover:text-foreground"><X className="h-5 w-5" /></button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs font-medium">Platform</label>
                  <select className="w-full rounded-lg border bg-background p-2 text-sm" value={uploadPlatform} onChange={e => { setUploadPlatform(e.target.value); setUploadContentType("") }}>
                    <option value="">No platform (general)</option>
                    {PLATFORMS.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium">Content Type</label>
                  <select className="w-full rounded-lg border bg-background p-2 text-sm" value={uploadContentType} onChange={e => setUploadContentType(e.target.value)}>
                    <option value="">Any type</option>
                    {uploadPlatform ? PLATFORMS.find(p => p.id === uploadPlatform)?.contentTypes.map(ct => <option key={ct.id} value={ct.id}>{ct.label}</option>) : ["image", "video", "document"].map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div><label className="mb-1 block text-xs font-medium">Tags</label><Input placeholder="e.g. campaign, product-launch" value={uploadTags} onChange={e => setUploadTags(e.target.value)} /></div>
              <div className="rounded-lg border-2 border-dashed p-8 text-center cursor-pointer hover:bg-muted/50 transition-colors" onClick={() => fileInputRef.current?.click()}>
                <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">{uploadFiles ? `${uploadFiles.length} file${uploadFiles.length > 1 ? "s" : ""} selected` : "Click to select files or drag & drop"}</p>
                <p className="text-xs text-muted-foreground mt-1">Images, videos, PDFs, documents</p>
                <input ref={fileInputRef} type="file" multiple accept="image/*,video/*,.pdf,.doc,.docx,.txt,.md" className="hidden" onChange={e => setUploadFiles(e.target.files)} />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowUpload(false)}>Cancel</Button>
                <Button onClick={handleUpload} disabled={!uploadFiles || uploading} className="gap-2">
                  {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                  {uploading ? "Uploading..." : "Upload"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
