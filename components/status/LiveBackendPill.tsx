"use client";

import { useQuery } from "@tanstack/react-query";
import type { DevHealth } from "@/lib/types/api";

async function fetchHealth(): Promise<DevHealth> {
  const res = await fetch("/api/backend/health", { cache: "no-store" });
  if (!res.ok) {
    throw new Error("unreachable");
  }
  return res.json() as Promise<DevHealth>;
}

export function LiveBackendPill() {
  const q = useQuery({ queryKey: ["dev-health"], queryFn: fetchHealth, retry: 1, refetchInterval: 15_000 });

  if (q.isPending) {
    return (
      <span className="inline-flex items-center gap-2 rounded-full border border-line bg-panel px-3 py-1 text-xs font-medium text-mist">
        <span className="h-2 w-2 rounded-full bg-sand animate-pulse" aria-hidden />
        Checking API…
      </span>
    );
  }

  if (q.isError || !q.data || q.data.status !== "ok") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full border border-warn/40 bg-warn/10 px-3 py-1 text-xs font-medium text-warn">
        <span className="h-2 w-2 rounded-full bg-warn" aria-hidden />
        Dev API offline — run <code className="font-mono text-[11px]">make run-api</code>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-sea/30 bg-sea/10 px-3 py-1 text-xs font-medium text-sea">
      <span className="h-2 w-2 rounded-full bg-sea-bright" aria-hidden />
      Backend connected
    </span>
  );
}
