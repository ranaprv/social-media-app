"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { IdeaGenerator } from "@/components/content-studio/idea-generator"
import { ContentGenerator } from "@/components/content-studio/content-generator"
import { WritingTools } from "@/components/content-studio/writing-tools"
import { BrandVoiceConfig } from "@/components/content-studio/brand-voice"
import { Lightbulb, PenTool, Wand2, BookOpen, Sparkles } from "lucide-react"

const TABS = [
  { id: "ideas" as const, label: "Idea Generator", icon: Lightbulb },
  { id: "generate" as const, label: "Content Generator", icon: PenTool },
  { id: "tools" as const, label: "Writing Tools", icon: Wand2 },
  { id: "brand-voice" as const, label: "Brand Voice", icon: BookOpen },
]

interface SavedIdea {
  title: string
  description: string
  platforms: string[]
  content_type: string
}

export default function ContentStudioPage() {
  const [activeTab, setActiveTab] = useState<"ideas" | "generate" | "tools" | "brand-voice">("ideas")
  const [savedIdea, setSavedIdea] = useState<SavedIdea | null>(null)

  function handleSaveIdea(idea: SavedIdea) {
    setSavedIdea(idea)
    setActiveTab("generate")
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="h-6 w-6 text-primary" />
            <h1 className="text-3xl font-bold">AI Content Studio</h1>
          </div>
          <p className="text-muted-foreground">Generate ideas, create content, refine your writing, and train your brand voice — all powered by AI.</p>
        </div>

        <div className="flex gap-2">
          {TABS.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${isActive ? "bg-primary text-primary-foreground shadow-md" : "bg-card text-muted-foreground hover:bg-muted hover:text-foreground border"}`}>
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            )
          })}
        </div>

        <div>
          {activeTab === "ideas" && <IdeaGenerator onSaveIdea={handleSaveIdea} />}
          {activeTab === "generate" && <ContentGenerator savedIdea={savedIdea} onClearIdea={() => setSavedIdea(null)} />}
          {activeTab === "tools" && <WritingTools />}
          {activeTab === "brand-voice" && <BrandVoiceConfig />}
        </div>
      </div>
    </DashboardLayout>
  )
}
