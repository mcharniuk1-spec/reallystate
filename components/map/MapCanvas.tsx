"use client";

import { useEffect, useRef, useState, useCallback, type MutableRefObject } from "react";
import type { Listing } from "@/lib/types/listing";
import type { Map as MapLibreMap, Marker as MapLibreMarker } from "maplibre-gl";

const BULGARIA_CENTER: [number, number] = [25.4, 42.7];
const DEFAULT_ZOOM = 7;
const MAP_3D_PITCH = 14;
const MAP_3D_BEARING = -8;
const CLUSTER_GRAVITY_RADIUS_FACTOR = 0.2;
const CLUSTER_GRAVITY_MIN_VISIBLE_PROPERTIES = 21;
const VARNA_CENTER: [number, number] = [27.91, 43.21];

type Props = {
  listings: MapListing[];
  highlightId?: string | null;
  onSelect?: (id: string) => void;
};

export type MapListing = Listing & {
  map_marker_kind?: "property" | "cluster";
  map_cluster_count?: number;
  map_cluster_label?: string;
  map_cluster_items?: string[];
};

export function MapCanvas({ listings, highlightId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<MapLibreMarker[]>([]);
  const didFitRef = useRef(false);
  const isAutoCenteringRef = useRef(false);
  const [ready, setReady] = useState(false);
  const [is3D, setIs3D] = useState(true);

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
          style: {
            version: 8,
            sources: {
              "openstreetmap-raster": {
                type: "raster",
                tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                tileSize: 256,
                attribution: "© OpenStreetMap contributors",
              },
            },
            layers: [
              {
                id: "openstreetmap-raster",
                type: "raster",
                source: "openstreetmap-raster",
              },
            ],
          },
          center: BULGARIA_CENTER,
          zoom: DEFAULT_ZOOM,
          pitch: MAP_3D_PITCH,
          bearing: MAP_3D_BEARING,
          maxBounds: [
            [20.0, 40.5],
            [30.5, 45.0],
          ],
        });

        map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
        mapRef.current = map;

        let initialized = false;
        const initializeMapLayers = () => {
          if (cancelled || initialized) return;
          initialized = true;
          try {
            if (!map.isStyleLoaded()) {
              initialized = false;
              return;
            }
            addBuildingLayer(map);
            setBuildingVisibility(map, "visible");
          } finally {
            if (initialized) setReady(true);
          }
        };

        map.on("load", initializeMapLayers);
        map.on("styledata", initializeMapLayers);
        window.setTimeout(() => {
          if (cancelled) return;
          if (!initialized) {
            try {
              if (map.isStyleLoaded()) {
                addBuildingLayer(map);
                setBuildingVisibility(map, "visible");
              }
            } finally {
              initialized = true;
              setReady(true);
            }
          }
        }, 1800);
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
        const isCluster = (l.map_cluster_count ?? 1) > 1 || l.map_marker_kind === "cluster";
        el.className = isCluster ? "bge-price-pin bge-cluster-pin" : "bge-price-pin";
        el.dataset.id = l.reference_id;
        el.dataset.items = l.map_cluster_items?.join("|") ?? l.reference_id;
        el.title = isCluster
          ? `${l.map_cluster_label ?? "Area"}: ${l.map_cluster_count ?? 1} properties`
          : l.title ?? l.reference_id;
        el.textContent = isCluster ? `${l.map_cluster_count ?? 1}` : l.price ? `${Math.round(l.price / 1000)}k` : "•";

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([l.longitude, l.latitude])
          .addTo(map);

        el.addEventListener("click", (e) => {
          e.stopPropagation();
          onSelect?.(l.reference_id);
        });

        markersRef.current.push(marker);
      }

      if (!didFitRef.current) {
        fitToListings(map, listings);
        didFitRef.current = true;
        window.setTimeout(() => pinLargestNearbyAggregation(map, listings, is3D, isAutoCenteringRef), 250);
      }
    })();
  }, [listings, ready, onSelect, is3D]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;

    let timer: number | undefined;
    const handleMoveSettled = () => {
      if (isAutoCenteringRef.current) return;
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        pinLargestNearbyAggregation(map, listings, is3D, isAutoCenteringRef);
      }, 180);
    };

    map.on("moveend", handleMoveSettled);
    map.on("zoomend", handleMoveSettled);

    return () => {
      window.clearTimeout(timer);
      map.off("moveend", handleMoveSettled);
      map.off("zoomend", handleMoveSettled);
    };
  }, [listings, ready, is3D]);

  // Highlight pin
  useEffect(() => {
    for (const m of markersRef.current) {
      const el = m.getElement();
      const id = el.dataset.id;
      const containsHighlighted = Boolean(highlightId && (id === highlightId || el.dataset.items?.split("|").includes(highlightId)));
      if (containsHighlighted) {
        el.classList.add("is-selected");
        el.style.zIndex = "10";
      } else {
        el.classList.remove("is-selected");
        el.style.zIndex = "";
      }
    }

    const map = mapRef.current;
    const selected = listings.find((item) => item.reference_id === highlightId);
    if (map && selected?.latitude != null && selected.longitude != null) {
      map.easeTo({
        center: [selected.longitude, selected.latitude],
        zoom: Math.max(map.getZoom(), 15.5),
        pitch: is3D ? MAP_3D_PITCH : map.getPitch(),
        bearing: is3D ? MAP_3D_BEARING : map.getBearing(),
        duration: 850,
      });
    }
  }, [highlightId]);

  const toggle3D = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;

    const next = !is3D;
    setIs3D(next);

    if (next) {
      map.easeTo({ pitch: MAP_3D_PITCH, bearing: MAP_3D_BEARING, zoom: Math.max(map.getZoom(), 14), duration: 800 });
      setBuildingVisibility(map, "visible");
    } else {
      map.easeTo({ pitch: 0, bearing: 0, duration: 800 });
      setBuildingVisibility(map, "none");
    }
  }, [is3D]);

  const flyToVarna = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;
    map.flyTo({ center: VARNA_CENTER, zoom: 15, pitch: is3D ? MAP_3D_PITCH : 0, bearing: is3D ? MAP_3D_BEARING : 0, duration: 2000 });
  }, [is3D]);

  return (
    <div className="relative h-full w-full overflow-hidden bg-paper">
      <div ref={containerRef} className="h-full w-full" />

      <style jsx global>{`
        .bge-price-pin {
          min-width: 36px;
          height: 24px;
          border-radius: 999px;
          border: 2px solid rgba(255, 255, 255, 0.92);
          background: rgba(9, 63, 66, 0.9);
          color: white;
          cursor: pointer;
          display: grid;
          place-items: center;
          font: 800 11px/1 Arial, system-ui, sans-serif;
          padding: 0 8px;
          box-shadow: 0 8px 18px rgba(3, 18, 20, 0.34);
          transition: transform 150ms ease, background 150ms ease, box-shadow 150ms ease;
          user-select: none;
        }
        .bge-price-pin:hover,
        .bge-price-pin.is-selected {
          background: #087763;
          box-shadow: 0 10px 24px rgba(8, 119, 99, 0.38);
          transform: scale(1.18);
        }
        .bge-cluster-pin {
          min-width: 42px;
          height: 30px;
          border-color: rgba(209, 243, 238, 0.96);
          background: rgba(5, 84, 89, 0.92);
          font-size: 12px;
        }
        .bge-cluster-pin::after {
          content: "";
          position: absolute;
          inset: -7px;
          border-radius: 999px;
          border: 2px solid rgba(134, 216, 206, 0.42);
        }
      `}</style>

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
          <div className="rounded-xl border border-line/50 bg-white/90 px-3 py-2 text-[10px] font-semibold text-mist shadow-lg backdrop-blur-sm">
            OSM base / building objects require matched footprints
          </div>
        </div>
      )}
    </div>
  );
}

function addBuildingLayer(map: MapLibreMap) {
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
        "fill-extrusion-opacity": 0.78,
      },
      layout: {
        visibility: "visible",
      },
    });
  }

}

function setBuildingVisibility(map: MapLibreMap, visibility: "visible" | "none") {
  if (map.getLayer("bge-3d-buildings")) {
    map.setLayoutProperty("bge-3d-buildings", "visibility", visibility);
  }
}

function pinLargestNearbyAggregation(
  map: MapLibreMap,
  listings: MapListing[],
  is3D: boolean,
  autoCenteringRef: MutableRefObject<boolean>,
) {
  const canvas = map.getCanvas();
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return;

  const center = { x: width / 2, y: height / 2 };
  const nearbyRadius = Math.sqrt(width * height) * CLUSTER_GRAVITY_RADIUS_FACTOR;
  const visible = listings
    .filter((item) => item.latitude != null && item.longitude != null)
    .map((item) => {
      const point = map.project([item.longitude as number, item.latitude as number]);
      const count = item.map_cluster_count ?? 1;
      const distanceFromCenter = Math.hypot(point.x - center.x, point.y - center.y);
      return { item, point, count, distanceFromCenter };
    })
    .filter(({ point }) => point.x >= 0 && point.x <= width && point.y >= 0 && point.y <= height);

  const visibleProperties = visible.reduce((sum, entry) => sum + entry.count, 0);
  if (visibleProperties < CLUSTER_GRAVITY_MIN_VISIBLE_PROPERTIES) return;

  const target = visible
    .filter((entry) => entry.distanceFromCenter <= nearbyRadius)
    .sort((a, b) => b.count - a.count || a.distanceFromCenter - b.distanceFromCenter)[0];

  if (!target || target.count <= 1 || target.distanceFromCenter < 12) return;

  autoCenteringRef.current = true;
  map.easeTo({
    center: [target.item.longitude as number, target.item.latitude as number],
    pitch: is3D ? MAP_3D_PITCH : 0,
    bearing: is3D ? MAP_3D_BEARING : 0,
    duration: 700,
    essential: true,
  });
  window.setTimeout(() => {
    autoCenteringRef.current = false;
  }, 780);
}

function fitToListings(map: MapLibreMap, listings: Listing[]) {
  const coords = listings
    .filter((item) => item.latitude != null && item.longitude != null)
    .slice(0, 600)
    .map((item) => [item.longitude as number, item.latitude as number] as [number, number]);
  if (coords.length < 2) return;
  const lngs = coords.map(([lng]) => lng);
  const lats = coords.map(([, lat]) => lat);
  map.fitBounds(
    [
      [Math.min(...lngs), Math.min(...lats)],
      [Math.max(...lngs), Math.max(...lats)],
    ],
    { padding: 72, maxZoom: 12.5, duration: 0 },
  );
}
