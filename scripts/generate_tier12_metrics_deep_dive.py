from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REGISTRY_PATH = ROOT / "data/source_registry.json"
SCRAPE_STATUS_PATH = ROOT / "docs/exports/scrape-status-dashboard.json"
SOURCE_ANALYSIS_PATH = ROOT / "docs/exports/tier12-source-analysis.json"
OUTPUT_MD = ROOT / "docs/exports/tier12-source-metrics-deep-dive.md"
OUTPUT_XLSX = ROOT / "docs/exports/tier12-source-metrics-deep-dive.xlsx"
OUTPUT_JSON = ROOT / "docs/exports/tier12-source-metrics-deep-dive.json"

INTENT_TYPES = {"sale", "long_term_rent", "short_term_rent"}


def pct(part: int, whole: int) -> float:
    if whole <= 0:
        return 0.0
    return round((part / whole) * 100, 1)


def clamp_pct(value: float) -> float:
    return round(min(max(value, 0.0), 100.0), 1)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_declared_offers(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def derive_service_coverage(declared_offers: list[str], scraped_services: dict[str, int]) -> dict[str, Any]:
    declared_intents = [item for item in declared_offers if item in INTENT_TYPES]
    scraped_intents = sorted(key for key, count in scraped_services.items() if count > 0)
    if not declared_intents:
        return {
            "declared_intents": [],
            "scraped_intents": scraped_intents,
            "covered": 0,
            "total": 0,
            "pct": 0.0,
        }
    covered = len(set(declared_intents) & set(scraped_intents))
    return {
        "declared_intents": declared_intents,
        "scraped_intents": scraped_intents,
        "covered": covered,
        "total": len(declared_intents),
        "pct": pct(covered, len(declared_intents)),
    }


def format_counts(values: dict[str, int]) -> str:
    if not values:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(values.items()))


def top_field_summary(field_counts: dict[str, int], saved_listings: int) -> str:
    if not field_counts:
        return "none captured yet"
    ordered = sorted(field_counts.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{field} {count}/{saved_listings}" for field, count in ordered[:6])


def automation_recommendations(row: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    saved = row["saved_listings"]
    photo = row["with_photo_urls"]
    readable = row["with_readable_local_photos"]
    desc = row["with_description"]
    categories = row["category_counts"]
    unknown_count = categories.get("unknown", 0)
    service_cov = row["service_coverage"]["pct"]

    if saved == 0:
        notes.append("Repair category entrypoints first, then validate one stable detail-URL family before broad pagination.")
        notes.append("Run product-by-product detail fetch with full-gallery download enabled from the first successful item.")
    else:
        notes.append("Keep category-first discovery and push every card into a detail-page queue; do not rely on homepage sampling.")
        if desc < saved:
            notes.append("Add detail-page fallback extraction for missing descriptions and keep raw HTML for retries.")
        if photo < saved:
            notes.append("Normalize gallery extraction so each item attempts the full reachable photo set, not only the lead image.")
        if readable < photo:
            notes.append("Add image URL normalization, decode validation, and re-download retries for unreadable or lazy-loaded media.")
        if unknown_count and saved and pct(unknown_count, saved) >= 25.0:
            notes.append("Improve item classification with title heuristics, structured-data parsing, and URL-path category mapping.")
        if service_cov < 100.0:
            notes.append("Expand intent coverage by crawling explicit sale and rent bucket pages separately and tracking them as independent queues.")
    if row["benchmark_progress_pct"] < 100.0:
        notes.append("Increase batch depth per category until the source clears the 100-item benchmark or a real blocker is observed.")
    return notes[:5]


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    registry = load_json(SOURCE_REGISTRY_PATH)["sources"]
    scrape_status = {item["source_name"]: item for item in load_json(SCRAPE_STATUS_PATH)["sources"]}
    source_analysis = {item["source_name"]: item for item in load_json(SOURCE_ANALYSIS_PATH)["sources"]}

    rows: list[dict[str, Any]] = []
    tier_totals: dict[int, dict[str, Any]] = defaultdict(lambda: {"sources": 0, "saved": 0, "estimated": 0})

    for source in registry:
        tier = source.get("tier")
        if tier not in {1, 2}:
            continue

        name = source["source_name"]
        status = scrape_status.get(name, {})
        analysis = source_analysis.get(name, {})
        declared_offers = parse_declared_offers(analysis.get("services_declared", ""))
        saved = int(status.get("saved_listings") or analysis.get("saved_listings") or 0)
        desc = int(status.get("with_description") or analysis.get("with_description") or 0)
        photo = int(status.get("with_photo_urls") or analysis.get("with_photo_urls") or 0)
        readable = int(status.get("with_readable_local_photos") or analysis.get("with_readable_local_photos") or 0)
        estimated_total = int(analysis.get("estimated_total_listings") or 0)
        service_counts = status.get("service_counts") or {}
        category_counts = status.get("category_counts") or {}
        field_counts = status.get("field_counts") or {}
        service_coverage = derive_service_coverage(declared_offers, service_counts)

        row = {
            "tier": tier,
            "source_name": name,
            "primary_url": source.get("primary_url", ""),
            "access_mode": source.get("access_mode", ""),
            "legal_mode": source.get("legal_mode", ""),
            "best_extraction_method": analysis.get("best_extraction_method") or source.get("best_extraction_method", ""),
            "declared_offers": declared_offers,
            "estimated_total_listings": estimated_total,
            "saved_listings": saved,
            "estimated_coverage_pct": pct(saved, estimated_total) if estimated_total else 0.0,
            "benchmark_progress_pct": clamp_pct((saved / 100) * 100 if saved else 0.0),
            "with_description": desc,
            "description_pct": pct(desc, saved),
            "with_photo_urls": photo,
            "photo_pct": pct(photo, saved),
            "with_readable_local_photos": readable,
            "readable_pct": pct(readable, saved),
            "service_counts": service_counts,
            "category_counts": category_counts,
            "field_counts": field_counts,
            "field_summary": top_field_summary(field_counts, saved),
            "service_coverage": service_coverage,
            "list_organization": analysis.get("list_organization", ""),
            "full_list_strategy": analysis.get("full_list_strategy", ""),
            "detail_url_pattern": analysis.get("detail_url_pattern", ""),
            "detail_requirement": analysis.get("detail_requirement", ""),
            "discovery_entrypoints": analysis.get("discovery_entrypoints", "").splitlines() if analysis.get("discovery_entrypoints") else [],
            "apartment_entrypoints": analysis.get("apartment_entrypoints", "").splitlines() if analysis.get("apartment_entrypoints") else [],
            "state": status.get("state", ""),
            "next_step": status.get("next_step", ""),
        }
        row["automation_recommendations"] = automation_recommendations(row)
        rows.append(row)

        tier_totals[tier]["sources"] += 1
        tier_totals[tier]["saved"] += saved
        tier_totals[tier]["estimated"] += estimated_total

    rows.sort(key=lambda item: (item["tier"], item["source_name"].lower()))
    return rows, tier_totals


def write_markdown(rows: list[dict[str, Any]], tier_totals: dict[int, dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# Tier 1-2 source metrics deep dive")
    lines.append("")
    lines.append("Generated from `data/source_registry.json`, `docs/exports/tier12-source-analysis.json`, and `docs/exports/scrape-status-dashboard.json`.")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("FACT:")
    lines.append("- `estimated_total_listings` is the saved site-scale estimate from the project source analysis snapshot, not a fresh live recount from today.")
    lines.append("- `saved_listings` is the currently landed on-disk corpus from `data/scraped/*/listings/*.json`.")
    lines.append("- `with_description`, `with_photo_urls`, and `with_readable_local_photos` are evidence-backed completeness counters from the saved corpus.")
    lines.append("")
    lines.append("INTERPRETATION:")
    lines.append("- This report separates website scale from landed scraper output, so we do not confuse source potential with confirmed capture.")
    lines.append("")
    lines.append("GAP:")
    lines.append("- PostgreSQL `canonical_listing` proof is still pending for the live volume gate.")
    lines.append("- Some sites expose additional property categories beyond what is currently landed in the corpus.")
    lines.append("")
    lines.append("## Tier summary")
    lines.append("")
    for tier in sorted(tier_totals):
        data = tier_totals[tier]
        estimated_cov = pct(data["saved"], data["estimated"]) if data["estimated"] else 0.0
        lines.append(
            f"- Tier {tier}: {data['sources']} sources, landed corpus {data['saved']}, estimated site scale {data['estimated']}, landed-vs-estimated {estimated_cov}%"
        )
    lines.append("")
    lines.append("## Source summary table")
    lines.append("")
    lines.append(
        "| Tier | Source | Declared offers | Estimated active items | Landed items | Landed vs estimated | 100-item benchmark | Description % | Photo URL % | Readable photo % | Declared intent coverage |"
    )
    lines.append(
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for row in rows:
        lines.append(
            "| {tier} | {source_name} | {offers} | {estimated_total_listings} | {saved_listings} | {estimated_coverage_pct}% | {benchmark_progress_pct}% | {description_pct}% | {photo_pct}% | {readable_pct}% | {intent_pct}% |".format(
                tier=row["tier"],
                source_name=row["source_name"],
                offers=", ".join(row["declared_offers"]) or "none",
                estimated_total_listings=row["estimated_total_listings"],
                saved_listings=row["saved_listings"],
                estimated_coverage_pct=row["estimated_coverage_pct"],
                benchmark_progress_pct=row["benchmark_progress_pct"],
                description_pct=row["description_pct"],
                photo_pct=row["photo_pct"],
                readable_pct=row["readable_pct"],
                intent_pct=row["service_coverage"]["pct"],
            )
        )
    lines.append("")
    lines.append("## Per-source details")
    lines.append("")

    for row in rows:
        lines.append(f"### {row['source_name']}")
        lines.append("")
        lines.append(f"- Tier: `{row['tier']}`")
        lines.append(f"- URL: {row['primary_url']}")
        lines.append(f"- Access/legal: `{row['access_mode']}` / `{row['legal_mode']}`")
        lines.append(f"- Declared website offering: `{', '.join(row['declared_offers']) or 'none recorded'}`")
        lines.append(
            f"- Estimated active items on website: `{row['estimated_total_listings']}`"
        )
        lines.append(
            f"- Confirmed landed active items in current corpus: `{row['saved_listings']}`"
        )
        lines.append(
            f"- Progress vs estimated site scale: `{row['estimated_coverage_pct']}%`"
        )
        lines.append(
            f"- Progress vs 100-item benchmark: `{row['benchmark_progress_pct']}%`"
        )
        lines.append(
            f"- Completeness: description `{row['with_description']}/{row['saved_listings']}` ({row['description_pct']}%), photo URLs `{row['with_photo_urls']}/{row['saved_listings']}` ({row['photo_pct']}%), readable local photos `{row['with_readable_local_photos']}/{row['saved_listings']}` ({row['readable_pct']}%)"
        )
        lines.append(
            f"- Declared intent coverage: `{row['service_coverage']['covered']}/{row['service_coverage']['total']}` ({row['service_coverage']['pct']}%) from `{', '.join(row['service_coverage']['scraped_intents']) or 'none landed yet'}`"
        )
        lines.append(f"- Services landed: {format_counts(row['service_counts'])}")
        lines.append(f"- Property categories landed: {format_counts(row['category_counts'])}")
        lines.append(f"- Fields captured most often: {row['field_summary']}")
        lines.append(f"- Current state: {row['state'] or 'not stated'}")
        lines.append(f"- Method used now: {row['best_extraction_method'] or 'not recorded'}")
        lines.append(f"- How the list is organized: {row['list_organization'] or 'not recorded'}")
        lines.append(f"- Full-list strategy: {row['full_list_strategy'] or 'not recorded'}")
        lines.append(f"- Detail-page requirement: {row['detail_requirement'] or 'not recorded'}")
        lines.append(f"- Detail URL pattern: `{row['detail_url_pattern'] or 'not mapped yet'}`")
        if row["discovery_entrypoints"]:
            lines.append(f"- Discovery entrypoints: `{'; '.join(row['discovery_entrypoints'])}`")
        if row["apartment_entrypoints"]:
            lines.append(f"- Apartment entrypoints: `{'; '.join(row['apartment_entrypoints'])}`")
        lines.append(f"- Next step already recorded: {row['next_step'] or 'not recorded'}")
        lines.append("- What to automate better:")
        for note in row["automation_recommendations"]:
            lines.append(f"  - {note}")
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(rows: list[dict[str, Any]], tier_totals: dict[int, dict[str, Any]]) -> None:
    OUTPUT_JSON.write_text(
        json.dumps({"rows": rows, "tier_totals": tier_totals}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_xlsx(rows: list[dict[str, Any]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "tier12_metrics"
    headers = [
        "tier",
        "source_name",
        "primary_url",
        "access_mode",
        "legal_mode",
        "declared_offers",
        "estimated_active_items",
        "landed_items",
        "landed_vs_estimated_pct",
        "benchmark_100_pct",
        "description_pct",
        "photo_url_pct",
        "readable_photo_pct",
        "declared_intent_coverage_pct",
        "services_landed",
        "categories_landed",
        "fields_captured",
        "method_used",
        "full_list_strategy",
        "detail_url_pattern",
        "next_step",
        "automation_recommendations",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for row in rows:
        ws.append(
            [
                row["tier"],
                row["source_name"],
                row["primary_url"],
                row["access_mode"],
                row["legal_mode"],
                ", ".join(row["declared_offers"]),
                row["estimated_total_listings"],
                row["saved_listings"],
                row["estimated_coverage_pct"],
                row["benchmark_progress_pct"],
                row["description_pct"],
                row["photo_pct"],
                row["readable_pct"],
                row["service_coverage"]["pct"],
                format_counts(row["service_counts"]),
                format_counts(row["category_counts"]),
                row["field_summary"],
                row["best_extraction_method"],
                row["full_list_strategy"],
                row["detail_url_pattern"],
                row["next_step"],
                " | ".join(row["automation_recommendations"]),
            ]
        )

    widths = {
        "A": 8,
        "B": 24,
        "C": 34,
        "D": 18,
        "E": 24,
        "F": 34,
        "G": 18,
        "H": 14,
        "I": 20,
        "J": 18,
        "K": 16,
        "L": 16,
        "M": 18,
        "N": 26,
        "O": 34,
        "P": 34,
        "Q": 40,
        "R": 26,
        "S": 48,
        "T": 38,
        "U": 40,
        "V": 60,
    }
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    wb.save(OUTPUT_XLSX)


def main() -> None:
    rows, tier_totals = build_rows()
    write_markdown(rows, tier_totals)
    write_json(rows, tier_totals)
    write_xlsx(rows)
    print(f"Wrote {OUTPUT_MD}")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
