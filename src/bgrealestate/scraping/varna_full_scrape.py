"""Manifest-driven Varna scraper runner and nationwide full scraper.

This runner is intentionally pattern-led:

- reads `data/scrape_patterns/regions/varna/sections.json`
- executes only source/segment buckets with reusable saved patterns by default
- enforces Varna acceptance at parse/save time
- can also run all-Bulgaria scraping directly from `scripts/live_scraper.py`
- requires full local gallery capture for threshold counting
- can run source groups in parallel while keeping section order stable per source
"""

from __future__ import annotations

import json
import re
import runpy
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST_PATH = REPO / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
DEFAULT_OUTPUT_PATH = REPO / "docs" / "exports" / "varna-full-scrape-summary.json"
DEFAULT_ALL_OUTPUT_PATH = REPO / "docs" / "exports" / "all-full-scrape-summary.json"
SCRAPED_ROOT = REPO / "data" / "scraped"
PATTERN_STATUS_PATH = REPO / "docs" / "exports" / "tier12-pattern-status.json"
DASHBOARD_REFRESH_SCRIPTS: tuple[str, ...] = (
    "generate_source_item_photo_coverage.py",
    "generate_tier12_pattern_status.py",
    "generate_scrape_status_dashboard.py",
)

_LIVE = runpy.run_path(str(REPO / "scripts" / "live_scraper.py"))
SOURCE_CONFIGS: dict[str, dict[str, Any]] = _LIVE["SOURCE_CONFIGS"]
scrape_source: Callable[..., Any] = _LIVE["scrape_source"]

NEGATIVE_CITY_TOKENS = [
    "софия",
    "пловдив",
    "бургас",
    "русе",
    "стара загора",
    "велико търново",
    "sofia",
    "plovdiv",
    "burgas",
    "ruse",
    "stara zagora",
]


@dataclass(frozen=True)
class VarnaSection:
    section_id: str
    source_name: str
    source_key: str
    segment_key: str
    vertical_key: str
    entry_urls: tuple[str, ...]
    page_suffix: str
    discovery_templates: dict[str, Any]
    pattern_status: str
    support_status: str
    activation_ready: bool
    region_key: str
    entry_scope: str
    section_label: str
    varna_filter: dict[str, Any]


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _build_sections(manifest: dict[str, Any], *, patterned_only: bool = True) -> list[VarnaSection]:
    sections: list[VarnaSection] = []
    for raw in manifest.get("sections", []):
        patterns = raw.get("patterns") or {}
        source_spec = patterns.get("source") or {}
        section_spec = patterns.get("section") or {}
        list_spec = patterns.get("list_page") or {}
        source_key = source_spec.get("source_key")
        if not source_key or source_key not in SOURCE_CONFIGS:
            continue
        pattern_status = str(source_spec.get("pattern_status") or "Unknown")
        support_status = str(section_spec.get("support_status") or source_spec.get("support_status") or "pattern_incomplete")
        activation_ready = bool(source_spec.get("activation_ready"))
        if patterned_only and (pattern_status != "Patterned" or support_status != "supported"):
            continue
        sections.append(
            VarnaSection(
                section_id=str(raw["section_id"]),
                source_name=str(raw["source_name"]),
                source_key=str(source_key),
                segment_key=str(raw["segment_key"]),
                vertical_key=str(raw.get("vertical_key") or "all"),
                entry_urls=tuple(raw.get("entry_urls") or list_spec.get("entry_urls") or []),
                page_suffix=str(list_spec.get("page_suffix") or SOURCE_CONFIGS[source_key].get("page_suffix") or "?page={}"),
                discovery_templates=dict(list_spec.get("discovery_templates") or {}),
                pattern_status=pattern_status,
                support_status=support_status,
                activation_ready=activation_ready,
                region_key=str(raw.get("region_key") or "varna"),
                entry_scope=str(section_spec.get("entry_scope") or list_spec.get("entry_scope") or ""),
                section_label=str(raw.get("section_label") or raw["section_id"]),
                varna_filter=dict(patterns.get("varna_enforcement") or {}),
            )
        )
    return sections


def _segment_expected_intent(segment_key: str) -> str:
    return "long_term_rent" if segment_key.startswith("rent_") else "sale"


def _haystack_from_parsed(parsed: dict[str, Any], html: str = "") -> str:
    bits = [
        parsed.get("title") or "",
        parsed.get("description") or "",
        parsed.get("city") or "",
        parsed.get("district") or "",
        parsed.get("address_text") or "",
        parsed.get("listing_url") or "",
        html[:4000],
    ]
    return normalize_text(" ".join(str(bit) for bit in bits if bit))


def _contains_varna_signal(haystack: str, varna_filter: dict[str, Any]) -> bool:
    positives = [
        *varna_filter.get("city_tokens_bg", []),
        *varna_filter.get("city_tokens_lat", []),
        *varna_filter.get("region_tokens_bg", []),
        *varna_filter.get("region_tokens_lat", []),
    ]
    return any(normalize_text(token) in haystack for token in positives if token)


def _contains_explicit_non_varna(haystack: str) -> bool:
    return any(token in haystack for token in NEGATIVE_CITY_TOKENS)


def is_varna_listing(parsed: dict[str, Any], html: str, section: VarnaSection) -> bool:
    city = normalize_text(str(parsed.get("city") or ""))
    address = normalize_text(str(parsed.get("address_text") or ""))
    if city:
        if "varna" in city or "варна" in city:
            return True
        return False
    if address and ("varna" in address or "варна" in address):
        return True

    haystack = _haystack_from_parsed(parsed, html)
    if _contains_explicit_non_varna(haystack) and not _contains_varna_signal(haystack, section.varna_filter):
        return False
    if _contains_varna_signal(haystack, section.varna_filter):
        return True
    if "varna_only" in section.entry_scope and not _contains_explicit_non_varna(haystack):
        return True
    if any("varna" in normalize_text(url) or "варна" in normalize_text(url) for url in section.entry_urls) and not _contains_explicit_non_varna(haystack):
        return True
    return False


def is_section_item_complete(obj: dict[str, Any], section: VarnaSection, *, require_full_gallery: bool = True) -> bool:
    if (obj.get("source_section_id") or "") not in {"", section.section_id} and obj.get("source_section_id") != section.section_id:
        return False
    if obj.get("source_name") != section.source_name:
        return False
    if obj.get("segment_key") and obj.get("segment_key") != section.segment_key:
        return False
    intent = obj.get("listing_intent") or ""
    if intent and intent != _segment_expected_intent(section.segment_key):
        return False
    region = obj.get("region_key") or ""
    if region and region != "varna":
        return False
    if require_full_gallery and not bool(obj.get("full_gallery_downloaded")):
        return False
    if not obj.get("description"):
        return False
    if obj.get("price") is None:
        return False
    if not (obj.get("city") or obj.get("address_text")):
        return False
    return True


def count_saved_section_items(section: VarnaSection, *, require_full_gallery: bool = True) -> int:
    listing_dir = SCRAPED_ROOT / section.source_key / "listings"
    if not listing_dir.exists():
        return 0
    count = 0
    for listing_path in listing_dir.glob("*.json"):
        try:
            obj = json.loads(listing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if is_section_item_complete(obj, section, require_full_gallery=require_full_gallery):
            count += 1
    return count


def is_source_item_complete(obj: dict[str, Any], *, require_full_gallery: bool = True) -> bool:
    if require_full_gallery and not bool(obj.get("full_gallery_downloaded")):
        return False
    if not obj.get("description"):
        return False
    if obj.get("price") is None:
        return False
    if not (obj.get("city") or obj.get("address_text")):
        return False
    return True


def count_saved_source_items(source_key: str, *, require_full_gallery: bool = True) -> int:
    listing_dir = SCRAPED_ROOT / source_key / "listings"
    if not listing_dir.exists():
        return 0
    count = 0
    for listing_path in listing_dir.glob("*.json"):
        try:
            obj = json.loads(listing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if is_source_item_complete(obj, require_full_gallery=require_full_gallery):
            count += 1
    return count


def patterned_source_keys(*, patterned_only: bool = True) -> list[str]:
    if not patterned_only or not PATTERN_STATUS_PATH.exists():
        return sorted(SOURCE_CONFIGS)
    payload = json.loads(PATTERN_STATUS_PATH.read_text(encoding="utf-8"))
    patterned_names = {
        row.get("source_name")
        for row in payload.get("sources", [])
        if row.get("pattern_status") == "Patterned"
    }
    keys = [
        key
        for key, cfg in SOURCE_CONFIGS.items()
        if cfg.get("name") in patterned_names
    ]
    return sorted(keys)


def build_config_override(section: VarnaSection) -> dict[str, Any]:
    base = SOURCE_CONFIGS[section.source_key]
    if section.source_key == "homes_bg":
        api_templates = []
        for template in section.discovery_templates.get("api_templates") or []:
            api_templates.append((section.section_id, template))
        return {
            "name": section.source_name,
            "func": "_scrape_homes_bg",
            "api_templates": api_templates,
        }
    if section.source_key == "imot_bg":
        return {
            "name": section.source_name,
            "func": "_scrape_imot_bg",
            "search_routes": [(section.section_id, url) for url in section.entry_urls],
        }
    return {
        "name": section.source_name,
        "func": "generic",
        "base_url": base["base_url"],
        "listing_pattern": base["listing_pattern"],
        "page_suffix": section.page_suffix or base.get("page_suffix", "?page={}"),
        "search_urls": list(section.entry_urls),
        "buckets": [
            {
                "label": section.section_id,
                "search_urls": list(section.entry_urls),
                "page_suffix": section.page_suffix or base.get("page_suffix", "?page={}"),
            }
        ],
    }


def make_accept_predicate(section: VarnaSection) -> Callable[[dict[str, Any], str, str, str], bool]:
    expected_intent = _segment_expected_intent(section.segment_key)

    def _accept(parsed: dict[str, Any], url: str, html: str, bucket_label: str) -> bool:
        if parsed.get("listing_intent") and parsed["listing_intent"] != expected_intent:
            return False
        return is_varna_listing(parsed, html, section)

    return _accept


def make_save_context_builder(section: VarnaSection) -> Callable[[dict[str, Any], str, str, str], dict[str, Any]]:
    def _build(parsed: dict[str, Any], url: str, html: str, bucket_label: str) -> dict[str, Any]:
        return {
            "source_section_id": section.section_id,
            "region_key": section.region_key,
            "segment_key": section.segment_key,
            "vertical_key": section.vertical_key,
            "section_label": section.section_label,
            "pattern_bucket_label": bucket_label,
            "varna_entry_scope": section.entry_scope,
        }

    return _build


def _listings_goal(current_count: int, target_per_section: int) -> int:
    remaining = max(0, target_per_section - current_count)
    if remaining <= 0:
        return 0
    return max(remaining * 3, remaining + 25)


def run_section_scrape(
    section: VarnaSection,
    *,
    max_pages: int,
    target_per_section: int,
    download_photos: bool,
    require_full_gallery: bool,
    dry_run: bool,
    max_waves: int = 3,
) -> dict[str, Any]:
    before = count_saved_section_items(section, require_full_gallery=require_full_gallery)
    result: dict[str, Any] = {
        "section_id": section.section_id,
        "source_name": section.source_name,
        "source_key": section.source_key,
        "segment_key": section.segment_key,
        "before_count": before,
        "target_per_section": target_per_section,
        "planned_max_listings": _listings_goal(before, target_per_section),
        "entry_urls": list(section.entry_urls),
        "status": "skipped_threshold_reached" if before >= target_per_section else "planned",
        "waves": [],
    }
    if before >= target_per_section or dry_run:
        return result

    after = before
    status = "stalled_no_progress"
    for wave in range(1, max(1, max_waves) + 1):
        current = after
        goal = _listings_goal(current, target_per_section)
        if goal <= 0:
            status = "threshold_reached"
            break

        wave_pages = max(1, max_pages * wave)
        stats = scrape_source(
            section.source_key,
            download_photos=download_photos,
            max_pages=wave_pages,
            max_listings=goal,
            config_override=build_config_override(section),
            accept_parsed=make_accept_predicate(section),
            save_context_builder=make_save_context_builder(section),
        )
        after = count_saved_section_items(section, require_full_gallery=require_full_gallery)
        wave_result = {
            "wave": wave,
            "before_count": current,
            "after_count": after,
            "added_count": max(0, after - current),
            "max_pages": wave_pages,
            "planned_max_listings": goal,
            "scrape_stats": {
                "discovery_pages_fetched": stats.discovery_pages_fetched,
                "listing_urls_discovered": stats.listing_urls_discovered,
                "listing_pages_fetched": stats.listing_pages_fetched,
                "listing_pages_parsed": stats.listing_pages_parsed,
                "photos_found": stats.photos_found,
                "photos_downloaded": stats.photos_downloaded,
                "photos_failed": stats.photos_failed,
                "with_description": stats.with_description,
            },
        }
        result["waves"].append(wave_result)
        if after >= target_per_section:
            status = "threshold_reached"
            break
        if after <= current:
            status = "stalled_no_progress"
            break
        status = "partial_progress"

    result.update(
        {
            "after_count": after,
            "added_count": max(0, after - before),
            "status": status,
        }
    )
    return result


def run_source_sections(
    source_key: str,
    sections: list[VarnaSection],
    *,
    max_pages: int,
    target_per_section: int,
    download_photos: bool,
    require_full_gallery: bool,
    dry_run: bool,
    max_waves: int,
) -> dict[str, Any]:
    sections = sorted(sections, key=lambda item: item.section_id)
    out = {
        "source_key": source_key,
        "source_name": sections[0].source_name if sections else source_key,
        "sections": [],
    }
    for section in sections:
        out["sections"].append(
            run_section_scrape(
                section,
                max_pages=max_pages,
                target_per_section=target_per_section,
                download_photos=download_photos,
                require_full_gallery=require_full_gallery,
                dry_run=dry_run,
                max_waves=max_waves,
            )
        )
    return out


def refresh_dashboard_artifacts() -> list[str]:
    outputs: list[str] = []
    for script_name in DASHBOARD_REFRESH_SCRIPTS:
        script = REPO / "scripts" / script_name
        runpy.run_path(str(script), run_name="__main__")
        outputs.append(str(script))
    return outputs


def run_parallel_varna_scrape(
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    target_per_section: int = 100,
    max_pages: int = 8,
    download_photos: bool = True,
    require_full_gallery: bool = True,
    patterned_only: bool = True,
    dry_run: bool = True,
    parallel_sources: int = 4,
    sources: list[str] | None = None,
    output_path: Path | None = DEFAULT_OUTPUT_PATH,
    max_waves: int = 3,
    refresh_dashboard: bool = False,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    sections = _build_sections(manifest, patterned_only=patterned_only)
    if sources:
        wanted = {item.strip().lower() for item in sources if item.strip()}
        sections = [section for section in sections if section.source_key.lower() in wanted or section.source_name.lower() in wanted]

    grouped: dict[str, list[VarnaSection]] = {}
    for section in sections:
        grouped.setdefault(section.source_key, []).append(section)

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, parallel_sources)) as executor:
        futures = {
            executor.submit(
                run_source_sections,
                source_key,
                source_sections,
                max_pages=max_pages,
                target_per_section=target_per_section,
                download_photos=download_photos,
                require_full_gallery=require_full_gallery,
                dry_run=dry_run,
                max_waves=max_waves,
            ): source_key
            for source_key, source_sections in sorted(grouped.items())
        }
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: item["source_name"].lower())
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "manifest_path": str(manifest_path),
        "target_per_section": target_per_section,
        "max_pages": max_pages,
        "download_photos": download_photos,
        "require_full_gallery": require_full_gallery,
        "patterned_only": patterned_only,
        "dry_run": dry_run,
        "parallel_sources": parallel_sources,
        "max_waves": max_waves,
        "source_count": len(results),
        "results": results,
    }
    if refresh_dashboard:
        payload["dashboard_refresh_scripts"] = refresh_dashboard_artifacts()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def run_source_full_scrape(
    source_key: str,
    *,
    max_pages: int,
    target_per_source: int,
    download_photos: bool,
    require_full_gallery: bool,
    dry_run: bool,
    max_waves: int,
) -> dict[str, Any]:
    before = count_saved_source_items(source_key, require_full_gallery=require_full_gallery)
    result: dict[str, Any] = {
        "source_key": source_key,
        "source_name": SOURCE_CONFIGS[source_key]["name"],
        "before_count": before,
        "target_per_source": target_per_source,
        "planned_max_listings": _listings_goal(before, target_per_source),
        "status": "skipped_threshold_reached" if before >= target_per_source else "planned",
        "waves": [],
    }
    if before >= target_per_source or dry_run:
        return result

    after = before
    status = "stalled_no_progress"
    for wave in range(1, max(1, max_waves) + 1):
        current = after
        goal = _listings_goal(current, target_per_source)
        if goal <= 0:
            status = "threshold_reached"
            break

        wave_pages = max(1, max_pages * wave)
        stats = scrape_source(
            source_key,
            download_photos=download_photos,
            max_pages=wave_pages,
            max_listings=goal,
        )
        after = count_saved_source_items(source_key, require_full_gallery=require_full_gallery)
        result["waves"].append(
            {
                "wave": wave,
                "before_count": current,
                "after_count": after,
                "added_count": max(0, after - current),
                "max_pages": wave_pages,
                "planned_max_listings": goal,
                "scrape_stats": {
                    "discovery_pages_fetched": stats.discovery_pages_fetched,
                    "listing_urls_discovered": stats.listing_urls_discovered,
                    "listing_pages_fetched": stats.listing_pages_fetched,
                    "listing_pages_parsed": stats.listing_pages_parsed,
                    "photos_found": stats.photos_found,
                    "photos_downloaded": stats.photos_downloaded,
                    "photos_failed": stats.photos_failed,
                    "with_description": stats.with_description,
                },
            }
        )
        if after >= target_per_source:
            status = "threshold_reached"
            break
        if after <= current:
            status = "stalled_no_progress"
            break
        status = "partial_progress"

    result.update(
        {
            "after_count": after,
            "added_count": max(0, after - before),
            "status": status,
        }
    )
    return result


def run_parallel_all_scrape(
    *,
    target_per_source: int = 100,
    max_pages: int = 8,
    download_photos: bool = True,
    require_full_gallery: bool = True,
    patterned_only: bool = True,
    dry_run: bool = True,
    parallel_sources: int = 4,
    sources: list[str] | None = None,
    output_path: Path | None = DEFAULT_ALL_OUTPUT_PATH,
    max_waves: int = 3,
    refresh_dashboard: bool = False,
) -> dict[str, Any]:
    source_keys = patterned_source_keys(patterned_only=patterned_only)
    if sources:
        wanted = {item.strip().lower() for item in sources if item.strip()}
        source_keys = [
            key
            for key in source_keys
            if key.lower() in wanted or SOURCE_CONFIGS[key]["name"].lower() in wanted
        ]

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, parallel_sources)) as executor:
        futures = {
            executor.submit(
                run_source_full_scrape,
                source_key,
                max_pages=max_pages,
                target_per_source=target_per_source,
                download_photos=download_photos,
                require_full_gallery=require_full_gallery,
                dry_run=dry_run,
                max_waves=max_waves,
            ): source_key
            for source_key in source_keys
        }
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: item["source_name"].lower())
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "geo_scope": "all_bulgaria",
        "target_per_source": target_per_source,
        "max_pages": max_pages,
        "download_photos": download_photos,
        "require_full_gallery": require_full_gallery,
        "patterned_only": patterned_only,
        "dry_run": dry_run,
        "parallel_sources": parallel_sources,
        "max_waves": max_waves,
        "source_count": len(results),
        "results": results,
    }
    if refresh_dashboard:
        payload["dashboard_refresh_scripts"] = refresh_dashboard_artifacts()
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


__all__ = [
    "run_parallel_all_scrape",
    "run_parallel_varna_scrape",
    "count_saved_source_items",
    "count_saved_section_items",
    "is_source_item_complete",
    "is_varna_listing",
    "is_section_item_complete",
    "refresh_dashboard_artifacts",
]
