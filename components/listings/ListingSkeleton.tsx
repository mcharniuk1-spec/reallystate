export function ListingSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3 p-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="rounded-2xl border border-line bg-panel p-3 space-y-3"
        >
          <div className="skeleton aspect-[16/10]" />
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 space-y-2">
              <div className="skeleton h-5 w-24" />
              <div className="skeleton h-3 w-32" />
            </div>
            <div className="skeleton h-5 w-16 rounded-full" />
          </div>
          <div className="flex gap-2">
            <div className="skeleton h-3 w-16" />
            <div className="skeleton h-3 w-12" />
            <div className="skeleton h-3 w-14" />
          </div>
          <div className="flex justify-between">
            <div className="skeleton h-2.5 w-20" />
            <div className="skeleton h-2.5 w-12" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function PropertyDetailSkeleton() {
  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
      <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-6">
          <div className="skeleton aspect-[16/10] rounded-3xl" />
          <div className="skeleton h-32 rounded-2xl" />
          <div className="skeleton h-24 rounded-2xl" />
        </div>
        <div className="space-y-5">
          <div className="skeleton h-36 rounded-2xl" />
          <div className="skeleton h-48 rounded-2xl" />
          <div className="skeleton h-28 rounded-2xl" />
          <div className="skeleton h-32 rounded-2xl" />
        </div>
      </div>
    </div>
  );
}
