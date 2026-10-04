/**
 * AirVision AI — loading skeletons
 * Shimmer placeholders shown while data is being fetched.
 */

export function Skeleton({ className = '' }) {
  return (
    <div
      className={`animate-pulse rounded-xl bg-slate-200 dark:bg-slate-800 ${className}`}
    />
  )
}

export function KpiSkeleton() {
  return (
    <div className="card p-5">
      <Skeleton className="mb-3 h-4 w-24" />
      <Skeleton className="mb-2 h-9 w-28" />
      <Skeleton className="h-3 w-20" />
    </div>
  )
}

export function ChartSkeleton({ height = 260 }) {
  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-4 w-20" />
      </div>
      <Skeleton className="mb-3 h-40 w-full" />
      <div className="space-y-2" style={{ height }}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="animate-pulse rounded bg-slate-200 dark:bg-slate-800"
            style={{ height: `${(height / 6) - 4}px`, opacity: 1 - i * 0.12 }}
          />
        ))}
      </div>
    </div>
  )
}

export function TableSkeleton({ rows = 6 }) {
  return (
    <div className="space-y-2.5">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full" />
      ))}
    </div>
  )
}
