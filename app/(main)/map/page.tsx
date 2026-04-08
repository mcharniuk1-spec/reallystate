import { AppShell } from "@/components/shell/AppShell";

export default function MapPage() {
  return (
    <AppShell
      title="Map"
      subtitle="MapLibre GL + deck.gl layers will load viewport clusters and building summaries from map APIs. Weak geometry falls back to 2D pins."
    >
      <div className="rounded-3xl border border-dashed border-sea/35 bg-sea/5 p-12 text-center">
        <p className="font-display text-2xl text-ink">Map canvas</p>
        <p className="mt-3 text-mist max-w-md mx-auto leading-relaxed">
          Dependencies are already declared (<code className="text-ink">maplibre-gl</code>,{" "}
          <code className="text-ink">@deck.gl/*</code>). Wire them once `/map/viewport` and tile endpoints are
          stable.
        </p>
      </div>
    </AppShell>
  );
}
