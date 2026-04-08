import type { Metadata } from "next";
import { SiteHeader } from "@/components/shell/SiteHeader";

export const metadata: Metadata = {
  title: "Chat · BGEstate",
};

const SAMPLE_THREADS = [
  { id: "t1", title: "Varna apartment search", preview: "Found 23 apartments matching...", time: "2m ago", tab: "search" as const, unread: true },
  { id: "t2", title: "Investment yield analysis", preview: "Varna STR yield averages 4.08%...", time: "1h ago", tab: "search" as const, unread: false },
  { id: "t3", title: "Sarafovo 2-bed inquiry", preview: "Waiting for owner response...", time: "3h ago", tab: "property" as const, unread: true },
  { id: "t4", title: "Sozopol villa viewing", preview: "Available Saturday 10am–2pm", time: "1d ago", tab: "property" as const, unread: false },
];

export default function ChatPage() {
  return (
    <div className="min-h-screen flex flex-col bg-paper">
      <SiteHeader />

      <main className="flex-1 mx-auto w-full max-w-5xl px-4 py-6 sm:px-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-display text-2xl sm:text-3xl tracking-tight text-ink">Messages</h1>
            <p className="mt-1 text-sm text-mist">AI search chats and property conversations</p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
          {/* Thread list */}
          <div className="space-y-4">
            {/* Search threads */}
            <div>
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-mist mb-2 px-1">
                Search chats (AI)
              </h3>
              <div className="space-y-1.5">
                {SAMPLE_THREADS.filter((t) => t.tab === "search").map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    className="w-full text-left rounded-xl border border-line bg-panel p-3 hover:border-sea/30 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-sea to-sea-bright flex items-center justify-center text-white text-[10px] font-bold shrink-0">
                          AI
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-ink truncate">{t.title}</p>
                          <p className="text-xs text-mist truncate">{t.preview}</p>
                        </div>
                      </div>
                      <div className="shrink-0 flex flex-col items-end gap-1">
                        <span className="text-[10px] text-mist">{t.time}</span>
                        {t.unread && <span className="h-2 w-2 rounded-full bg-sea" />}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Property threads */}
            <div>
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-mist mb-2 px-1">
                Property chats
              </h3>
              <div className="space-y-1.5">
                {SAMPLE_THREADS.filter((t) => t.tab === "property").map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    className="w-full text-left rounded-xl border border-line bg-panel p-3 hover:border-sea/30 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-sand/20 flex items-center justify-center text-sand text-sm shrink-0">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                          </svg>
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-ink truncate">{t.title}</p>
                          <p className="text-xs text-mist truncate">{t.preview}</p>
                        </div>
                      </div>
                      <div className="shrink-0 flex flex-col items-end gap-1">
                        <span className="text-[10px] text-mist">{t.time}</span>
                        {t.unread && <span className="h-2 w-2 rounded-full bg-sand" />}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Chat area */}
          <div className="rounded-2xl border border-line bg-panel shadow-lift flex flex-col min-h-[500px]">
            <div className="px-5 py-4 border-b border-line">
              <p className="text-sm font-semibold text-ink">Varna apartment search</p>
              <p className="text-xs text-mist">AI assistant · Started 2m ago</p>
            </div>

            <div className="flex-1 p-5 space-y-4 overflow-y-auto">
              <div className="flex gap-2.5">
                <div className="shrink-0 h-7 w-7 rounded-full bg-gradient-to-br from-sea to-sea-bright flex items-center justify-center text-white text-[9px] font-bold">AI</div>
                <div className="max-w-[80%] rounded-2xl rounded-tl-md bg-paper border border-line px-4 py-2.5 text-sm text-ink leading-relaxed">
                  Hi! I can help you find properties in Bulgaria. I see you&apos;re interested in Varna apartments. The average price for a 2-bed in Varna is around €85K, with Sea Garden being the most popular district. Would you like me to search within a specific budget?
                </div>
              </div>

              <div className="flex gap-2.5 flex-row-reverse">
                <div className="shrink-0 h-7 w-7 rounded-full bg-sea flex items-center justify-center text-white text-[9px] font-bold">U</div>
                <div className="max-w-[80%] rounded-2xl rounded-tr-md bg-sea text-white px-4 py-2.5 text-sm leading-relaxed">
                  Show me 2-bed apartments in Varna under €90K with sea view
                </div>
              </div>

              <div className="flex gap-2.5">
                <div className="shrink-0 h-7 w-7 rounded-full bg-gradient-to-br from-sea to-sea-bright flex items-center justify-center text-white text-[9px] font-bold">AI</div>
                <div className="max-w-[80%] rounded-2xl rounded-tl-md bg-paper border border-line px-4 py-2.5 text-sm text-ink leading-relaxed">
                  <p>Found 23 apartments matching your criteria:</p>
                  <div className="mt-2 rounded-xl bg-sea/5 border border-sea/10 p-3 text-xs space-y-1">
                    <p className="font-semibold text-sea">Top picks:</p>
                    <p>• Sarafovo 2-bed, sea view — €89,000 (Homes.bg)</p>
                    <p>• Sea Garden studio+1 — €78,000 (imot.bg)</p>
                    <p>• Chaika 2-bed, balcony — €85,000 (OLX.bg)</p>
                  </div>
                  <p className="mt-2">I&apos;ve highlighted these on the map. The Sarafovo apartment has a pool and is 200m from the beach. Want me to show more details?</p>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-line/50">
              <p className="text-center text-xs text-mist">
                Use the chat bar at the bottom of any page to continue conversations.
                Full chat integration requires AI backend (BD-07).
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
