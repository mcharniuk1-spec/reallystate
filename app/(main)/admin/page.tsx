import type { Metadata } from "next";
import { SiteHeader } from "@/components/shell/SiteHeader";

export const metadata: Metadata = {
  title: "Admin · BGEstate",
};

const KPI_CARDS = [
  { label: "Active listings", value: "4,218", delta: "+12%", up: true },
  { label: "Sources online", value: "8 / 10", delta: "2 down", up: false },
  { label: "Crawl jobs (24h)", value: "342", delta: "+5%", up: true },
  { label: "Parser failures", value: "7", delta: "-3", up: true },
  { label: "Duplicate pairs", value: "23", delta: "pending", up: false },
  { label: "Avg freshness", value: "2.4h", delta: "target: 1h", up: false },
];

const SOURCES = [
  { name: "Homes.bg", status: "healthy", listings: 1240, lastCrawl: "12m ago" },
  { name: "imot.bg", status: "healthy", listings: 980, lastCrawl: "8m ago" },
  { name: "OLX.bg", status: "healthy", listings: 654, lastCrawl: "15m ago" },
  { name: "alo.bg", status: "healthy", listings: 412, lastCrawl: "22m ago" },
  { name: "SUPRIMMO", status: "healthy", listings: 328, lastCrawl: "18m ago" },
  { name: "Address.bg", status: "degraded", listings: 245, lastCrawl: "1h ago" },
  { name: "BulgarianProperties", status: "healthy", listings: 189, lastCrawl: "30m ago" },
  { name: "LUXIMMO", status: "healthy", listings: 102, lastCrawl: "45m ago" },
  { name: "property.bg", status: "down", listings: 0, lastCrawl: "3h ago" },
  { name: "imoti.net", status: "legal_hold", listings: 68, lastCrawl: "fixture only" },
];

const QUEUE_ITEMS = [
  { queue: "Parser failures", count: 7, severity: "warn" },
  { queue: "Duplicate review", count: 23, severity: "info" },
  { queue: "Geocode review", count: 5, severity: "info" },
  { queue: "Compliance hold", count: 2, severity: "critical" },
  { queue: "Publish queue", count: 0, severity: "ok" },
];

function StatusDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    healthy: "bg-emerald-400",
    degraded: "bg-amber-400",
    down: "bg-red-400 animate-pulse",
    legal_hold: "bg-purple-400",
  };
  return <span className={`inline-block h-2 w-2 rounded-full ${colors[status] ?? "bg-mist/40"}`} />;
}

export default function AdminPage() {
  return (
    <div className="min-h-screen flex flex-col bg-paper">
      <SiteHeader />

      <div className="border-b border-line bg-panel">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-2xl sm:text-3xl tracking-tight text-ink">Operator dashboard</h1>
              <p className="mt-1 text-sm text-mist">Source health, crawl jobs, and review queues</p>
            </div>
            <span className="hidden sm:inline rounded-full border border-warn/30 bg-warn/10 px-3 py-1 text-xs font-semibold text-warn">
              Demo data
            </span>
          </div>
        </div>
      </div>

      <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 space-y-6">
        {/* KPI row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {KPI_CARDS.map((kpi) => (
            <div key={kpi.label} className="rounded-2xl border border-line bg-panel p-4 shadow-lift">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-mist">{kpi.label}</p>
              <p className="mt-1 font-display text-2xl text-ink">{kpi.value}</p>
              <p className={`mt-0.5 text-xs font-medium ${kpi.up ? "text-emerald-600" : "text-warn"}`}>
                {kpi.delta}
              </p>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
          {/* Source health table */}
          <div className="rounded-2xl border border-line bg-panel shadow-lift overflow-hidden">
            <div className="px-5 py-4 border-b border-line flex items-center justify-between">
              <h2 className="text-sm font-semibold text-ink">Source health</h2>
              <span className="text-xs text-mist">{SOURCES.length} sources</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-line/50 text-xs text-mist">
                    <th className="text-left font-medium px-5 py-2.5">Source</th>
                    <th className="text-left font-medium px-3 py-2.5">Status</th>
                    <th className="text-right font-medium px-3 py-2.5">Listings</th>
                    <th className="text-right font-medium px-5 py-2.5">Last crawl</th>
                  </tr>
                </thead>
                <tbody>
                  {SOURCES.map((s) => (
                    <tr key={s.name} className="border-b border-line/30 hover:bg-paper/50 transition-colors">
                      <td className="px-5 py-3 font-medium text-ink">{s.name}</td>
                      <td className="px-3 py-3">
                        <span className="inline-flex items-center gap-1.5">
                          <StatusDot status={s.status} />
                          <span className={`text-xs capitalize ${
                            s.status === "healthy" ? "text-emerald-600" :
                            s.status === "degraded" ? "text-amber-600" :
                            s.status === "down" ? "text-red-600" :
                            "text-purple-600"
                          }`}>
                            {s.status.replace(/_/g, " ")}
                          </span>
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right text-mist tabular-nums">
                        {s.listings.toLocaleString()}
                      </td>
                      <td className="px-5 py-3 text-right text-mist text-xs">{s.lastCrawl}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Queues sidebar */}
          <div className="space-y-4">
            <div className="rounded-2xl border border-line bg-panel p-5 shadow-lift">
              <h2 className="text-sm font-semibold text-ink mb-3">Review queues</h2>
              <div className="space-y-2.5">
                {QUEUE_ITEMS.map((q) => (
                  <div key={q.queue} className="flex items-center justify-between py-2 border-b border-line/30 last:border-0">
                    <span className="text-sm text-ink">{q.queue}</span>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                      q.severity === "critical" ? "bg-red-100 text-red-700" :
                      q.severity === "warn" ? "bg-amber-100 text-amber-700" :
                      q.count === 0 ? "bg-emerald-100 text-emerald-700" :
                      "bg-mist/10 text-mist"
                    }`}>
                      {q.count}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent crawl activity */}
            <div className="rounded-2xl border border-line bg-panel p-5 shadow-lift">
              <h2 className="text-sm font-semibold text-ink mb-3">Recent activity</h2>
              <div className="space-y-3">
                {[
                  { time: "2m ago", text: "Homes.bg crawl completed — 42 new, 8 updated" },
                  { time: "8m ago", text: "imot.bg crawl completed — 31 new, 12 updated" },
                  { time: "15m ago", text: "OLX.bg API sync — 18 new listings" },
                  { time: "22m ago", text: "alo.bg crawl completed — 9 new, 3 removed" },
                  { time: "1h ago", text: "Address.bg timeout — retry scheduled" },
                ].map((a, i) => (
                  <div key={i} className="flex gap-2.5">
                    <span className="shrink-0 mt-1.5 h-1.5 w-1.5 rounded-full bg-sea/40" />
                    <div>
                      <p className="text-xs text-ink leading-relaxed">{a.text}</p>
                      <p className="text-[10px] text-mist">{a.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
