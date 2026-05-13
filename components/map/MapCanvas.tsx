"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type MutableRefObject } from "react";
import type { Listing } from "@/lib/types/listing";
import type { Map as MapLibreMap, StyleSpecification } from "maplibre-gl";

const BULGARIA_CENTER: [number, number] = [25.4, 42.7];
const DEFAULT_ZOOM = 7;
const MAP_3D_PITCH = 45;
const MAP_3D_BEARING = -12;
const MAX_VIEW_MARKERS = 20;
const CLUSTER_GRAVITY_RADIUS_FACTOR = 0.2;
const CLUSTER_GRAVITY_MIN_VISIBLE_PROPERTIES = 21;
const VARNA_CENTER: [number, number] = [27.91, 43.21];
const VECTOR_SOURCE_ID = "openfreemap-vector";
const BUILDING_LAYER_ID = "bge-3d-buildings";
const BULGARIA_BOUNDS = {
  minLng: 22.25,
  maxLng: 28.85,
  minLat: 41.15,
  maxLat: 44.25,
};

type Props = {
  listings: MapListing[];
  highlightId?: string | null;
  onSelect?: (id: string, markerItems?: string[]) => void;
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
  lat: number;
  lng: number;
  isCluster: boolean;
};

type ProjectedListing = {
  item: MapListing;
  x: number;
  y: number;
  lat: number;
  lng: number;
};

type MarkerGroup = {
  points: ProjectedListing[];
  x: number;
  y: number;
  lat: number;
  lng: number;
};

export function MapCanvas({ listings, highlightId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const lastFitKeyRef = useRef<string | null>(null);
  const isAutoCenteringRef = useRef(false);
  const [ready, setReady] = useState(false);
  const [mapIssue, setMapIssue] = useState<string | null>(null);
  const [is3D, setIs3D] = useState(false);
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
          pitch: 0,
          bearing: 0,
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
            setBuildingVisibility(map, "none");
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
                setBuildingVisibility(map, "none");
                map.resize();
              }
            } finally {
              initialized = true;
              setReady(true);
            }
          }
        }, 1800);
      } catch {
        setMapIssue("Map engine unavailable; fallback property points are shown.");
        setReady(true);
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

  const visibleMarkers = screenMarkers.length ? screenMarkers : fallbackScreenMarkers(listings, containerRef);

  return (
    <div className="relative isolate h-full w-full overflow-hidden bg-paper" data-map-testid="property-map">
      <div className="bge-map-fallback absolute inset-0" aria-hidden />
      <div ref={containerRef} className="relative h-full w-full" />
      {visibleMarkers.map((marker) => {
        const selected = Boolean(highlightId && (marker.id === highlightId || marker.items.includes(highlightId)));
        return (
          <button
            key={marker.id}
            type="button"
            onPointerDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelect?.(marker.id, marker.items);
            }}
            onMouseDown={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelect?.(marker.id, marker.items);
            }}
            onClickCapture={(event) => {
              event.preventDefault();
              event.stopPropagation();
              onSelect?.(marker.id, marker.items);
            }}
            onClick={() => onSelect?.(marker.id, marker.items)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                event.stopPropagation();
                onSelect?.(marker.id, marker.items);
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
            <span className="bge-pin-main">{marker.text}</span>
            {marker.isCluster ? <span className="bge-pin-sub">items</span> : null}
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
            linear-gradient(28deg, transparent 0 42%, rgba(34, 126, 104, 0.16) 42.2% 43%, transparent 43.2% 100%),
            linear-gradient(153deg, transparent 0 37%, rgba(34, 126, 104, 0.13) 37.2% 38%, transparent 38.2% 100%),
            linear-gradient(90deg, rgba(8, 95, 86, 0.12) 1px, transparent 1px),
            linear-gradient(rgba(8, 95, 86, 0.12) 1px, transparent 1px),
            radial-gradient(circle at 76% 40%, rgba(73, 167, 184, 0.24), transparent 24%),
            radial-gradient(circle at 48% 52%, rgba(54, 142, 103, 0.22), transparent 32%),
            linear-gradient(135deg, #edf1e8 0%, #dbe8dc 42%, #cadfcf 100%);
          background-size: 96px 96px, 96px 96px, auto, auto, auto;
        }
        .bge-price-pin {
          min-width: 44px;
          min-height: 30px;
          border-radius: 999px;
          border: 2px solid rgba(255, 255, 255, 0.92);
          background: rgba(9, 63, 66, 0.9);
          color: white;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1px;
          font: 800 11px/1 Arial, system-ui, sans-serif;
          padding: 4px 9px;
          box-shadow: 0 8px 18px rgba(3, 18, 20, 0.34);
          transition: transform 150ms ease, background 150ms ease, box-shadow 150ms ease;
          user-select: none;
        }
        .bge-price-pin:hover,
        .bge-price-pin.is-selected {
          background: #087763;
          box-shadow: 0 10px 24px rgba(8, 119, 99, 0.38);
          transform: translate(-50%, -50%) scale(1.18) !important;
        }
        .bge-cluster-pin {
          min-width: 50px;
          min-height: 38px;
          border-color: rgba(209, 243, 238, 0.96);
          background: rgba(5, 84, 89, 0.92);
          font-size: 13px;
        }
        .bge-cluster-pin::after {
          content: "";
          position: absolute;
          inset: -7px;
          border-radius: 999px;
          border: 2px solid rgba(134, 216, 206, 0.42);
        }
        .bge-pin-sub {
          font-size: 8px;
          font-weight: 800;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          opacity: 0.78;
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
            {mapIssue ?? (is3D ? "3D OSM building layer at building zoom" : "2D viewport groups")}
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

  const points = listings
    .filter((item) => item.latitude != null && item.longitude != null)
    .map((item) => {
      const point = map.project([item.longitude as number, item.latitude as number]);
      return {
        item,
        x: point.x,
        y: point.y,
        lat: item.latitude as number,
        lng: item.longitude as number,
      };
    })
    .filter((point) => point.x >= -80 && point.x <= width + 80 && point.y >= -80 && point.y <= height + 80);

  return groupProjectedListings(points, width, height);
}

function fallbackScreenMarkers(listings: MapListing[], containerRef: MutableRefObject<HTMLDivElement | null>): ScreenMarker[] {
  const width = containerRef.current?.clientWidth || 720;
  const height = containerRef.current?.clientHeight || 960;
  const padX = Math.max(48, Math.min(width * 0.08, 96));
  const padY = Math.max(64, Math.min(height * 0.08, 112));

  const points = listings
    .filter((item) => item.latitude != null && item.longitude != null)
    .map((item) => {
      const lngRatio = ((item.longitude as number) - BULGARIA_BOUNDS.minLng) / (BULGARIA_BOUNDS.maxLng - BULGARIA_BOUNDS.minLng);
      const latRatio = (BULGARIA_BOUNDS.maxLat - (item.latitude as number)) / (BULGARIA_BOUNDS.maxLat - BULGARIA_BOUNDS.minLat);
      const x = padX + clamp(lngRatio, 0, 1) * Math.max(1, width - padX * 2);
      const y = padY + clamp(latRatio, 0, 1) * Math.max(1, height - padY * 2);
      return {
        item,
        x,
        y,
        lat: item.latitude as number,
        lng: item.longitude as number,
      };
    });

  return groupProjectedListings(points, width, height);
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function groupProjectedListings(points: ProjectedListing[], width: number, height: number): ScreenMarker[] {
  if (points.length <= MAX_VIEW_MARKERS) {
    return points.map((point) => groupToMarker({ points: [point], x: point.x, y: point.y, lat: point.lat, lng: point.lng }));
  }

  const groups =
    points.length < 40
      ? mergeClosestPoints(points)
      : gridGroupPoints(points, width, height);

  return groups
    .sort((a, b) => b.points.length - a.points.length || a.x - b.x)
    .slice(0, MAX_VIEW_MARKERS)
    .map(groupToMarker);
}

function mergeClosestPoints(points: ProjectedListing[]): MarkerGroup[] {
  const groups = points.map((point) => ({ points: [point], x: point.x, y: point.y, lat: point.lat, lng: point.lng }));

  while (groups.length > MAX_VIEW_MARKERS) {
    let bestA = 0;
    let bestB = 1;
    let bestDistance = Number.POSITIVE_INFINITY;
    for (let a = 0; a < groups.length; a += 1) {
      for (let b = a + 1; b < groups.length; b += 1) {
        const distance = Math.hypot(groups[a].x - groups[b].x, groups[a].y - groups[b].y);
        if (distance < bestDistance) {
          bestA = a;
          bestB = b;
          bestDistance = distance;
        }
      }
    }
    groups[bestA] = mergeGroups(groups[bestA], groups[bestB]);
    groups.splice(bestB, 1);
  }

  return groups;
}

function gridGroupPoints(points: ProjectedListing[], width: number, height: number): MarkerGroup[] {
  const landscape = width >= height;
  const cols = landscape ? 5 : 4;
  const rows = landscape ? 4 : 5;
  const groups = new Map<string, MarkerGroup>();

  for (const point of points) {
    const col = clamp(Math.floor((clamp(point.x, 0, width) / Math.max(width, 1)) * cols), 0, cols - 1);
    const row = clamp(Math.floor((clamp(point.y, 0, height) / Math.max(height, 1)) * rows), 0, rows - 1);
    const key = `${col}:${row}`;
    const existing = groups.get(key);
    const nextPoint = { points: [point], x: point.x, y: point.y, lat: point.lat, lng: point.lng };
    groups.set(key, existing ? mergeGroups(existing, nextPoint) : nextPoint);
  }

  return [...groups.values()];
}

function mergeGroups(a: MarkerGroup, b: MarkerGroup): MarkerGroup {
  const points = [...a.points, ...b.points];
  const count = points.length;
  return {
    points,
    x: points.reduce((sum, point) => sum + point.x, 0) / count,
    y: points.reduce((sum, point) => sum + point.y, 0) / count,
    lat: points.reduce((sum, point) => sum + point.lat, 0) / count,
    lng: points.reduce((sum, point) => sum + point.lng, 0) / count,
  };
}

function groupToMarker(group: MarkerGroup): ScreenMarker {
  const representative = [...group.points].sort((a, b) => {
    const scoreDelta = (b.item.scrape_quality_score ?? 0) - (a.item.scrape_quality_score ?? 0);
    if (scoreDelta) return scoreDelta;
    return (b.item.photo_count_local ?? b.item.local_image_files?.length ?? 0) - (a.item.photo_count_local ?? a.item.local_image_files?.length ?? 0);
  })[0].item;
  const isCluster = group.points.length > 1;
  const cityLabel = [representative.district ?? representative.resort, representative.city ?? representative.region].filter(Boolean).join(", ") || "Bulgaria";

  return {
    id: representative.reference_id,
    items: group.points.map((point) => point.item.reference_id),
    title: isCluster ? `${cityLabel}: ${group.points.length} properties` : representative.title ?? representative.reference_id,
    text: isCluster ? `${group.points.length}` : representative.price ? `${Math.round(representative.price / 1000)}k` : "•",
    x: group.x,
    y: group.y,
    lat: group.lat,
    lng: group.lng,
    isCluster,
  };
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
  const rawVisibleCount = listings
    .filter((item) => item.latitude != null && item.longitude != null)
    .filter((item) => {
      const point = map.project([item.longitude as number, item.latitude as number]);
      return point.x >= 0 && point.x <= width && point.y >= 0 && point.y <= height;
    }).length;

  if (rawVisibleCount < CLUSTER_GRAVITY_MIN_VISIBLE_PROPERTIES) return;

  const target = projectScreenMarkers(map, listings)
    .map((marker) => ({
      marker,
      distanceFromCenter: Math.hypot(marker.x - center.x, marker.y - center.y),
    }))
    .filter((entry) => entry.distanceFromCenter <= nearbyRadius)
    .sort((a, b) => b.marker.items.length - a.marker.items.length || a.distanceFromCenter - b.distanceFromCenter)[0];

  if (!target || target.marker.items.length <= 1 || target.distanceFromCenter < 12) return;

  autoCenteringRef.current = true;
  map.easeTo({
    center: [target.marker.lng, target.marker.lat],
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
