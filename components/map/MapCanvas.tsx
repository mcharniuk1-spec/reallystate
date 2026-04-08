"use client";

import { useEffect, useRef, useState } from "react";
import type { Listing } from "@/lib/types/listing";

const BULGARIA_CENTER: [number, number] = [25.4, 42.7];
const DEFAULT_ZOOM = 7;

type Props = {
  listings: Listing[];
  highlightId?: string | null;
  onSelect?: (id: string) => void;
};

export function MapCanvas({ listings, highlightId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    let cancelled = false;

    (async () => {
      try {
        const maplibregl = await import("maplibre-gl");
        await import("maplibre-gl/dist/maplibre-gl.css");

        if (cancelled || !containerRef.current) return;

        const map = new maplibregl.Map({
          container: containerRef.current,
          style: {
            version: 8,
            name: "BGEstate",
            sources: {
              osm: {
                type: "raster",
                tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                tileSize: 256,
                attribution: "&copy; OpenStreetMap contributors",
              },
            },
            layers: [
              {
                id: "osm-tiles",
                type: "raster",
                source: "osm",
                minzoom: 0,
                maxzoom: 19,
              },
            ],
          },
          center: BULGARIA_CENTER,
          zoom: DEFAULT_ZOOM,
          maxBounds: [
            [20.0, 40.5],
            [30.5, 45.0],
          ],
        });

        map.addControl(new maplibregl.NavigationControl(), "top-right");
        mapRef.current = map;

        map.on("load", () => {
          if (!cancelled) setReady(true);
        });
      } catch {
        /* MapLibre CSS import may fail in SSR; silently degrade */
      }
    })();

    return () => {
      cancelled = true;
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;

    for (const m of markersRef.current) m.remove();
    markersRef.current = [];

    (async () => {
      const maplibregl = await import("maplibre-gl");

      for (const l of listings) {
        if (l.latitude == null || l.longitude == null) continue;

        const el = document.createElement("div");
        el.className = "bge-pin";
        el.dataset.id = l.reference_id;
        el.style.cssText = `
          width:14px;height:14px;border-radius:50%;
          background:#0b6b57;border:2.5px solid #fff;
          box-shadow:0 2px 6px rgba(0,0,0,.25);cursor:pointer;
          transition:transform 150ms ease,background 150ms ease;
        `;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([l.longitude, l.latitude])
          .addTo(map);

        el.addEventListener("click", (e) => {
          e.stopPropagation();
          onSelect?.(l.reference_id);
        });

        markersRef.current.push(marker);
      }
    })();
  }, [listings, ready, onSelect]);

  useEffect(() => {
    for (const m of markersRef.current) {
      const el = m.getElement();
      const id = el.dataset.id;
      if (id === highlightId) {
        el.style.transform = "scale(1.6)";
        el.style.background = "#0d8a72";
        el.style.zIndex = "10";
      } else {
        el.style.transform = "";
        el.style.background = "#0b6b57";
        el.style.zIndex = "";
      }
    }
  }, [highlightId]);

  return (
    <div ref={containerRef} className="h-full w-full rounded-2xl overflow-hidden bg-paper">
      {!ready && (
        <div className="h-full w-full flex items-center justify-center">
          <div className="text-center">
            <div className="mx-auto h-8 w-8 rounded-full border-2 border-sea border-t-transparent animate-spin" />
            <p className="mt-3 text-xs text-mist">Loading map...</p>
          </div>
        </div>
      )}
    </div>
  );
}
