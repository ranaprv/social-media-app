"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Languages,
  Copy,
  Loader2,
  Globe,
} from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

const LANGUAGES = [
  { code: "es", name: "Spanish" },
  { code: "fr", name: "French" },
  { code: "de", name: "German" },
  { code: "it", name: "Italian" },
  { code: "pt", name: "Portuguese" },
  { code: "ja", name: "Japanese" },
  { code: "ko", name: "Korean" },
  { code: "zh", name: "Chinese" },
  { code: "ar", name: "Arabic" },
  { code: "hi", name: "Hindi" },
  { code: "ru", name: "Russian" },
  { code: "nl", name: "Dutch" },
]

interface TranslationResult {
  translated: string
  target_language: string
  target_language_name: string
  char_count: number
  error?: string
}

interface MultiLangTranslatorProps {
  initialCaption?: string
}

export function MultiLangTranslator({ initialCaption = "" }: MultiLangTranslatorProps) {
  const [caption, setCaption] = useState(initialCaption)
  const [selectedLangs, setSelectedLangs] = useState<string[]>(["es", "fr", "de"])
  const [results, setResults] = useState<Record<string, TranslationResult>>({})
  const [loading, setLoading] = useState(false)

  const toggleLang = (code: string) => {
    setSelectedLangs((prev) =>
      prev.includes(code) ? prev.filter((l) => l !== code) : [...prev, code]
    )
  }

  const translate = async () => {
    if (!caption || selectedLangs.length === 0) return
    setLoading(true)
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (token) headers["Authorization"] = `Bearer ${token}`

      const response = await fetch(`${API_BASE}/scheduler/translate/multi`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          caption,
          target_languages: selectedLangs,
        }),
      })
      if (response.ok) {
        const data = await response.json()
        setResults(data.translations || {})
      }
    } finally {
      setLoading(false)
    }
  }

  const copyTranslation = async (text: string) => {
    await navigator.clipboard.writeText(text)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Languages className="h-4 w-4" />
          Multi-Language Translator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Textarea
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          placeholder="Enter caption to translate..."
          className="min-h-[60px] text-sm"
        />

        <div className="flex flex-wrap gap-1.5">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => toggleLang(lang.code)}
              className={`rounded-full px-2 py-0.5 text-[10px] font-medium transition-all ${
                selectedLangs.includes(lang.code)
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {lang.name}
            </button>
          ))}
        </div>

        <Button onClick={translate} disabled={loading || !caption || selectedLangs.length === 0} className="w-full" size="sm">
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Globe className="h-4 w-4 mr-2" />}
          {loading ? "Translating..." : `Translate to ${selectedLangs.length} language(s)`}
        </Button>

        {Object.keys(results).length > 0 && (
          <div className="space-y-2 pt-2 border-t">
            {Object.entries(results).map(([code, result]) => (
              <div key={code} className="rounded-lg border p-2.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[9px]">{result.target_language_name}</Badge>
                  {!result.error && (
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => copyTranslation(result.translated)}>
                      <Copy className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                {result.error ? (
                  <p className="text-[10px] text-red-500">{result.error}</p>
                ) : (
                  <p className="text-xs">{result.translated}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
