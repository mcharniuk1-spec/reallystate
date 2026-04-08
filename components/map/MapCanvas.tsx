"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { Listing } from "@/lib/types/listing";

const BULGARIA_CENTER: [number, number] = [25.4, 42.7];
const DEFAULT_ZOOM = 7;
const VARNA_CENTER: [number, number] = [27.91, 43.21];

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
  const [is3D, setIs3D] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    let cancelled = false;

    (async () => {
      try {
        const maplibregl = await import("maplibre-gl");
        // @ts-expect-error CSS import handled by bundler
        await import("maplibre-gl/dist/maplibre-gl.css");
        if (cancelled || !containerRef.current) return;

        const map = new maplibregl.Map({
          container: containerRef.current,
          style: "https://tiles.openfreemap.org/styles/liberty",
          center: BULGARIA_CENTER,
          zoom: DEFAULT_ZOOM,
          pitch: 0,
          bearing: 0,
          maxBounds: [
            [20.0, 40.5],
            [30.5, 45.0],
          ],
        });

        map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
        mapRef.current = map;

        map.on("load", () => {
          if (cancelled) return;

          addBuildingLayer(map);
          setReady(true);
        });
      } catch {
        /* MapLibre load may fail in SSR; silently degrade */
      }
    })();

    return () => {
      cancelled = true;
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  // Markers for listings
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

  // Highlight pin
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

  const toggle3D = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    const next = !is3D;
    setIs3D(next);

    if (next) {
      map.easeTo({ pitch: 55, bearing: -20, zoom: Math.max(map.getZoom(), 14), duration: 800 });
      setBuildingVisibility(map, "visible");
    } else {
      map.easeTo({ pitch: 0, bearing: 0, duration: 800 });
      setBuildingVisibility(map, "none");
    }
  }, [is3D]);

  const flyToVarna = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;
    map.flyTo({ center: VARNA_CENTER, zoom: 15, pitch: is3D ? 55 : 0, bearing: is3D ? -20 : 0, duration: 2000 });
  }, [is3D]);

  return (
    <div className="relative h-full w-full overflow-hidden bg-paper">
      <div ref={containerRef} className="h-full w-full" />

      {!ready && (
        <div className="absolute inset-0 flex items-center justify-center bg-paper">
          <div className="text-center">
            <div className="mx-auto h-8 w-8 rounded-full border-2 border-sea border-t-transparent animate-spin" />
            <p className="mt-3 text-xs text-mist">Loading map...</p>
          </div>
        </div>
      )}

      {/* Map controls */}
      {ready && (
        <div className="absolute bottom-4 left-4 flex flex-col gap-2 z-10">
          {/* 2D / 3D toggle */}
          <button
            type="button"
            onClick={toggle3D}
            className={`flex items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-semibold shadow-lg backdrop-blur-sm transition-colors ${
              is3D
                ? "bg-sea text-white"
                : "bg-white/90 text-ink hover:bg-white border border-line/50"
            }`}
            title={is3D ? "Switch to 2D" : "Switch to 3D buildings"}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {is3D ? (
                <>
                  <path d="M12 3L2 9l10 6 10-6-10-6z" />
                  <path d="M2 17l10 6 10-6" />
                  <path d="M2 13l10 6 10-6" />
                </>
              ) : (
                <>
                  <path d="M12 3L2 9l10 6 10-6-10-6z" />
                  <path d="M2 17l10 6 10-6" />
                  <path d="M2 13l10 6 10-6" />
                </>
              )}
            </svg>
            {is3D ? "3D" : "2D"}
          </button>

          {/* Fly to Varna */}
          <button
            type="button"
            onClick={flyToVarna}
            className="flex items-center gap-1.5 rounded-xl bg-white/90 border border-line/50 px-3 py-2 text-xs font-semibold text-ink shadow-lg backdrop-blur-sm hover:bg-white transition-colors"
            title="Fly to Varna"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
            Varna
          </button>
        </div>
      )}
    </div>
  );
}

function addBuildingLayer(map: maplibregl.Map) {
  const style = map.getStyle();
  if (!style?.sources) return;

  const vectorSourceId = Object.keys(style.sources).find((key) => {
    const src = style.sources[key];
    return src && "type" in src && src.type === "vector";
  });

  if (!vectorSourceId) return;

  const existingLayers = style.layers?.map((l) => l.id) ?? [];

  if (!existingLayers.includes("bge-3d-buildings")) {
    map.addLayer({
      id: "bge-3d-buildings",
      source: vectorSourceId,
      "source-layer": "building",
      type: "fill-extrusion",
      minzoom: 14,
      paint: {
        "fill-extrusion-color": [
          "interpolate",
          ["linear"],
          ["get", "render_height"],
          0, "#d4c9a8",
          20, "#b8a882",
          50, "#9a8d6e",
          100, "#7e7460",
        ],
        "fill-extrusion-height": [
          "interpolate",
          ["linear"],
          ["zoom"],
          14, 0,
          15.5, ["get", "render_height"],
        ],
        "fill-extrusion-base": [
          "case",
          ["has", "render_min_height"],
          ["get", "render_min_height"],
          0,
        ],
        "fill-extrusion-opacity": 0.75,
      },
      layout: {
        visibility: "none",
      },
    });
  }
}

function setBuildingVisibility(map: maplibregl.Map, visibility: "visible" | "none") {
  if (map.getLayer("bge-3d-buildings")) {
    map.setLayoutProperty("bge-3d-buildings", "visibility", visibility);
  }
}
