#!/usr/bin/env python3
"""Generate reusable website-side inventory analysis for tier-1/2 sources."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
EXPORTS = REPO / "docs" / "exports"
SCRAPE_STATUS_PATH = EXPORTS / "scrape-status-dashboard.json"
SOURCE_ANALYSIS_PATH = EXPORTS / "tier12-source-analysis.json"

OUTPUT_JSON = EXPORTS / "website-inventory-analysis.json"
OUTPUT_MD = EXPORTS / "website-inventory-analysis.md"


MANUAL_EVIDENCE: dict[str, dict] = {
    "Address.bg": {
        "website_total": {
            "value": 18701,
            "kind": "exact",
            "basis": "live_embedded_json",
            "url": "https://address.bg/sale",
            "notes": "Computed as sale total 16935 plus rent total 1766 from live `offers-object` payloads.",
        },
        "inventory_rows": [
            {
                "service": "sale",
                "property": "all",
                "count": 16935,
                "kind": "exact",
                "basis": "live_embedded_json",
                "url": "https://address.bg/sale",
                "notes": "Page payload exposes `total=16935`.",
            },
            {
                "service": "long_term_rent",
                "property": "all",
                "count": 1766,
                "kind": "exact",
                "basis": "live_embedded_json",
                "url": "https://address.bg/rent",
                "notes": "Page payload exposes `total=1766`.",
            },
        ],
        "counting_method": "Read the live search page and extract `offers-object.total` from the embedded JSON payload.",
        "counting_gap": "Property-type split still needs category-specific entry pages or in-payload estate-type aggregation.",
    },
    "alo.bg": {
        "website_total": {
            "value": 75961,
            "kind": "lower_bound",
            "basis": "largest_live_category_count",
            "url": "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/",
            "notes": "Sale apartments alone already exceed the older source estimate, so current total must be at least this large.",
        },
        "inventory_rows": [
            {
                "service": "sale",
                "property": "apartment",
                "count": 75961,
                "kind": "exact",
                "basis": "live_meta_description",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/",
                "notes": "Meta description says `75961 обяви`.",
            },
            {
                "service": "sale",
                "property": "house",
                "count": 24695,
                "kind": "exact",
                "basis": "live_meta_description",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/",
                "notes": "Meta description says `24695 обяви`.",
            },
            {
                "service": "sale",
                "property": "land",
                "count": None,
                "kind": "unavailable",
                "basis": "configured_url_404",
                "url": "https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/",
                "notes": "Configured land URL returned 404 during this run and needs remapping.",
            },
            {
                "service": "long_term_rent",
                "property": "apartment",
                "count": None,
                "kind": "unavailable",
                "basis": "configured_url_404",
                "url": "https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/",
                "notes": "Configured rent URL returned 404 during this run and needs remapping.",
            },
        ],
        "counting_method": "Extract counts from the live category page meta description on mapped product pages.",
        "counting_gap": "Land and rent routes need refreshed discovery URLs before the source can have a trustworthy total.",
    },
    "Bazar.bg": {
        "website_total": {
            "value": 221272,
            "kind": "exact",
            "basis": "live_category_switcher",
            "url": "https://bazar.bg/obiavi/kashti-i-vili",
            "notes": "The page header exposes `Имоти 221 272 обяви`.",
        },
        "inventory_rows": [
            {
                "service": "all",
                "property": "all",
                "count": 221272,
                "kind": "exact",
                "basis": "live_category_switcher",
                "url": "https://bazar.bg/obiavi/kashti-i-vili",
                "notes": "Real-estate umbrella count exposed in the top category switcher.",
            },
            {
                "service": "sale",
                "property": "apartment",
                "count": None,
                "kind": "partial_visible_breakdown",
                "basis": "live_city_shortcuts",
                "url": "https://bazar.bg/obiavi/apartamenti",
                "notes": "Apartment page exposes visible city/subtype slices such as `2-стаен София 12 376` and `3-стаен София 13 540`, but not a single clean apartment total.",
            },
        ],
        "counting_method": "Read the visible category switcher for portal total, then mine shortcut blocks for subtype/city slices.",
        "counting_gap": "A clean apartment/house/land total still needs either a dedicated count endpoint or a DOM/XHR trace.",
    },
    "OLX.bg": {
        "website_total": {
            "value": 1000,
            "kind": "lower_bound",
            "basis": "live_listing_count_banner",
            "url": "https://www.olx.bg/nedvizhimi-imoti/",
            "notes": "The live banner says `повече от 1000 обяви`, so this is only a floor.",
        },
        "inventory_rows": [
            {
                "service": "all",
                "property": "all",
                "count": 1000,
                "kind": "lower_bound",
                "basis": "live_listing_count_banner",
                "url": "https://www.olx.bg/nedvizhimi-imoti/",
                "notes": "Banner text: `Открихме повече от 1000 обяви`.",
            },
        ],
        "counting_method": "Read the search results banner rendered on the listing page.",
        "counting_gap": "The page only exposes a lower bound; precise per-category totals require client-side API/XHR tracing.",
    },
    "property.bg": {
        "website_total": {
            "value": 4229,
            "kind": "lower_bound",
            "basis": "live_meta_description",
            "url": "https://www.property.bg/bulgaria/apartments/",
            "notes": "The apartments page meta description says `Over 4229 properties`; wording is category-oriented but still needs one confirmation pass.",
        },
        "inventory_rows": [
            {
                "service": "sale",
                "property": "apartment",
                "count": 4229,
                "kind": "lower_bound",
                "basis": "live_meta_description",
                "url": "https://www.property.bg/bulgaria/apartments/",
                "notes": "Meta description says `Over 4229 properties` on the apartments page.",
            },
        ],
        "counting_method": "Extract category counts from live page metadata.",
        "counting_gap": "Sale-selection and rent-selection pages still need their own counts to separate apartments from broader portal inventory.",
    },
    "SUPRIMMO": {
        "website_total": {
            "value": 4628,
            "kind": "lower_bound",
            "basis": "live_meta_description",
            "url": "https://www.suprimmo.bg/bulgaria/apartamenti/",
            "notes": "The apartments page meta description says `Over 4628 ...`, which is a category lower bound rather than a whole-site total.",
        },
        "inventory_rows": [
            {
                "service": "sale",
                "property": "apartment",
                "count": 4628,
                "kind": "lower_bound",
                "basis": "live_meta_description",
                "url": "https://www.suprimmo.bg/bulgaria/apartamenti/",
                "notes": "Meta description exposes `4628` as the visible apartment count floor.",
            },
        ],
        "counting_method": "Extract category counts from live page metadata on the canonical product page.",
        "counting_gap": "Houses, land, sale-selection, and rent-selection still need separate count captures.",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f}%"


def kind_label(kind: str) -> str:
    labels = {
        "exact": "Exact",
        "lower_bound": "Lower bound",
        "estimate": "Estimate",
        "unavailable": "Unavailable",
        "partial_visible_breakdown": "Partial visible breakdown",
    }
    return labels.get(kind, kind.replace("_", " ").title())


def build_inventory() -> dict:
    scrape_status = load_json(SCRAPE_STATUS_PATH)
    source_analysis = load_json(SOURCE_ANALYSIS_PATH)
    analysis_by_name = {row["source_name"]: row for row in source_analysis["sources"]}

    rows: list[dict] = []
    for status_row in scrape_status["sources"]:
        source_name = status_row["source_name"]
        analysis_row = analysis_by_name.get(source_name, {})
        manual = MANUAL_EVIDENCE.get(source_name, {})

        total_info = manual.get("website_total")
        if not total_info:
            estimate = analysis_row.get("estimated_total_listings")
            total_info = {
                "value": estimate,
                "kind": "estimate" if estimate else "unavailable",
                "basis": "analysis_estimate" if estimate else "unavailable",
                "url": status_row.get("primary_url") or "",
                "notes": "Fallback to the saved tier-1/2 source analysis estimate because no live category count was confirmed in this run."
                if estimate else
                "No trustworthy website-side total is saved yet.",
            }

        website_total = total_info.get("value")
        coverage_pct = None
        if website_total:
            coverage_pct = (status_row["saved_listings"] / website_total) * 100

        source_entry = {
            "tier": status_row["tier"],
            "source_name": source_name,
            "primary_url": status_row.get("primary_url", ""),
            "website_total": total_info,
            "saved_listings": status_row["saved_listings"],
            "coverage_pct": coverage_pct,
            "inventory_rows": manual.get("inventory_rows", []),
            "counting_method": manual.get(
                "counting_method",
                "Use the configured category entry pages first, then extract visible counts, embedded JSON totals, or traced XHR payloads.",
            ),
            "counting_gap": manual.get(
                "counting_gap",
                "Website-side category totals are not yet confirmed and still depend on a source-specific live counting pass.",
            ),
            "analysis_estimate": analysis_row.get("estimated_total_listings"),
            "best_extraction_method": analysis_row.get("best_extraction_method", ""),
            "state": status_row.get("state", ""),
            "next_step": status_row.get("next_step", ""),
        }

        if source_entry["analysis_estimate"] and website_total and source_entry["analysis_estimate"] < website_total:
            source_entry["estimate_conflict"] = (
                f"Saved analysis estimate {source_entry['analysis_estimate']} is below the confirmed/lower-bound live count {website_total}."
            )
        else:
            source_entry["estimate_conflict"] = ""

        rows.append(source_entry)

    totals = {
        "sources": len(rows),
        "with_live_total": sum(1 for row in rows if row["website_total"]["kind"] in {"exact", "lower_bound"}),
        "with_inventory_rows": sum(1 for row in rows if row["inventory_rows"]),
    }

    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "totals": totals,
        "sources": rows,
    }


def render_md(payload: dict) -> str:
    lines = [
        "# Website Inventory Analysis",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "This artifact separates website-side inventory evidence from landed scraper corpus counts.",
        "",
    ]

    for row in payload["sources"]:
        total = row["website_total"]
        lines.extend(
            [
                f"## {row['source_name']}",
                "",
                f"- Tier: `{row['tier']}`",
                f"- Website total: `{total.get('value')}` ({kind_label(total.get('kind', 'unavailable'))})",
                f"- Coverage vs landed corpus: `{row['saved_listings']}` saved / `{fmt_pct(row['coverage_pct'])}`",
                f"- Total basis: `{total.get('basis', '')}`",
                f"- Total notes: {total.get('notes', '')}",
                f"- Counting method: {row['counting_method']}",
                f"- Counting gap: {row['counting_gap']}",
            ]
        )
        if row.get("estimate_conflict"):
            lines.append(f"- Estimate conflict: {row['estimate_conflict']}")
        lines.append("")
        if row["inventory_rows"]:
            lines.extend(
                [
                    "| Service | Property | Count | Kind | Basis | URL | Notes |",
                    "| --- | --- | ---: | --- | --- | --- | --- |",
                ]
            )
            for item in row["inventory_rows"]:
                lines.append(
                    f"| {item['service']} | {item['property']} | {item['count'] if item['count'] is not None else 'n/a'} | "
                    f"{kind_label(item['kind'])} | {item['basis']} | {item['url']} | {item['notes']} |"
                )
            lines.append("")
        else:
            lines.append("No category-level website counts are saved yet for this source.")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = build_inventory()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
