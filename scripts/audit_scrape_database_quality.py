#!/usr/bin/env python3
"""Offline scrape corpus and schema quality audit.

This is intentionally file-backed: it reads data/scraped/**/listings/*.json
and static schema/model files, then writes a reproducible report for scraper
and data agents. It does not perform live network checks and does not require
SQLAlchemy or PostgreSQL.
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parent.parent
SCRAPED_ROOT = REPO / "data" / "scraped"
REGISTRY_PATH = REPO / "data" / "source_registry.json"
EXPORTS = REPO / "docs" / "exports"
MEDIA_ROOT = REPO / "data" / "media"
SQL_SCHEMA = REPO / "sql" / "schema.sql"
DOMAIN_MODELS = REPO / "src" / "bgrealestate" / "models.py"
DB_MODELS = REPO / "src" / "bgrealestate" / "db" / "models.py"

ACTION1_KEYS = {
    "address_bg",
    "bulgarianproperties",
    "homes_bg",
    "imot_bg",
    "luximmo",
    "property_bg",
    "suprimmo",
}

COMMERCIAL_CATEGORIES = {"office", "shop", "garage", "land"}
PHONE_RE_VALID = re.compile(r"^(?:0\d{8,9}|359\d{8,9})$")
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


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def norm_phone(value: Any) -> str:
    digits = re.sub(r"\D+", "", str(value or ""))
    if digits.startswith("00359"):
        digits = "359" + digits[5:]
    if digits.startswith("3590"):
        digits = "359" + digits[4:]
    return digits


def is_valid_bg_phone(value: Any) -> bool:
    return bool(PHONE_RE_VALID.match(norm_phone(value)))


def text_blob(row: dict[str, Any]) -> str:
    return "\n".join(
        str(row.get(key) or "")
        for key in ("title", "description", "listing_url", "city", "district", "region", "address_text")
    )


def price_status(row: dict[str, Any]) -> str:
    return str((row.get("crawl_provenance") or {}).get("price_status") or "").lower()


def remote_urls(row: dict[str, Any]) -> list[str]:
    return [str(item) for item in (row.get("image_urls") or []) if str(item).strip()]


def local_files(row: dict[str, Any]) -> list[str]:
    return [str(item) for item in (row.get("local_image_files") or []) if str(item).strip()]


def normalized_image_key(url: str) -> str:
    out = str(url).split("?", 1)[0]
    out = re.sub(r"/(?:small1|medium|thumb|thumbnail|100x666|150x|200x|250x|300x|370x200)/", "/SIZE/", out)
    return out


def classify_row(row: dict[str, Any], source_key: str) -> tuple[str, list[str], list[str]]:
    """Return estimated status, hard reasons, warnings for offline QA."""
    reasons: list[str] = []
    warnings: list[str] = []
    title = str(row.get("title") or "").strip()
    desc = str(row.get("description") or "").strip()
    category = str(row.get("property_category") or "").lower()
    intent = str(row.get("listing_intent") or "").lower()
    area = row.get("area_sqm")
    price = row.get("price")
    remote = len(remote_urls(row))
    local = len(local_files(row))
    persisted_multi = (
        row.get("source_publication_type") == "multi_unit_or_development"
        or row.get("scrape_acceptance_status") == "not_single_entity"
        or bool(row.get("suspected_multi_unit_publication"))
    )
    heuristic_multi = bool(MULTI_UNIT_RE.search(text_blob(row)))
    multi = persisted_multi or heuristic_multi

    if not row.get("listing_url"):
        reasons.append("missing_listing_url")
    if not title:
        reasons.append("missing_title")
    elif len(title) < 8:
        reasons.append("thin_title")
    if not desc:
        reasons.append("missing_description")
    elif len(desc) < 40:
        reasons.append("description_too_short")
    elif len(desc) < 160:
        warnings.append("thin_description")
    if price == 0:
        reasons.append("zero_price_invalid")
    elif price is None and price_status(row) not in {"on_request", "undefined"}:
        reasons.append("missing_price_without_status")
    elif isinstance(price, (int, float)) and price < 1000 and intent == "sale":
        warnings.append("low_sale_price")
    if area is None and category not in {"garage"}:
        reasons.append("missing_area")
    elif isinstance(area, (int, float)):
        if 0 < area < 2:
            reasons.append("suspicious_area_below_2sqm")
        if category in {"apartment", "office", "shop"} and area > 1000:
            reasons.append("suspicious_unit_area_too_large")
        if category == "house" and area > 5000:
            reasons.append("suspicious_house_area_too_large")
    if not (row.get("city") or row.get("address_text")):
        reasons.append("missing_city_or_address")
    if category in {"", "unknown", "missing"}:
        warnings.append("unknown_property_category")
    if intent in {"", "unknown", "mixed", "missing"}:
        warnings.append("unknown_or_mixed_intent")
    if remote <= 0:
        reasons.append("missing_remote_gallery")
    elif source_key in ACTION1_KEYS and remote == 1:
        reasons.append("one_remote_photo_gallery_suspect")
    if remote > 0 and local < remote:
        reasons.append("partial_local_gallery")
    if multi:
        warnings.append("multi_unit_or_development")
    if reasons:
        return "LOST", sorted(set(reasons)), sorted(set(warnings))
    if multi:
        return "GROUPED_PUBLICATION", [], sorted(set(warnings))
    return "SCRAPED_OK", [], sorted(set(warnings))


def inspect_source(source_dir: Path) -> dict[str, Any]:
    files = sorted((source_dir / "listings").glob("*.json"))
    summary: dict[str, Any] = {
        "source_key": source_dir.name,
        "rows": len(files),
        "bad_json": 0,
        "source_names": Counter(),
        "stored_status": Counter(),
        "stored_acceptance": Counter(),
        "stored_publication_type": Counter(),
        "estimated_quality": Counter(),
        "estimated_reasons": Counter(),
        "estimated_warnings": Counter(),
        "bucket_counts": Counter(),
        "intent_counts": Counter(),
        "category_counts": Counter(),
        "source_section_counts": Counter(),
        "bucket_quality": defaultdict(Counter),
        "bucket_reasons": defaultdict(Counter),
        "field_gaps": Counter(),
        "phone_total": 0,
        "phone_valid": 0,
        "phone_invalid": 0,
        "remote_photos": 0,
        "local_photos": 0,
        "full_gallery_flagged": 0,
        "rows_remote_no_local": 0,
        "rows_duplicate_remote_variants": 0,
        "local_paths_total": 0,
        "local_paths_existing": 0,
        "duplicate_listing_url_keys": 0,
        "duplicate_reference_id_keys": 0,
        "duplicate_external_id_keys": 0,
        "db_import_default_candidate_rows": 0,
        "pending_or_missing_qa_rows": 0,
        "examples": defaultdict(list),
    }
    urls: Counter[str] = Counter()
    refs: Counter[str] = Counter()
    external_ids: Counter[str] = Counter()
    for path in files:
        row = load_json(path)
        if row is None:
            summary["bad_json"] += 1
            continue
        stored_status = str(row.get("scrape_status") or "MISSING")
        acceptance = str(row.get("scrape_acceptance_status") or "MISSING")
        publication_type = str(row.get("source_publication_type") or "MISSING")
        estimated_status, reasons, warnings = classify_row(row, source_dir.name)
        title = str(row.get("title") or "").strip()
        desc = str(row.get("description") or "").strip()
        category = str(row.get("property_category") or "MISSING")
        intent = str(row.get("listing_intent") or "MISSING")
        remote = remote_urls(row)
        local = local_files(row)

        summary["source_names"][str(row.get("source_name") or "MISSING")] += 1
        summary["stored_status"][stored_status] += 1
        summary["stored_acceptance"][acceptance] += 1
        summary["stored_publication_type"][publication_type] += 1
        summary["estimated_quality"][estimated_status] += 1
        summary["bucket_counts"][str(row.get("bucket_key") or "MISSING")] += 1
        bucket = str(row.get("bucket_key") or "MISSING")
        summary["bucket_quality"][bucket][estimated_status] += 1
        summary["intent_counts"][intent] += 1
        summary["category_counts"][category] += 1
        summary["source_section_counts"][str(row.get("source_section_id") or "MISSING")] += 1
        for reason in reasons:
            summary["estimated_reasons"][reason] += 1
            summary["bucket_reasons"][bucket][reason] += 1
            if len(summary["examples"][reason]) < 3:
                summary["examples"][reason].append(
                    {
                        "path": str(path.relative_to(REPO)),
                        "reference_id": row.get("reference_id"),
                        "title": title,
                        "listing_url": row.get("listing_url"),
                    }
                )
        for warning in warnings:
            summary["estimated_warnings"][warning] += 1
        if stored_status in {"PENDING_QA", "MISSING", "UNKNOWN"}:
            summary["pending_or_missing_qa_rows"] += 1
        if (
            stored_status not in {"LOST", "PENDING_QA", "UNKNOWN", "MISSING"}
            and publication_type != "multi_unit_or_development"
            and acceptance != "not_single_entity"
            and row.get("suspected_multi_unit_publication") is not True
        ):
            summary["db_import_default_candidate_rows"] += 1
        if not title:
            summary["field_gaps"]["missing_title"] += 1
        elif len(title) < 8:
            summary["field_gaps"]["thin_title"] += 1
        if not desc:
            summary["field_gaps"]["missing_description"] += 1
        elif len(desc) < 160:
            summary["field_gaps"]["thin_description"] += 1
        if row.get("price") is None and price_status(row) not in {"on_request", "undefined"}:
            summary["field_gaps"]["missing_price_without_status"] += 1
        if row.get("price") == 0:
            summary["field_gaps"]["zero_price"] += 1
        if row.get("area_sqm") is None:
            summary["field_gaps"]["missing_area"] += 1
        if category.lower() in {"", "unknown", "missing"}:
            summary["field_gaps"]["unknown_property_category"] += 1
        if not (row.get("city") or row.get("address_text")):
            summary["field_gaps"]["missing_city_or_address"] += 1
        for phone in row.get("phones") or []:
            summary["phone_total"] += 1
            if is_valid_bg_phone(phone):
                summary["phone_valid"] += 1
            else:
                summary["phone_invalid"] += 1
        summary["remote_photos"] += len(remote)
        summary["local_photos"] += len(local)
        summary["full_gallery_flagged"] += 1 if row.get("full_gallery_downloaded") else 0
        if remote and not local:
            summary["rows_remote_no_local"] += 1
        if len({normalized_image_key(url) for url in remote}) < len(remote):
            summary["rows_duplicate_remote_variants"] += 1
        for rel in local:
            summary["local_paths_total"] += 1
            p = REPO / rel
            if p.exists() and p.stat().st_size > 0:
                summary["local_paths_existing"] += 1
        urls[str(row.get("listing_url") or "")] += 1
        refs[str(row.get("reference_id") or "")] += 1
        external_ids[str(row.get("external_id") or "")] += 1

    summary["duplicate_listing_url_keys"] = sum(1 for key, value in urls.items() if key and value > 1)
    summary["duplicate_reference_id_keys"] = sum(1 for key, value in refs.items() if key and value > 1)
    summary["duplicate_external_id_keys"] = sum(1 for key, value in external_ids.items() if key and value > 1)
    return normalize_counters(summary)


def normalize_counters(value: Any) -> Any:
    if isinstance(value, Counter):
        return dict(value.most_common())
    if isinstance(value, defaultdict):
        return {key: normalize_counters(val) for key, val in value.items()}
    if isinstance(value, dict):
        return {key: normalize_counters(val) for key, val in value.items()}
    if isinstance(value, list):
        return [normalize_counters(item) for item in value]
    return value


def class_fields(path: Path, class_name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                stmt.target.id
                for stmt in node.body
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
            }
    return set()


def sql_columns_for_table(sql: str, table: str) -> set[str]:
    match = re.search(
        rf"create table if not exists {re.escape(table)} \((.*?)\n\);",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )
    columns: set[str] = set()
    if match:
        for raw_line in match.group(1).splitlines():
            line = raw_line.strip().rstrip(",")
            if not line or line.lower().startswith(("constraint", "unique", "primary", "foreign")):
                continue
            col = line.split()[0].strip('"')
            columns.add(col)
    for alter in re.finditer(
        rf"alter table {re.escape(table)} add column if not exists ([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        flags=re.IGNORECASE,
    ):
        columns.add(alter.group(1))
    return columns


def schema_alignment() -> dict[str, Any]:
    sql = SQL_SCHEMA.read_text(encoding="utf-8")
    canonical_sql = sql_columns_for_table(sql, "canonical_listing")
    canonical_domain = class_fields(DOMAIN_MODELS, "CanonicalListing")
    canonical_db_model = class_fields(DB_MODELS, "CanonicalListingModel")
    first_class_needed = {
        "price_status",
        "source_publication_type",
        "scrape_status",
        "scrape_acceptance_status",
        "single_entity_candidate",
        "listing_status",
        "photo_count_remote",
        "photo_count_local",
        "full_gallery_downloaded",
        "local_image_storage_keys",
        "image_report_status",
        "image_description_coverage",
    }
    return {
        "canonical_sql_columns": sorted(canonical_sql),
        "canonical_domain_fields": sorted(canonical_domain),
        "canonical_db_model_fields": sorted(canonical_db_model),
        "domain_fields_missing_from_db_model": sorted(canonical_domain - canonical_db_model),
        "sql_columns_missing_from_db_model": sorted(canonical_sql - canonical_db_model),
        "db_model_fields_missing_from_sql": sorted(canonical_db_model - canonical_sql),
        "recommended_first_class_columns_absent_from_sql": sorted(first_class_needed - canonical_sql),
        "all_bulgaria_control_plane_conflict": {
            "fact": "source_section and crawl_run are constrained to region_key = 'varna', while current Action1 listing JSON uses all-Bulgaria bucket labels such as sale_all, sale_apartments, rent_personal, buy_commercial.",
            "risk": "If source_section_id is persisted into canonical_listing without an all-Bulgaria source_section row, the FK fails; if it is omitted, segment/bucket provenance is lost.",
        },
    }


def build_report(payload: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Scrape Database And Corpus Quality Audit",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Executive Findings",
        "",
        "- FACT: PostgreSQL was not available in this environment; this audit is file-backed plus static schema/model analysis.",
        f"- FACT: Current scraped JSON corpus contains `{payload['totals']['rows']}` rows across `{len(payload['sources'])}` source directories; Action1 seven-source rows total `{payload['totals']['action1_rows']}`.",
        f"- FACT: Stored QA state is stale/incomplete: `{payload['totals']['pending_or_missing_qa_rows']}` rows have `PENDING_QA`, missing, or unknown `scrape_status`.",
        f"- FACT: Offline Action1 QA estimate: `{payload['totals']['action1_estimated_ok']}` accepted single-unit candidates, `{payload['totals']['action1_estimated_lost']}` LOST rows, `{payload['totals']['action1_estimated_grouped']}` grouped/development publications.",
        "- INTERPRETATION: The corpus is large enough for product testing, but not safe for default canonical import until QA state, source-publication identity, contact normalization, and first-class DB fields are fixed.",
        "- GAP: Live URL existence, PostgreSQL row counts, and image semantic descriptions were not verified here.",
        "",
        "## Source Summary",
        "",
        "| Source key | Rows | Stored status top | Estimated OK | Estimated LOST | Estimated grouped | Pending/missing QA | Import candidates by current importer | Top reasons |",
        "|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for source in payload["sources"]:
        status_top = ", ".join(f"{k}:{v}" for k, v in list(source["stored_status"].items())[:3])
        reasons = ", ".join(f"{k}:{v}" for k, v in list(source["estimated_reasons"].items())[:5])
        estimated = source["estimated_quality"]
        lines.append(
            f"| `{source['source_key']}` | {source['rows']} | {status_top or 'none'} | "
            f"{estimated.get('SCRAPED_OK', 0)} | {estimated.get('LOST', 0)} | {estimated.get('GROUPED_PUBLICATION', 0)} | "
            f"{source['pending_or_missing_qa_rows']} | {source['db_import_default_candidate_rows']} | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Action1 Bucket Quality Matrix",
            "",
            "| Source key | Bucket | Estimated OK | Estimated LOST | Estimated grouped | Top bucket reasons |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for source in payload["sources"]:
        if source["source_key"] not in ACTION1_KEYS:
            continue
        for bucket in ("buy_personal", "buy_commercial", "rent_personal", "rent_commercial", "MISSING"):
            q = source.get("bucket_quality", {}).get(bucket)
            if not q:
                continue
            reasons = source.get("bucket_reasons", {}).get(bucket, {})
            reason_text = ", ".join(f"{k}:{v}" for k, v in list(reasons.items())[:4])
            lines.append(
                f"| `{source['source_key']}` | `{bucket}` | {q.get('SCRAPED_OK', 0)} | "
                f"{q.get('LOST', 0)} | {q.get('GROUPED_PUBLICATION', 0)} | {reason_text} |"
            )
    lines.extend(
        [
            "",
            "## Cross-Source Issues For Scraper Agent",
            "",
            "1. Re-run or apply the quality gate after every Action1 continuation before import/export. Current JSON has many `PENDING_QA` rows, so importer dry-run logic cannot distinguish accepted rows from unreviewed rows.",
            "2. Treat `source_publication_type` as mandatory. Grouped/development pages must remain source publications until unit-level URL, price/price-status, area, and media are present.",
            "3. Normalize and validate contacts. Phone extraction is polluted by dates, IDs, UI counters, and JavaScript numbers on several sources.",
            "4. Deduplicate remote gallery variants before comparing remote vs local counts; property-family sources often count `big`, `medium`, and `small1` versions of the same photo.",
            "5. Preserve image binaries as local files, but add semantic image-report coverage before using photo content for smart search.",
            "6. Capture bucket/segment provenance in a DB-safe way. Current `source_section_id` strings are useful in JSON but are not aligned with the Varna-only DB control plane.",
            "7. Do not import rows with `PENDING_QA`, missing `scrape_status`, `LOST`, grouped/development, or inactive markers by default.",
            "",
            "## Source Instructions",
            "",
        ]
    )
    instructions = {
        "address_bg": "Backfill full high-resolution gallery and fix missing city/address extraction. Many rows are one-photo suspects or have oversized unit/house areas.",
        "bulgarianproperties": "Prioritize local-gallery completeness and area semantics; development pages must be grouped unless unit-level evidence exists.",
        "homes_bg": "Expand beyond sale apartments, remove duplicate URL rows, use offer JSON/API for active status and all gallery images.",
        "imot_bg": "Keep as strongest corpus, but repair partial gallery, missing area, grouped development separation, and category precision.",
        "luximmo": "Fix missing area and oversized unit area; de-duplicate gallery size variants; keep development pages grouped.",
        "property_bg": "Stored QA is almost entirely pending even though offline estimate is strong; apply QA and reduce thin descriptions/low sale price warnings.",
        "suprimmo": "Fix missing area, low sale price warnings, grouped development classification, and gallery variant duplication.",
        "alo_bg": "Add formal QA fields and contact cleanup; current rows are small but unreviewed.",
        "bazar_bg": "Add bucket keys, QA fields, contact cleanup, and remote gallery de-duplication.",
        "domaza": "Resolve missing area and add QA status before any import.",
        "home2u": "Fix thin titles and missing areas; add QA status.",
        "olx_bg": "Add bucket keys, QA status, area extraction, location extraction, and contact cleanup.",
        "yavlena": "Do not import until description and zero-price issues are resolved; add QA status and price-status provenance.",
    }
    for source in payload["sources"]:
        lines.extend([f"### {source['source_key']}", "", instructions.get(source["source_key"], "Review parser and add QA status before import."), ""])
        lines.append(f"- FACT: rows={source['rows']}; estimated_quality={source['estimated_quality']}.")
        lines.append(f"- FACT: field_gaps={source['field_gaps']}.")
        lines.append(
            f"- FACT: phones total/valid/invalid={source['phone_total']}/{source['phone_valid']}/{source['phone_invalid']}; "
            f"remote/local photos={source['remote_photos']}/{source['local_photos']}."
        )
        if source["examples"]:
            first_reason, examples = next(iter(source["examples"].items()))
            lines.append(f"- Example `{first_reason}`: `{examples[0].get('reference_id')}` — {examples[0].get('title')}")
        lines.append("")
    schema = payload["schema_alignment"]
    lines.extend(
        [
            "## Database Structure Issues",
            "",
            "- FACT: `CanonicalListing` domain fields missing from `CanonicalListingModel`: "
            + ", ".join(f"`{x}`" for x in schema["domain_fields_missing_from_db_model"][:40]),
            "- FACT: Recommended first-class QA/media fields absent from SQL: "
            + ", ".join(f"`{x}`" for x in schema["recommended_first_class_columns_absent_from_sql"]),
            "- FACT: `source_section` / `crawl_run` are still constrained to `region_key = 'varna'`, while Action1 is all-Bulgaria.",
            "- INTERPRETATION: DB import can lose QA/media/segment evidence or fail when model/schema alignment is exercised with a real SQLAlchemy/PostgreSQL runtime.",
            "",
            "## Required Acceptance Gate",
            "",
            "- `python3 scripts/audit_scrape_database_quality.py` regenerates this report.",
            "- Action1 quality gate is run and applied or importer blocks unreviewed `PENDING_QA` rows.",
            "- Import dry-run works without requiring DB-only dependencies, or reports dependency failure as a blocker.",
            "- DB model, SQL schema, and import payload agree on canonical listing fields.",
            "- Scraper fixes are verified with fixture/parser regression tests and no live-network test dependencies.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    registry = load_json(REGISTRY_PATH) or {"sources": []}
    registry_names = {row["source_name"]: row for row in registry.get("sources", []) if isinstance(row, dict) and row.get("source_name")}
    sources = [inspect_source(path) for path in sorted(SCRAPED_ROOT.iterdir()) if (path / "listings").exists()]
    totals = {
        "rows": sum(source["rows"] for source in sources),
        "action1_rows": sum(source["rows"] for source in sources if source["source_key"] in ACTION1_KEYS),
        "pending_or_missing_qa_rows": sum(source["pending_or_missing_qa_rows"] for source in sources),
        "db_import_default_candidate_rows": sum(source["db_import_default_candidate_rows"] for source in sources),
        "action1_estimated_ok": sum(source["estimated_quality"].get("SCRAPED_OK", 0) for source in sources if source["source_key"] in ACTION1_KEYS),
        "action1_estimated_lost": sum(source["estimated_quality"].get("LOST", 0) for source in sources if source["source_key"] in ACTION1_KEYS),
        "action1_estimated_grouped": sum(source["estimated_quality"].get("GROUPED_PUBLICATION", 0) for source in sources if source["source_key"] in ACTION1_KEYS),
    }
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "registry_source_count": len(registry_names),
        "totals": totals,
        "sources": sources,
        "schema_alignment": schema_alignment(),
    }
    EXPORTS.mkdir(parents=True, exist_ok=True)
    json_path = EXPORTS / "scrape-database-quality-audit-2026-05-13.json"
    md_path = EXPORTS / "scrape-database-quality-audit-2026-05-13.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(build_report(payload), encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(
        f"rows={totals['rows']} action1={totals['action1_rows']} "
        f"pending_or_missing_qa={totals['pending_or_missing_qa_rows']} "
        f"action1_ok/lost/grouped={totals['action1_estimated_ok']}/{totals['action1_estimated_lost']}/{totals['action1_estimated_grouped']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
