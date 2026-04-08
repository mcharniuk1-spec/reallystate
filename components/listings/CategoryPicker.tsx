"use client";

import { CATEGORIES, INTENTS, type ListingIntent, type PropertyCategory } from "@/lib/types/listing";

export function IntentToggle({
  value,
  onChange,
}: {
  value: ListingIntent | null;
  onChange: (v: ListingIntent | null) => void;
}) {
  return (
    <div className="flex gap-1 rounded-xl bg-paper p-1 border border-line">
      <button
        type="button"
        onClick={() => onChange(null)}
        className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
          value === null ? "bg-sea text-white shadow-sm" : "text-mist hover:text-ink"
        }`}
      >
        All
      </button>
      {INTENTS.map((i) => (
        <button
          key={i.value}
          type="button"
          onClick={() => onChange(value === i.value ? null : i.value)}
          className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
            value === i.value ? "bg-sea text-white shadow-sm" : "text-mist hover:text-ink"
          }`}
        >
          {i.label}
        </button>
      ))}
    </div>
  );
}

export function CategoryPicker({
  selected,
  onChange,
}: {
  selected: PropertyCategory | null;
  onChange: (v: PropertyCategory | null) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1.5">
      <button
        type="button"
        onClick={() => onChange(null)}
        className={`rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
          selected === null
            ? "border-sea bg-sea/10 text-sea"
            : "border-line text-mist hover:border-sea/30 hover:text-ink"
        }`}
      >
        All types
      </button>
      {CATEGORIES.map((c) => (
        <button
          key={c.value}
          type="button"
          onClick={() => onChange(selected === c.value ? null : c.value)}
          className={`rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
            selected === c.value
              ? "border-sea bg-sea/10 text-sea"
              : "border-line text-mist hover:border-sea/30 hover:text-ink"
          }`}
        >
          {c.label}
        </button>
      ))}
    </div>
  );
}
