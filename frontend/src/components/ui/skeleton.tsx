import { useMemo } from "react"
import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
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
