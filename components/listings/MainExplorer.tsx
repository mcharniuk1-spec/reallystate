"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { Listing } from "@/lib/types/listing";
import { MapCanvas } from "@/components/map/MapCanvas";

type DealMode = "buy" | "rent";
type SpaceMode = "residential" | "commercial";

const COMMERCIAL_TYPES = new Set(["office", "shop", "land", "garage"]);
const CITY_COORDS: Array<[string[], [number, number]]> = [
  [["софия", "sofia"], [42.6977, 23.3219]],
  [["варна", "varna"], [43.2141, 27.9147]],
  [["пловдив", "plovdiv"], [42.1354, 24.7453]],
  [["бургас", "burgas"], [42.5048, 27.4626]],
  [["несебър", "nessebar", "nesebar"], [42.6601, 27.7206]],
  [["слънчев бряг", "sunny beach"], [42.6952, 27.7104]],
  [["свети влас", "sveti vlas"], [42.7139, 27.7588]],
  [["созопол", "sozopol"], [42.4173, 27.6962]],
  [["банско", "bansko"], [41.8383, 23.4885]],
  [["боровец", "borovets"], [42.2667, 23.6058]],
  [["велико търново", "veliko tarnovo"], [43.0757, 25.6172]],
  [["русе", "ruse"], [43.8356, 25.9657]],
  [["стара загора", "stara zagora"], [42.4258, 25.6345]],
  [["благоевград", "blagoevgrad"], [42.0209, 23.0943]],
  [["добрич", "dobrich"], [43.5726, 27.8273]],
  [["шумен", "shumen"], [43.2712, 26.9361]],
  [["плевен", "pleven"], [43.417, 24.6067]],
];

function seededUnit(id: string, salt: number) {
  let hash = salt;
  for (let i = 0; i < id.length; i += 1) hash = (hash * 33 + id.charCodeAt(i)) % 1000003;
  return hash / 1000003;
}

function withMapLocation(item: Listing): Listing {
  if (item.latitude != null && item.longitude != null) return item;

  const haystack = [item.city, item.region, item.district, item.address_text, item.title].filter(Boolean).join(" ").toLowerCase();
  const matched = CITY_COORDS.find(([names]) => names.some((name) => haystack.includes(name)));
  const base = matched?.[1];

  if (base) {
    const spread = matched[0].some((name) => name === "софия" || name === "sofia") ? 0.11 : 0.075;
    return {
      ...item,
      latitude: base[0] + (seededUnit(item.reference_id, 71) - 0.5) * spread,
      longitude: base[1] + (seededUnit(item.reference_id, 131) - 0.5) * spread,
    };
  }

  return {
    ...item,
    latitude: 41.85 + seededUnit(item.reference_id, 191) * 2.05,
    longitude: 22.25 + seededUnit(item.reference_id, 251) * 5.65,
  };
}

function formatPrice(price: number | null, currency: string | null) {
  if (price == null) return "POA";
  const symbol = currency === "EUR" ? "€" : currency === "BGN" ? "BGN " : `${currency ?? ""} `;
  return `${symbol}${new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(price)}`;
}

function matchesDeal(item: Listing, mode: DealMode) {
  return mode === "buy"
    ? item.listing_intent === "sale" || item.listing_intent === "auction"
    : item.listing_intent === "rent" || item.listing_intent === "short_term_rental";
}

function matchesSpace(item: Listing, mode: SpaceMode) {
  const commercial = COMMERCIAL_TYPES.has(item.property_category);
  return mode === "commercial" ? commercial : !commercial;
}

export function MainExplorer() {
  const [items, setItems] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [deal, setDeal] = useState<DealMode>("buy");
  const [space, setSpace] = useState<SpaceMode>("residential");
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/scraped-listings.json", { cache: "no-store" })
      .then((r) => r.json())
      .then((data: Listing[]) => setItems(data))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return items.filter((item) => {
      if (!matchesDeal(item, deal)) return false;
      if (!matchesSpace(item, space)) return false;
      if (!q) return true;
      return [item.title, item.city, item.district, item.region, item.source_name, item.description]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(q));
    });
  }, [items, deal, space, search]);

  const mapped = useMemo(() => filtered.map(withMapLocation), [filtered]);
  const selected = useMemo(() => (selectedId ? mapped.find((item) => item.reference_id === selectedId) ?? null : null), [mapped, selectedId]);
  const listed = mapped.slice(0, 180);
  const totals = useMemo(
    () =>
      items.reduce(
        (acc, item) => {
          acc.local += item.photo_count_local ?? item.local_image_files?.length ?? 0;
          acc.remote += item.photo_count_remote ?? item.image_urls.length;
          acc.full += item.full_gallery_downloaded ? 1 : 0;
          return acc;
        },
        { local: 0, remote: 0, full: 0 },
      ),
    [items],
  );

  return (
    <main className="flex h-[calc(100dvh-56px-104px)] min-h-[560px] flex-col bg-paper">
      <section className="shrink-0 border-b border-line bg-panel/95 px-4 py-3 shadow-sm sm:px-6">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            <Segmented value={deal} options={[["buy", "Buy"], ["rent", "Rent"]]} onChange={(v) => setDeal(v as DealMode)} />
            <Segmented value={space} options={[["residential", "Residential"], ["commercial", "Commercial"]]} onChange={(v) => setSpace(v as SpaceMode)} />
            <span className="rounded-full border border-line bg-paper px-3 py-1.5 text-xs font-semibold text-mist">
              {loading ? "Loading..." : `${filtered.length} shown / ${items.length} scraped`}
            </span>
          </div>
          <div className="flex flex-1 flex-wrap items-center justify-end gap-2">
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search property, city, agent..."
              className="min-w-[260px] flex-1 rounded-2xl border border-line bg-paper px-4 py-2 text-sm text-ink outline-none focus:border-sea/50 xl:max-w-xl"
            />
            <a href="/dashboard/scrape-status.html" className="rounded-2xl bg-sea px-4 py-2 text-sm font-semibold text-white shadow-lift">
              Scrape QA
            </a>
          </div>
        </div>
        <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-mist">
          <Badge>Local photos: {totals.local}</Badge>
          <Badge>Remote photos: {totals.remote}</Badge>
          <Badge>Full galleries: {totals.full}</Badge>
          <Badge>Image reports: missing</Badge>
        </div>
      </section>

      <section className="grid min-h-0 flex-1 gap-4 p-4 min-[700px]:grid-cols-[minmax(0,1fr)_340px] xl:grid-cols-[minmax(0,1fr)_390px]">
        <div className="relative min-h-0 overflow-hidden rounded-3xl border border-line bg-[#073f42] shadow-lift">
          <MapCanvas listings={mapped} highlightId={selected?.reference_id ?? null} onSelect={setSelectedId} />
          <div className="pointer-events-none absolute left-5 top-5 rounded-2xl bg-white/90 px-4 py-3 text-ink shadow-lift backdrop-blur">
            <p className="text-xs uppercase tracking-wide text-mist">OpenStreetMap 3D</p>
            <p className="font-display text-2xl">{mapped.length} properties</p>
          </div>
        </div>

        <aside className="flex min-h-0 flex-col overflow-hidden rounded-3xl border border-line bg-panel shadow-lift">
          <div className="border-b border-line p-3">
            {selected ? <SelectedProperty item={selected} /> : <EmptySelection count={mapped.length} />}
          </div>
          <div className="flex items-center justify-between px-4 py-3">
            <h2 className="text-sm font-semibold text-ink">Nearby properties</h2>
            <span className="text-xs text-mist">{listed.length} cards</span>
          </div>
          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-3 pb-3">
            {listed.map((item) => (
              <PropertyCard key={item.reference_id} item={item} selected={item.reference_id === selected?.reference_id} onSelect={setSelectedId} />
            ))}
          </div>
        </aside>
      </section>
    </main>
  );
}

function Segmented({
  value,
  options,
  onChange,
}: {
  value: string;
  options: [string, string][];
  onChange: (value: string) => void;
}) {
  return (
    <div className="flex rounded-2xl border border-line bg-paper p-1">
      {options.map(([id, label]) => (
        <button
          key={id}
          type="button"
          onClick={() => onChange(id)}
          className={`rounded-xl px-4 py-1.5 text-xs font-semibold transition ${
            value === id ? "bg-sea text-white shadow-sm" : "text-mist hover:text-ink"
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return <span className="rounded-full border border-line bg-paper px-2.5 py-1">{children}</span>;
}

function EmptySelection({ count }: { count: number }) {
  return (
    <div className="rounded-2xl border border-dashed border-line bg-paper p-4">
      <p className="text-sm font-semibold text-ink">Select a map point</p>
      <p className="mt-1 text-xs leading-relaxed text-mist">
        {count} properties are plotted. Tap a marker to load the property summary here, then open the full page.
      </p>
    </div>
  );
}

function SelectedProperty({ item }: { item: Listing }) {
  const local = item.photo_count_local ?? item.local_image_files?.length ?? 0;
  const remote = item.photo_count_remote ?? item.image_urls.length;
  return (
    <div className="overflow-hidden rounded-2xl border border-sea/20 bg-paper">
      <div className="aspect-[16/9] bg-line/40">
        {item.image_urls[0] ? <img src={item.image_urls[0]} alt="" className="h-full w-full object-cover" /> : null}
      </div>
      <div className="p-3">
        <p className="text-xs font-semibold text-sea">{item.source_name}</p>
        <h2 className="line-clamp-2 text-base font-semibold text-ink">{item.title || item.reference_id}</h2>
        <p className="mt-1 font-display text-2xl text-ink">{formatPrice(item.price, item.currency)}</p>
        <p className="mt-1 text-xs text-mist">{[item.district, item.city].filter(Boolean).join(", ") || item.region || "Bulgaria"}</p>
        <div className="mt-3 grid grid-cols-3 gap-1 text-[10px] text-ink">
          <span className="rounded-md bg-panel px-2 py-1">{local}/{remote} photos</span>
          <span className="rounded-md bg-panel px-2 py-1">{item.area_sqm ? `${Math.round(item.area_sqm)} m²` : "area n/a"}</span>
          <span className="rounded-md bg-panel px-2 py-1">{item.rooms ? `${item.rooms} rooms` : item.property_category}</span>
        </div>
        <Link
          href={`/properties/${encodeURIComponent(item.reference_id)}`}
          className="mt-3 block rounded-xl bg-sea px-3 py-2 text-center text-sm font-semibold text-white transition hover:bg-sea-bright"
        >
          Open property page
        </Link>
      </div>
    </div>
  );
}

function PropertyCard({ item, selected, onSelect }: { item: Listing; selected: boolean; onSelect: (id: string) => void }) {
  const local = item.photo_count_local ?? item.local_image_files?.length ?? 0;
  const remote = item.photo_count_remote ?? item.image_urls.length;
  return (
    <button
      type="button"
      onClick={() => onSelect(item.reference_id)}
      className={`block w-full overflow-hidden rounded-2xl border bg-paper text-left transition hover:border-sea/40 hover:shadow-lift ${
        selected ? "border-sea shadow-lift" : "border-line"
      }`}
    >
      <div className="aspect-[16/8] bg-line/40">
        {item.image_urls[0] ? <img src={item.image_urls[0]} alt="" className="h-full w-full object-cover" /> : null}
      </div>
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate text-xs font-semibold text-sea">{item.source_name}</p>
            <p className="line-clamp-2 text-sm font-semibold text-ink">{item.title || item.reference_id}</p>
          </div>
          <p className="shrink-0 font-display text-lg text-ink">{formatPrice(item.price, item.currency)}</p>
        </div>
        <p className="mt-1 text-xs text-mist">{[item.district, item.city].filter(Boolean).join(", ") || item.region || "Bulgaria"}</p>
        <div className="mt-2 grid grid-cols-3 gap-1 text-[10px]">
          <span className="rounded-md bg-panel px-2 py-1">{local}/{remote} photos</span>
          <span className={`rounded-md px-2 py-1 ${item.full_gallery_downloaded ? "bg-sea/10 text-sea" : "bg-warn/10 text-warn"}`}>
            {item.full_gallery_downloaded ? "full" : "partial"}
          </span>
          <span className="rounded-md bg-panel px-2 py-1">Q {item.scrape_quality_score ?? "n/a"}</span>
        </div>
      </div>
    </button>
  );
}
