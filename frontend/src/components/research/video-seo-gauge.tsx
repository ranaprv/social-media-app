"use client"

interface VideoSEOGaugeProps {
  score: number
  size?: "sm" | "md" | "lg"
}

export function VideoSEOGauge({ score, size = "md" }: VideoSEOGaugeProps) {
  const getColor = (s: number) => {
    if (s >= 80) return "text-green-600 bg-green-50"
    if (s >= 50) return "text-yellow-600 bg-yellow-50"
    return "text-red-600 bg-red-50"
  }
  
  const getLabel = (s: number) => {
    if (s >= 80) return "Excellent"
    if (s >= 60) return "Good"
    if (s >= 40) return "Fair"
    return "Poor"
  }

  const sizeClasses = {
    sm: "h-12 w-12 text-lg",
    md: "h-16 w-16 text-2xl",
    lg: "h-20 w-20 text-3xl",
  }

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`flex items-center justify-center rounded-full ${getColor(score)} ${sizeClasses[size]} font-bold`}>
        {score}
      </div>
      <span className="text-xs text-muted-foreground">{getLabel(score)}</span>
    </div>
  )
}
