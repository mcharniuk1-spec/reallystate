"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { Listing, ListingSourceLink } from "@/lib/types/listing";
import { buildLocationAggregateReferenceIndex, getListingSourceLinks, normalizeText } from "@/lib/listing-source-links";
import { MapCanvas, type MapListing } from "@/components/map/MapCanvas";

type DealMode = "buy" | "rent";
type SpaceMode = "residential" | "commercial";
type SearchMode = "region" | "description" | "all";

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
  if (price == null || price <= 0) return "Undefined";
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

function getCombinedDescription(item: Listing) {
  return [item.description, item.image_report_md, item.image_report_json].filter(Boolean).join("\n\n");
}

function searchFields(item: Listing, mode: SearchMode) {
  const regionFields = [item.city, item.district, item.region, item.resort, item.address_text, item.source_name];
  const descriptionFields = [item.title, item.description, item.image_report_md, item.image_report_json, item.amenities?.join(" ")];
  if (mode === "region") return regionFields;
  if (mode === "description") return descriptionFields;
  return [...regionFields, ...descriptionFields];
}

function buildSourceLinkIndex(items: Listing[]) {
  const index = new Map<string, ListingSourceLink[]>();
  for (const item of items) {
    index.set(item.reference_id, getListingSourceLinks(item, items));
  }
  return index;
}

export function MainExplorer() {
  const [items, setItems] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [deal, setDeal] = useState<DealMode>("buy");
  const [space, setSpace] = useState<SpaceMode>("residential");
  const [searchMode, setSearchMode] = useState<SearchMode>("all");
  const [search, setSearch] = useState("");
  const [aggregateOnly, setAggregateOnly] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedMapItemIds, setSelectedMapItemIds] = useState<string[] | null>(null);
  const [expandedDescriptions, setExpandedDescriptions] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetch("/data/scraped-listings.json", { cache: "no-store" })
      .then((r) => r.json())
      .then((data: Listing[]) => setItems(data))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const q = normalizeText(search);
    return items.filter((item) => {
      if (!matchesDeal(item, deal)) return false;
      if (!matchesSpace(item, space)) return false;
      if (!q) return true;
      return searchFields(item, searchMode)
        .filter(Boolean)
        .some((value) => normalizeText(String(value)).includes(q));
    });
  }, [items, deal, space, search, searchMode]);

  const baseMapped = useMemo(() => filtered.map(withMapLocation), [filtered]);
  const sourceLinksByReference = useMemo(() => buildSourceLinkIndex(baseMapped), [baseMapped]);
  const locationGroupsByReference = useMemo(() => buildLocationAggregateReferenceIndex(baseMapped), [baseMapped]);
  const aggregateCount = useMemo(
    () => baseMapped.filter((item) => (locationGroupsByReference.get(item.reference_id)?.length ?? 0) > 1).length,
    [baseMapped, locationGroupsByReference],
  );
  const mapped = useMemo(
    () => (aggregateOnly ? baseMapped.filter((item) => (locationGroupsByReference.get(item.reference_id)?.length ?? 0) > 1) : baseMapped),
    [aggregateOnly, baseMapped, locationGroupsByReference],
  );
  const selected = useMemo(() => (selectedId ? mapped.find((item) => item.reference_id === selectedId) ?? null : null), [mapped, selectedId]);
  const selectedGroupItems = useMemo(() => {
    if (!selectedMapItemIds?.length) return [];
    const ids = new Set(selectedMapItemIds);
    return mapped.filter((item) => ids.has(item.reference_id));
  }, [mapped, selectedMapItemIds]);
  const isGroupSelection = selectedGroupItems.length > 1;
  const listed = useMemo(() => {
    if (isGroupSelection) return selectedGroupItems;
    if (selected) return [selected, ...mapped.filter((item) => item.reference_id !== selected.reference_id)];
    return mapped;
  }, [isGroupSelection, mapped, selected, selectedGroupItems]);
  const mapListings = useMemo(() => mapped as MapListing[], [mapped]);
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
  const handleMapSelect = useCallback((id: string, markerItemIds?: string[]) => {
    setSelectedId(id);
    setSelectedMapItemIds(markerItemIds?.length ? markerItemIds : [id]);
  }, []);

  useEffect(() => {
    if (selectedId && !mapped.some((item) => item.reference_id === selectedId)) {
      setSelectedId(null);
      setSelectedMapItemIds(null);
    }
  }, [mapped, selectedId]);

  return (
    <main className="flex min-h-[calc(100dvh-56px)] flex-col bg-paper pb-[108px]">
      <section className="shrink-0 border-b border-line bg-panel/95 px-4 py-3 shadow-sm sm:px-6">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            <Segmented value={deal} options={[["buy", "Buy"], ["rent", "Rent"]]} onChange={(v) => setDeal(v as DealMode)} />
            <Segmented value={space} options={[["residential", "Residential"], ["commercial", "Commercial"]]} onChange={(v) => setSpace(v as SpaceMode)} />
            <span className="rounded-full border border-line bg-paper px-3 py-1.5 text-xs font-semibold text-mist">
              {loading ? "Loading..." : `${filtered.length} shown / ${items.length} scraped`}
            </span>
            <button
              type="button"
              onClick={() => setAggregateOnly((value) => !value)}
              className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                aggregateOnly ? "border-sea bg-sea text-white" : "border-line bg-paper text-mist hover:text-ink"
              }`}
            >
              Aggregate ({aggregateCount})
            </button>
          </div>
          <div className="flex flex-1 flex-wrap items-center justify-end gap-2">
            <Segmented
              value={searchMode}
              options={[
                ["all", "All"],
                ["region", "Region"],
                ["description", "Description"],
              ]}
              onChange={(v) => setSearchMode(v as SearchMode)}
            />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={searchMode === "region" ? "Search city, district, address..." : searchMode === "description" ? "Search full description and image reports..." : "Search region or description..."}
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
          <Badge>Map points: up to 20</Badge>
        </div>
      </section>

      <section className="grid gap-4 p-4 min-[900px]:h-[calc(100dvh-312px)] min-[900px]:min-h-[430px] min-[900px]:grid-cols-[minmax(0,7fr)_minmax(280px,3fr)] min-[900px]:items-stretch">
        <div className="relative h-[min(58dvh,540px)] min-h-[320px] overflow-hidden rounded-3xl border border-line bg-[#073f42] shadow-lift min-[900px]:h-full">
          <MapCanvas listings={mapListings} highlightId={selected?.reference_id ?? null} onSelect={handleMapSelect} />
          <div className="pointer-events-none absolute left-5 top-5 rounded-2xl bg-white/90 px-4 py-3 text-ink shadow-lift backdrop-blur">
            <p className="text-xs uppercase tracking-wide text-mist">OpenStreetMap</p>
            <p className="font-display text-2xl">{mapped.length} properties</p>
            <p className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-mist">viewport groups</p>
          </div>
        </div>

        <aside className="flex h-[min(62dvh,620px)] min-h-[360px] flex-col overflow-hidden rounded-3xl border border-line bg-panel shadow-lift min-[900px]:h-full">
          <div className="property-scroll min-h-0 flex-1 space-y-2 overflow-y-scroll px-2.5 pb-3 pr-1.5 [scrollbar-gutter:stable]">
            <PanelHeader
              count={mapped.length}
              listedCount={listed.length}
              selected={selected}
              isGroupSelection={isGroupSelection}
              selectedGroupItems={selectedGroupItems}
            />
            {listed.map((item) => (
              <PropertyCard
                key={item.reference_id}
                item={item}
                selected={item.reference_id === selected?.reference_id}
                expanded={Boolean(expandedDescriptions[item.reference_id])}
                sourceLinks={sourceLinksByReference.get(item.reference_id) ?? []}
                locationGroupCount={locationGroupsByReference.get(item.reference_id)?.length ?? 1}
                onSelect={setSelectedId}
                onToggleDescription={(id) => setExpandedDescriptions((state) => ({ ...state, [id]: !state[id] }))}
              />
            ))}
          </div>
        </aside>
      </section>
      <style jsx global>{`
        .property-scroll::-webkit-scrollbar {
          width: 10px;
        }
        .property-scroll::-webkit-scrollbar-track {
          background: rgba(228, 220, 207, 0.55);
          border-radius: 999px;
        }
        .property-scroll::-webkit-scrollbar-thumb {
          background: rgba(92, 107, 132, 0.46);
          border: 2px solid rgba(248, 245, 238, 0.96);
          border-radius: 999px;
        }
        .property-scroll {
          scrollbar-color: rgba(92, 107, 132, 0.56) rgba(228, 220, 207, 0.55);
          scrollbar-width: thin;
        }
      `}</style>
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

function PanelHeader({
  count,
  listedCount,
  selected,
  isGroupSelection,
  selectedGroupItems,
}: {
  count: number;
  listedCount: number;
  selected: Listing | null;
  isGroupSelection: boolean;
  selectedGroupItems: Listing[];
}) {
  const groupLabel = selectedGroupItems[0]
    ? [selectedGroupItems[0].district ?? selectedGroupItems[0].resort, selectedGroupItems[0].city ?? selectedGroupItems[0].region].filter(Boolean).join(", ")
    : null;
  return (
    <div className="sticky top-0 z-10 border-b border-line bg-panel/95 pb-2 pt-2 backdrop-blur">
      <div className="rounded-2xl border border-dashed border-line bg-paper p-3">
        <p className="text-sm font-semibold text-ink">
          {isGroupSelection ? `Selected group${groupLabel ? `: ${groupLabel}` : ""}` : selected ? "Selected property" : "Select a map point"}
        </p>
        <p className="mt-1 text-xs leading-relaxed text-mist">
          {isGroupSelection
            ? `${listedCount} properties from this map group are shown below.`
            : selected
              ? "The chosen property is first in the scrollable list; the rest of the results remain below it."
              : `${count} properties are plotted. Tap a marker to pin a property first or open one map group.`}
        </p>
      </div>
      <div className="flex items-center justify-between px-1 pt-2">
        <h2 className="text-sm font-semibold text-ink">{isGroupSelection ? "Group properties" : "Properties"}</h2>
        <span className="text-xs text-mist">{listedCount} cards</span>
      </div>
    </div>
  );
}

function PropertyCard({
  item,
  selected,
  expanded,
  sourceLinks,
  locationGroupCount,
  onSelect,
  onToggleDescription,
}: {
  item: Listing;
  selected: boolean;
  expanded: boolean;
  sourceLinks: ListingSourceLink[];
  locationGroupCount: number;
  onSelect: (id: string) => void;
  onToggleDescription: (id: string) => void;
}) {
  const local = item.photo_count_local ?? item.local_image_files?.length ?? 0;
  const remote = item.photo_count_remote ?? item.image_urls.length;
  const description = getCombinedDescription(item);
  const shownDescription = expanded ? description : description.slice(0, 220);
  const uniqueSourceLinks = sourceLinks.length
    ? sourceLinks
    : [
        {
          reference_id: item.reference_id,
          source_name: item.source_name,
          source_key: item.source_key,
          listing_url: item.listing_url,
          external_id: item.external_id,
          listing_intent: item.listing_intent,
          price: item.price,
          currency: item.currency,
          evidence: ["current source"],
          is_current: true,
        } satisfies ListingSourceLink,
      ];
  return (
    <article
      className={`block w-full overflow-hidden rounded-2xl border bg-paper text-left transition hover:border-sea/40 hover:shadow-lift ${
        selected ? "border-sea shadow-lift" : "border-line"
      }`}
    >
      <button type="button" onClick={() => onSelect(item.reference_id)} className="block w-full text-left">
        <div className="aspect-[16/5.8] bg-line/40">
          {item.image_urls[0] ? <img src={item.image_urls[0]} alt="" className="h-full w-full object-cover" /> : null}
        </div>
        <div className="p-2.5">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-xs font-semibold text-sea">{item.source_name}</p>
              <p className="line-clamp-2 text-xs font-semibold text-ink">{item.title || item.reference_id}</p>
            </div>
            <p className="shrink-0 font-display text-base text-ink">{formatPrice(item.price, item.currency)}</p>
          </div>
          <p className="mt-1 text-xs text-mist">{[item.district, item.city].filter(Boolean).join(", ") || item.region || "Bulgaria"}</p>
          <div className="mt-2 grid grid-cols-3 gap-1 text-[10px]">
            <span className="rounded-md bg-panel px-2 py-1">{local}/{remote} photos</span>
            <span className={`rounded-md px-2 py-1 ${item.full_gallery_downloaded ? "bg-sea/10 text-sea" : "bg-warn/10 text-warn"}`}>
              {item.full_gallery_downloaded ? "full" : "partial"}
            </span>
            <span className="rounded-md bg-panel px-2 py-1">Q {item.scrape_quality_score ?? "n/a"}</span>
          </div>
          {locationGroupCount > 1 ? (
            <p className="mt-2 rounded-md bg-sea/10 px-2 py-1 text-[10px] font-semibold text-sea">{locationGroupCount} same-location rows</p>
          ) : null}
        </div>
      </button>
      <div className="border-t border-line/60 px-2.5 pb-2.5 pt-2">
        {description ? (
          <>
            <p className="whitespace-pre-line text-xs leading-relaxed text-mist">
              {shownDescription}
              {!expanded && description.length > shownDescription.length ? "..." : ""}
            </p>
            <button
              type="button"
              onClick={() => onToggleDescription(item.reference_id)}
              className="mt-2 rounded-full border border-line px-3 py-1 text-[11px] font-semibold text-ink hover:border-sea/40"
            >
              {expanded ? "Fold description" : "Show full description"}
            </button>
          </>
        ) : (
          <p className="text-xs text-mist">No description captured yet.</p>
        )}
        <div className="mt-3 grid gap-2">
          {uniqueSourceLinks.map((source) => (
            <a
              key={`${source.source_name}:${source.listing_url}`}
              href={source.listing_url}
              target="_blank"
              rel="noreferrer"
              className="block rounded-xl border border-line bg-panel px-3 py-2 text-center text-xs font-semibold text-ink transition hover:border-sea/40 hover:text-sea"
            >
              {source.is_current ? "Current source" : "Source"}: {source.source_name}
            </a>
          ))}
          <Link
            href={`/properties/${encodeURIComponent(item.reference_id)}`}
            className="block rounded-xl bg-sea px-3 py-2 text-center text-xs font-semibold text-white transition hover:bg-sea-bright"
          >
            Open property page
          </Link>
        </div>
      </div>
    </article>
  );
}
