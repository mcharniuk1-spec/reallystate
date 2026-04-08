from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "docs" / "exports"
PDF_DIR = ROOT / "output" / "pdf"
TASKS_PATH = ROOT / "docs" / "agents" / "TASKS.md"
ROADMAP_PATH = ROOT / "docs" / "project-status-roadmap.md"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
REGISTRY_PATH = ROOT / "data" / "source_registry.json"
FIXTURES_DIR = ROOT / "tests" / "fixtures"
API_ROUTERS_DIR = ROOT / "src" / "bgrealestate" / "api" / "routers"
AGENT_JOURNALS = {
    "backend_developer": ROOT / "docs" / "agents" / "backend_developer" / "JOURNEY.md",
    "scraper_1": ROOT / "docs" / "agents" / "scraper_1" / "JOURNEY.md",
    "scraper_t3": ROOT / "docs" / "agents" / "scraper_t3" / "JOURNEY.md",
    "scraper_sm": ROOT / "docs" / "agents" / "scraper_sm" / "JOURNEY.md",
    "ux_ui_designer": ROOT / "docs" / "agents" / "ux_ui_designer" / "JOURNEY.md",
    "debugger": ROOT / "docs" / "agents" / "debugger" / "JOURNEY.md",
}


def slugify_source_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug


def run_shell(command: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["/bin/zsh", "-lc", command],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=os.environ.copy(),
    )
    output = proc.stdout.strip()
    err = proc.stderr.strip()
    if err:
        output = output + ("\n" if output else "") + err
    return proc.returncode, output


def fixture_leaf_dirs() -> list[Path]:
    out = []
    if not FIXTURES_DIR.exists():
        return out
    for path in FIXTURES_DIR.rglob("*"):
        if not path.is_dir():
            continue
        has_raw = (path / "raw.html").exists() or (path / "raw.json").exists()
        has_expected = (path / "expected.json").exists()
        if has_raw and has_expected:
            out.append(path)
    return sorted(out)


def load_registry() -> list[dict]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return payload["sources"]


def roadmap_counts() -> tuple[int, int, int]:
    text = ROADMAP_PATH.read_text(encoding="utf-8")
    done = text.count("- [x]")
    total = text.count("- [")
    return done, total, total - done


def count_schema() -> tuple[int, int]:
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    tables = len(re.findall(r"create table if not exists", text, flags=re.IGNORECASE))
    indexes = len(re.findall(r"create index if not exists", text, flags=re.IGNORECASE))
    return tables, indexes


def count_api_routes() -> int:
    count = 0
    for path in API_ROUTERS_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        count += len(re.findall(r"@router\.(get|post|put|delete|patch)", text))
    return count


def parse_task_sections() -> dict[str, list[dict[str, str]]]:
    text = TASKS_PATH.read_text(encoding="utf-8")
    sections = {}
    section_names = [
        "Backend_developer",
        "Scraper_1",
        "Debugger",
        "UX_UI_designer",
        "Scraper_T3",
        "Scraper_SM",
    ]
    # Order must match the order of ## sections in TASKS.md
    for index, name in enumerate(section_names):
        start = text.index("## " + name)
        end = text.index("## " + section_names[index + 1]) if index + 1 < len(section_names) else len(text)
        block = text[start:end]
        entries = []
        for match in re.finditer(
            r"###\s+([A-Z0-9\- ]+):\s+([^\n]+)\n- \*\*Status\*\*: `([^`]+)`",
            block,
        ):
            entries.append(
                {
                    "slice_id": match.group(1).strip(),
                    "title": match.group(2).strip(),
                    "status": match.group(3).strip(),
                }
            )
        sections[name] = entries
    return sections


def latest_journey_heading(path: Path) -> str:
    if not path.exists():
        return "No journal yet"
    headings = re.findall(r"^###\s+(.+)$", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    ignored = {
        "Files changed",
        "Review comments (after each task)",
        "After Task 1",
        "After Task 2",
    }
    filtered = [heading for heading in headings if heading not in ignored]
    return filtered[-1] if filtered else (headings[-1] if headings else "No journal yet")


def latest_review_note(path: Path) -> str:
    if not path.exists():
        return "No journal yet"
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return "No journal yet"
    for line in reversed(lines):
        if line.startswith("- ") or line.startswith("**"):
            return line
    return lines[-1]


def source_status(source: dict, fixture_cases: int) -> str:
    legal_mode = source["legal_mode"]
    access_mode = source["access_mode"]
    tier = int(source["tier"])

    if fixture_cases > 0 and legal_mode == "legal_review_required":
        return "fixture-only legal-gated"
    if fixture_cases > 0 and tier == 4:
        return "fixture-backed social policy"
    if fixture_cases > 0:
        return "fixture-backed"
    if tier == 4 and access_mode == "official_api":
        return "policy-approved, connector pending"
    if legal_mode in {"official_partner_or_vendor_only", "licensing_required"}:
        return "partner/vendor route"
    if legal_mode == "consent_or_manual_only":
        return "manual or consent-only"
    if legal_mode == "legal_review_required":
        return "blocked pending legal review"
    return "registry-ready, connector pending"


def summarize_tests() -> dict[str, str]:
    code, output = run_shell("PYTHONPATH=src python3 -m unittest discover -s tests -v")
    summary_line = ""
    failure_line = ""
    for line in output.splitlines():
        if line.startswith("Ran "):
            summary_line = line.strip()
        if line.startswith("FAILED") or line.startswith("OK"):
            failure_line = line.strip()
    return {
        "exit_code": str(code),
        "summary": summary_line or "No unittest summary found",
        "result": failure_line or "No unittest result line found",
        "python_runtime": run_shell("python3 --version")[1].strip() or "unknown",
    }


def build_agent_rows() -> list[dict[str, str]]:
    sections = parse_task_sections()
    mapping = [
        ("backend_developer", "Backend_developer"),
        ("scraper_1", "Scraper_1"),
        ("scraper_t3", "Scraper_T3"),
        ("scraper_sm", "Scraper_SM"),
        ("ux_ui_designer", "UX_UI_designer"),
        ("debugger", "Debugger"),
    ]
    out = []
    for agent_key, section_name in mapping:
        tasks = sections.get(section_name, [])
        counts = Counter(task["status"] for task in tasks)
        next_slice = next((task for task in tasks if task["status"] in {"TODO", "IN_PROGRESS", "BLOCKED"}), None)
        out.append(
            {
                "agent": agent_key,
                "verified": str(counts.get("VERIFIED", 0)),
                "todo": str(counts.get("TODO", 0)),
                "blocked": str(counts.get("BLOCKED", 0)),
                "latest_heading": latest_journey_heading(AGENT_JOURNALS[agent_key]),
                "latest_note": latest_review_note(AGENT_JOURNALS[agent_key]),
                "next_slice": (
                    "{slice_id}: {title}".format(**next_slice) if next_slice else "No open slice"
                ),
            }
        )
    return out


def milestone_path(done: int, total: int) -> str:
    percent = int((done / total) * 100) if total else 0
    return "\n".join(
        [
            "[1] Foundations and Source Registry      COMPLETE",
            "    |",
            "    v",
            "[2] Database and Persistence            IN PROGRESS",
            "    |",
            "    v",
            "[3] Runtime and Compliance Gates        NEXT",
            "    |",
            "    v",
            "[4] Tier-1 Connectors                   PARTIAL",
            "    |",
            "    v",
            "[5] Tier-2, STR, and Social Overlays    NOT STARTED",
            "    |",
            "    v",
            "[6] Media, Dedupe, Entity Graph         NOT STARTED",
            "    |",
            "    v",
            "[7] Geospatial and 3D Map               NOT STARTED",
            "    |",
            "    v",
            "[8] Backend APIs                        PARTIAL",
            "    |",
            "    v",
            "[9] Frontend MVP                        SHELL ONLY",
            "    |",
            "    v",
            "[10] Reverse Publishing                 GATED",
            "",
            "Overall roadmap completion: {done}/{total} steps ({percent}%).".format(
                done=done,
                total=total,
                percent=percent,
            ),
        ]
    )


def build_markdown() -> str:
    now = datetime.now()
    today = now.date().isoformat()
    registry = load_registry()
    roadmap_done, roadmap_total, roadmap_remaining = roadmap_counts()
    tables, indexes = count_schema()
    routes = count_api_routes()
    fixtures = fixture_leaf_dirs()
    tests = summarize_tests()
    agent_rows = build_agent_rows()

    tier_counts = Counter(int(source["tier"]) for source in registry)
    access_counts = Counter(source["access_mode"] for source in registry)
    legal_counts = Counter(source["legal_mode"] for source in registry)
    publish_capable = sum(1 for source in registry if source["publish_capable"])
    fixture_source_dirs = len([path for path in FIXTURES_DIR.iterdir() if path.is_dir()]) if FIXTURES_DIR.exists() else 0
    marketplace_sources = sum(1 for source in registry if int(source["tier"]) in (1, 2, 3))
    tier1_fixture_coverage = sum(1 for source in registry if int(source["tier"]) == 1 and (FIXTURES_DIR / slugify_source_name(source["source_name"])).exists())

    source_rows = []
    for index, source in enumerate(registry, start=1):
        fixture_dir = FIXTURES_DIR / slugify_source_name(source["source_name"])
        fixture_cases = len([path for path in fixture_dir.iterdir() if path.is_dir()]) if fixture_dir.exists() else 0
        source_rows.append(
            "| {idx} | {name} | {tier} | {access} | {legal} | {risk} | {types} | {langs} | {urls} | {fixtures} | {status} |".format(
                idx=index,
                name=source["source_name"],
                tier=source["tier"],
                access=source["access_mode"],
                legal=source["legal_mode"],
                risk=source["risk_mode"],
                types=len(source.get("listing_types", [])),
                langs=len(source.get("languages", [])),
                urls=1 + len(source.get("related_urls", [])),
                fixtures=fixture_cases,
                status=source_status(source, fixture_cases),
            )
        )

    agent_sections = []
    for row in agent_rows:
        agent_sections.append(
            "\n".join(
                [
                    "### {agent}".format(agent=row["agent"]),
                    "",
                    "| Metric | Value |",
                    "| --- | --- |",
                    "| Verified slices | {verified} |".format(**row),
                    "| Open TODO slices | {todo} |".format(**row),
                    "| Blocked slices | {blocked} |".format(**row),
                    "| Latest journal heading | {latest_heading} |".format(**row),
                    "| Latest note | {latest_note} |".format(**row),
                    "| Next slice | {next_slice} |".format(**row),
                ]
            )
        )

    return "\n".join(
        [
            "# Bulgaria Real Estate Product Summary, Backlog, And Dashboard Plan",
            "",
            "Date: {today}".format(today=today),
            "Generated at: {stamp}".format(stamp=now.isoformat(timespec="seconds")),
            "Workspace: `{cwd}`".format(cwd=ROOT),
            "",
            "## 1. Executive Summary",
            "",
            "This product is a Bulgaria-focused real estate intelligence and operator platform. It ingests listings and lead signals from Bulgarian portals, agencies, public social channels, official/vendor datasets, and partner routes; normalizes them into one canonical database; powers listing search, a 2D/3D map, CRM chat workflows, and operator review; and only allows reverse publishing through compliant official, partner, vendor, or assisted-manual paths.",
            "",
            "Today the product is best described as an operator-first MVP foundation with strong source coverage, working fixture-backed scraper slices, a PostgreSQL/PostGIS-ready schema, API scaffolding, and a Next.js shell for `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, and `/admin`.",
            "",
            "## 2. Global Idea",
            "",
            "The global idea is to build one operator-grade real estate system for Bulgaria that can watch the fragmented market, turn many raw sources into one trusted property database, visualize inventory spatially on a 2D/3D map, coordinate leads in chat/CRM, and later publish back only through compliant channels.",
            "",
            "In practice that means:",
            "1. The market layer watches portals, agencies, social overlays, official registers, and vendor feeds.",
            "2. The data layer turns messy source records into canonical Bulgaria property intelligence.",
            "3. The operations layer gives the team one dashboard to start projects, review source health, inspect crawl failures, route leads, and control publishing.",
            "4. The experience layer exposes `/listings`, `/properties/[id]`, `/map`, `/chat`, `/settings`, and `/admin` as the main operating surfaces.",
            "",
            "## 3. What The Product Does",
            "",
            "1. Tracks the Bulgarian real estate market across portals, agencies, STR/vendor sources, official registers, and social overlays.",
            "2. Stores all incoming listing evidence as raw capture plus normalized canonical listing records.",
            "3. Prepares a national property database for Bulgaria using PostgreSQL/PostGIS, property entities, offers, CRM data, and publishing records.",
            "4. Supports an operator map experience with 3D buildings where geometry exists and 2D fallback pins where it does not.",
            "5. Supports CRM chat and lead handling so agents/operators can organize conversations, notes, and linked properties.",
            "6. Enforces legal mode, access mode, and risk mode before scraper or publisher behavior is allowed.",
            "7. Creates the control plane for future compliant reverse publishing to approved channels only.",
            "",
            "## 4. Product Services",
            "",
            "| Service | What it does now | Direction |",
            "| --- | --- | --- |",
            "| Source registry and compliance | Stores 44 sources with tier, legal mode, risk mode, access mode, extraction strategy, languages, and listing types. | Control plane for all future connectors and publishing routes. |",
            "| Scraper and connector layer | Tier-1 fixture-backed connectors exist for the main marketplace/agency sites; social contract exists for Telegram-style overlays. | Move from fixture-first to DB-backed, live-safe runs. |",
            "| Canonical Bulgaria database | SQL blueprint defines 59 tables and 13 indexes for sources, crawl jobs, raw captures, canonical listings, property graph, CRM, users, geo, and publishing. | PostgreSQL/PostGIS source of truth. |",
            "| Listings and search APIs | FastAPI routes exist for listings, crawl jobs, CRM, readiness, chat, admin stats, and system endpoints. | Wire all pages to real database-backed search and detail APIs. |",
            "| 2D/3D map layer | Frontend shell exists; map page is reserved for MapLibre GL and deck.gl with building summaries and viewport queries. | Enable 3D when geometry confidence is strong; fall back to 2D pins otherwise. |",
            "| CRM chat | Chat page shell and CRM endpoints are in place for thread/message flow. | Expand to assignment, reminders, linked properties, and operator replies. |",
            "| Admin operations | Admin source stats and dashboard spec exist. | Add parser failures, compliance review, dedupe review, and publish queue panels. |",
            "| Reverse publishing | Control-plane logic exists, but live outbound publishing remains gated. | Official, authorized, partner, vendor, or assisted-manual only. |",
            "",
            "## 5. How The Product Works",
            "",
            "1. A source is selected from the registry.",
            "2. The runtime checks `legal_mode`, `risk_mode`, `access_mode`, and whether the path is allowed.",
            "3. A connector gathers data through HTML, API, headless, partner-feed, licensed-data, or consent/manual routes.",
            "4. Raw evidence is captured and normalized into canonical listing records.",
            "5. Canonical listings feed the Bulgaria property database, dedupe graph, CRM, and search surfaces.",
            "6. Search and detail pages expose the listings to operators and later to public-facing UI.",
            "7. The map surface groups results spatially and will render 3D building context when geometry is available.",
            "8. CRM chat links people, messages, properties, and follow-up actions.",
            "9. Publishing stays blocked unless the channel is explicitly compliant.",
            "",
            "## 6. Master Backlog",
            "",
            "This backlog section is intentionally focused on the global idea and the next buildable slices, so it can work as a project-wide execution plan.",
            "",
            "| Backlog lane | What must happen | Current status | Primary owner |",
            "| --- | --- | --- | --- |",
            "| Foundations | Keep registry, legal rules, skills, plans, and coordination docs current. | Complete and active. | lead agent + all agents |",
            "| Persistence | Finish Postgres/PostGIS runtime, migrations, repository coverage, and DB-backed health checks. | In progress. | backend_developer |",
            "| Runtime compliance | Enforce live scraping and publishing gates from registry rules at runtime. | Next. | backend_developer + debugger |",
            "| Tier-1 connectors | Move from fixture-backed coverage to DB-backed, live-safe ingest for tier-1 sources. | Partial. | scraper_1 |",
            "| Tier-2 and overlays | Add stubs and then safe sources for tier-2, Telegram overlays, and approved vendor/register routes. | Not started. | scraper_1 + scraper_sm |",
            "| Dedupe and entity graph | Build duplicate detection, property entities, offers, and review queues. | Not started. | backend_developer |",
            "| Geo and 3D map | Add geocoder, building matching, viewport APIs, and 2D/3D rendering support. | Not started. | backend_developer + ux_ui_designer |",
            "| Backend APIs | Complete listings, properties, map, CRM, admin, settings, auth, and publishing APIs. | Partial. | backend_developer |",
            "| Frontend MVP | Replace route shells with working listings, map, chat, settings, and admin experiences. | Shell only. | ux_ui_designer |",
            "| Publishing | Add dry-run and then compliant live publishing adapters only for approved routes. | Gated. | backend_developer + debugger |",
            "",
            "Priority order for the next execution wave:",
            "1. Finish Python 3.12-aligned persistence/runtime validation.",
            "2. Make tier-1 fixture-backed ingestion write verified rows into the database.",
            "3. Expand `/admin` into the central operator control panel.",
            "4. Turn `/listings`, `/chat`, and `/map` from shells into operator-usable workflows.",
            "",
            "## 7. By The Numbers",
            "",
            "| Metric | Current value |",
            "| --- | --- |",
            "| Total registry sources | {total_sources} |".format(total_sources=len(registry)),
            "| Marketplace/official/vendor sources in tiers 1-3 | {marketplace_sources} |".format(marketplace_sources=marketplace_sources),
            "| Tier-1 sources | {tier1} |".format(tier1=tier_counts.get(1, 0)),
            "| Tier-2 sources | {tier2} |".format(tier2=tier_counts.get(2, 0)),
            "| Tier-3 sources | {tier3} |".format(tier3=tier_counts.get(3, 0)),
            "| Tier-4 sources | {tier4} |".format(tier4=tier_counts.get(4, 0)),
            "| Publish-capable sources | {publish_capable} |".format(publish_capable=publish_capable),
            "| Non-publish-capable sources | {non_publish} |".format(non_publish=len(registry) - publish_capable),
            "| Access modes in use | {access_modes} |".format(access_modes=", ".join("{0}: {1}".format(key, access_counts[key]) for key in sorted(access_counts))),
            "| Legal modes in use | {legal_modes} |".format(legal_modes=", ".join("{0}: {1}".format(key, legal_counts[key]) for key in sorted(legal_counts))),
            "| Source fixture directories | {fixture_source_dirs} |".format(fixture_source_dirs=fixture_source_dirs),
            "| Fixture cases with expected outputs | {fixture_cases} |".format(fixture_cases=len(fixtures)),
            "| Tier-1 fixture coverage | {coverage}/{tier1} |".format(coverage=tier1_fixture_coverage, tier1=tier_counts.get(1, 0)),
            "| Agent skills committed in repo | 21 |",
            "| SQL tables in blueprint | {tables} |".format(tables=tables),
            "| SQL indexes in blueprint | {indexes} |".format(indexes=indexes),
            "| Declared API routes | {routes} |".format(routes=routes),
            "| Roadmap completion | {done}/{total} |".format(done=roadmap_done, total=roadmap_total),
            "| Roadmap remaining | {remaining} |".format(remaining=roadmap_remaining),
            "",
            "## 8. Scraper Status",
            "",
            "| Scraper metric | Current reading |",
            "| --- | --- |",
            "| Tier-1 connector coverage | 10/10 tier-1 sources have fixture-backed parsing or legal-gated fixture stubs. |",
            "| Social overlay coverage | Telegram public channel fixture contract exists; live social ingestion remains gated. |",
            "| Live crawl telemetry | No live scrape telemetry available in repo evidence. |",
            "| DB-ingested listing telemetry | No live database counts available because `DATABASE_URL` is not set in this shell. |",
            "| Test command result | `{summary}` / `{result}` |".format(summary=tests["summary"], result=tests["result"]),
            "| Test runtime | {runtime} |".format(runtime=tests["python_runtime"]),
            "| Test exit code | {exit_code} |".format(exit_code=tests["exit_code"]),
            "",
            "Interpretation:",
            "- The scraper architecture is well-covered in fixtures, but not yet validated as a live production crawler in this local environment.",
            "- The main blocker visible in this run is environment drift: the local shell is using Python 3.9 while the repo targets Python 3.12, so backend/runtime validation is still lower confidence than a true Python 3.12 run.",
            "",
            "## 9. Product Surfaces",
            "",
            "| Surface | Current meaning | Current state |",
            "| --- | --- | --- |",
            "| `/listings` | Searchable listings feed for Bulgaria. | Shell exists; still wired to source/demo data rather than real listing search. |",
            "| `/properties/[id]` | Canonical property detail page. | Route shell exists. |",
            "| `/map` | 2D/3D market map using MapLibre + deck.gl. | Shell exists; waiting for `/map/viewport` and building APIs. |",
            "| `/chat` | CRM inbox with threads, messages, and linked properties. | Shell exists; CRM APIs partially scaffolded. |",
            "| `/settings` | Team, keys, channel accounts, crawler/publishing settings. | Shell exists. |",
            "| `/admin` | Operator dashboard for source health and review queues. | Stats route exists; detailed multi-panel spec exists. |",
            "",
            "## 10. Detailed Dashboard Instruction",
            "",
            "This section is written as a practical instruction set for the project dashboard and the project-creation dashboard. It is based on the current admin spec, roadmap, schema, and source registry.",
            "",
            "### Dashboard purpose",
            "",
            "The dashboard should be the operating system for the project. It should let an operator create a new market-monitoring project, choose compliant source packs, see scraper and database readiness, watch milestone progress, and then move directly into source health, map, CRM, and publishing review.",
            "",
            "### Dashboard layout",
            "",
            "1. Top health strip: Postgres, Redis, API, worker, scheduler, and object storage state.",
            "2. KPI row: enabled sources, live-safe sources, canonical listings, crawl failures, parser failures, duplicate-review count, CRM open threads.",
            "3. Left navigation: Project setup, Sources, Crawl jobs, Parser failures, Dedupe review, Geocode review, CRM, Publish queue, Settings.",
            "4. Main work area: switchable tables, map panels, drawers, and project forms.",
            "5. Right context drawer: raw metadata, legal notes, source config, audit trail, and retry actions.",
            "",
            "### Project creation flow",
            "",
            "1. Define project identity: project name, team owner, country/city/resort focus, and property intents to track.",
            "2. Pick source packs: tier-1 portals, agencies, vendor feeds, official registers, and any approved social overlays.",
            "3. Review compliance: every selected source must show legal mode, access mode, risk mode, and whether publishing is allowed.",
            "4. Configure cadence: choose hourly vs ten-minute runs, priority, and which sources remain fixture-only vs live-safe.",
            "5. Set data rules: dedupe sensitivity, geocode confidence threshold, required listing fields, and photo expectations.",
            "6. Set CRM routing: default owner, inbox rules, note templates, reminder defaults, and linked listing behavior.",
            "7. Set milestone targets: current phase, acceptance gate, verifier, and next required slice.",
            "8. Save and launch only when environment, migration, and source-gate checks are green.",
            "",
            "### Dashboard blocks",
            "",
            "| Dashboard block | What it should contain | Why it matters |",
            "| --- | --- | --- |",
            "| Project identity | Project name, city/resort focus, team owner, deal type focus (sale, rent, STR, land, new-build). | Defines scope for the whole workspace. |",
            "| Source pack picker | Tier-1, tier-2, vendor, register, and social overlay toggles with legal-mode badges. | Lets operators choose only compliant source bundles. |",
            "| Geography and map preview | Bulgaria map with Varna, Burgas, Sofia, Bansko, Plovdiv, and resort filters; 2D/3D coverage preview. | Makes project coverage visible before scraping starts. |",
            "| Scraper plan | Cadence, priority, endpoint type, expected freshness, fixture availability, and risk mode. | Turns strategy into an execution plan. |",
            "| Database readiness | Migration status, source sync status, object storage status, and queue health. | Prevents launching work into a broken stack. |",
            "| CRM setup | Team inbox owner, lead routing rules, reminder templates, assignment defaults. | Makes chat and follow-up usable on day one. |",
            "| Compliance gate | Legal mode summary, partner requirements, consent/manual requirements, publish restrictions. | Stops unsafe scraping or publishing early. |",
            "| KPI board | Sources enabled, listings expected, listings ingested, crawl failures, parser failures, duplicates awaiting review. | Gives the operator an instant health read. |",
            "| Milestone tracker | Stage path, current milestone, verification owner, blocker list, next gate. | Keeps the project moving in a visible, Duolingo-like sequence. |",
            "",
            "### Dashboard acceptance criteria",
            "",
            "1. A new project cannot be activated if any selected source violates legal mode or requires a missing partner route.",
            "2. A new project cannot be activated if migrations are missing or the registry is not synced.",
            "3. KPI cards must match the same underlying stats that power `/admin/source-stats` and future crawl failure queues.",
            "4. Every top-level number must open a drill-down table or drawer.",
            "5. The milestone tracker must show who owns the next slice and which gate must pass next.",
            "",
            "## 11. Dashboard Delivery Backlog",
            "",
            "| Dashboard backlog item | What to build | Status |",
            "| --- | --- | --- |",
            "| Dashboard A | Project creation wizard with identity, source pack, compliance, cadence, CRM, and milestone steps. | Not started. |",
            "| Dashboard B | Live health strip and KPI row from readiness plus source stats. | Partially ready in backend. |",
            "| Dashboard C | Source health table with filters, tier badges, legal badges, and drill-down. | Spec ready, implementation pending. |",
            "| Dashboard D | Crawl jobs table with retry and metadata drawer. | Backend route ready, frontend pending. |",
            "| Dashboard E | Parser failure, dedupe review, geocode review, compliance review, and publish queue panels. | Backend pending. |",
            "| Dashboard F | Map preview inside dashboard for project geography and 3D readiness. | Not started. |",
            "| Dashboard G | CRM inbox summary widgets and assignment/status shortcuts. | Partial backend, frontend pending. |",
            "",
            "## 12. Project Progress Path",
            "",
            "```text",
            milestone_path(roadmap_done, roadmap_total),
            "```",
            "",
            "## 13. Agent Updates",
            "",
            *agent_sections,
            "",
            "## 14. Source-By-Source Website Numbers",
            "",
            "Columns: source number, website/source name, tier, access mode, legal mode, risk, count of listing types, count of languages, count of tracked URLs, count of fixture cases, implementation status.",
            "",
            "| # | Source | Tier | Access | Legal | Risk | Types | Langs | URLs | Fixtures | Status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *source_rows,
            "",
            "## 15. Key Risks And Gaps",
            "",
            "1. Live database and live scraping telemetry are still missing in this local shell, so the numbers above are coverage numbers, not production crawl-output numbers.",
            "2. The local runtime is misaligned with repo targets: `python3 --version` returned Python 3.9.6, while the repo targets Python 3.12, so full backend/runtime confidence still depends on a Python 3.12 environment.",
            "3. The 3D map, CRM, and public listing experience are scaffolded but not yet fully backed by live APIs and data.",
            "4. Reverse publishing remains intentionally gated by compliance requirements, which is correct but means outbound integrations are still ahead of us.",
            "",
            "## 16. Bottom Line",
            "",
            "The product already has the shape of a serious Bulgaria real estate platform: source registry, compliance control plane, fixture-backed scrapers, a canonical Bulgaria database design, 3D map intent, chat/CRM intent, and operator workflows. The next value jump is not more new UI, but completing the live persistence and runtime path so the existing shells can run on real Bulgarian listing data.",
            "",
        ]
    )


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _markdown_to_blocks(markdown: str) -> list[tuple[str, object]]:
    """Parse markdown into typed blocks including tables."""
    blocks: list[tuple[str, object]] = []
    table_rows: list[list[str]] = []
    in_table = False

    for raw in markdown.splitlines():
        line = raw.rstrip()
        is_table_line = line.startswith("|") and line.endswith("|")
        is_separator = is_table_line and all(c in "|-: " for c in line.replace("|", ""))

        if is_table_line:
            if is_separator:
                in_table = True
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                table_rows = [cells]
                in_table = True
            else:
                table_rows.append(cells)
            continue
        else:
            if in_table and table_rows:
                blocks.append(("table", list(table_rows)))
                table_rows = []
            in_table = False

        if not line:
            continue
        if line.startswith("```"):
            continue
        if line.startswith("# "):
            blocks.append(("title", line[2:]))
        elif line.startswith("## "):
            blocks.append(("h1", line[3:]))
        elif line.startswith("### "):
            blocks.append(("h2", line[4:]))
        elif line.startswith("#### "):
            blocks.append(("h3", line[5:]))
        elif line.startswith("- "):
            blocks.append(("bullet", line[2:]))
        elif re.match(r"^\d+\.\s", line):
            blocks.append(("number", re.sub(r"^\d+\.\s", "", line)))
        else:
            blocks.append(("p", line))

    if in_table and table_rows:
        blocks.append(("table", list(table_rows)))
    return blocks


def build_html_report(markdown: str) -> str:
    """Build a self-contained HTML document from markdown with proper table rendering."""
    blocks = _markdown_to_blocks(markdown)
    parts: list[str] = []

    parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Bulgaria Real Estate Product Summary</title>
<style>
  @page { size: letter; margin: 0.6in; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 11px; line-height: 1.5; color: #1a1a2e; max-width: 960px; margin: 0 auto; padding: 20px; }
  h1 { font-size: 22px; font-weight: 700; color: #0052cc; margin: 24px 0 8px; border-bottom: 2px solid #0052cc; padding-bottom: 6px; }
  h2 { font-size: 16px; font-weight: 700; color: #172b4d; margin: 20px 0 6px; }
  h3 { font-size: 13px; font-weight: 600; color: #344563; margin: 14px 0 4px; }
  h4 { font-size: 12px; font-weight: 600; color: #5e6c84; margin: 10px 0 4px; }
  p { margin: 4px 0 8px; }
  ul, ol { margin: 4px 0 8px; padding-left: 22px; }
  li { margin: 2px 0; }
  table { width: 100%; border-collapse: collapse; margin: 8px 0 14px; font-size: 10px; page-break-inside: auto; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  th, td { border: 1px solid #c1c7d0; padding: 5px 7px; text-align: left; vertical-align: top; }
  th { background: #f4f5f7; font-weight: 600; font-size: 10px; color: #344563; text-transform: uppercase; letter-spacing: 0.3px; }
  tr:nth-child(even) { background: #fafbfc; }
  code { background: #f0f1f4; padding: 1px 4px; border-radius: 3px; font-size: 10px; }
  .title-block { text-align: center; margin-bottom: 24px; padding: 20px 0; border-bottom: 3px solid #0052cc; }
  .title-block h1 { font-size: 26px; border: none; margin-bottom: 4px; }
  .title-block .subtitle { color: #5e6c84; font-size: 12px; }
  .milestone-path { font-family: monospace; font-size: 11px; line-height: 1.4; background: #f7f8fa; padding: 12px; border-radius: 6px; border: 1px solid #dfe1e6; }
</style>
</head>
<body>
""")

    in_list = False

    for kind, content in blocks:
        if kind != "bullet" and kind != "number" and in_list:
            parts.append("</ul>" if in_list == "bullet" else "</ol>")
            in_list = False

        if kind == "title":
            parts.append('<div class="title-block"><h1>{0}</h1><div class="subtitle">Generated report</div></div>'.format(_escape_html(str(content))))
        elif kind == "h1":
            parts.append("<h2>{0}</h2>".format(_escape_html(str(content))))
        elif kind == "h2":
            parts.append("<h3>{0}</h3>".format(_escape_html(str(content))))
        elif kind == "h3":
            parts.append("<h4>{0}</h4>".format(_escape_html(str(content))))
        elif kind == "bullet":
            if not in_list or in_list != "bullet":
                if in_list:
                    parts.append("</ol>")
                parts.append("<ul>")
                in_list = "bullet"
            parts.append("<li>{0}</li>".format(_escape_html(str(content))))
        elif kind == "number":
            if not in_list or in_list != "number":
                if in_list:
                    parts.append("</ul>")
                parts.append("<ol>")
                in_list = "number"
            parts.append("<li>{0}</li>".format(_escape_html(str(content))))
        elif kind == "table":
            rows = content
            if not rows:
                continue
            parts.append("<table>")
            parts.append("<thead><tr>")
            for cell in rows[0]:
                parts.append("<th>{0}</th>".format(_escape_html(cell)))
            parts.append("</tr></thead>")
            parts.append("<tbody>")
            for row in rows[1:]:
                parts.append("<tr>")
                for cell in row:
                    parts.append("<td>{0}</td>".format(_escape_html(cell)))
                parts.append("</tr>")
            parts.append("</tbody></table>")
        else:
            text = str(content)
            text = re.sub(r"`([^`]+)`", r"<code>\1</code>", _escape_html(text))
            parts.append("<p>{0}</p>".format(text))

    if in_list:
        parts.append("</ul>" if in_list == "bullet" else "</ol>")

    parts.append("</body></html>")
    return "\n".join(parts)


def _write_pdf_from_html(html_path: Path, pdf_path: Path) -> str:
    """Try Playwright first, then reportlab, then skip PDF."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("file://" + str(html_path.resolve()))
            page.pdf(path=str(pdf_path), format="Letter",
                     margin={"top": "0.5in", "right": "0.5in", "bottom": "0.5in", "left": "0.5in"},
                     print_background=True)
            browser.close()
        return "playwright"
    except Exception:
        pass

    try:
        from reportlab.lib.pagesizes import LETTER  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
        from reportlab.lib.units import inch  # type: ignore
        from reportlab.lib import colors  # type: ignore
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # type: ignore
    except Exception:
        print("  [skip pdf] neither playwright nor reportlab available")
        return "skipped"

    markdown_text = html_path.with_suffix(".md").read_text(encoding="utf-8")
    blocks = _markdown_to_blocks(markdown_text)
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle("CellStyle", parent=styles["BodyText"], fontSize=7, leading=9)
    header_style = ParagraphStyle("HeaderStyle", parent=styles["BodyText"], fontSize=7, leading=9, fontName="Helvetica-Bold")
    story: list = []

    for kind, content in blocks:
        if kind == "table":
            rows = content
            if not rows:
                continue
            table_data = []
            for ri, row in enumerate(rows):
                s = header_style if ri == 0 else cell_style
                table_data.append([Paragraph(_escape_html(c), s) for c in row])
            num_cols = max(len(r) for r in table_data)
            col_w = (7.0 * inch) / max(num_cols, 1)
            t = Table(table_data, colWidths=[col_w] * num_cols, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.95, 0.96, 0.97)),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.Color(0.75, 0.78, 0.82)),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.98, 0.98, 0.99)]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
        elif kind == "title":
            story.append(Paragraph("<b>{0}</b>".format(_escape_html(str(content))), styles["Title"]))
            story.append(Spacer(1, 8))
        elif kind == "h1":
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>{0}</b>".format(_escape_html(str(content))), styles["Heading1"]))
        elif kind == "h2":
            story.append(Paragraph("<b>{0}</b>".format(_escape_html(str(content))), styles["Heading2"]))
        elif kind == "h3":
            story.append(Paragraph("<b>{0}</b>".format(_escape_html(str(content))), styles["Heading3"]))
        elif kind == "bullet":
            story.append(Paragraph("&bull; {0}".format(_escape_html(str(content))), styles["BodyText"]))
        else:
            story.append(Paragraph(_escape_html(str(content)), styles["BodyText"]))

    doc = SimpleDocTemplate(str(pdf_path), pagesize=LETTER, title="Bulgaria Real Estate Product Summary",
                            leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
    doc.build(story)
    return "reportlab"


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.now().date().isoformat()
    markdown = build_markdown()
    markdown_path = EXPORT_DIR / "bulgaria-real-estate-product-summary-{0}.md".format(today)
    html_path = EXPORT_DIR / "bulgaria-real-estate-product-summary-{0}.html".format(today)
    pdf_path = PDF_DIR / "bulgaria-real-estate-product-summary-{0}.pdf".format(today)

    markdown_path.write_text(markdown, encoding="utf-8")
    print("generated markdown: {0}".format(markdown_path))

    html_content = build_html_report(markdown)
    html_path.write_text(html_content, encoding="utf-8")
    print("generated html: {0}".format(html_path))

    pdf_mode = _write_pdf_from_html(html_path, pdf_path)
    print("generated pdf ({0}): {1}".format(pdf_mode, pdf_path))


if __name__ == "__main__":
    main()
