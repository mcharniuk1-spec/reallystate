import type { Metadata } from "next";
import { SiteHeader } from "@/components/shell/SiteHeader";

export const metadata: Metadata = {
  title: "Settings · BGEstate",
};

const SAVED_SEARCHES = [
  { name: "Varna 2-bed under €90K", filters: "Buy · Apartment · 2 rooms · €50K–€90K · Varna", alerts: true },
  { name: "Burgas sea view rentals", filters: "Rent · All types · Sea view · Burgas coast", alerts: true },
  { name: "Sofia investment apartments", filters: "Buy · Apartment · Studio/1-bed · Sofia", alerts: false },
];

const SAVED_PROPERTIES = [
  { id: "demo-001", title: "3-room apartment", location: "Lozenets, Sofia", price: "€185,000" },
  { id: "demo-004", title: "2-room apartment", location: "Sarafovo, Burgas", price: "€89,000" },
  { id: "demo-006", title: "Luxury villa", location: "Sozopol", price: "€340,000" },
];

export default function SettingsPage() {
  return (
    <div className="min-h-screen flex flex-col bg-paper">
      <SiteHeader />

      <div className="border-b border-line bg-panel">
        <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6">
          <h1 className="font-display text-2xl sm:text-3xl tracking-tight text-ink">Settings</h1>
          <p className="mt-1 text-sm text-mist">Manage your profile, saved searches, and alert preferences</p>
        </div>
      </div>

      <main className="flex-1 mx-auto w-full max-w-4xl px-4 py-6 sm:px-6 space-y-6">
        {/* Profile */}
        <section className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
          <h2 className="text-sm font-semibold text-ink mb-4">Profile</h2>
          <div className="flex items-start gap-4">
            <div className="h-14 w-14 rounded-full bg-gradient-to-br from-sea to-sea-bright flex items-center justify-center text-white text-lg font-bold shrink-0">
              U
            </div>
            <div className="flex-1 space-y-3">
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="block text-xs text-mist mb-1">Name</label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink placeholder:text-mist/40 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20"
                    disabled
                  />
                </div>
                <div>
                  <label className="block text-xs text-mist mb-1">Email</label>
                  <input
                    type="email"
                    placeholder="you@example.com"
                    className="w-full rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink placeholder:text-mist/40 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20"
                    disabled
                  />
                </div>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="block text-xs text-mist mb-1">Language</label>
                  <select className="w-full rounded-xl border border-line bg-paper px-3 py-2 text-sm text-ink focus:outline-none focus:border-sea/40" disabled>
                    <option>English</option>
                    <option>Български</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-mist mb-1">Mode</label>
                  <div className="flex gap-1 rounded-xl bg-paper border border-line p-1">
                    <span className="rounded-lg bg-sea text-white px-3 py-1.5 text-xs font-semibold">Buyer</span>
                    <span className="rounded-lg px-3 py-1.5 text-xs text-mist">Renter</span>
                    <span className="rounded-lg px-3 py-1.5 text-xs text-mist">Seller</span>
                  </div>
                </div>
              </div>
              <p className="text-[10px] text-mist/60">Profile editing requires auth backend (BD-13)</p>
            </div>
          </div>
        </section>

        {/* Saved searches */}
        <section className="rounded-2xl border border-line bg-panel shadow-lift overflow-hidden">
          <div className="px-6 py-4 border-b border-line flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink">Saved searches</h2>
            <span className="text-xs text-mist">{SAVED_SEARCHES.length} searches</span>
          </div>
          <div className="divide-y divide-line/50">
            {SAVED_SEARCHES.map((s) => (
              <div key={s.name} className="px-6 py-4 flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink truncate">{s.name}</p>
                  <p className="text-xs text-mist truncate mt-0.5">{s.filters}</p>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <label className="relative inline-flex items-center cursor-not-allowed">
                    <div className={`w-8 h-[18px] rounded-full transition-colors ${s.alerts ? "bg-sea" : "bg-line"}`}>
                      <div className={`absolute top-[2px] h-[14px] w-[14px] rounded-full bg-white shadow-sm transition-transform ${s.alerts ? "translate-x-[18px]" : "translate-x-[2px]"}`} />
                    </div>
                  </label>
                  <span className="text-[10px] text-mist w-8">{s.alerts ? "On" : "Off"}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Saved properties */}
        <section className="rounded-2xl border border-line bg-panel shadow-lift overflow-hidden">
          <div className="px-6 py-4 border-b border-line flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink">Saved properties</h2>
            <span className="text-xs text-mist">{SAVED_PROPERTIES.length} saved</span>
          </div>
          <div className="divide-y divide-line/50">
            {SAVED_PROPERTIES.map((p) => (
              <div key={p.id} className="px-6 py-4 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="h-10 w-14 rounded-lg skeleton shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-ink truncate">{p.title}</p>
                    <p className="text-xs text-mist truncate">{p.location}</p>
                  </div>
                </div>
                <span className="font-display text-sm text-ink shrink-0">{p.price}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Notifications */}
        <section className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
          <h2 className="text-sm font-semibold text-ink mb-4">Alert preferences</h2>
          <div className="space-y-3">
            {[
              { label: "Email alerts for saved searches", desc: "Get notified when new listings match", enabled: true },
              { label: "Price drop alerts", desc: "Notification when saved property price changes", enabled: true },
              { label: "Weekly market digest", desc: "Summary of new listings and price trends", enabled: false },
            ].map((n) => (
              <div key={n.label} className="flex items-center justify-between py-2">
                <div>
                  <p className="text-sm text-ink">{n.label}</p>
                  <p className="text-xs text-mist">{n.desc}</p>
                </div>
                <div className={`w-8 h-[18px] rounded-full ${n.enabled ? "bg-sea" : "bg-line"} relative cursor-not-allowed`}>
                  <div className={`absolute top-[2px] h-[14px] w-[14px] rounded-full bg-white shadow-sm transition-transform ${n.enabled ? "translate-x-[18px]" : "translate-x-[2px]"}`} />
                </div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-[10px] text-mist/60">Notifications require auth backend (BD-13)</p>
        </section>
      </main>
    </div>
  );
}
