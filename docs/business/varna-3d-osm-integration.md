# Varna 3D OSM Building Integration Plan

## 1. Goal

Render a 3D interactive map of Varna city showing building footprints extruded to real height, with property listing pins overlaid on buildings. This is the visual centerpiece of the MVP map experience.

## 2. Technology Decision

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **MapLibre GL JS + 3D extrusion** | Open-source, free, self-hosted, fast, great ecosystem | Requires own tile pipeline | **PRIMARY — use this** |
| deck.gl BuildingLayer | Advanced 3D, good for data-heavy overlays | Heavier bundle, more complex | Use alongside MapLibre for overlay layers |
| CesiumJS + Cesium OSM Buildings | Highest fidelity 3D, global coverage | Requires Cesium ion account (free tier available) | **FALLBACK** for marketing renders |
| Blosm (Blender addon) | Beautiful offline 3D renders | Not for runtime web; Blender dependency | Use for **static marketing images only** |
| OSM Buildings JS library | Purpose-built for OSM | Smaller community, some bugs reported | Skip — MapLibre handles this natively |

## 3. Data Pipeline

### 3.1 OSM Data Acquisition

```
Step 1: Download Bulgaria OSM extract
  Source: https://download.geofabrik.de/europe/bulgaria-latest.osm.pbf
  Size: ~100 MB

Step 2: Clip to Varna bounding box
  Bbox: 43.17°N – 43.25°N, 27.85°E – 27.98°E
  Tool: osmium extract --bbox 27.85,43.17,27.98,43.25 bulgaria-latest.osm.pbf -o varna.osm.pbf

Step 3: Extract buildings
  Tool: osmium tags-filter varna.osm.pbf w/building -o varna-buildings.osm.pbf

Step 4: Convert to GeoJSON
  Tool: ogr2ogr -f GeoJSON varna-buildings.geojson varna-buildings.osm.pbf multipolygons

Step 5: Generate vector tiles
  Tool: tippecanoe -o varna-buildings.mbtiles -z 18 -Z 10 --drop-densest-as-needed varna-buildings.geojson
  OR: Convert to PMTiles for static hosting (no tile server needed)
  Tool: pmtiles convert varna-buildings.mbtiles varna-buildings.pmtiles
```

### 3.2 Building Height Data

OSM buildings in Varna have varying quality of height data:

| Tag | Coverage | Fallback |
|---|---|---|
| `height` | ~15–25% of buildings | Use `building:levels × 3.0m` |
| `building:levels` | ~30–40% of buildings | Default to 3 levels (9m) for residential |
| Neither | ~40–50% of buildings | Estimate from building type: `apartments`=15m, `house`=6m, `commercial`=12m |

The pipeline should apply these fallbacks during GeoJSON generation.

### 3.3 Script: `scripts/import_osm_buildings_varna.py`

```python
# Pseudo-code for the backend_developer to implement
def pipeline():
    download_geofabrik_extract("bulgaria")
    clip_to_varna_bbox()
    extract_buildings()
    enrich_heights()  # Apply fallback heights
    convert_to_geojson()
    generate_vector_tiles()  # MBTiles or PMTiles
    optionally_import_to_postgis()  # For backend queries
```

### 3.4 PostGIS Storage

Buildings should also be imported into PostGIS `building_entity` table for:
- Spatial queries (which buildings are in viewport)
- Joining listings to buildings (nearest building match)
- Analytics (building density, height distribution)

```sql
-- Already defined in sql/schema.sql
-- building_entity table should receive:
--   osm_id, geometry (POLYGON), height, levels, building_type, name, address
```

## 4. Frontend Integration

### 4.1 MapLibre GL JS 3D Building Layer

```javascript
// Core implementation reference for ux_ui_designer
map.addSource('varna-buildings', {
  type: 'vector',
  url: 'pmtiles:///data/tiles/varna-buildings.pmtiles'
});

map.addLayer({
  id: 'varna-3d-buildings',
  type: 'fill-extrusion',
  source: 'varna-buildings',
  'source-layer': 'buildings',
  paint: {
    'fill-extrusion-color': [
      'interpolate', ['linear'], ['get', 'height'],
      0, '#d4e6f1',
      10, '#85c1e9',
      20, '#3498db',
      40, '#2874a6'
    ],
    'fill-extrusion-height': ['get', 'height'],
    'fill-extrusion-base': 0,
    'fill-extrusion-opacity': 0.7
  }
});
```

### 4.2 Property Pin Layer (on top of buildings)

```javascript
map.addLayer({
  id: 'property-pins',
  type: 'circle',
  source: 'listings-geojson',
  paint: {
    'circle-radius': 6,
    'circle-color': '#e94560',
    'circle-stroke-width': 2,
    'circle-stroke-color': '#fff'
  }
});
```

### 4.3 Interaction: Building Click → Property Summary

When user clicks a 3D building:
1. Query PostGIS for listings matched to that building
2. Show building summary drawer with:
   - Building address
   - Number of listings in this building
   - Price range
   - Listing cards

### 4.4 Tile Serving Options

| Option | Complexity | Cost | Recommendation |
|---|---|---|---|
| PMTiles (static file) | Very low | Free (static hosting) | **Use for MVP** |
| MBTiles + Martin server | Low | Self-hosted | Use when needing dynamic queries |
| Mapbox/MapTiler hosted | Zero setup | Paid ($50–200/mo) | Skip — self-host is fine |

## 5. Blosm Usage (Marketing Only)

[Blosm](https://github.com/vvoovv/blosm) addon for Blender:

**Use case:** Generate beautiful 3D renders of Varna for:
- Landing page hero images
- Social media marketing material
- Investor presentation visuals

**Workflow:**
1. Install Blosm in Blender
2. Import Varna area (coordinates: 43.21°N, 27.91°E)
3. Import buildings + terrain + streets
4. Apply materials and lighting
5. Render high-res images
6. Export to landing page / presentation

**Not for:** Runtime web rendering (too heavy, requires Blender)

## 6. MVP Scope Constraints

- **Geography:** Varna city proper only (bbox: 43.17–43.25°N, 27.85–27.98°E)
- **Buildings:** ~15,000–25,000 estimated building footprints from OSM
- **Tile size:** ~5–15 MB for Varna-only PMTiles (very manageable)
- **Expansion gate:** Requires DBG-05 (stage-1 scraping verification) before adding Burgas/resorts
- **Fallback:** Where 3D data is poor, automatically show 2D footprints (flat polygons)

## 7. Dependencies

| Component | Owner | Status |
|---|---|---|
| OSM data download + processing | backend_developer | New task (BD-08) |
| PostGIS building_entity table | backend_developer | Schema exists |
| MapLibre 3D layer | ux_ui_designer | Part of UX-04 |
| PMTiles serving | backend_developer | New task |
| Building-to-listing matching | backend_developer | Part of BD-06 |
| Blosm marketing renders | ux_ui_designer (optional) | Deferred |
