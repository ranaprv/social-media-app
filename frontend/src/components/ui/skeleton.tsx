import { useState } from "react"
import { cn } from "@/lib/utils"

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} {...props} />
}

export function SkeletonCard() {
  return (
    <div className="rounded-lg border p-6">
      <div className="flex items-center justify-between pb-4">
        <Skeleton className="h-4 w-[120px]" />
        <Skeleton className="h-4 w-4" />
      </div>
      <Skeleton className="mb-2 h-8 w-[80px]" />
      <Skeleton className="h-3 w-[160px]" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      <div className="flex gap-4 border-b pb-2">
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 w-[100px]" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 py-2">
          <Skeleton className="h-4 w-[100px]" />
          <Skeleton className="h-4 w-[100px]" />
          <Skeleton className="h-4 w-[80px]" />
        </div>
      ))}
    </div>
  )
}

export function SkeletonChart() {
  const [heights] = useState(() => Array.from({ length: 12 }).map(() => 30 + Math.random() * 70))
  return (
    <div className="h-[300px] w-full rounded-lg border p-4">
      <Skeleton className="mb-4 h-4 w-[140px]" />
      <div className="flex h-[240px] items-end gap-2">
        {heights.map((h, i) => (
          <Skeleton
            key={i}
            className="flex-1"
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
    </div>
  )
}

export function SkeletonResearchCard({ count = 3 }: { count?: number }) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-lg border p-4 space-y-3">
          <div className="flex items-start justify-between">
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-[160px]" />
              <div className="flex gap-2">
                <Skeleton className="h-3 w-[80px]" />
                <Skeleton className="h-3 w-[60px]" />
                <Skeleton className="h-3 w-[70px]" />
              </div>
              <div className="flex gap-1 mt-1">
                <Skeleton className="h-4 w-[50px] rounded-full" />
                <Skeleton className="h-4 w-[50px] rounded-full" />
              </div>
            </div>
            <Skeleton className="h-12 w-12 rounded-full" />
          </div>
          <Skeleton className="h-6 w-[60px]" />
        </div>
      ))}
    </div>
  )
}

export function EmptyState({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-3 text-4xl">{icon}</div>
      <h3 className="mb-1 text-sm font-medium">{title}</h3>
      <p className="text-xs text-muted-foreground max-w-xs">{description}</p>
    </div>
  )
}
