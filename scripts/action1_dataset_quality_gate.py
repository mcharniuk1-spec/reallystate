#!/usr/bin/env python3
"""Mark Action1 scraped rows with quality state, LOST queue, and identity class.

The script is intentionally file-backed: it audits `data/scraped/<source>/listings`
without requiring a database. It can optionally check a bounded set of source
URLs, but URL checks are not required for offline classification.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parent.parent
SCRAPED_ROOT = REPO / "data" / "scraped"
EXPORTS = REPO / "docs" / "exports"
RUNS = REPO / "data" / "runs"
QUALITY_CACHE = RUNS / "action1_quality_rollup_latest.json"

ACTION1_SOURCES = {
    "address_bg": "Address.bg",
    "bulgarianproperties": "BulgarianProperties",
    "homes_bg": "Homes.bg",
    "imot_bg": "imot.bg",
    "luximmo": "LUXIMMO",
    "property_bg": "property.bg",
    "suprimmo": "SUPRIMMO",
}

ALLOWED_HOSTS = {
    "address_bg": ("address.bg", "www.address.bg"),
    "bulgarianproperties": ("bulgarianproperties.com", "www.bulgarianproperties.com"),
    "homes_bg": ("homes.bg", "www.homes.bg"),
    "imot_bg": ("imot.bg", "www.imot.bg"),
    "luximmo": ("luximmo.bg", "www.luximmo.bg"),
    "property_bg": ("property.bg", "www.property.bg"),
    "suprimmo": ("suprimmo.bg", "www.suprimmo.bg"),
}

GALLERY_CAPABLE = set(ACTION1_SOURCES)
COMMERCIAL_CATEGORIES = {"office", "shop", "land", "garage"}

MULTI_UNIT_RE = re.compile(
    r"\b\d+\s*[-–/]\s*\d+\s*(bedroom|bed|room|спалн|стайн|стаен)\b"
    r"|apartments\s*\(various\s*types\)|various_types|different apartments|apartments available|units available"
    r"|selection of|choice of|prices?\s+from|starting\s+from|цени\s+от|цена\s+от|цени\s+започва"
    r"|price\s+per\s+sq\.?\s*m|цена\s+на\s+кв\.?\s*м"
    r"|new development|project development|whole residential building|entire residential building"
    r"|жилищна сграда\s+(?:с|предлага|включва|разполага)|новострояща\s+се\s+жилищна\s+сграда"
    r"|комплекс\s+от\s+\d+|проект\s+с\s+\d+|вилно\s+селище|сграда\s+с\s+\d+\s+(?:апартамента|жилища)",
    re.IGNORECASE,
)

BOILERPLATE_RE = re.compile(
    r"cookie|javascript|enable cookies|all rights reserved|следете ни|вижте всички|"
    r"този сайт използва|общи условия|privacy policy|GDPR",
    re.IGNORECASE,
)

FOREIGN_MARKET_RE = re.compile(
    r"/(?:greece|turkey|romania|serbia|cyprus|spain|italy|croatia)/|"
    r"_in_(?:greece|turkey|romania|serbia|cyprus|spain|italy|croatia)\b|"
    r"\b(?:Greece|Turkey|Romania|Serbia|Cyprus|Spain|Italy|Croatia)\b",
    re.IGNORECASE,
)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def count_remote(row: dict[str, Any]) -> int:
    value = row.get("photo_count_remote")
    if isinstance(value, int):
        return value
    return len(row.get("image_urls") or [])


def count_local(row: dict[str, Any]) -> int:
    value = row.get("photo_count_local")
    if isinstance(value, int):
        return value
    return len(row.get("local_image_files") or [])


def text_blob(row: dict[str, Any]) -> str:
    return "\n".join(str(row.get(key) or "") for key in ("title", "description", "listing_url", "city", "district", "region", "address_text"))


def source_url_host_ok(source_key: str, url: str) -> bool:
    parsed = urlparse(url or "")
    host = (parsed.netloc or "").lower()
    return bool(parsed.scheme in {"http", "https"} and host in ALLOWED_HOSTS.get(source_key, ()))


def in_bulgaria_coordinates(row: dict[str, Any]) -> bool:
    lat = row.get("latitude")
    lon = row.get("longitude")
    if lat is None or lon is None:
        return True
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return False
    return 41.0 <= lat_f <= 44.5 and 22.0 <= lon_f <= 29.5


def price_status(row: dict[str, Any]) -> str:
    provenance = row.get("crawl_provenance") or {}
    return str(provenance.get("price_status") or "").lower()


def classify_multi_unit(row: dict[str, Any]) -> tuple[bool, str]:
    blob = text_blob(row)
    if row.get("source_publication_type") == "multi_unit_or_development":
        return True, "persisted_multi_unit_publication"
    if row.get("scrape_acceptance_status") == "not_single_entity":
        return True, "persisted_not_single_entity"
    if row.get("suspected_multi_unit_publication"):
        return True, "persisted_multi_unit_flag"
    if MULTI_UNIT_RE.search(blob):
        return True, "strong_multi_unit_pattern"
    return False, ""


def recommended_method(source_key: str, reasons: list[str], multi_unit: bool) -> str:
    if multi_unit:
        return "Do not promote as one property; either split only with unit-level URL/price/area/media evidence or keep as grouped publication."
    if "partial_local_gallery" in reasons:
        return "Run media backfill from saved image_urls; preserve image order and readable-file validation."
    if source_key == "address_bg":
        return "Refetch detail page; use Address.bg detail anchors under /storage/uploads/offers/.../1000x666/ and then download all missing images."
    if source_key == "bulgarianproperties":
        return "Refetch detail page; prefer Product JSON-LD/body description and /big/ gallery URLs; exclude recommendation-card media."
    if source_key == "homes_bg":
        return "Refetch API/detail pair; parse offer JSON, photos array, status, sqm-specific title area, and coordinates only inside Bulgaria."
    if source_key == "imot_bg":
        return "Refetch detail page; parse data-src-gallery, .adParams, active/inactive page markers, and source ID from canonical URL."
    if source_key in {"luximmo", "property_bg", "suprimmo"}:
        return "Refetch detail page; parse dataLayer plus labeled unit fields (RZP/ZP/total area) and classify development pages separately."
    return "Refetch detail page with source-specific parser and full-gallery media backfill."


def local_reasons(source_key: str, row: dict[str, Any]) -> tuple[list[str], list[str], bool, str]:
    lost: list[str] = []
    warnings: list[str] = []
    url = str(row.get("listing_url") or "")
    title = str(row.get("title") or "").strip()
    desc = str(row.get("description") or "").strip()
    category = str(row.get("property_category") or "").lower()
    area = row.get("area_sqm")
    remote = count_remote(row)
    local = count_local(row)
    multi_unit, multi_reason = classify_multi_unit(row)

    if not url:
        lost.append("missing_listing_url")
    elif not source_url_host_ok(source_key, url):
        lost.append("source_domain_mismatch")
    if FOREIGN_MARKET_RE.search(url):
        lost.append("foreign_market_url")
    if not title:
        lost.append("missing_title")
    elif len(title) < 8:
        lost.append("thin_title")
    if not desc:
        lost.append("missing_description")
    elif len(desc) < 40:
        lost.append("description_too_short")
    elif BOILERPLATE_RE.search(desc) and len(desc) < 300:
        lost.append("description_boilerplate_suspect")
    elif len(desc) < 160:
        warnings.append("thin_description")
    if row.get("price") == 0:
        lost.append("zero_price_invalid")
    elif row.get("price") is None and price_status(row) not in {"on_request", "undefined"}:
        lost.append("missing_price_without_status")
    if str(row.get("listing_status") or "").lower() in {"inactive", "removed", "expired"}:
        lost.append("inactive_listing_status")
    if area is None and category not in {"garage"}:
        lost.append("missing_area")
    elif isinstance(area, (int, float)):
        area_f = float(area)
        if 0 < area_f < 2:
            lost.append("suspicious_area_below_2sqm")
        if category in {"apartment", "office", "shop"} and area_f > 1000:
            lost.append("suspicious_unit_area_too_large")
        if category == "house" and area_f > 5000:
            lost.append("suspicious_house_area_too_large")
    if not (row.get("city") or row.get("address_text")):
        lost.append("missing_city_or_address")
    if not in_bulgaria_coordinates(row):
        lost.append("outside_bulgaria_coordinates")
    if remote <= 0:
        lost.append("missing_remote_gallery")
    elif source_key in GALLERY_CAPABLE and remote == 1:
        lost.append("one_remote_photo_gallery_suspect")
    if remote > 0 and local < remote:
        lost.append("partial_local_gallery")
    if multi_unit:
        warnings.append(f"multi_unit_publication:{multi_reason}")
    return sorted(set(lost)), sorted(set(warnings)), multi_unit, multi_reason


def check_url(client: httpx.Client, url: str) -> dict[str, Any]:
    out = {"checked": True, "url": url, "status_code": None, "final_url": "", "status": "unknown"}
    try:
        response = client.get(url)
    except Exception as exc:
        out["status"] = "error"
        out["error"] = type(exc).__name__
        return out
    out["status_code"] = response.status_code
    out["final_url"] = str(response.url)
    text = response.text[:5000].lower() if response.text else ""
    if response.status_code in {404, 410}:
        out["status"] = "not_found"
    elif response.status_code in {401, 403, 429, 503}:
        out["status"] = "blocked_or_rate_limited"
    elif response.status_code >= 400:
        out["status"] = "http_error"
    elif any(marker in text for marker in ("не е активна", "обявата е изтрита", "offer not found", "page not found", "404")):
        out["status"] = "inactive_or_removed_marker"
    else:
        out["status"] = "exists"
    return out


def audit(args: argparse.Namespace) -> dict[str, Any]:
    generated_at = datetime.now(tz=timezone.utc).isoformat()
    item_rows: list[dict[str, Any]] = []
    lost_queue: list[dict[str, Any]] = []
    multi_rows: list[dict[str, Any]] = []
    source_totals: dict[str, Counter[str]] = defaultdict(Counter)
    source_reason_counts: dict[str, Counter[str]] = defaultdict(Counter)
    quality_rollup: Counter[str] = Counter()
    per_source_quality: dict[str, Counter[str]] = defaultdict(Counter)

    paths: list[tuple[str, str, Path]] = []
    for source_key, source_name in ACTION1_SOURCES.items():
        listing_dir = SCRAPED_ROOT / source_key / "listings"
        source_paths = sorted(listing_dir.glob("*.json"))
        if args.limit_per_source > 0:
            source_paths = source_paths[: args.limit_per_source]
        paths.extend((source_key, source_name, path) for path in source_paths)

    url_check_budget = args.url_check_limit
    url_check_per_source: dict[str, int] = defaultdict(int)
    client: Any = None
    if args.check_urls:
        import httpx

        client = httpx.Client(
            timeout=args.url_timeout,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 bgrealestate-quality-audit"},
        )
    try:
        for source_key, source_name, path in paths:
            row = read_json(path)
            if not row:
                continue
            lost_reasons, warning_reasons, multi_unit, multi_reason = local_reasons(source_key, row)
            url_evidence = None
            source_budget_ok = args.url_check_per_source <= 0 or url_check_per_source[source_key] < args.url_check_per_source
            should_check_url = bool(args.check_urls and url_check_budget > 0 and source_budget_ok and (lost_reasons or multi_unit))
            if should_check_url:
                assert client is not None
                url_evidence = check_url(client, str(row.get("listing_url") or ""))
                url_check_budget -= 1
                url_check_per_source[source_key] += 1
                if url_evidence["status"] in {"not_found", "inactive_or_removed_marker"}:
                    lost_reasons.append("source_url_not_available")
                elif url_evidence["status"] == "exists":
                    warning_reasons.append("source_url_exists")

            lost_reasons = sorted(set(lost_reasons))
            warning_reasons = sorted(set(warning_reasons))
            scrape_status = "LOST" if lost_reasons else ("GROUPED_PUBLICATION" if multi_unit else "SCRAPED_OK")
            acceptance = "not_scraped_rescrape_required" if lost_reasons else ("not_single_entity" if multi_unit else "accepted_single_entity_candidate")
            next_action = recommended_method(source_key, lost_reasons, multi_unit)
            source_publication_type = "multi_unit_or_development" if multi_unit else "single_unit_candidate"

            source_totals[source_key]["items"] += 1
            source_totals[source_key][scrape_status] += 1
            if multi_unit:
                source_totals[source_key]["multi_unit_or_development"] += 1
            for reason in lost_reasons:
                source_reason_counts[source_key][reason] += 1

            evidence_row = {
                "source_key": source_key,
                "source_name": source_name,
                "reference_id": row.get("reference_id") or path.stem,
                "listing_json_path": str(path.relative_to(REPO)),
                "listing_url": row.get("listing_url"),
                "title": row.get("title"),
                "scrape_status": scrape_status,
                "scrape_acceptance_status": acceptance,
                "source_publication_type": source_publication_type,
                "lost_reasons": lost_reasons,
                "warning_reasons": warning_reasons,
                "next_scrape_action": next_action,
                "url_evidence": url_evidence,
                "description_chars": len(str(row.get("description") or "")),
                "price": row.get("price"),
                "area_sqm": row.get("area_sqm"),
                "city": row.get("city"),
                "district": row.get("district"),
                "photo_count_remote": count_remote(row),
                "photo_count_local": count_local(row),
                "multi_unit_reason": multi_reason,
            }
            item_rows.append(evidence_row)
            if lost_reasons:
                lost_queue.append(evidence_row)
            if multi_unit:
                multi_rows.append(evidence_row)

            if args.apply:
                prev_a1 = dict(row.get("action1_quality") or {})
                prev_status = str(prev_a1.get("status") or "").strip()
                prev_bad_or_grouped = prev_status in {"LOST", "GROUPED_PUBLICATION"}
                now_good_single_unit = scrape_status == "SCRAPED_OK" and not multi_unit

                rescrape = dict(prev_a1.get("rescrape") or {})
                if (prev_bad_or_grouped and now_good_single_unit) and not rescrape.get("rescraped_ok_at"):
                    rescrape["rescraped_ok_at"] = generated_at
                if (not prev_bad_or_grouped) and (not now_good_single_unit):
                    rescrape.setdefault("bad_first_seen_at", generated_at)
                if not now_good_single_unit:
                    rescrape["bad_seen_count"] = int(rescrape.get("bad_seen_count") or 0) + 1
                rescrape["was_bad_or_grouped"] = bool(prev_bad_or_grouped or (not now_good_single_unit))

                quality = {
                    "status": scrape_status,
                    "acceptance_status": acceptance,
                    "lost_reasons": lost_reasons,
                    "warning_reasons": warning_reasons,
                    "last_quality_audit_at": generated_at,
                    "next_scrape_action": next_action,
                    "url_evidence": url_evidence,
                }
                row["scrape_status"] = scrape_status
                row["scrape_acceptance_status"] = acceptance
                row["scrape_quality"] = quality
                row["is_scraped"] = scrape_status != "LOST"
                row["needs_rescrape"] = scrape_status == "LOST"
                row["source_publication_type"] = source_publication_type
                row["single_entity_candidate"] = not multi_unit and scrape_status != "LOST"
                row["action1_quality"] = {
                    "status": scrape_status,
                    "good_single_unit": bool(now_good_single_unit),
                    "lost_reasons": lost_reasons,
                    "warning_reasons": warning_reasons,
                    "checked_at": generated_at,
                    "rescrape": rescrape,
                }
                if multi_unit:
                    row["suspected_multi_unit_publication"] = True
                    provenance = dict(row.get("crawl_provenance") or {})
                    provenance["identity_status"] = "source_publication_requires_unit_level_review"
                    row["crawl_provenance"] = provenance
                warnings = set(row.get("scrape_warnings") or [])
                warnings.update(warning_reasons)
                if lost_reasons:
                    warnings.add("lost_rescrape_required")
                if warnings:
                    row["scrape_warnings"] = sorted(warnings)
                write_json(path, row)

            # Rollups (work even when not applying; rescrape_ok requires prior on-disk state).
            quality_rollup["total"] += 1
            per_source_quality[source_key]["total"] += 1
            if scrape_status == "SCRAPED_OK" and not multi_unit:
                quality_rollup["good_single_unit"] += 1
                per_source_quality[source_key]["good_single_unit"] += 1
            elif scrape_status == "GROUPED_PUBLICATION" or multi_unit:
                quality_rollup["grouped_publication"] += 1
                per_source_quality[source_key]["grouped_publication"] += 1
            else:
                quality_rollup["bad_lost"] += 1
                per_source_quality[source_key]["bad_lost"] += 1
            prev_a1 = dict(row.get("action1_quality") or {})
            prev_status = str(prev_a1.get("status") or "").strip()
            if prev_status in {"LOST", "GROUPED_PUBLICATION"} and scrape_status == "SCRAPED_OK" and not multi_unit:
                quality_rollup["rescraped_ok"] += 1
                per_source_quality[source_key]["rescraped_ok"] += 1
    finally:
        if client is not None:
            client.close()

    totals = {
        source_key: {
            **dict(counter),
            "reason_counts": dict(source_reason_counts[source_key].most_common()),
            "quality": dict(per_source_quality[source_key]),
        }
        for source_key, counter in sorted(source_totals.items())
    }
    return {
        "generated_at": generated_at,
        "applied": bool(args.apply),
        "url_checks_requested": int(args.url_check_limit if args.check_urls else 0),
        "url_checks_completed": sum(1 for item in item_rows if item.get("url_evidence")),
        "url_checks_per_source": dict(url_check_per_source),
        "quality_rollup": dict(quality_rollup),
        "sources": totals,
        "lost_queue": lost_queue,
        "multi_unit_publications": multi_rows,
        "items": item_rows,
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "source_key",
        "reference_id",
        "scrape_status",
        "scrape_acceptance_status",
        "source_publication_type",
        "lost_reasons",
        "warning_reasons",
        "listing_url",
        "title",
        "price",
        "area_sqm",
        "city",
        "photo_count_remote",
        "photo_count_local",
        "next_scrape_action",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: json.dumps(row.get(field), ensure_ascii=False) if isinstance(row.get(field), list) else row.get(field) for field in fields})


def write_markdown(data: dict[str, Any], path: Path) -> None:
    lines = [
        "# Action1 Dataset Quality Gate",
        "",
        f"Generated: {data['generated_at']}",
        "",
        "FACT: `LOST` means the row is quarantined as not properly scraped and queued for the next scraping session; the source URL and raw evidence are preserved.",
        "FACT: `GROUPED_PUBLICATION` means the source page appears to describe a multi-unit/development publication, not one sellable/rentable entity.",
        "",
        "## Source Summary",
        "",
        "| Source | Items | SCRAPED_OK | LOST | GROUPED_PUBLICATION | Multi-unit/development | Top LOST reasons |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for source_key, source in data["sources"].items():
        reasons = ", ".join(f"{key}:{value}" for key, value in list((source.get("reason_counts") or {}).items())[:8])
        lines.append(
            f"| {source_key} | {source.get('items', 0)} | {source.get('SCRAPED_OK', 0)} | "
            f"{source.get('LOST', 0)} | {source.get('GROUPED_PUBLICATION', 0)} | "
            f"{source.get('multi_unit_or_development', 0)} | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `docs/exports/action1-lost-rescrape-queue.json`",
            "- `docs/exports/action1-lost-rescrape-queue.csv`",
            "- `docs/exports/action1-multi-unit-publications.json`",
            "- `docs/exports/action1-dataset-quality-gate.json`",
            "",
            "## Pattern Updates",
            "",
            "- Address.bg: detail page gallery must use high-resolution `/storage/uploads/offers/.../1000x666/` anchors; one-photo rows are LOST unless source evidence proves only one image.",
            "- BulgarianProperties: full description must come from Product JSON-LD/body text, not the short meta snippet; gallery must use listing `/big/` images and exclude recommendations.",
            "- Homes.bg: parse offer JSON and sqm-specific area, not the first number in title text.",
            "- imot.bg: parse detail `data-src-gallery`, `.adParams`, title/location, and active/inactive markers; one-photo and missing-price rows go to the rescrape queue.",
            "- LUXIMMO/property.bg/SUPRIMMO: use dataLayer plus labeled unit fields and classify development pages separately from single units.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Action1 dataset quality and mark LOST/grouped rows.")
    parser.add_argument("--apply", action="store_true", help="Write quality fields back to listing JSON files.")
    parser.add_argument("--check-urls", action="store_true", help="Check a bounded set of suspect source URLs.")
    parser.add_argument("--url-check-limit", type=int, default=0, help="Maximum suspect URLs to check.")
    parser.add_argument("--url-check-per-source", type=int, default=0, help="Maximum suspect URLs to check per source; 0 means no per-source cap.")
    parser.add_argument("--limit-per-source", type=int, default=0, help="Limit local listing files audited per source; 0 means all.")
    parser.add_argument("--url-timeout", type=float, default=12.0)
    parser.add_argument("--output", type=Path, default=EXPORTS / "action1-dataset-quality-gate.json")
    args = parser.parse_args()

    data = audit(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lost_path = EXPORTS / "action1-lost-rescrape-queue.json"
    lost_path.write_text(json.dumps(data["lost_queue"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    multi_path = EXPORTS / "action1-multi-unit-publications.json"
    multi_path.write_text(json.dumps(data["multi_unit_publications"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(data["lost_queue"], EXPORTS / "action1-lost-rescrape-queue.csv")
    write_markdown(data, EXPORTS / "action1-dataset-quality-gate.md")
    # Small cache for fast Telegram PULSE stats (no full JSON scan required).
    RUNS.mkdir(parents=True, exist_ok=True)
    QUALITY_CACHE.write_text(
        json.dumps(
            {
                "generated_at": data.get("generated_at"),
                "applied": bool(data.get("applied")),
                "quality_rollup": data.get("quality_rollup") or {},
                "per_source_quality_rollup": {
                    sk: (row.get("quality") or {}) for sk, row in (data.get("sources") or {}).items()
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}")
    print(f"LOST queue: {len(data['lost_queue'])}; multi-unit/development: {len(data['multi_unit_publications'])}; url checks: {data['url_checks_completed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
