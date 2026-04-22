#!/usr/bin/env python3
"""Generate a tier-1/2 scraping status dashboard."""

from __future__ import annotations

import html
import json
import runpy
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO / "data" / "source_registry.json"
SCRAPED_ROOT = REPO / "data" / "scraped"
MEDIA_ROOT = REPO / "data" / "media"
EXPORTS = REPO / "docs" / "exports"
DASHBOARD_DIR = REPO / "docs" / "dashboard"

OUTPUT_HTML = DASHBOARD_DIR / "scrape-status.html"
OUTPUT_JSON = EXPORTS / "scrape-status-dashboard.json"
WEBSITE_INVENTORY_JSON = EXPORTS / "website-inventory-analysis.json"
PATTERN_STATUS_JSON = EXPORTS / "tier12-pattern-status.json"

COMBO_FIELDS = [
    ("price", "price"),
    ("area_sqm", "size"),
    ("rooms", "rooms"),
    ("floor", "floor"),
    ("city", "city"),
    ("district", "district"),
    ("address_text", "address"),
    ("geo", "geo"),
    ("phones", "phones"),
    ("amenities", "amenities"),
]

COMBO_ORDER = [
    ("sale", "apartment"),
    ("long_term_rent", "apartment"),
    ("sale", "house"),
    ("long_term_rent", "house"),
    ("sale", "land"),
    ("long_term_rent", "land"),
    ("sale", "office"),
    ("long_term_rent", "office"),
    ("sale", "unknown"),
    ("long_term_rent", "unknown"),
]

SERVICE_LABELS = {
    "sale": "Buy",
    "long_term_rent": "Rent",
    "short_term_rent": "Short-term rent",
}

PROPERTY_LABELS = {
    "apartment": "Apartment",
    "house": "House",
    "land": "Land",
    "office": "Commercial",
    "unknown": "Unclassified",
}

NEXT_STEP_OVERRIDES = {
    "alo.bg": "Run the stalled category-targeted continuation and confirm apartment sale/rent detail capture from `alo.bg/obiavi/...` pages.",
    "Domaza": "Map the language-canonical search entrypoints and recover the first working detail URL family before broad pagination.",
    "Home2U": "Repair the city landing pages into stable listing archives, then fetch detail pages product by product.",
    "Yavlena": "Recover detail-page descriptions for the already large on-disk corpus and keep sale buckets fresh.",
    "imot.bg": "Improve item classification and image download completeness; the volume is present but category precision is weak.",
    "Homes.bg": "Expand beyond the current apartment-heavy subset by widening the API scopes and continuing city pagination.",
}

STATE_OVERRIDES = {
    "alo.bg": "Configured, zero landed corpus",
    "Domaza": "Configured, zero landed corpus",
    "Home2U": "Configured, zero landed corpus",
    "Imoti.info": "Licensing required",
    "Imoteka.bg": "Legal review required",
    "imoti.net": "Legal review required",
}


def load_registry_rows() -> list[dict]:
    rows = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["sources"]
    return [row for row in rows if row.get("tier") in (1, 2)]


def load_source_configs() -> dict[str, dict]:
    configs = runpy.run_path(str(REPO / "scripts" / "live_scraper.py"))["SOURCE_CONFIGS"]
    return {cfg["name"]: {"source_key": key, **cfg} for key, cfg in configs.items()}


def load_inventory_analysis() -> dict[str, dict]:
    if not WEBSITE_INVENTORY_JSON.exists():
        return {}
    payload = json.loads(WEBSITE_INVENTORY_JSON.read_text(encoding="utf-8"))
    return {row["source_name"]: row for row in payload.get("sources", [])}


def load_pattern_status() -> dict[str, dict]:
    if not PATTERN_STATUS_JSON.exists():
        return {}
    payload = json.loads(PATTERN_STATUS_JSON.read_text(encoding="utf-8"))
    return {row["source_name"]: row for row in payload.get("sources", [])}


def _safe_ref(reference_id: str) -> str:
    return "".join("_" if c in '/:*?"<>|\\' else c for c in reference_id)


def build_source_stats() -> dict[str, dict]:
    stats: dict[str, dict] = defaultdict(
        lambda: {
            "saved_listings": 0,
            "with_description": 0,
            "with_photo_urls": 0,
            "with_readable_local_photos": 0,
            "fields": Counter(),
            "service_counts": Counter(),
            "category_counts": Counter(),
            "combo_rows": defaultdict(lambda: {"count": 0, "description": 0, "photo_urls": 0, "readable_photos": 0, "fields": Counter()}),
        }
    )

    for listing_path in SCRAPED_ROOT.glob("*/listings/*.json"):
        try:
            payload = json.loads(listing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        source_name = payload.get("source_name") or listing_path.parent.parent.name
        entry = stats[source_name]
        entry["saved_listings"] += 1

        intent = payload.get("listing_intent") or "unknown"
        category = payload.get("property_category") or "unknown"
        combo = entry["combo_rows"][(intent, category)]
        combo["count"] += 1

        if payload.get("description"):
            entry["with_description"] += 1
            combo["description"] += 1
            entry["fields"]["description"] += 1

        if payload.get("image_urls"):
            entry["with_photo_urls"] += 1
            combo["photo_urls"] += 1
            entry["fields"]["image_urls"] += 1

        reference_id = payload.get("reference_id") or ""
        media_dir = MEDIA_ROOT / _safe_ref(reference_id) if reference_id else None
        if media_dir and media_dir.exists() and any(media_dir.iterdir()):
            entry["with_readable_local_photos"] += 1
            combo["readable_photos"] += 1
            entry["fields"]["readable_photos"] += 1

        entry["service_counts"][intent] += 1
        entry["category_counts"][category] += 1

        if payload.get("price") is not None:
            entry["fields"]["price"] += 1
            combo["fields"]["price"] += 1
        if payload.get("area_sqm") is not None:
            entry["fields"]["area_sqm"] += 1
            combo["fields"]["area_sqm"] += 1
        if payload.get("rooms") is not None:
            entry["fields"]["rooms"] += 1
            combo["fields"]["rooms"] += 1
        if payload.get("floor") is not None:
            entry["fields"]["floor"] += 1
            combo["fields"]["floor"] += 1
        if payload.get("city"):
            entry["fields"]["city"] += 1
            combo["fields"]["city"] += 1
        if payload.get("district"):
            entry["fields"]["district"] += 1
            combo["fields"]["district"] += 1
        if payload.get("address_text"):
            entry["fields"]["address_text"] += 1
            combo["fields"]["address_text"] += 1
        if payload.get("latitude") is not None and payload.get("longitude") is not None:
            entry["fields"]["geo"] += 1
            combo["fields"]["geo"] += 1
        if payload.get("phones"):
            entry["fields"]["phones"] += 1
            combo["fields"]["phones"] += 1
        if payload.get("amenities"):
            entry["fields"]["amenities"] += 1
            combo["fields"]["amenities"] += 1

    return stats


def flatten_search_urls(cfg: dict) -> tuple[list[str], list[str]]:
    all_urls: list[str] = []
    apartment_urls: list[str] = []
    bucket_groups = cfg.get("buckets") or [{"label": "default", "search_urls": cfg.get("search_urls") or []}]
    for bucket in bucket_groups:
        urls = bucket.get("search_urls") or []
        all_urls.extend(urls)
        label = bucket.get("label", "").lower()
        if "apartment" in label or any("apart" in url.lower() for url in urls):
            apartment_urls.extend(urls)
    return all_urls, apartment_urls


def classify_state(row: dict, stats: dict) -> str:
    source_name = row["source_name"]
    if source_name in STATE_OVERRIDES:
        return STATE_OVERRIDES[source_name]
    if row.get("legal_mode") == "licensing_required":
        return "Licensing required"
    if row.get("legal_mode") == "legal_review_required":
        return "Legal review required"
    saved = stats.get("saved_listings", 0)
    if saved >= 100 and stats.get("with_description", 0) == 0:
        return "High-volume corpus, description gap"
    if saved >= 100:
        return "High-volume corpus on disk"
    if saved > 0:
        return "Partial corpus on disk"
    return "Planned / no landed corpus"


def next_step(row: dict, stats: dict, cfg: dict | None) -> str:
    source_name = row["source_name"]
    if source_name in NEXT_STEP_OVERRIDES:
        return NEXT_STEP_OVERRIDES[source_name]
    if row.get("legal_mode") == "licensing_required":
        return "Do not broaden crawling. Move this source through licensing or partner-feed negotiation first."
    if row.get("legal_mode") == "legal_review_required":
        return "Run a legal/access review before new live work, then choose headless tracing or partner route."
    if stats.get("saved_listings", 0) == 0 and cfg:
        return "Execute the configured discovery buckets again, validate the first working detail pages, then harvest item by item."
    if stats.get("saved_listings", 0) == 0:
        return "Map apartment/category entry pages first, capture fixtures, then build detail-page recovery."
    if stats.get("with_description", 0) < stats.get("saved_listings", 0):
        return "Close the text gap on detail pages before widening source coverage."
    if stats.get("with_readable_local_photos", 0) < stats.get("with_photo_urls", 0):
        return "Improve local media downloads and readability before the next large batch."
    return "Continue category-by-category refreshes and push the file-backed corpus into PostgreSQL for `S1-18` evidence."


def build_rows() -> tuple[list[dict], dict]:
    registry_rows = load_registry_rows()
    configs = load_source_configs()
    source_stats = build_source_stats()
    inventory_analysis = load_inventory_analysis()
    pattern_analysis = load_pattern_status()
    rows: list[dict] = []
    totals = {
        "tier_counts": Counter(),
        "saved_sources": 0,
        "saved_listings": 0,
        "with_description": 0,
        "with_photo_urls": 0,
        "with_readable_local_photos": 0,
        "with_website_totals": 0,
        "patterned_sources": 0,
    }

    for row in sorted(registry_rows, key=lambda item: (item["tier"], item["source_name"].lower())):
        source_name = row["source_name"]
        cfg = configs.get(source_name)
        stats = source_stats.get(source_name, {})
        discovery_links, apartment_links = flatten_search_urls(cfg) if cfg else ([], [])
        state = classify_state(row, stats)
        next_actions = next_step(row, stats, cfg)
        inventory = inventory_analysis.get(source_name, {})
        pattern = pattern_analysis.get(source_name, {})

        combo_rows: list[dict] = []
        raw_combos = stats.get("combo_rows") or {}
        ordered_seen = set()
        for combo_key in COMBO_ORDER:
            combo = raw_combos.get(combo_key)
            if combo and combo["count"]:
                ordered_seen.add(combo_key)
                combo_rows.append({"intent": combo_key[0], "category": combo_key[1], **combo})
        for combo_key, combo in sorted(raw_combos.items(), key=lambda item: (item[0][0], item[0][1])):
            if combo_key in ordered_seen or not combo["count"]:
                continue
            combo_rows.append({"intent": combo_key[0], "category": combo_key[1], **combo})

        source_entry = {
            "tier": row["tier"],
            "source_name": source_name,
            "primary_url": row.get("primary_url", ""),
            "related_urls": row.get("related_urls") or [],
            "access_mode": row.get("access_mode", ""),
            "risk_mode": row.get("risk_mode", ""),
            "legal_mode": row.get("legal_mode", ""),
            "listing_types": row.get("listing_types") or [],
            "best_extraction_method": row.get("best_extraction_method", ""),
            "notes": row.get("notes", ""),
            "saved_listings": stats.get("saved_listings", 0),
            "with_description": stats.get("with_description", 0),
            "with_photo_urls": stats.get("with_photo_urls", 0),
            "with_readable_local_photos": stats.get("with_readable_local_photos", 0),
            "service_counts": dict(stats.get("service_counts") or {}),
            "category_counts": dict(stats.get("category_counts") or {}),
            "field_counts": dict(stats.get("fields") or {}),
            "state": state,
            "next_step": next_actions,
            "discovery_links": discovery_links,
            "apartment_links": apartment_links,
            "combo_rows": combo_rows,
            "website_total": inventory.get("website_total") or {},
            "website_inventory_rows": inventory.get("inventory_rows") or [],
            "website_coverage_pct": inventory.get("coverage_pct"),
            "counting_method": inventory.get("counting_method", ""),
            "counting_gap": inventory.get("counting_gap", ""),
            "estimate_conflict": inventory.get("estimate_conflict", ""),
            "pattern_status": pattern.get("pattern_status", "without_pattern_status"),
            "pattern_issue": pattern.get("pattern_issue", "Pattern status not generated yet."),
            "count_status": pattern.get("count_status", "without_live_count_method"),
            "recent_status": pattern.get("recent_status", "without_recent_count_method"),
            "varna_status": pattern.get("varna_status", "without_varna_count_method"),
            "recent_under_2m": pattern.get("recent_under_2m") or {},
            "varna_split": pattern.get("varna_split") or {},
            "pattern_method": pattern.get("method", ""),
            "pattern_code_paths": pattern.get("code_paths") or [],
            "db_status": pattern.get("db_status", "without_database_target"),
            "db_notes": pattern.get("db_notes", ""),
            "sample": pattern.get("sample"),
        }
        rows.append(source_entry)
        totals["tier_counts"][row["tier"]] += 1
        if source_entry["saved_listings"]:
            totals["saved_sources"] += 1
        if source_entry["website_total"].get("value") is not None:
            totals["with_website_totals"] += 1
        totals["saved_listings"] += source_entry["saved_listings"]
        totals["with_description"] += source_entry["with_description"]
        totals["with_photo_urls"] += source_entry["with_photo_urls"]
        totals["with_readable_local_photos"] += source_entry["with_readable_local_photos"]
        if source_entry["pattern_status"] == "Patterned":
            totals["patterned_sources"] += 1

    return rows, totals


def percent(part: int, whole: int) -> str:
    if whole <= 0:
        return "0%"
    return f"{(part / whole) * 100:.0f}%"


def esc(value: object) -> str:
    return html.escape(str(value))


def link_list(urls: list[str]) -> str:
    if not urls:
        return '<span class="muted">Not mapped yet</span>'
    return "".join(f'<a href="{esc(url)}" target="_blank" rel="noreferrer">{esc(url)}</a>' for url in urls)


def website_total_text(row: dict) -> str:
    total = row["website_total"]
    if total.get("value") is None:
        return "Not saved yet"
    kind = total.get("kind", "unavailable").replace("_", " ")
    return f"{total['value']} ({kind})"


def inventory_table(items: list[dict]) -> str:
    if not items:
        return '<div class="empty">No website-side category counts are saved yet for this source.</div>'
    body: list[str] = []
    for item in items:
        url = item.get("url") or ""
        url_html = (
            f'<a href="{esc(url)}" target="_blank" rel="noreferrer">{esc(url)}</a>'
            if url else '<span class="muted">No URL saved</span>'
        )
        body.append(
            "<tr>"
            f"<td>{esc(SERVICE_LABELS.get(item['service'], item['service']))}</td>"
            f"<td>{esc(PROPERTY_LABELS.get(item['property'], item['property']))}</td>"
            f"<td>{item['count'] if item.get('count') is not None else 'n/a'}</td>"
            f"<td>{esc(item.get('kind', '').replace('_', ' ').title())}</td>"
            f"<td>{esc(item.get('basis', ''))}</td>"
            f"<td>{url_html}</td>"
            f"<td>{esc(item.get('notes', ''))}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        "<thead><tr>"
        "<th>Service</th><th>Property</th><th>Website count</th><th>Count kind</th><th>Basis</th><th>Evidence URL</th><th>Notes</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def combo_table(rows: list[dict]) -> str:
    if not rows:
        return '<div class="empty">No landed corpus yet for this source.</div>'
    body: list[str] = []
    for row in rows:
        fields = row["fields"]
        attr_bits = [f"{label} {fields.get(key, 0)}/{row['count']}" for key, label in COMBO_FIELDS if fields.get(key, 0)]
        attr_text = ", ".join(attr_bits) if attr_bits else "No secondary fields captured yet"
        body.append(
            "<tr>"
            f"<td>{esc(SERVICE_LABELS.get(row['intent'], row['intent']))}</td>"
            f"<td>{esc(PROPERTY_LABELS.get(row['category'], row['category']))}</td>"
            f"<td>{row['count']}</td>"
            f"<td>{row['description']}</td>"
            f"<td>{row['photo_urls']}</td>"
            f"<td>{row['readable_photos']}</td>"
            f"<td>{fields.get('price', 0)}</td>"
            f"<td>{fields.get('area_sqm', 0)}</td>"
            f"<td>{fields.get('rooms', 0)}</td>"
            f"<td>{fields.get('floor', 0)}</td>"
            f"<td>{fields.get('city', 0)}</td>"
            f"<td>{fields.get('district', 0)}</td>"
            f"<td>{fields.get('address_text', 0)}</td>"
            f"<td>{fields.get('geo', 0)}</td>"
            f"<td>{fields.get('phones', 0)}</td>"
            f"<td>{fields.get('amenities', 0)}</td>"
            f"<td>{esc(attr_text)}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        "<thead><tr>"
        "<th>Service</th><th>Property</th><th>Listings</th><th>Description</th><th>Photo URLs</th><th>Readable photos</th>"
        "<th>Price</th><th>Size</th><th>Rooms</th><th>Floor</th><th>City</th><th>District</th><th>Address</th><th>Geo</th><th>Phones</th><th>Amenities</th><th>Attributes captured</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def summary_table(rows: list[dict]) -> str:
    body: list[str] = []
    for row in rows:
        website_value = row["website_total"].get("value")
        coverage = percent(row["saved_listings"], website_value) if website_value else "n/a"
        body.append(
            "<tr>"
            f"<td>{row['tier']}</td>"
            f"<td>{esc(row['source_name'])}</td>"
            f'<td><a href="{esc(row["primary_url"])}" target="_blank" rel="noreferrer">{esc(row["primary_url"])}</a></td>'
            f"<td>{esc(row['state'])}</td>"
            f"<td>{esc(row['pattern_status'])}</td>"
            f"<td>{esc(row['count_status'])}</td>"
            f"<td>{esc(row['recent_status'])}</td>"
            f"<td>{esc(row['varna_status'])}</td>"
            f"<td>{row['saved_listings']}</td>"
            f"<td>{row['with_description']}</td>"
            f"<td>{row['with_photo_urls']}</td>"
            f"<td>{row['with_readable_local_photos']}</td>"
            f"<td>{esc(website_total_text(row))}</td>"
            f"<td>{esc(str(row['recent_under_2m'].get('value', 'n/a')))}</td>"
            f"<td>{esc(row['varna_split'].get('text', 'n/a+n/a'))}</td>"
            f"<td>{esc(coverage)}</td>"
            f"<td>{esc(', '.join(row['listing_types']) or '-')}</td>"
            f"<td>{esc(row['access_mode'])}</td>"
            f"<td>{esc(row['legal_mode'])}</td>"
            f"<td>{esc(row['next_step'])}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        "<thead><tr>"
        "<th>Tier</th><th>Source</th><th>Primary link</th><th>State</th><th>Pattern</th><th>Count</th><th>Recent</th><th>Varna</th><th>Saved listings</th><th>Descriptions</th><th>Photo URLs</th><th>Readable photos</th><th>Website total</th><th>&lt;2m</th><th>Varna city+region</th><th>Coverage vs website</th><th>Declared scope</th><th>Access</th><th>Legal</th><th>Further steps</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def source_cards(rows: list[dict]) -> str:
    cards: list[str] = []
    for row in rows:
        service_counts = ", ".join(f"{SERVICE_LABELS.get(k, k)}={v}" for k, v in sorted(row["service_counts"].items())) or "No landed rows"
        category_counts = ", ".join(f"{PROPERTY_LABELS.get(k, k)}={v}" for k, v in sorted(row["category_counts"].items())) or "No landed rows"
        field_counts = row["field_counts"]
        field_summary = ", ".join(
            f"{label} {field_counts.get(key, 0)}/{row['saved_listings'] or 0}"
            for key, label in COMBO_FIELDS
            if key in field_counts
        ) or "No secondary fields captured yet"
        sample = row.get("sample") or {}
        sample_summary = (
            f"{sample.get('local_photo_count', 0)}/{sample.get('remote_photo_count', 0)} photos · {sample.get('listing_path', 'n/a')}"
            if sample else "No saved sample item yet"
        )
        website_value = row["website_total"].get("value")
        coverage = percent(row["saved_listings"], website_value) if website_value else "n/a"
        estimate_note = (
            f"<p><strong>Estimate conflict:</strong> {esc(row['estimate_conflict'])}</p>"
            if row.get("estimate_conflict") else ""
        )
        cards.append(
            '<section class="source-card">'
            f'<div class="source-head"><div><h2>{esc(row["source_name"])}</h2><div class="meta">Tier {row["tier"]} · {esc(row["state"])} · {esc(row["pattern_status"])}</div></div>'
            f'<div class="badge">{esc(row["access_mode"])}</div></div>'
            '<div class="stats-grid">'
            f'<div class="stat"><span>Saved listings</span><strong>{row["saved_listings"]}</strong></div>'
            f'<div class="stat"><span>Website total</span><strong>{esc(website_total_text(row))}</strong></div>'
            f'<div class="stat"><span>Pattern status</span><strong>{esc(row["pattern_status"])}</strong></div>'
            f'<div class="stat"><span>Live count status</span><strong>{esc(row["count_status"])}</strong></div>'
            f'<div class="stat"><span>Recent &lt;2m status</span><strong>{esc(row["recent_status"])}</strong></div>'
            f'<div class="stat"><span>Varna status</span><strong>{esc(row["varna_status"])}</strong></div>'
            f'<div class="stat"><span>Coverage vs website</span><strong>{esc(coverage)}</strong></div>'
            f'<div class="stat"><span>Description coverage</span><strong>{percent(row["with_description"], row["saved_listings"])}</strong></div>'
            f'<div class="stat"><span>Photo URL coverage</span><strong>{percent(row["with_photo_urls"], row["saved_listings"])}</strong></div>'
            f'<div class="stat"><span>Readable photo coverage</span><strong>{percent(row["with_readable_local_photos"], row["saved_listings"])}</strong></div>'
            "</div>"
            '<div class="details-grid">'
            f'<div><h3>Links</h3><div class="stack"><a href="{esc(row["primary_url"])}" target="_blank" rel="noreferrer">{esc(row["primary_url"])}</a>{link_list(row["related_urls"])}</div></div>'
            f"<div><h3>Apartment entrypoints</h3><div class='stack'>{link_list(row['apartment_links'])}</div></div>"
            f"<div><h3>Discovery entrypoints</h3><div class='stack'>{link_list(row['discovery_links'])}</div></div>"
            f"<div><h3>Scope</h3><p>{esc(', '.join(row['listing_types']) or '-')}</p><p class='muted'>{esc(row['best_extraction_method'])}</p></div>"
            "</div>"
            f"<p><strong>Pattern issue:</strong> {esc(row['pattern_issue'])}</p>"
            f"<p><strong>Pattern method:</strong> {esc(row['pattern_method'] or 'Not documented yet')}</p>"
            f"<p><strong>Pattern code paths:</strong> {esc(', '.join(row['pattern_code_paths']) or 'Not mapped yet')}</p>"
            f"<p><strong>Website total basis:</strong> {esc(row['website_total'].get('basis', 'not saved'))}</p>"
            f"<p><strong>Website total notes:</strong> {esc(row['website_total'].get('notes', 'No website-side total is saved yet.'))}</p>"
            f"<p><strong>Counting method:</strong> {esc(row['counting_method'] or 'Not documented yet')}</p>"
            f"<p><strong>Counting gap:</strong> {esc(row['counting_gap'] or 'No gap note saved yet')}</p>"
            f"<p><strong>Posted &lt;2 months:</strong> {esc(str(row['recent_under_2m'].get('value', 'n/a')))} ({esc(row['recent_status'])})</p>"
            f"<p><strong>Varna city+region:</strong> {esc(row['varna_split'].get('text', 'n/a+n/a'))} ({esc(row['varna_status'])})</p>"
            f"<p><strong>DB status:</strong> {esc(row['db_status'])} — {esc(row['db_notes'])}</p>"
            f"<p><strong>Best saved sample:</strong> {esc(sample_summary)}</p>"
            + estimate_note
            + f"<p><strong>Services scraped:</strong> {esc(service_counts)}</p>"
            f"<p><strong>Property categories scraped:</strong> {esc(category_counts)}</p>"
            f"<p><strong>Other captured variables:</strong> {esc(field_summary)}</p>"
            f"<p><strong>Next step:</strong> {esc(row['next_step'])}</p>"
            '<h3>Website Inventory Evidence</h3>'
            + inventory_table(row["website_inventory_rows"])
            + '<h3>Landed Corpus Matrix</h3>'
            + combo_table(row["combo_rows"])
            + "</section>"
        )
    return "".join(cards)


def render_html(rows: list[dict], totals: dict) -> str:
    generated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tier_counts = totals["tier_counts"]
    desc_rate = percent(totals["with_description"], totals["saved_listings"])
    photo_rate = percent(totals["with_photo_urls"], totals["saved_listings"])
    readable_rate = percent(totals["with_readable_local_photos"], totals["with_photo_urls"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>BGEstate Scrape Status Dashboard</title>
  <style>
    :root {{
      --bg: #f4efe6;
      --panel: #fffdf8;
      --ink: #1e293b;
      --muted: #5b6472;
      --line: #d8cfbf;
      --accent: #bf6b28;
      --accent-dark: #8f4d18;
      --sea: #175b72;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
      background:
        radial-gradient(circle at top left, rgba(191,107,40,.08), transparent 30%),
        linear-gradient(180deg, #f8f2e7 0%, var(--bg) 100%);
      color: var(--ink);
    }}
    a {{ color: var(--sea); text-decoration: none; display: block; }}
    a:hover {{ text-decoration: underline; }}
    .hero {{
      padding: 30px 24px 18px;
      border-bottom: 1px solid rgba(30,41,59,.08);
      background: linear-gradient(135deg, rgba(191,107,40,.10), rgba(23,91,114,.10));
    }}
    .hero h1 {{ margin: 0 0 8px; font-size: 34px; line-height: 1.08; }}
    .hero p {{ max-width: 980px; margin: 0; color: var(--muted); font-size: 15px; }}
    .meta-line {{ margin-top: 12px; font-size: 12px; color: var(--muted); }}
    .wrap {{ max-width: 1500px; margin: 0 auto; padding: 22px; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .kpi, .panel, .source-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 8px 24px rgba(30,41,59,.05);
    }}
    .kpi {{ padding: 16px; }}
    .kpi span {{ display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }}
    .kpi strong {{ display: block; font-size: 28px; margin-top: 6px; }}
    .panel {{ padding: 18px; margin-bottom: 18px; }}
    .panel h2 {{ margin: 0 0 12px; font-size: 22px; }}
    .panel p {{ color: var(--muted); }}
    .table-wrap {{ overflow: auto; border: 1px solid rgba(30,41,59,.08); border-radius: 12px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 1080px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 13px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid rgba(30,41,59,.08); vertical-align: top; text-align: left; }}
    th {{ position: sticky; top: 0; background: #fbf7ef; font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
    tr:nth-child(even) td {{ background: rgba(23,91,114,.02); }}
    .source-card {{ padding: 18px; margin-bottom: 18px; }}
    .source-head {{
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .source-head h2 {{ margin: 0; font-size: 24px; }}
    .meta {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
    .badge {{
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(191,107,40,.12);
      color: var(--accent-dark);
      font: 700 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: .06em;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }}
    .stat {{
      border: 1px solid rgba(30,41,59,.08);
      border-radius: 12px;
      padding: 12px;
      background: rgba(255,255,255,.72);
    }}
    .stat span {{ display: block; color: var(--muted); font-size: 12px; }}
    .stat strong {{ display: block; margin-top: 6px; font: 700 24px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .details-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin-bottom: 12px;
    }}
    .details-grid h3 {{ margin: 0 0 6px; font-size: 14px; }}
    .stack {{ display: grid; gap: 4px; }}
    .muted {{ color: var(--muted); font-size: 12px; }}
    .empty {{
      padding: 14px;
      border: 1px dashed rgba(30,41,59,.18);
      border-radius: 12px;
      color: var(--muted);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    @media (max-width: 900px) {{
      .hero h1 {{ font-size: 28px; }}
      .wrap {{ padding: 14px; }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <h1>Tier 1-2 Scraping Status Dashboard</h1>
    <p>This dashboard tracks both sides of scraper progress: the landed corpus already saved on disk and the website-side inventory counts we have confirmed or estimated by category. Each source block now shows what the website appears to offer, how much has actually been landed, how strong the counting evidence is, and the next operational step.</p>
    <div class="meta-line">Generated: {esc(generated_at)} · Sources with landed corpus: {totals["saved_sources"]}/{tier_counts[1] + tier_counts[2]}</div>
  </header>
  <main class="wrap">
    <section class="kpis">
      <div class="kpi"><span>Tier 1 sources</span><strong>{tier_counts[1]}</strong></div>
      <div class="kpi"><span>Tier 2 sources</span><strong>{tier_counts[2]}</strong></div>
      <div class="kpi"><span>Sources with website totals</span><strong>{totals["with_website_totals"]}</strong></div>
      <div class="kpi"><span>Patterned sources</span><strong>{totals["patterned_sources"]}</strong></div>
      <div class="kpi"><span>Saved listings on disk</span><strong>{totals["saved_listings"]}</strong></div>
      <div class="kpi"><span>Description coverage</span><strong>{esc(desc_rate)}</strong></div>
      <div class="kpi"><span>Photo URL coverage</span><strong>{esc(photo_rate)}</strong></div>
      <div class="kpi"><span>Readable photo rate</span><strong>{esc(readable_rate)}</strong></div>
    </section>
    <section class="panel">
      <h2>All tier links, current state, and further steps</h2>
      <p>This is the top-level tracker for every tier 1-2 source from the registry. The state column reflects the current on-disk corpus, legal gate, and operational readiness.</p>
      {summary_table(rows)}
    </section>
    <section class="panel">
      <h2>Current progress logic</h2>
      <p><strong>High-volume corpus on disk</strong> means the source already has substantial saved listing JSONs and can feed the <code>S1-18</code> volume gate once PostgreSQL import is verified. <strong>Partial corpus</strong> means the parser works but the source still needs broader category/page coverage. <strong>Configured, zero landed corpus</strong> means the repo already knows likely listing entrypoints, but the next live pass has not landed stable item pages yet.</p>
    </section>
    {source_cards(rows)}
  </main>
</body>
</html>
"""


def write_outputs(rows: list[dict], totals: dict) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sources": rows,
        "totals": {
            "tier_counts": dict(totals["tier_counts"]),
            "saved_sources": totals["saved_sources"],
            "with_website_totals": totals["with_website_totals"],
            "patterned_sources": totals["patterned_sources"],
            "saved_listings": totals["saved_listings"],
            "with_description": totals["with_description"],
            "with_photo_urls": totals["with_photo_urls"],
            "with_readable_local_photos": totals["with_readable_local_photos"],
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_HTML.write_text(render_html(rows, totals), encoding="utf-8")


def main() -> int:
    rows, totals = build_rows()
    write_outputs(rows, totals)
    print(f"Wrote {OUTPUT_HTML}")
    print(f"Wrote {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
