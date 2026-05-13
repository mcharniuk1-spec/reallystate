"use client";

import { useMemo, useState } from "react";

type Mode = "buyer" | "renter" | "seller";

const PROPERTIES = [
  { id: "demo-001", title: "3-room apartment", location: "Lozenets, Sofia", price: "EUR 185,000", status: "Liked" },
  { id: "demo-004", title: "2-room apartment", location: "Sarafovo, Burgas", price: "EUR 89,000", status: "Chat open" },
  { id: "demo-006", title: "Luxury villa", location: "Sozopol", price: "EUR 340,000", status: "Liked" },
];

const SEARCHES = [
  "Buy · Apartment · 2 rooms · Varna · under EUR 90K",
  "Rent · Burgas coast · sea view · furnished",
  "Buy · Sofia · studio or 1-bed · investment",
];

export function AccountCabinet() {
  const [mode, setMode] = useState<Mode>("buyer");
  const [liked, setLiked] = useState(() => new Set(PROPERTIES.map((item) => item.id)));

  const modeLabel = useMemo(() => {
    if (mode === "buyer") return "Buying";
    if (mode === "renter") return "Renting";
    return "Selling";
  }, [mode]);

  function toggleLike(propertyId: string) {
    setLiked((prev) => {
      const next = new Set(prev);
      if (next.has(propertyId)) next.delete(propertyId);
      else next.add(propertyId);
      return next;
    });
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
      <aside className="space-y-4">
        <section className="rounded-xl border border-line bg-panel p-5 shadow-lift">
          <div className="flex items-center gap-3">
            <div className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-gradient-to-br from-sea to-sea-bright text-sm font-bold text-white">
              U
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-ink">User Account</p>
              <p className="truncate text-xs text-mist">buyer@example.com</p>
            </div>
          </div>
          <div className="mt-5 grid grid-cols-3 gap-1 rounded-xl border border-line bg-paper p-1">
            {(["buyer", "renter", "seller"] as const).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setMode(item)}
                className={`rounded-lg px-2 py-2 text-xs font-semibold capitalize transition-colors ${
                  mode === item ? "bg-sea text-white" : "text-mist hover:text-ink"
                }`}
              >
                {item}
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-line bg-panel p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-mist">Mode</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{modeLabel}</p>
          <div className="mt-4 grid grid-cols-2 gap-2 text-center">
            <div className="rounded-lg bg-paper p-3">
              <p className="text-lg font-semibold text-ink">{liked.size}</p>
              <p className="text-[11px] text-mist">Liked</p>
            </div>
            <div className="rounded-lg bg-paper p-3">
              <p className="text-lg font-semibold text-ink">1</p>
              <p className="text-[11px] text-mist">Chats</p>
            </div>
          </div>
        </section>
      </aside>

      <div className="space-y-6">
        <section className="rounded-xl border border-line bg-panel p-5 shadow-lift">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-xs text-mist">Name</span>
              <input className="h-11 w-full rounded-xl border border-line bg-paper px-3 text-sm text-ink outline-none focus:border-sea/40" defaultValue="User Account" />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs text-mist">Email</span>
              <input className="h-11 w-full rounded-xl border border-line bg-paper px-3 text-sm text-ink outline-none focus:border-sea/40" defaultValue="buyer@example.com" />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs text-mist">Phone</span>
              <input className="h-11 w-full rounded-xl border border-line bg-paper px-3 text-sm text-ink outline-none focus:border-sea/40" placeholder="+359 ..." />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs text-mist">Language</span>
              <select className="h-11 w-full rounded-xl border border-line bg-paper px-3 text-sm text-ink outline-none focus:border-sea/40" defaultValue="en">
                <option value="en">English</option>
                <option value="bg">Bulgarian</option>
              </select>
            </label>
          </div>
        </section>

        <section className="overflow-hidden rounded-xl border border-line bg-panel shadow-lift">
          <div className="flex items-center justify-between border-b border-line px-5 py-4">
            <h2 className="text-sm font-semibold text-ink">Liked properties</h2>
            <span className="text-xs text-mist">{liked.size} active</span>
          </div>
          <div className="divide-y divide-line/60">
            {PROPERTIES.map((property) => {
              const isLiked = liked.has(property.id);
              return (
                <div key={property.id} className="grid gap-3 px-5 py-4 sm:grid-cols-[1fr_auto] sm:items-center">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="h-14 w-20 shrink-0 rounded-lg bg-paper" />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-ink">{property.title}</p>
                      <p className="truncate text-xs text-mist">{property.location}</p>
                      <p className="mt-1 text-xs font-semibold text-ink">{property.price}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-paper px-3 py-1 text-[11px] text-mist">{property.status}</span>
                    <button
                      type="button"
                      onClick={() => toggleLike(property.id)}
                      className={`h-9 rounded-lg px-3 text-xs font-semibold ${
                        isLiked ? "bg-sea text-white" : "border border-line text-mist"
                      }`}
                    >
                      {isLiked ? "Liked" : "Like"}
                    </button>
                    <a href="/chat" className="h-9 rounded-lg bg-ink px-3 py-2 text-xs font-semibold text-paper">
                      Chat
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="rounded-xl border border-line bg-panel p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink">Saved searches</h2>
            <button type="button" className="rounded-lg border border-line px-3 py-1.5 text-xs font-semibold text-ink">
              New
            </button>
          </div>
          <div className="space-y-2">
            {SEARCHES.map((search) => (
              <div key={search} className="flex items-center justify-between gap-3 rounded-lg bg-paper px-3 py-3">
                <p className="truncate text-sm text-ink">{search}</p>
                <label className="relative inline-flex h-5 w-9 shrink-0 items-center rounded-full bg-sea">
                  <input type="checkbox" className="sr-only" defaultChecked />
                  <span className="ml-[18px] h-4 w-4 rounded-full bg-white shadow-sm" />
                </label>
              </div>
            ))}
          </div>
        </section>

        {mode === "seller" ? (
          <section className="rounded-xl border border-line bg-panel p-5 shadow-lift">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-sm font-semibold text-ink">Seller workspace</h2>
                <p className="text-xs text-mist">Drafts, review status, and owner-representative chats</p>
              </div>
              <a href="/post" className="rounded-xl bg-sea px-4 py-2 text-sm font-semibold text-white">
                Post listing
              </a>
            </div>
          </section>
        ) : null}
      </div>
    </div>
  );
}
