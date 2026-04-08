import Link from "next/link";

import { AppShell } from "@/components/shell/AppShell";
import { LiveBackendPill } from "@/components/status/LiveBackendPill";
import { fetchDevHealth, fetchSources } from "@/lib/server/fetch-backend";

export default async function HomePage() {
  const [health, sources] = await Promise.all([fetchDevHealth(), fetchSources()]);

  return (
    <AppShell>
      <div className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
        <section>
          <p className="text-sm font-semibold uppercase tracking-widest text-sea">Platform shell</p>
          <h1 className="mt-3 font-display text-5xl sm:text-6xl tracking-tight text-balance leading-[1.05] text-ink">
            One surface for listings, map, and CRM
          </h1>
          <p className="mt-6 text-lg text-mist max-w-xl leading-relaxed">
            This UI follows the MVP route order: listings and property detail first, then map, chat, settings, and
            operator admin. It already reads your Python dev API for health and the source registry.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-4">
            <LiveBackendPill />
            {health.ok && (
              <span className="text-sm text-mist">
                Stage: <span className="text-ink font-medium">{health.data.stage ?? "—"}</span>
              </span>
            )}
          </div>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              href="/listings"
              className="inline-flex items-center justify-center rounded-full bg-sea px-6 py-3 text-sm font-semibold text-white shadow-lift hover:bg-sea-bright transition-colors"
            >
              Open listings
            </Link>
            <Link
              href="/map"
              className="inline-flex items-center justify-center rounded-full border border-line bg-panel px-6 py-3 text-sm font-semibold text-ink hover:border-sea/40 transition-colors"
            >
              Map preview
            </Link>
          </div>
        </section>

        <aside className="rounded-3xl border border-line bg-panel p-8 shadow-lift">
          <h2 className="font-display text-2xl text-ink">Registry snapshot</h2>
          <p className="mt-2 text-sm text-mist leading-relaxed">
            Live from <code className="text-ink bg-paper px-1 rounded">GET /sources</code> on the dev API.
          </p>
          {!sources.ok ? (
            <p className="mt-6 text-sm text-warn">{sources.error}</p>
          ) : (
            <dl className="mt-6 grid grid-cols-2 gap-4">
              <div className="rounded-2xl bg-paper p-4 border border-line/80">
                <dt className="text-xs uppercase tracking-wide text-mist">Sources</dt>
                <dd className="mt-1 font-display text-3xl text-ink">{sources.data.count}</dd>
              </div>
              <div className="rounded-2xl bg-paper p-4 border border-line/80">
                <dt className="text-xs uppercase tracking-wide text-mist">API</dt>
                <dd className="mt-1 text-lg font-semibold text-sea">{health.ok ? "Reachable" : "Down"}</dd>
              </div>
            </dl>
          )}
        </aside>
      </div>
    </AppShell>
  );
}
