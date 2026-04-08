"use client";

import { useState } from "react";
import {
  AMENITIES,
  CONSTRUCTION_TYPES,
  SORT_OPTIONS,
  type Amenity,
  type ConstructionType,
  type SortOption,
} from "@/lib/types/listing";

export type AdvancedFilters = {
  priceMin: number | null;
  priceMax: number | null;
  areaMin: number | null;
  areaMax: number | null;
  roomsMin: number | null;
  roomsMax: number | null;
  floorMin: number | null;
  floorMax: number | null;
  yearMin: number | null;
  yearMax: number | null;
  constructionTypes: ConstructionType[];
  amenities: Amenity[];
  sort: SortOption;
};

export const DEFAULT_FILTERS: AdvancedFilters = {
  priceMin: null,
  priceMax: null,
  areaMin: null,
  areaMax: null,
  roomsMin: null,
  roomsMax: null,
  floorMin: null,
  floorMax: null,
  yearMin: null,
  yearMax: null,
  constructionTypes: [],
  amenities: [],
  sort: "newest",
};

function RangeRow({
  label,
  min,
  max,
  onMinChange,
  onMaxChange,
  placeholderMin = "Min",
  placeholderMax = "Max",
  unit,
}: {
  label: string;
  min: number | null;
  max: number | null;
  onMinChange: (v: number | null) => void;
  onMaxChange: (v: number | null) => void;
  placeholderMin?: string;
  placeholderMax?: string;
  unit?: string;
}) {
  const parse = (s: string) => {
    const n = parseInt(s, 10);
    return Number.isNaN(n) ? null : n;
  };

  return (
    <div>
      <label className="block text-[11px] font-semibold uppercase tracking-wider text-mist mb-1.5">
        {label} {unit && <span className="font-normal normal-case">({unit})</span>}
      </label>
      <div className="flex gap-2">
        <input
          type="number"
          value={min ?? ""}
          onChange={(e) => onMinChange(parse(e.target.value))}
          placeholder={placeholderMin}
          className="w-full rounded-lg border border-line bg-paper px-2.5 py-1.5 text-xs text-ink placeholder:text-mist/40 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        />
        <span className="text-mist text-xs self-center">–</span>
        <input
          type="number"
          value={max ?? ""}
          onChange={(e) => onMaxChange(parse(e.target.value))}
          placeholder={placeholderMax}
          className="w-full rounded-lg border border-line bg-paper px-2.5 py-1.5 text-xs text-ink placeholder:text-mist/40 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
        />
      </div>
    </div>
  );
}

function ChipGroup<T extends string>({
  label,
  options,
  selected,
  onToggle,
}: {
  label: string;
  options: { value: T; label: string }[];
  selected: T[];
  onToggle: (v: T) => void;
}) {
  return (
    <div>
      <label className="block text-[11px] font-semibold uppercase tracking-wider text-mist mb-1.5">
        {label}
      </label>
      <div className="flex flex-wrap gap-1.5">
        {options.map((o) => {
          const active = selected.includes(o.value);
          return (
            <button
              key={o.value}
              type="button"
              onClick={() => onToggle(o.value)}
              className={`rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors ${
                active
                  ? "border-sea bg-sea/10 text-sea"
                  : "border-line text-mist hover:border-sea/30 hover:text-ink"
              }`}
            >
              {o.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function FilterPanel({
  filters,
  onChange,
  open,
  onToggle,
}: {
  filters: AdvancedFilters;
  onChange: (f: AdvancedFilters) => void;
  open: boolean;
  onToggle: () => void;
}) {
  const [localFilters, setLocalFilters] = useState(filters);

  const update = (patch: Partial<AdvancedFilters>) => {
    const next = { ...localFilters, ...patch };
    setLocalFilters(next);
    onChange(next);
  };

  const toggleArrayItem = <T extends string>(arr: T[], item: T): T[] =>
    arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];

  const activeCount = [
    localFilters.priceMin,
    localFilters.priceMax,
    localFilters.areaMin,
    localFilters.areaMax,
    localFilters.roomsMin,
    localFilters.roomsMax,
    localFilters.floorMin,
    localFilters.floorMax,
    localFilters.yearMin,
    localFilters.yearMax,
  ].filter((v) => v != null).length +
    localFilters.constructionTypes.length +
    localFilters.amenities.length +
    (localFilters.sort !== "newest" ? 1 : 0);

  const clearAll = () => {
    setLocalFilters(DEFAULT_FILTERS);
    onChange(DEFAULT_FILTERS);
  };

  return (
    <>
      {/* Toggle button */}
      <button
        type="button"
        onClick={onToggle}
        className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors ${
          open || activeCount > 0
            ? "border-sea bg-sea/10 text-sea"
            : "border-line text-mist hover:border-sea/30 hover:text-ink"
        }`}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="8" y1="12" x2="20" y2="12" />
          <line x1="12" y1="18" x2="20" y2="18" />
          <circle cx="6" cy="12" r="2" fill="currentColor" />
          <circle cx="10" cy="18" r="2" fill="currentColor" />
        </svg>
        Filters
        {activeCount > 0 && (
          <span className="ml-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-sea text-[9px] font-bold text-white">
            {activeCount}
          </span>
        )}
      </button>

      {/* Panel (mobile: full overlay, desktop: dropdown) */}
      {open && (
        <>
          {/* Backdrop (mobile) */}
          <div
            className="fixed inset-0 bg-ink/20 z-40 lg:hidden"
            onClick={onToggle}
          />

          <div className="fixed inset-x-0 bottom-0 top-16 z-50 lg:absolute lg:top-full lg:left-0 lg:right-auto lg:bottom-auto lg:mt-2 lg:w-[380px] lg:rounded-2xl lg:border lg:border-line lg:shadow-lift bg-panel overflow-hidden flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-line px-4 py-3">
              <h3 className="text-sm font-semibold text-ink">Advanced filters</h3>
              <div className="flex items-center gap-2">
                {activeCount > 0 && (
                  <button
                    type="button"
                    onClick={clearAll}
                    className="text-xs font-medium text-sea hover:text-sea-bright"
                  >
                    Clear all
                  </button>
                )}
                <button
                  type="button"
                  onClick={onToggle}
                  className="rounded-lg p-1 text-mist hover:text-ink hover:bg-paper transition-colors"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Scrollable body */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
              {/* Sort */}
              <div>
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-mist mb-1.5">
                  Sort by
                </label>
                <select
                  value={localFilters.sort}
                  onChange={(e) => update({ sort: e.target.value as SortOption })}
                  className="w-full rounded-lg border border-line bg-paper px-2.5 py-1.5 text-xs text-ink focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20"
                >
                  {SORT_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>

              <RangeRow
                label="Price"
                unit="€"
                min={localFilters.priceMin}
                max={localFilters.priceMax}
                onMinChange={(v) => update({ priceMin: v })}
                onMaxChange={(v) => update({ priceMax: v })}
                placeholderMin="0"
                placeholderMax="No max"
              />

              <RangeRow
                label="Area"
                unit="m²"
                min={localFilters.areaMin}
                max={localFilters.areaMax}
                onMinChange={(v) => update({ areaMin: v })}
                onMaxChange={(v) => update({ areaMax: v })}
              />

              <RangeRow
                label="Rooms"
                min={localFilters.roomsMin}
                max={localFilters.roomsMax}
                onMinChange={(v) => update({ roomsMin: v })}
                onMaxChange={(v) => update({ roomsMax: v })}
                placeholderMin="1"
                placeholderMax="5+"
              />

              <RangeRow
                label="Floor"
                min={localFilters.floorMin}
                max={localFilters.floorMax}
                onMinChange={(v) => update({ floorMin: v })}
                onMaxChange={(v) => update({ floorMax: v })}
              />

              <RangeRow
                label="Year built"
                min={localFilters.yearMin}
                max={localFilters.yearMax}
                onMinChange={(v) => update({ yearMin: v })}
                onMaxChange={(v) => update({ yearMax: v })}
                placeholderMin="1960"
                placeholderMax="2026"
              />

              <ChipGroup
                label="Construction"
                options={CONSTRUCTION_TYPES}
                selected={localFilters.constructionTypes}
                onToggle={(v) =>
                  update({ constructionTypes: toggleArrayItem(localFilters.constructionTypes, v) })
                }
              />

              <ChipGroup
                label="Amenities"
                options={AMENITIES}
                selected={localFilters.amenities}
                onToggle={(v) =>
                  update({ amenities: toggleArrayItem(localFilters.amenities, v) })
                }
              />
            </div>

            {/* Footer with result count (mobile) */}
            <div className="border-t border-line p-4 lg:hidden">
              <button
                type="button"
                onClick={onToggle}
                className="w-full rounded-full bg-sea py-2.5 text-sm font-semibold text-white hover:bg-sea-bright transition-colors"
              >
                Show results
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
}
