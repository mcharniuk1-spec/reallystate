#!/usr/bin/env python3
"""Generate a root-level HTML page with source links and scrape progress."""

from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO / "data" / "source_registry.json"
VARNA_SECTIONS_PATH = REPO / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json"
PATTERN_STATUS_PATH = REPO / "docs" / "exports" / "tier12-pattern-status.json"
SCRAPED_ROOT = REPO / "data" / "scraped"
OUTPUT_HTML = REPO / "source-links-tier1-4.html"

BUY_TYPES = {"sale", "new_build", "auction_sale"}
RENT_TYPES = {"long_term_rent", "short_term_rent"}
COMMERCIAL_CATEGORIES = {"office", "commercial", "shop", "industrial", "warehouse"}

SEGMENTS = [
    ("buy_personal", "Buy Residential"),
    ("buy_commercial", "Buy Commercial"),
    ("rent_personal", "Rent Residential"),
    ("rent_commercial", "Rent Commercial"),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry() -> list[dict[str, Any]]:
    payload = load_json(REGISTRY_PATH)
    return sorted(
        payload.get("sources", []),
        key=lambda row: (row.get("tier", 99), row.get("source_name", "").lower()),
    )


def load_section_links() -> dict[tuple[str, str], list[str]]:
    if not VARNA_SECTIONS_PATH.exists():
        return {}
    payload = load_json(VARNA_SECTIONS_PATH)
    mapping: dict[tuple[str, str], list[str]] = {}
    for section in payload.get("sections", []):
        mapping[(section["source_name"], section["segment_key"])] = list(section.get("entry_urls") or [])
    return mapping


def load_pattern_status() -> dict[str, dict[str, Any]]:
    if not PATTERN_STATUS_PATH.exists():
        return {}
    payload = load_json(PATTERN_STATUS_PATH)
    return {row["source_name"]: row for row in payload.get("sources", [])}


def source_dir_name(source_name: str) -> str:
    return source_name.lower().replace(".", "").replace(" ", "").replace("-", "").replace("/", "")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def is_commercial(category: str | None) -> bool:
    return normalize_text(category) in COMMERCIAL_CATEGORIES


def classify_segment(listing: dict[str, Any]) -> str | None:
    intent = normalize_text(listing.get("listing_intent"))
    category = normalize_text(listing.get("property_category"))
    if intent in BUY_TYPES:
        return "buy_commercial" if is_commercial(category) else "buy_personal"
    if intent in RENT_TYPES:
        return "rent_commercial" if is_commercial(category) else "rent_personal"
    return None


def supports_buy(row: dict[str, Any]) -> bool:
    listing_types = set(row.get("listing_types") or [])
    return bool(listing_types & BUY_TYPES)


def supports_rent(row: dict[str, Any]) -> bool:
    listing_types = set(row.get("listing_types") or [])
    return bool(listing_types & RENT_TYPES)


def is_supported(row: dict[str, Any], segment_key: str) -> bool:
    if segment_key.startswith("buy_"):
        return supports_buy(row)
    return supports_rent(row)


def fallback_link(row: dict[str, Any]) -> str:
    primary = (row.get("primary_url") or "").strip()
    if primary:
        return primary
    for candidate in row.get("related_urls") or []:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def cell_links(
    source_name: str,
    segment_key: str,
    row: dict[str, Any],
    section_links: dict[tuple[str, str], list[str]],
) -> list[str]:
    urls = list(section_links.get((source_name, segment_key)) or [])
    if urls:
        return urls
    if is_supported(row, segment_key):
        fallback = fallback_link(row)
        return [fallback] if fallback else []
    return []


def collect_listing_metrics() -> dict[str, dict[str, dict[str, Any]]]:
    metrics: dict[str, dict[str, dict[str, Any]]] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "items": 0,
                "with_description": 0,
                "remote_photos": 0,
                "local_photos": 0,
                "full_gallery_items": 0,
                "described_images": 0,
            }
        )
    )
    if not SCRAPED_ROOT.exists():
        return metrics

    for source_dir in SCRAPED_ROOT.iterdir():
        listings_dir = source_dir / "listings"
        if not listings_dir.exists():
            continue
        for listing_path in listings_dir.glob("*.json"):
            try:
                listing = load_json(listing_path)
            except Exception:
                continue
            source_name = listing.get("source_name") or source_dir.name
            segment_key = classify_segment(listing)
            if not segment_key:
                continue
            bucket = metrics[source_name][segment_key]
            bucket["items"] += 1
            if (listing.get("description") or "").strip():
                bucket["with_description"] += 1
            remote_photos = len(listing.get("image_urls") or [])
            local_photos = len(listing.get("local_image_files") or [])
            bucket["remote_photos"] += remote_photos
            bucket["local_photos"] += local_photos
            if local_photos and local_photos >= remote_photos:
                bucket["full_gallery_items"] += 1
    return metrics


def coverage_class(
    pattern_row: dict[str, Any] | None,
    items: int,
    supported: bool,
    source_total: int | None,
) -> str:
    if not supported:
        return "unsupported"
    if source_total and source_total > 0:
        ratio = items / source_total
        if ratio >= 0.8:
            return "done" if pattern_row and pattern_row.get("pattern_status") == "Patterned" else "strong"
        if ratio >= 0.3:
            return "strong"
        if ratio > 0:
            return "partial"
        return "empty"
    if items >= 100:
        return "done" if pattern_row and pattern_row.get("pattern_status") == "Patterned" else "strong"
    if items > 0:
        return "partial"
    return "empty"


def source_total_value(pattern_row: dict[str, Any] | None) -> int | None:
    if not pattern_row:
        return None
    total = ((pattern_row.get("website_total_active") or {}).get("value"))
    return total if isinstance(total, int) and total > 0 else None


def metric_lines(bucket: dict[str, Any] | None, source_total: int | None) -> tuple[str, str, str, str, str]:
    if not bucket or not bucket["items"]:
        source_total_text = str(source_total) if source_total else "unknown"
        return (
            f"scraped 0/{source_total_text} site",
            "full 0/0 items",
            "desc 0/0 items",
            "images 0/0 local/remote",
            "img described 0/0",
        )
    items = bucket["items"]
    desc = bucket["with_description"]
    avg_local = bucket["local_photos"] / items if items else 0.0
    gallery = bucket["full_gallery_items"]
    source_total_text = str(source_total) if source_total else "unknown"
    return (
        f"scraped {items}/{source_total_text} site",
        f"full {gallery}/{items} items",
        f"desc {desc}/{items} items",
        f"images {bucket['local_photos']}/{bucket['remote_photos']} local/remote ({avg_local:.1f}/item)",
        f"img described {bucket['described_images']}/{bucket['local_photos']}",
    )


def render_cell(
    urls: list[str],
    bucket: dict[str, Any] | None,
    pattern_row: dict[str, Any] | None,
    supported: bool,
) -> str:
    source_total = source_total_value(pattern_row)
    state = coverage_class(pattern_row, bucket["items"] if bucket else 0, supported, source_total)
    if not supported:
        return '<td class="segment-cell unsupported"><div class="status-line">unsupported</div></td>'

    start_line, full_line, desc_line, image_line, image_desc_line = metric_lines(bucket, source_total)
    links_html = "".join(
        f'<a href="{html.escape(url)}" target="_blank" rel="noreferrer">{html.escape(url)}</a>'
        for url in urls
    )
    pattern_text = pattern_row.get("pattern_status", "n/a") if pattern_row else "n/a"
    issue_text = pattern_row.get("pattern_issue", "") if pattern_row else ""
    meta_html = (
        f'<div class="status-pill">{html.escape(pattern_text)}</div>'
        f'<div class="metric-line"><strong>{html.escape(start_line)}</strong></div>'
        f'<div class="metric-line">{html.escape(full_line)}</div>'
        f'<div class="metric-line">{html.escape(desc_line)}</div>'
        f'<div class="metric-line">{html.escape(image_line)}</div>'
        f'<div class="metric-line">{html.escape(image_desc_line)}</div>'
    )
    if issue_text and pattern_text != "Patterned":
        meta_html += f'<div class="issue-line">{html.escape(issue_text)}</div>'
    if not links_html:
        meta_html += '<div class="empty-link">No saved route</div>'
    return f'<td class="segment-cell {state}">{meta_html}{links_html}</td>'


def render_html(
    rows: list[dict[str, Any]],
    section_links: dict[tuple[str, str], list[str]],
    pattern_status: dict[str, dict[str, Any]],
    listing_metrics: dict[str, dict[str, dict[str, Any]]],
) -> str:
    body: list[str] = []
    for row in rows:
        source_name = row.get("source_name", "")
        pattern_row = pattern_status.get(source_name)
        cells: list[str] = []
        for segment_key, _ in SEGMENTS:
            urls = cell_links(source_name, segment_key, row, section_links)
            bucket = listing_metrics.get(source_name, {}).get(segment_key)
            cells.append(render_cell(urls, bucket, pattern_row, is_supported(row, segment_key)))
        source_badge = row.get("source_type", "source")
        body.append(
            "<tr>"
            f"<td>{row.get('tier', '')}</td>"
            f"<td><div class='platform-name'>{html.escape(source_name)}</div><div class='platform-meta'>{html.escape(source_badge)}</div></td>"
            + "".join(cells)
            + "</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Real Estate Source Links</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f4ee;
      color: #1f2937;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
    }}
    p {{
      margin: 0 0 18px;
      color: #5b6472;
      max-width: 1100px;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 0 0 18px;
    }}
    .legend span {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #475569;
    }}
    .legend i {{
      width: 14px;
      height: 14px;
      display: inline-block;
      border-radius: 4px;
      border: 1px solid rgba(15, 23, 42, 0.1);
    }}
    .table-wrap {{
      overflow: auto;
      background: #fffdf8;
      border: 1px solid #d8cfbf;
      border-radius: 14px;
      box-shadow: 0 8px 24px rgba(30, 41, 59, 0.05);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1500px;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid #ece4d6;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #fbf7ef;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: #6b7280;
    }}
    td:first-child, th:first-child {{
      width: 60px;
    }}
    td:nth-child(2), th:nth-child(2) {{
      min-width: 220px;
    }}
    .platform-name {{
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .platform-meta {{
      font-size: 12px;
      color: #6b7280;
    }}
    .segment-cell {{
      min-width: 250px;
    }}
    .segment-cell.done {{
      background: #dcfce7;
    }}
    .segment-cell.strong {{
      background: #e0f2fe;
    }}
    .segment-cell.partial {{
      background: #fef3c7;
    }}
    .segment-cell.empty {{
      background: #fee2e2;
    }}
    .segment-cell.unsupported {{
      background: #f1f5f9;
      color: #94a3b8;
    }}
    .status-pill {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      background: rgba(255,255,255,0.75);
      margin-bottom: 8px;
    }}
    .status-line, .metric-line, .issue-line, .empty-link {{
      font-size: 12px;
      line-height: 1.45;
      margin-bottom: 4px;
    }}
    .issue-line {{
      color: #7c2d12;
    }}
    .empty-link {{
      color: #64748b;
    }}
    a {{
      display: block;
      color: #145a74;
      text-decoration: none;
      margin-top: 6px;
      word-break: break-word;
      font-size: 12px;
    }}
    a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <h1>Real Estate Source Links</h1>
  <p>Platforms from tiers 1-4 with direct website links grouped by buy/rent and residential/commercial buckets. Each colored cell shows saved scrape coverage against the latest saved website total for that source, plus per-item completeness and image-capture counts for that bucket.</p>
  <div class="legend">
    <span><i style="background:#dcfce7"></i> High website coverage and patterned source</span>
    <span><i style="background:#e0f2fe"></i> Medium website coverage or strong saved corpus</span>
    <span><i style="background:#fef3c7"></i> Some saved items, partial coverage</span>
    <span><i style="background:#fee2e2"></i> No saved items yet</span>
    <span><i style="background:#f1f5f9"></i> Unsupported bucket</span>
  </div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Tier</th>
          <th>Platform</th>
          <th>Buy Residential</th>
          <th>Buy Commercial</th>
          <th>Rent Residential</th>
          <th>Rent Commercial</th>
        </tr>
      </thead>
      <tbody>
        {''.join(body)}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


def main() -> None:
    rows = load_registry()
    section_links = load_section_links()
    pattern_status = load_pattern_status()
    listing_metrics = collect_listing_metrics()
    OUTPUT_HTML.write_text(
        render_html(rows, section_links, pattern_status, listing_metrics),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
