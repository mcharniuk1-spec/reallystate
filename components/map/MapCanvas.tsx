"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type MutableRefObject } from "react";
import type { Listing } from "@/lib/types/listing";
import type { Map as MapLibreMap, StyleSpecification } from "maplibre-gl";

const BULGARIA_CENTER: [number, number] = [25.4, 42.7];
const DEFAULT_ZOOM = 7;
const MAP_3D_PITCH = 14;
const MAP_3D_BEARING = -8;
const CLUSTER_GRAVITY_RADIUS_FACTOR = 0.2;
const CLUSTER_GRAVITY_MIN_VISIBLE_PROPERTIES = 21;
const VARNA_CENTER: [number, number] = [27.91, 43.21];
const VECTOR_SOURCE_ID = "openfreemap-vector";
const BUILDING_LAYER_ID = "bge-3d-buildings";

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

type ScreenMarker = {
  id: string;
  items: string[];
  title: string;
  text: string;
  x: number;
  y: number;
  isCluster: boolean;
};

export function MapCanvas({ listings, highlightId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const lastFitKeyRef = useRef<string | null>(null);
  const isAutoCenteringRef = useRef(false);
  const [ready, setReady] = useState(false);
  const [mapIssue, setMapIssue] = useState<string | null>(null);
  const [is3D, setIs3D] = useState(true);
  const [screenMarkers, setScreenMarkers] = useState<ScreenMarker[]>([]);
  const fitKey = useMemo(
    () =>
      listings
        .filter((item) => item.latitude != null && item.longitude != null)
        .map((item) => `${item.reference_id}:${item.latitude}:${item.longitude}:${item.map_cluster_count ?? 1}`)
        .join("|"),
    [listings],
  );
  const updateScreenMarkers = useCallback((map: MapLibreMap | null = mapRef.current) => {
    if (!map) return;
    setScreenMarkers(projectScreenMarkers(map, listings));
  }, [listings]);

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
          style: buildMapStyle(),
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
        map.getCanvas().style.cursor = "grab";
        map.on("dragstart", () => {
          map.getCanvas().style.cursor = "grabbing";
        });
        map.on("dragend", () => {
          map.getCanvas().style.cursor = "grab";
        });
        map.on("error", (event) => {
          const message = event?.error?.message ?? "Map tiles are not fully available.";
          if (message.toLowerCase().includes("tile") || message.toLowerCase().includes("fetch")) {
            setMapIssue("Some OSM/OpenFreeMap tiles did not load; offline fallback remains visible.");
          } else {
            setMapIssue(message);
          }
          setReady(true);
        });

        const resizeObserver = new ResizeObserver(() => map.resize());
        resizeObserver.observe(containerRef.current);
        window.setTimeout(() => map.resize(), 100);

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
            map.resize();
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
                map.resize();
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
      lastFitKeyRef.current = null;
      setScreenMarkers([]);
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;

    updateScreenMarkers(map);

    if (fitKey && lastFitKeyRef.current !== fitKey) {
      fitToListings(map, listings);
      lastFitKeyRef.current = fitKey;
      window.setTimeout(() => {
        updateScreenMarkers(map);
        pinLargestNearbyAggregation(map, listings, is3D, isAutoCenteringRef);
      }, 250);
    }
  }, [listings, ready, is3D, fitKey, updateScreenMarkers]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;

    const update = () => updateScreenMarkers(map);
    map.on("move", update);
    map.on("zoom", update);
    map.on("resize", update);
    update();

    return () => {
      map.off("move", update);
      map.off("zoom", update);
      map.off("resize", update);
    };
  }, [ready, updateScreenMarkers]);

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

  useEffect(() => {
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
      window.setTimeout(() => updateScreenMarkers(map), 900);
    }
  }, [highlightId, listings, is3D, updateScreenMarkers]);

  const setMapDimension = useCallback((next: boolean) => {
    const map = mapRef.current;
    if (!map) return;

    setIs3D(next);

    if (next) {
      map.easeTo({ pitch: MAP_3D_PITCH, bearing: MAP_3D_BEARING, duration: 800 });
      setBuildingVisibility(map, "visible");
    } else {
      map.easeTo({ pitch: 0, bearing: 0, duration: 800 });
      setBuildingVisibility(map, "none");
    }
  }, []);

  const zoomToAll = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;
    fitToListings(map, listings);
    window.setTimeout(() => pinLargestNearbyAggregation(map, listings, is3D, isAutoCenteringRef), 250);
  }, [is3D, listings]);

  const flyToVarna = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;
    map.flyTo({ center: VARNA_CENTER, zoom: 15, pitch: is3D ? MAP_3D_PITCH : 0, bearing: is3D ? MAP_3D_BEARING : 0, duration: 1400 });
  }, [is3D]);

  return (
    <div className="relative isolate h-full w-full overflow-hidden bg-paper" data-map-testid="property-map">
      <div className="bge-map-fallback absolute inset-0" aria-hidden />
      <div ref={containerRef} className="relative h-full w-full" />
      {screenMarkers.map((marker) => {
        const selected = Boolean(highlightId && (marker.id === highlightId || marker.items.includes(highlightId)));
        return (
          <button
            key={marker.id}
            type="button"
            onPointerDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelect?.(marker.id);
            }}
            onMouseDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelect?.(marker.id);
            }}
            onClickCapture={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelect?.(marker.id);
            }}
            onClick={() => onSelect?.(marker.id)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                event.stopPropagation();
                onSelect?.(marker.id);
              }
            }}
            className={`bge-price-pin ${marker.isCluster ? "bge-cluster-pin" : ""} ${selected ? "is-selected" : ""}`}
            style={{
              left: marker.x,
              top: marker.y,
              position: "absolute",
              pointerEvents: "auto",
              transform: "translate(-50%, -50%)",
                zIndex: selected ? 1100 : 1000,
            }}
            title={marker.title}
            aria-label={marker.isCluster ? `Map group ${marker.title}` : `Map property ${marker.title}`}
          >
            {marker.text}
          </button>
        );
      })}

      <style jsx global>{`
        .maplibregl-canvas {
          outline: none;
        }
        .maplibregl-marker {
          pointer-events: auto !important;
        }
        .bge-map-fallback {
          background:
            linear-gradient(90deg, rgba(8, 95, 86, 0.12) 1px, transparent 1px),
            linear-gradient(rgba(8, 95, 86, 0.12) 1px, transparent 1px),
            radial-gradient(circle at 76% 40%, rgba(73, 167, 184, 0.24), transparent 24%),
            radial-gradient(circle at 48% 52%, rgba(54, 142, 103, 0.22), transparent 32%),
            linear-gradient(135deg, #edf1e8 0%, #dbe8dc 42%, #cadfcf 100%);
          background-size: 96px 96px, 96px 96px, auto, auto, auto;
        }
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
        <div className="absolute bottom-4 left-4 flex flex-col gap-2" style={{ zIndex: 1200 }}>
          <div className="flex rounded-xl border border-line/50 bg-white/90 p-1 text-xs font-semibold text-ink shadow-lg backdrop-blur-sm">
            <button
              type="button"
              onClick={() => setMapDimension(false)}
              className={`rounded-lg px-3 py-1.5 transition ${!is3D ? "bg-sea text-white" : "hover:bg-panel"}`}
              title="Switch to flat 2D map"
            >
              2D
            </button>
            <button
              type="button"
              onClick={() => setMapDimension(true)}
              className={`rounded-lg px-3 py-1.5 transition ${is3D ? "bg-sea text-white" : "hover:bg-panel"}`}
              title="Switch to low-pitch 3D building view"
            >
              3D
            </button>
          </div>

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
          <button
            type="button"
            onClick={zoomToAll}
            className="flex items-center gap-1.5 rounded-xl bg-white/90 border border-line/50 px-3 py-2 text-xs font-semibold text-ink shadow-lg backdrop-blur-sm hover:bg-white transition-colors"
            title="Fit all visible grouped points"
          >
            Reset map
          </button>
          <div className="rounded-xl border border-line/50 bg-white/90 px-3 py-2 text-[10px] font-semibold text-mist shadow-lg backdrop-blur-sm">
            {mapIssue ?? "OSM + OpenFreeMap vector buildings"}
          </div>
        </div>
      )}
    </div>
  );
}

function projectScreenMarkers(map: MapLibreMap, listings: MapListing[]): ScreenMarker[] {
  const canvas = map.getCanvas();
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return [];

  return listings
    .filter((item) => item.latitude != null && item.longitude != null)
    .map((item) => {
      const isCluster = (item.map_cluster_count ?? 1) > 1 || item.map_marker_kind === "cluster";
      const point = map.project([item.longitude as number, item.latitude as number]);
      const title = isCluster
        ? `${item.map_cluster_label ?? "Area"}: ${item.map_cluster_count ?? 1} properties`
        : item.title ?? item.reference_id;
      return {
        id: item.reference_id,
        items: item.map_cluster_items ?? [item.reference_id],
        title,
        text: isCluster ? `${item.map_cluster_count ?? 1}` : item.price ? `${Math.round(item.price / 1000)}k` : "•",
        x: point.x,
        y: point.y,
        isCluster,
      };
    })
    .filter((marker) => marker.x >= -80 && marker.x <= width + 80 && marker.y >= -80 && marker.y <= height + 80);
}

function buildMapStyle(): StyleSpecification {
  return {
    version: 8,
    glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
    sources: {
      "openstreetmap-raster": {
        type: "raster",
        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "OpenStreetMap contributors",
      },
      [VECTOR_SOURCE_ID]: {
        type: "vector",
        tiles: ["https://tiles.openfreemap.org/planet/{z}/{x}/{y}.pbf"],
        minzoom: 0,
        maxzoom: 14,
        attribution: "OpenFreeMap",
      },
    },
    layers: [
      {
        id: "bge-map-background",
        type: "background",
        paint: {
          "background-color": "#e6eee4",
        },
      },
      {
        id: "openstreetmap-raster",
        type: "raster",
        source: "openstreetmap-raster",
        paint: {
          "raster-opacity": 0.96,
        },
      },
    ],
  } as StyleSpecification;
}

function addBuildingLayer(map: MapLibreMap) {
  if (!map.getSource(VECTOR_SOURCE_ID) || map.getLayer(BUILDING_LAYER_ID)) return;
  try {
    map.addLayer({
      id: BUILDING_LAYER_ID,
      source: VECTOR_SOURCE_ID,
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
  } catch {
    // Some free vector mirrors expose the base map but not building source layers.
  }
}

function setBuildingVisibility(map: MapLibreMap, visibility: "visible" | "none") {
  if (map.getLayer(BUILDING_LAYER_ID)) {
    map.setLayoutProperty(BUILDING_LAYER_ID, "visibility", visibility);
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
