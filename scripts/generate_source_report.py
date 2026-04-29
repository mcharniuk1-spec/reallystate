from __future__ import annotations

import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "source_registry.json"
EXPORT_DIR = ROOT / "docs" / "exports"


SOURCE_LINKS = {
    "Address.bg": ["https://address.bg/"],
    "alo.bg": ["https://www.alo.bg/"],
    "BulgarianProperties": ["https://www.bulgarianproperties.bg/", "https://www.bulgarianproperties.com/"],
    "Homes.bg": ["https://www.homes.bg/"],
    "imot.bg": ["https://www.imot.bg/"],
    "imoti.net": ["https://www.imoti.net/"],
    "LUXIMMO": ["https://www.luximmo.bg/"],
    "OLX.bg": ["https://www.olx.bg/", "https://developer.olx.bg/"],
    "property.bg": ["https://www.property.bg/"],
    "SUPRIMMO": ["https://www.suprimmo.bg/"],
    "ApartmentsBulgaria.com": ["https://www.apartmentsbulgaria.bg/"],
    "Bazar.bg": ["https://bazar.bg/"],
    "Domaza": ["https://www.domaza.bg/"],
    "Holding Group Real Estate": ["https://holdinggroup.bg/"],
    "Home2U": ["https://home2u.bg/"],
    "Imoteka.bg": ["https://imoteka.bg/"],
    "Imoti.info": ["https://imoti.info/"],
    "Indomio.bg": ["https://www.indomio.bg/"],
    "Lions Group": ["https://lionsgroup.bg/"],
    "Pochivka.bg": ["https://pochivka.bg/"],
    "realestates.bg": ["https://en.realestates.bg/"],
    "Realistimo": ["https://realistimo.com/"],
    "Rentica.bg": ["https://rentica.bg/"],
    "Svobodni-kvartiri.com": ["https://svobodni-kvartiri.com/"],
    "Unique Estates": ["https://ues.bg/"],
    "Vila.bg": ["https://vila.bg/"],
    "Yavlena": ["https://www.yavlena.com/"],
    "Airbnb": ["https://www.airbnb.com/"],
    "Airbtics": ["https://airbtics.com/"],
    "AirDNA": ["https://www.airdna.co/"],
    "BCPEA property auctions": ["https://sales.bcpea.org/properties"],
    "Booking.com": ["https://www.booking.com/"],
    "Flat Manager": ["https://flatmanager.bg/", "https://reserve.flatmanager.bg/"],
    "KAIS Cadastre": ["https://kais.cadastre.bg/bg/Map"],
    "Menada Bulgaria": ["https://menadabulgaria.com/"],
    "Property Register": ["https://portal.registryagency.bg/en/home-pr"],
    "Vrbo": ["https://www.vrbo.com/"],
    "Facebook public groups/pages": ["https://www.facebook.com/groups/438018083766467/"],
    "Instagram public profiles": [
        "https://www.instagram.com/bulgarianproperties.bg/",
        "https://www.instagram.com/bulgarianpropertiesagency/",
        "https://www.instagram.com/suprimmo.bg/",
        "https://www.instagram.com/suprimmo.varna/",
        "https://www.instagram.com/suprimmo.burgas/",
        "https://www.instagram.com/luximmo.bg/",
        "https://www.instagram.com/luximmo.burgas/",
        "https://www.instagram.com/rentica.bg/",
    ],
    "Telegram public channels": [
        "https://t.me/rentvarna",
        "https://t.me/varnarents",
        "https://t.me/real_estate_bg",
        "https://t.me/ads_in_bulgaria",
        "https://t.me/bgvarna_en",
        "https://t.me/kvartirivarna",
    ],
    "Threads public profiles": [],
    "Viber opt-in communities": [
        "https://invite.viber.com/?g2=AQA%2BxCYrr7Jy1VEh6Ic98YLAlDXOmJicE8MDwi%2F0NU%2FsFss%2FWRC%2B0lL9ufcuh96f",
        "https://invite.viber.com/?g2=AQAskgj%2FMFVozlMMEjg%2BuNw%2FEqgzSfOC5b8ZiLELo85k4haoyw9L%2B8j8wGKeBc0t",
        "https://invite.viber.com/?g2=AQBsW%2FKtZgB8VFEa8o8E52s45eL4D9wCwntSBjZysufmDhq3fLznCnlBiYx6vHYN&lang=en",
        "https://invite.viber.com/?g2=AQBqiGrgkj4dFFS6JHR01wsv8ntsQAaiglrdOkkM4MlwzwqoJZ%2FQ49cp0nvXLpUr&lang=bg",
    ],
    "WhatsApp opt-in groups": ["https://chat.whatsapp.com/HB3Kt48meI08eIaYSuJ1Go?mode=gi_t"],
    "X public search/accounts": ["https://x.com/super_imoti"],
}


DEBUG_ITEMS = [
    (
        "Development environment",
        "Local Python is 3.9.6 while the target stack says Python 3.12+.",
        "New language/library choices may fail locally or in Cursor agents.",
        "Create a pinned Python 3.12 toolchain through pyenv, uv, or Docker before backend expansion.",
        "postgres-postgis-schema / qa-review-release",
        "High",
    ),
    (
        "Document exports",
        "pandoc, Mermaid CLI, LibreOffice, python-docx, reportlab, openpyxl, pandas, and xlsxwriter are not installed.",
        "DOCX/PDF/XLSX workflows become less visual and harder to validate.",
        "Install export tooling or keep using the standard-library generator until the docs-export phase.",
        "docs-export",
        "Medium",
    ),
    (
        "Persistence",
        "The SQL file is a blueprint, not an Alembic migration set.",
        "Agents cannot safely evolve schema without migration history.",
        "Implement Alembic migrations and repository tests before live connectors.",
        "postgres-postgis-schema",
        "High",
    ),
    (
        "Crawler runtime",
        "There are no real Temporal workers, queues, rate-limit state, or crawl cursors yet.",
        "Source freshness and retries cannot be trusted in production.",
        "Implement SourceDiscoveryWorkflow, ListingDetailWorkflow, and durable crawl jobs.",
        "workflow-runtime",
        "High",
    ),
    (
        "Connectors",
        "No tier-1 source connector has offline fixtures or production parser coverage.",
        "The source matrix is useful, but ingestion is not market-complete yet.",
        "Start with Homes.bg fixture parser, then OLX API/alo.bg/imot.bg in gated slices.",
        "scraper-connector-builder / parser-fixture-qa",
        "High",
    ),
    (
        "Object storage",
        "raw_capture still includes body text for compatibility, despite the desired S3/MinIO raw store.",
        "Large captures and screenshots will bloat PostgreSQL.",
        "Make body optional or retention-limited when object storage is implemented.",
        "postgres-postgis-schema",
        "Medium",
    ),
    (
        "Frontend",
        "There is no Next.js web app yet.",
        "The product MVP pages are still only planned.",
        "Build /listings, /properties/[id], /map, /chat, /settings, and /admin after APIs exist.",
        "frontend-pages",
        "High",
    ),
    (
        "Compliance",
        "Source legal modes are in the registry, but not yet enforced by runtime middleware.",
        "A future connector could accidentally bypass source policy.",
        "Add a compliance gate before fetch, parse, publish, and channel onboarding.",
        "publishing-compliance / real-estate-source-registry",
        "High",
    ),
    (
        "MCP automation",
        ".cursor/mcp.json uses npx commands that need network and local Node availability.",
        "Cursor agents may fail if offline or if Node tooling is unavailable.",
        "Document prerequisites and allow agents to continue without MCP when unavailable.",
        "qa-review-release",
        "Medium",
    ),
]

FOUR_BUCKET_SOURCES = [
    "Address.bg",
    "BulgarianProperties",
    "Homes.bg",
    "imot.bg",
    "LUXIMMO",
    "property.bg",
    "SUPRIMMO",
]

FOUR_BUCKET_SEGMENTS = [
    ("buy_personal", "Buy residential"),
    ("buy_commercial", "Buy commercial"),
    ("rent_personal", "Rent residential"),
    ("rent_commercial", "Rent commercial"),
]


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _compact_counts(value: object) -> str:
    if not isinstance(value, dict):
        return ""
    return ", ".join(f"{key}:{count}" for key, count in sorted(value.items()))


def four_bucket_media_rows() -> list[list[str]]:
    data = _load_json(EXPORT_DIR / "source-item-photo-coverage.json")
    by_source = {row.get("source_name"): row for row in data.get("sources", [])}
    rows = [
        [
            "Source",
            "Items",
            "Descriptions",
            "Remote-photo items",
            "Local-photo items",
            "Full galleries",
            "Remote photos",
            "Local photos",
            "Services",
            "Categories",
        ]
    ]
    for name in FOUR_BUCKET_SOURCES:
        row = by_source.get(name, {})
        rows.append(
            [
                name,
                str(row.get("saved_listings", 0)),
                str(row.get("items_with_description", 0)),
                str(row.get("items_with_remote_photos", 0)),
                str(row.get("items_with_local_media", 0)),
                str(row.get("full_gallery_items", 0)),
                str(row.get("total_remote_photos", 0)),
                str(row.get("total_local_photos", 0)),
                _compact_counts(row.get("service_counts")),
                _compact_counts(row.get("category_counts")),
            ]
        )
    return rows


def four_bucket_pattern_rows() -> list[list[str]]:
    data = _load_json(ROOT / "data" / "scrape_patterns" / "regions" / "varna" / "sections.json")
    sections = data.get("sections", [])
    by_key = {(row.get("source_name"), row.get("segment_key")): row for row in sections}
    rows = [["Source", "Buy residential", "Buy commercial", "Rent residential", "Rent commercial"]]
    for source in FOUR_BUCKET_SOURCES:
        cells = [source]
        for segment_key, _label in FOUR_BUCKET_SEGMENTS:
            section = by_key.get((source, segment_key), {})
            patterns = section.get("patterns", {})
            detail = patterns.get("detail_page", {})
            media = patterns.get("media_gallery", {})
            status = "active" if section.get("active") else "inactive"
            detail_status = detail.get("status", "missing")
            media_status = media.get("status", "missing")
            entry_count = len(section.get("entry_urls") or [])
            cells.append(f"{status}; detail={detail_status}; media={media_status}; urls={entry_count}")
        rows.append(cells)
    return rows


def four_bucket_addendum_markdown() -> str:
    return f"""## 2026-04-28 Tier-1/2 Four-Bucket Scrape Addendum

This addendum is generated from `docs/exports/source-item-photo-coverage.json` and `data/scrape_patterns/regions/varna/sections.json`. It covers the current OpenClaw/Gemma4 handoff sources across the four product buckets from the operator screen: buy residential, buy commercial, rent residential, and rent commercial.

### Current Item And Photo Coverage

{md_table(four_bucket_media_rows())}

### Four-Bucket Pattern Readiness

{md_table(four_bucket_pattern_rows())}

### Agent Handoff Rules

1. Gemma4/OpenClaw must consume only local files listed in `local_image_files`.
2. Each property report must combine scraped page description, structured fields, source links, and ordered image descriptions.
3. Photo counts, price, size, city/address, and category must be checked before marking a listing complete.
4. Missing full-gallery status is a quality flag, not proof that the listing is unusable.
5. Live scraping remains operator-approved and must respect `legal_mode`, `risk_mode`, and `access_mode` from `data/source_registry.json`.
"""


def load_registry() -> list[dict]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for source in data["sources"]:
        links = SOURCE_LINKS.get(source["source_name"], [])
        source["primary_url"] = source.get("primary_url") or (links[0] if links else "")
        source["related_urls"] = source.get("related_urls") or links[1:]
    return data["sources"]


def write_registry_links(sources: list[dict]) -> None:
    data = {"sources": sources}
    REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_rows(sources: list[dict]) -> list[list[str]]:
    header = [
        "Source",
        "Tier",
        "Family",
        "Primary URL",
        "Related URLs",
        "Owner Group",
        "Access Mode",
        "Legal Mode",
        "Risk Mode",
        "Freshness",
        "Publish Capable",
        "Listing Types",
        "Best Extraction Method",
        "MVP Phase",
        "Notes",
    ]
    rows = [header]
    for source in sources:
        rows.append(
            [
                source["source_name"],
                str(source["tier"]),
                source["source_family"],
                source.get("primary_url", ""),
                "\n".join(source.get("related_urls", [])),
                source["owner_group"],
                source["access_mode"],
                source.get("legal_mode", ""),
                source["risk_mode"],
                source["freshness_target"],
                "yes" if source["publish_capable"] else "no",
                ", ".join(source.get("listing_types", [])),
                source.get("best_extraction_method", ""),
                source.get("mvp_phase", ""),
                source.get("notes", ""),
            ]
        )
    return rows


def summary_rows(sources: list[dict]) -> list[list[str]]:
    by_tier = {}
    by_risk = {}
    by_access = {}
    for source in sources:
        by_tier[source["tier"]] = by_tier.get(source["tier"], 0) + 1
        by_risk[source["risk_mode"]] = by_risk.get(source["risk_mode"], 0) + 1
        by_access[source["access_mode"]] = by_access.get(source["access_mode"], 0) + 1
    rows = [["Metric", "Value"]]
    rows.append(["Total sources", str(len(sources))])
    for tier in sorted(by_tier):
        rows.append([f"Tier {tier} sources", str(by_tier[tier])])
    for risk, count in sorted(by_risk.items()):
        rows.append([f"Risk: {risk}", str(count)])
    for access, count in sorted(by_access.items()):
        rows.append([f"Access: {access}", str(count)])
    rows.append(["Report generated at", datetime.now(timezone.utc).isoformat()])
    return rows


def debug_rows() -> list[list[str]]:
    return [["Area", "Inefficiency / Gap", "Why It Matters", "Recommended Fix", "Skill / Owner", "Priority"], *DEBUG_ITEMS]


def cell_ref(col: int, row: int) -> str:
    letters = ""
    while col:
        col, rem = divmod(col - 1, 26)
        letters = chr(65 + rem) + letters
    return f"{letters}{row}"


def sheet_xml(rows: list[list[str]]) -> str:
    rows_xml = []
    for r_idx, row in enumerate(rows, start=1):
        cells = []
        for c_idx, value in enumerate(row, start=1):
            style = ' s="1"' if r_idx == 1 else ""
            text = escape(str(value or ""))
            cells.append(f'<c r="{cell_ref(c_idx, r_idx)}" t="inlineStr"{style}><is><t>{text}</t></is></c>')
        rows_xml.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    cols_xml = "".join(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>' for i, width in enumerate([26, 8, 18, 42, 52, 28, 20, 26, 18, 18, 16, 34, 56, 32, 60], start=1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
  <cols>{cols_xml}</cols>
  <sheetData>{''.join(rows_xml)}</sheetData>
  <autoFilter ref="A1:{cell_ref(len(rows[0]), len(rows))}"/>
</worksheet>'''


def write_xlsx(path: Path, sheets: list[tuple[str, list[list[str]]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook_sheets = []
    rels = []
    overrides = []
    for idx, (name, _) in enumerate(sheets, start=1):
        workbook_sheets.append(f'<sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>')
        rels.append(f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>')
        overrides.append(f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    content_types = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {''.join(overrides)}
</Types>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs>
</styleSheet>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>''')
        zf.writestr("xl/workbook.xml", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{''.join(workbook_sheets)}</sheets></workbook>''')
        zf.writestr("xl/_rels/workbook.xml.rels", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{''.join(rels)}<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''')
        zf.writestr("xl/styles.xml", styles)
        zf.writestr("docProps/core.xml", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Bulgaria Real Estate Source Links</dc:title><dc:creator>Codex</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">{datetime.now(timezone.utc).isoformat()}</dcterms:created></cp:coreProperties>''')
        zf.writestr("docProps/app.xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Codex</Application></Properties>''')
        for idx, (_, rows) in enumerate(sheets, start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(rows))


def md_table(rows: list[list[str]], limit: Optional[int] = None) -> str:
    selected = rows if limit is None else rows[:limit]
    header = selected[0]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    for row in selected[1:]:
        safe = [str(cell).replace("\n", "<br>") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")
    return "\n".join(lines)


def write_markdown_report(path: Path, sources: list[dict]) -> str:
    rows = source_rows(sources)
    report = f"""# Bulgaria Real Estate Source Links And Debug Report

Generated: {datetime.now(timezone.utc).isoformat()}

## Executive Summary

The repository now has a source/link inventory for {len(sources)} Bulgarian real estate, short-term-rental, official-register, analytics, and social/messaging sources. The inventory is stored in `data/source_registry.json` and exported to `docs/exports/bulgaria-real-estate-source-links.xlsx`.

The platform should continue with a source-first implementation sequence: registry and legal gates, PostgreSQL/PostGIS persistence, fixture-backed tier-1 connectors, dedupe and geospatial matching, then map/listing/chat UI and reverse publishing.

## Deliverables

- `docs/exports/bulgaria-real-estate-source-links.xlsx`: workbook with source links, summary, and debug priorities.
- `docs/exports/bulgaria-real-estate-source-links.csv`: CSV copy of the main source/link table.
- `docs/exports/bulgaria-real-estate-source-report.md`: this structured report.
- `docs/exports/bulgaria-real-estate-source-report.docx`: Word-compatible report generated without external dependencies.

## Source Coverage Logic

Tier 1 is for the first ingestion wave: OLX via official API where possible, then crawl-friendly or high-value Bulgarian portals and agencies. Tier 2 is targeted expansion after parser gates. Tier 3 is partner/vendor/official-service first: Airbnb, Booking.com, Vrbo, AirDNA, Airbtics, official registers, cadastre, and auctions. Tier 4 is lead intelligence only: Telegram and public social overlays where appropriate, and consent-only Viber/WhatsApp/private-channel flows.

{four_bucket_addendum_markdown()}

## Source Link Table

{md_table(rows)}

## Debugging And Inefficiency Audit

{md_table(debug_rows())}

## Recommended Next Execution Order

1. Install or containerize Python 3.12+, PostgreSQL/PostGIS, Redis, MinIO, and Temporal.
2. Convert `sql/schema.sql` into Alembic migrations and repository tests.
3. Implement compliance gates for `legal_mode`, `access_mode`, and `risk_mode` before fetch/publish operations.
4. Build the first fixture-backed connector for `Homes.bg`.
5. Add OLX API integration only when credentials are configured; otherwise keep fixture-only parser work.
6. Implement media object-storage adapters before downloading real photo binaries at scale.
7. Build dedupe, geocoding, and building match review queues before public UI work.
8. Build `/listings` and `/properties/[id]` after search APIs exist, then `/map`, `/chat`, `/settings`, and `/admin`.
9. Keep Airbnb/Booking/Vrbo publishing on official partner/vendor paths only.

## Notes

The `.xlsx` and `.docx` were generated using standard-library Office Open XML packaging because spreadsheet/document libraries are not installed locally. Install `openpyxl`, `python-docx`, `pandoc`, Mermaid CLI, and LibreOffice for richer visual review in the docs-export phase.
"""
    path.write_text(report, encoding="utf-8")
    return report


def paragraph(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def docx_table(rows: list[list[str]], max_rows: Optional[int] = None) -> str:
    selected = rows if max_rows is None else rows[:max_rows]
    out = ["<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/><w:tblBorders><w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/><w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/><w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/></w:tblBorders></w:tblPr>"]
    for row in selected:
        out.append("<w:tr>")
        for cell in row:
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="2400" w:type="dxa"/></w:tcPr>{paragraph(str(cell).replace(chr(10), "; "))}</w:tc>')
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def write_docx(path: Path, sources: list[dict]) -> None:
    rows = source_rows(sources)
    body = [
        paragraph("Bulgaria Real Estate Source Links And Debug Report", "Title"),
        paragraph(f"Generated: {datetime.now(timezone.utc).isoformat()}"),
        paragraph("Executive Summary", "Heading1"),
        paragraph(f"The source inventory covers {len(sources)} Bulgarian real estate, short-term-rental, official-register, analytics, and social/messaging sources. It is designed as the handoff table for scraper, map, CRM, and reverse-publishing implementation."),
        paragraph("Source Coverage Logic", "Heading1"),
        paragraph("Tier 1 is for first ingestion. Tier 2 is for expansion after parser gates. Tier 3 is partner/vendor/official-service first. Tier 4 is lead intelligence only and must respect consent rules."),
        paragraph("2026-04-28 Tier-1/2 Four-Bucket Scrape Addendum", "Heading1"),
        paragraph("Generated from current scrape/photo coverage and Varna four-bucket pattern manifests for the OpenClaw/Gemma4 handoff."),
        paragraph("Current Item And Photo Coverage", "Heading1"),
        docx_table(four_bucket_media_rows(), max_rows=None),
        paragraph("Four-Bucket Pattern Readiness", "Heading1"),
        docx_table(four_bucket_pattern_rows(), max_rows=None),
        paragraph("Agent Handoff Rules", "Heading1"),
        paragraph("1. Gemma4/OpenClaw must consume only local files listed in local_image_files."),
        paragraph("2. Each property report must combine scraped page description, structured fields, source links, and ordered image descriptions."),
        paragraph("3. Photo counts, price, size, city/address, and category must be checked before marking a listing complete."),
        paragraph("4. Live scraping remains operator-approved and must respect legal_mode, risk_mode, and access_mode from data/source_registry.json."),
        paragraph("Main Source Link Table", "Heading1"),
        docx_table(rows, max_rows=None),
        paragraph("Debugging And Inefficiency Audit", "Heading1"),
        docx_table(debug_rows(), max_rows=None),
        paragraph("Next Execution Order", "Heading1"),
        paragraph("1. Containerize Python 3.12+, PostgreSQL/PostGIS, Redis, MinIO, and Temporal."),
        paragraph("2. Convert the SQL blueprint into Alembic migrations and repository tests."),
        paragraph("3. Enforce source legal gates before fetch and publish operations."),
        paragraph("4. Build the first offline fixture-backed Homes.bg connector."),
        paragraph("5. Build dedupe, geospatial, media, CRM, frontend, and publishing phases in the roadmap order."),
    ]
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>{''.join(body)}<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/></w:sectPr></w:body>
</w:document>'''
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:sz w:val="20"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>
</w:styles>'''
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>''')
        zf.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>''')
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", styles_xml)
        zf.writestr("docProps/core.xml", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Bulgaria Real Estate Source Report</dc:title><dc:creator>Codex</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">{datetime.now(timezone.utc).isoformat()}</dcterms:created></cp:coreProperties>''')
        zf.writestr("docProps/app.xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Codex</Application></Properties>''')


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_registry()
    write_registry_links(sources)
    rows = source_rows(sources)
    write_csv(EXPORT_DIR / "bulgaria-real-estate-source-links.csv", rows)
    write_xlsx(
        EXPORT_DIR / "bulgaria-real-estate-source-links.xlsx",
        [
            ("Sources", rows),
            ("Debug Priorities", debug_rows()),
            ("Summary", summary_rows(sources)),
        ],
    )
    write_markdown_report(EXPORT_DIR / "bulgaria-real-estate-source-report.md", sources)
    write_docx(EXPORT_DIR / "bulgaria-real-estate-source-report.docx", sources)
    print("generated source report exports")


if __name__ == "__main__":
    main()
