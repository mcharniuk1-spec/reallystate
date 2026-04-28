# Property Quality + Building Match Contract

Updated: 2026-04-28

## Purpose

This contract defines the checks every scraper, image-report, and QA agent must run before marking a property complete.

## Endpoint

Frontend/local Next endpoint:

```text
GET /api/property-quality/<encoded reference_id>
```

The endpoint reads `public/data/scraped-listings.json` and returns:

- parsed identity and source provenance,
- location/address fields,
- price, size, rooms, floor, and type facts,
- remote/local photo counts and full-gallery status,
- Gemma image-report status and report text paths/fields when present,
- conservative same-property source links,
- machine-readable checks for price/size plausibility, photo completeness, description fullness, image-report completion, and building-match readiness.

## Agent Rule

Any agent that scrapes, enriches, or validates a property must run equivalent checks:

1. **Photos:** remote count, local count, file existence/decodability, full-gallery flag, and partial-gallery reason.
2. **Image report:** one grouped apartment report plus ordered per-image descriptions for every local image.
3. **Description context:** combine scraped description and Gemma image report; reject thin/empty descriptions unless source has no text and gap is documented.
4. **Facts:** price, currency, area, rooms, floor, category, listing intent, city/district/region/address.
5. **Plausibility:** broad Bulgaria sanity ranges for price, area, and price per square meter.
6. **Source provenance:** preserve current listing URL and any conservative cross-source links.
7. **Building match:** do not claim building-level precision until address/geocode has been matched to an OSM/PostGIS building footprint.

## Building-Level Geospatial Requirement

The UI may show OSM map tiles and aggregated points now, but true building-object highlighting requires backend data:

- geocode listing address/city/district into a candidate coordinate,
- import OSM building footprints into PostGIS (`building_entity`),
- match property address/coordinate to one footprint with confidence and evidence,
- return building polygon/height/levels to the frontend,
- highlight that real footprint on the map.

Until this exists, agents must label the state as `building_match_required` or `building_match_pending`; they must not fabricate synthetic building boxes as verified real buildings.

## Completion Output

For every completed property, agents should be able to point to:

- listing JSON with all structured fields,
- local image files under `data/media/<reference_id>/`,
- image report Markdown and JSON,
- source-link evidence,
- property-quality check output,
- building match status and evidence when available.
