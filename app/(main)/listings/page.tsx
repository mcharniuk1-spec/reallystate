import Link from "next/link";

import { AppShell } from "@/components/shell/AppShell";
import { fetchSources } from "@/lib/server/fetch-backend";

function tierStyle(tier: number) {
  if (tier <= 1) return "bg-sea/15 text-sea border-sea/25";
  if (tier === 2) return "bg-sand/20 text-warn border-sand/30";
  return "bg-mist/10 text-mist border-line";
}

export default async function ListingsPage() {
  const sources = await fetchSources();

  return (
    <AppShell
      title="Listings"
      subtitle="Infinite feed and filters will bind to `/listings` search APIs. For now, the source registry shows ingestion coverage and legal posture per portal."
    >
      {!sources.ok ? (
        <div className="rounded-2xl border border-warn/30 bg-warn/5 p-6 text-warn">{sources.error}</div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2">
          {sources.data.sources.map((s) => (
            <li
              key={s.source_name}
              className="group rounded-2xl border border-line bg-panel p-5 shadow-lift hover:border-sea/25 transition-colors"
            >
              <div className="flex flex-wrap items-start justify-between gap-2">
                <h2 className="font-display text-xl text-ink">{s.source_name}</h2>
                <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${tierStyle(s.tier)}`}>
                  Tier {s.tier}
                </span>
              </div>
              <p className="mt-2 text-sm text-mist line-clamp-2">{s.primary_url}</p>
              <dl className="mt-4 grid grid-cols-2 gap-2 text-xs text-mist">
                <div>
                  <dt className="uppercase tracking-wide">Family</dt>
                  <dd className="text-ink font-medium">{s.family}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide">Access</dt>
                  <dd className="text-ink font-medium">{s.access_mode}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide">Legal</dt>
                  <dd className="text-ink font-medium">{s.legal_mode}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide">Risk</dt>
                  <dd className="text-ink font-medium">{s.risk_mode}</dd>
                </div>
              </dl>
              <div className="mt-4 flex justify-end">
                <Link
                  href={`/properties/preview-${encodeURIComponent(s.source_name)}`}
                  className="text-sm font-semibold text-sea opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  Preview property shell →
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
