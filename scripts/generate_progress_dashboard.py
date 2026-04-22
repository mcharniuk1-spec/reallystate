from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "docs" / "exports"
DASHBOARD_JSON = EXPORT_DIR / "progress-dashboard.json"
DASHBOARD_HTML = ROOT / "docs" / "dashboard" / "index.html"
ROADMAP = ROOT / "docs" / "project-status-roadmap.md"
SKILLS_DIR = ROOT / "agent-skills"
AGENTS_DIR = ROOT / "docs" / "agents"
TASKS_MD = AGENTS_DIR / "TASKS.md"
SOURCE_REGISTRY = ROOT / "data" / "source_registry.json"
PRODUCT_SUMMARY = ROOT / "docs" / "exports" / "bulgaria-real-estate-product-summary-2026-04-08.md"


def _roadmap_stats() -> dict[str, int]:
    text = ROADMAP.read_text(encoding="utf-8") if ROADMAP.exists() else ""
    done = text.count("- [x]")
    total = text.count("- [")
    return {"done": done, "total": total, "remaining": max(0, total - done)}


def _skills() -> list[str]:
    if not SKILLS_DIR.exists():
        return []
    out: list[str] = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            out.append(d.name)
    return out


def _parse_tasks_md() -> dict[str, list[dict[str, str]]]:
    """Parse TASKS.md into per-agent task lists with id, title, status."""
    if not TASKS_MD.exists():
        return {}
    text = TASKS_MD.read_text(encoding="utf-8")
    agents: dict[str, list[dict[str, str]]] = {}
    current_agent = ""
    current_task: dict[str, str] | None = None

    def _agent_key_from_heading(raw_heading: str) -> str:
        h = raw_heading.strip().lower()
        # Keep matching resilient to decorative headings and extra labels.
        if "backend_developer" in h or "backend developer" in h:
            return "backend_developer"
        if "scraper_t3" in h or "scraper t3" in h:
            return "scraper_t3"
        if "scraper_sm" in h or "scraper sm" in h:
            return "scraper_sm"
        if "scraper_1" in h or "scraper 1" in h:
            return "scraper_1"
        if "ux_ui_designer" in h or "ux/ui" in h or "ux ui" in h:
            return "ux_ui_designer"
        if "debugger" in h:
            return "debugger"
        if "lead agent" in h or "lead" in h:
            return "lead_agent"
        return ""

    for line in text.splitlines():
        line_s = line.strip()

        if line_s.startswith("## ") and not line_s.startswith("## Dependency"):
            heading_text = line_s[3:].strip()
            parsed_agent = _agent_key_from_heading(heading_text)
            if parsed_agent:
                current_agent = parsed_agent
                agents.setdefault(current_agent, [])
            else:
                # Decorative separators (e.g. "====") should not clear current agent.
                has_alnum = any(ch.isalnum() for ch in heading_text)
                if has_alnum:
                    current_agent = ""
            continue

        m = re.match(r"^###\s+(\S+):\s+(.+)$", line_s)
        if m and current_agent:
            task_id = m.group(1)
            task_title = m.group(2).strip()
            current_task = {"id": task_id, "title": task_title, "status": "TODO", "details": ""}
            agents[current_agent].append(current_task)
            continue

        if current_task and line_s.startswith("- **Status**:"):
            status_text = line_s.split(":", 1)[1].strip().strip("`").strip()
            u = status_text.upper()
            for s in ["VERIFIED", "DONE_AWAITING_VERIFY", "IN_PROGRESS", "TODO", "BLOCKED"]:
                if s in u:
                    current_task["status"] = s
                    break
            current_task["details"] = status_text
            continue

    return agents


def _parse_journey_tasks(path: Path) -> list[dict[str, str]]:
    """Extract completed tasks from a JOURNEY.md file with rich detail."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    tasks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    collecting_field: str | None = None

    _skip = {"task backlog", "scope", "review comments (after", "plan", "tier-1 source", "pattern per"}

    for line in text.splitlines():
        line_s = line.strip()
        if line_s.startswith("### "):
            heading = line_s[4:].strip()
            heading_lower = heading.lower()
            if any(heading_lower.startswith(s) for s in _skip):
                current = None
                collecting_field = None
                continue
            if heading.startswith("After "):
                continue
            current = {"title": heading, "summary": "", "action": "", "changed_files": "", "commands": "", "status": "", "review": ""}
            tasks.append(current)
            collecting_field = None
            continue

        if not current:
            continue

        def _extract_value(text_line: str) -> str:
            return text_line.split(":", 1)[1].strip().rstrip("*") if ":" in text_line else ""

        started_new_field = False
        if line_s.startswith("**Goal"):
            current["summary"] = _extract_value(line_s)
            collecting_field = "summary"
            started_new_field = True
        elif line_s.startswith("- **Action**:") or line_s.startswith("**Action"):
            current["action"] = _extract_value(line_s)
            collecting_field = "action"
            started_new_field = True
        elif "**Changed files" in line_s or "**Changed**" in line_s or "**Changed:" in line_s or "**Fixtures" in line_s or "**Deliverables" in line_s or "**Added" in line_s:
            val = _extract_value(line_s)
            collecting_field = "changed_files"
            if val:
                current["changed_files"] = val
            started_new_field = True
        elif "**Commands" in line_s or "**Verification" in line_s or "**Gate commands" in line_s or "**Verify" in line_s or "**Tests**" in line_s:
            current["commands"] = _extract_value(line_s)
            collecting_field = "commands"
            started_new_field = True
        elif line_s.startswith("- **Status**:"):
            current["status"] = _extract_value(line_s)
            collecting_field = None
            started_new_field = True
        elif line_s.startswith("- **Result**:") or line_s.startswith("**Result"):
            current["status"] = _extract_value(line_s)
            collecting_field = None
            started_new_field = True
        elif "**Review" in line_s:
            current["review"] = _extract_value(line_s)
            collecting_field = "review"
            started_new_field = True
        elif line_s.startswith("- **Evidence"):
            current["action"] = (current.get("action", "") + " " + _extract_value(line_s)).strip()
            collecting_field = "action"
            started_new_field = True
        elif line_s.startswith("- **Fix"):
            current["action"] = (current.get("action", "") + " Fix: " + _extract_value(line_s)).strip()
            collecting_field = None
            started_new_field = True
        elif "**Rationale" in line_s or "**Scope" in line_s or "**Do**" in line_s:
            val = _extract_value(line_s)
            if val and not current["action"]:
                current["action"] = val
            collecting_field = "action"
            started_new_field = True

        if not started_new_field and collecting_field and line_s:
            if line_s.startswith("- `"):
                item = line_s[2:].strip().strip("`").split("`")[0].strip()
                if item:
                    prev = current.get(collecting_field, "")
                    sep = ", " if prev else ""
                    current[collecting_field] = (prev + sep + item)[:500]
            elif line_s.startswith("- **") or line_s.startswith("- *"):
                pass
            elif line_s.startswith("- "):
                item = line_s[2:].strip().strip("`").split("`")[0].strip()
                if item:
                    prev = current.get(collecting_field, "")
                    sep = ", " if prev else ""
                    current[collecting_field] = (prev + sep + item)[:500]
            elif line_s.startswith("`") and collecting_field == "changed_files":
                item = line_s.strip("`").split("`")[0].strip()
                prev = current.get(collecting_field, "")
                sep = ", " if prev else ""
                current[collecting_field] = (prev + sep + item)[:500]

    return tasks


def _agent_skill_map() -> dict[str, list[str]]:
    """Return per-agent skill assignments."""
    return {
        "backend_developer": ["postgres-postgis-schema", "backend-data-engineering", "workflow-runtime", "db-sync-and-seeding", "railway-deploy", "ci-cd-pipeline", "test-generator", "context-engineering"],
        "scraper_1": ["scraper-connector-builder", "parser-fixture-qa", "real-estate-source-registry", "runtime-compliance-evaluator", "test-generator", "context-engineering"],
        "scraper_t3": ["scraper-connector-builder", "parser-fixture-qa", "real-estate-source-registry", "runtime-compliance-evaluator", "deep-research-workflow", "context-engineering"],
        "scraper_sm": ["scraper-connector-builder", "parser-fixture-qa", "real-estate-source-registry", "runtime-compliance-evaluator", "deep-research-workflow", "prompt-engineering", "context-engineering"],
        "ux_ui_designer": ["web-frontend-nextjs", "frontend-pages", "dashboard-visual-ops", "ux-dashboard-design", "web-performance-accessibility", "vercel-nextjs-deploy", "visual-3d-map", "context-engineering"],
        "debugger": ["debugger-golden-path", "qa-review-release", "security-audit", "test-generator", "ci-cd-pipeline", "context-engineering"],
        "lead_agent": ["claude-opus-planner", "software-architecture", "subagent-driven-development", "multi-agent-patterns", "daily-orchestration", "investor-pitch-yc", "presentation-pdf-reportlab", "project-progress-dashboard-web", "prompt-engineering", "context-engineering"],
    }


def _agent_data() -> list[dict[str, Any]]:
    mapping: dict[str, tuple[str, str, Path]] = {
        "debugger": ("Debugger", "Cross-agent verification, golden path, fixture regression, integration smoke tests, CI pipeline.", AGENTS_DIR / "debugger" / "JOURNEY.md"),
        "backend_developer": ("Backend Developer", "DB schema, migrations, API routes, persistence, orchestration, data pipelines.", AGENTS_DIR / "backend_developer" / "JOURNEY.md"),
        "ux_ui_designer": ("UX/UI Designer", "Next.js frontend, map UI, listings feed, property detail, AI chat panel, admin dashboard.", AGENTS_DIR / "ux_ui_designer" / "JOURNEY.md"),
        "scraper_1": ("Scraper 1 (Marketplaces)", "Tier-1/2 portal, classifieds, and agency connectors. HTTP-first, Playwright fallback.", AGENTS_DIR / "scraper_1" / "JOURNEY.md"),
        "scraper_t3": ("Scraper T3 (Vendor/Partner)", "Tier-3 vendor feeds, licensed data, official registers. No unauthorized scraping.", AGENTS_DIR / "scraper_t3" / "JOURNEY.md"),
        "scraper_sm": ("Scraper SM (Social)", "Tier-4 social overlays: Telegram, X, Facebook, Instagram. Consent-gated.", AGENTS_DIR / "scraper_sm" / "JOURNEY.md"),
        "lead_agent": ("Lead Agent", "Orchestration, planning, business strategy, investor materials, dashboard ops.", AGENTS_DIR / "lead_agent" / "JOURNEY.md"),
    }
    tasks_by_agent = _parse_tasks_md()
    skill_map = _agent_skill_map()
    result: list[dict[str, Any]] = []

    for key, (display_name, description, journey_path) in mapping.items():
        completed_tasks = _parse_journey_tasks(journey_path)
        agent_tasks = tasks_by_agent.get(key, [])
        verified = [t for t in agent_tasks if t["status"] == "VERIFIED"]
        todo = [t for t in agent_tasks if t["status"] == "TODO"]
        in_progress = [t for t in agent_tasks if t["status"] in {"IN_PROGRESS", "DONE_AWAITING_VERIFY"}]
        blocked = [t for t in agent_tasks if t["status"] == "BLOCKED"]
        total = len(agent_tasks)
        done_equiv = len(verified) + 0.5 * len(in_progress)
        efficiency_pct = round((done_equiv / total) * 100) if total else 0

        result.append({
            "key": key,
            "display_name": display_name,
            "description": description,
            "skills": skill_map.get(key, []),
            "journal": str(journey_path.relative_to(ROOT)) if journey_path.exists() else "",
            "completed_work": completed_tasks,
            "tasks": {
                "verified": verified,
                "in_progress": in_progress,
                "todo": todo,
                "blocked": blocked,
            },
            "counts": {
                "verified": len(verified),
                "in_progress": len(in_progress),
                "todo": len(todo),
                "blocked": len(blocked),
                "total": total,
                "journal_entries": len(completed_tasks),
                "efficiency_pct": efficiency_pct,
            },
        })
    return result


def _process_progress(tasks_by_agent: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    order = [
        ("backend_developer", "Backend/API/Data"),
        ("scraper_1", "Tier-1/2 Scraping"),
        ("scraper_t3", "Tier-3 Partner/Vendor"),
        ("scraper_sm", "Tier-4 Social Overlays"),
        ("ux_ui_designer", "Frontend/Product UX"),
        ("debugger", "Verification/Safety"),
        ("lead_agent", "Lead/Orchestration"),
    ]
    out: list[dict[str, Any]] = []
    for key, label in order:
        tasks = tasks_by_agent.get(key, [])
        done = [t for t in tasks if t["status"] == "VERIFIED"]
        current = [t for t in tasks if t["status"] in {"IN_PROGRESS", "DONE_AWAITING_VERIFY"}]
        blocked = [t for t in tasks if t["status"] == "BLOCKED"]
        nxt = [t for t in tasks if t["status"] == "TODO"]
        total = len(tasks)
        completed_equiv = len(done) + (0.5 * len(current))
        pct = round((completed_equiv / total) * 100) if total else 0
        out.append(
            {
                "key": key,
                "label": label,
                "total": total,
                "done_count": len(done),
                "current_count": len(current),
                "next_count": len(nxt),
                "blocked_count": len(blocked),
                "progress_percent": pct,
                "done_tasks": done,
                "current_tasks": current,
                "next_tasks": nxt[:10],
                "blocked_tasks": blocked,
                "comment": (
                    f"{len(done)} done, {len(current)} current, {len(nxt)} next"
                    + (f", {len(blocked)} blocked" if blocked else "")
                ),
            }
        )
    return out


def _all_tasks(tasks_by_agent: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    labels = {
        "backend_developer": "Backend Developer",
        "scraper_1": "Scraper 1",
        "scraper_t3": "Scraper T3",
        "scraper_sm": "Scraper SM",
        "ux_ui_designer": "UX/UI Designer",
        "debugger": "Debugger",
        "lead_agent": "Lead Agent",
    }
    rows: list[dict[str, str]] = []
    for owner_key, tasks in tasks_by_agent.items():
        owner = labels.get(owner_key, owner_key)
        for task in tasks:
            rows.append(
                {
                    "owner_key": owner_key,
                    "owner": owner,
                    "id": task.get("id", ""),
                    "title": task.get("title", ""),
                    "status": task.get("status", "TODO"),
                    "details": task.get("details", ""),
                }
            )
    status_rank = {"IN_PROGRESS": 0, "DONE_AWAITING_VERIFY": 1, "TODO": 2, "BLOCKED": 3, "VERIFIED": 4}
    rows.sort(key=lambda r: (status_rank.get(r["status"], 9), r["owner"], r["id"]))
    return rows


def _scan_fixture_quality(fixture_dir: Path) -> dict[str, Any]:
    """Scan all expected.json in a fixture directory tree and compute quality metrics."""
    expected_files = list(fixture_dir.rglob("expected.json"))
    if not expected_files:
        return {"items": 0, "fixture_dirs": 0, "quality": {}}

    sub_dirs = [d for d in fixture_dir.iterdir() if d.is_dir()]
    total = 0
    has_price = 0
    has_photos = 0
    has_geo = 0
    has_phone = 0
    has_area = 0
    has_rooms = 0
    has_address = 0
    has_description = 0
    has_category = 0
    photo_counts: list[int] = []
    listing_types: set[str] = set()

    for ef in expected_files:
        try:
            obj = json.loads(ef.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(obj, list):
            items = obj
        else:
            items = [obj]

        for item in items:
            if not isinstance(item, dict):
                continue
            total += 1
            if item.get("price"):
                has_price += 1
            imgs = item.get("image_urls") or []
            if imgs:
                has_photos += 1
                photo_counts.append(len(imgs))
            if item.get("latitude") and item.get("longitude"):
                has_geo += 1
            if item.get("phones"):
                has_phone += 1
            if item.get("area_sqm"):
                has_area += 1
            if item.get("rooms"):
                has_rooms += 1
            if item.get("address_text"):
                has_address += 1
            if item.get("description") or item.get("description_text"):
                has_description += 1
            cat = item.get("property_category", "")
            if cat and cat != "unknown":
                has_category += 1
            intent = item.get("listing_intent", "")
            if intent:
                listing_types.add(intent)

    def pct(n: int) -> int:
        return round((n / total) * 100) if total else 0

    return {
        "items": total,
        "fixture_dirs": len(sub_dirs),
        "quality": {
            "price_pct": pct(has_price),
            "photos_pct": pct(has_photos),
            "avg_photos": round(sum(photo_counts) / len(photo_counts), 1) if photo_counts else 0,
            "geo_pct": pct(has_geo),
            "phone_pct": pct(has_phone),
            "area_pct": pct(has_area),
            "rooms_pct": pct(has_rooms),
            "address_pct": pct(has_address),
            "description_pct": pct(has_description),
            "category_pct": pct(has_category),
            "listing_types": sorted(listing_types),
        },
    }


_SLUG_ALIASES: dict[str, list[str]] = {
    "bcpea_property_auctions": ["bcpea"],
    "telegram_public_channels": ["telegram_public"],
    "x_public_search_accounts": ["x_public"],
    "facebook_public_groups_pages": ["social"],
}


def _source_registry_stats() -> dict[str, Any]:
    if not SOURCE_REGISTRY.exists():
        return {"total": 0, "tiers": {}, "sources": []}
    data = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    tiers: dict[str, int] = {}
    access_modes: dict[str, int] = {}
    legal_modes: dict[str, int] = {}
    fixture_count = 0
    source_list: list[dict[str, Any]] = []

    fixtures_root = ROOT / "tests" / "fixtures"
    for s in sources:
        tier = str(s.get("tier", "?"))
        tiers[tier] = tiers.get(tier, 0) + 1
        am = s.get("access_mode", "unknown")
        access_modes[am] = access_modes.get(am, 0) + 1
        lm = s.get("legal_mode", "unknown")
        legal_modes[lm] = legal_modes.get(lm, 0) + 1

        slug = s["source_name"].lower().replace(".", "_").replace(" ", "_").replace("-", "_").replace("/", "_")
        fixture_dir = fixtures_root / slug
        if not fixture_dir.exists():
            for alt in _SLUG_ALIASES.get(slug, []):
                alt_dir = fixtures_root / alt
                if alt_dir.exists():
                    fixture_dir = alt_dir
                    break
        cases = 0
        scrape_quality: dict[str, Any] = {}
        if fixture_dir.exists():
            cases = sum(1 for d in fixture_dir.iterdir() if d.is_dir())
            scrape_quality = _scan_fixture_quality(fixture_dir)
        if cases > 0:
            fixture_count += 1

        source_list.append({
            "name": s["source_name"],
            "tier": s.get("tier"),
            "source_family": s.get("source_family", ""),
            "access_mode": am,
            "legal_mode": lm,
            "risk_mode": s.get("risk_mode", ""),
            "publish_capable": s.get("publish_capable", False),
            "fixture_cases": cases,
            "listing_types": s.get("listing_types", []),
            "scrape": scrape_quality,
        })

    return {
        "total": len(sources),
        "tiers": tiers,
        "access_modes": access_modes,
        "legal_modes": legal_modes,
        "with_fixtures": fixture_count,
        "sources": source_list,
    }


def _progress_path() -> list[dict[str, str]]:
    return [
        {"stage": "1", "name": "Foundations and Source Registry", "status": "COMPLETE"},
        {"stage": "2", "name": "Database and Persistence", "status": "IN PROGRESS"},
        {"stage": "3", "name": "Runtime and Compliance Gates", "status": "NEXT"},
        {"stage": "4", "name": "Tier-1 Connectors", "status": "PARTIAL"},
        {"stage": "5", "name": "Tier-2, STR, and Social Overlays", "status": "NOT STARTED"},
        {"stage": "6", "name": "Media, Dedupe, Entity Graph", "status": "NOT STARTED"},
        {"stage": "7", "name": "Geospatial and 3D Map", "status": "NOT STARTED"},
        {"stage": "8", "name": "Backend APIs", "status": "PARTIAL"},
        {"stage": "9", "name": "Frontend MVP", "status": "SHELL ONLY"},
        {"stage": "10", "name": "Reverse Publishing", "status": "GATED"},
    ]


def _dashboard_backlog() -> list[dict[str, str]]:
    return [
        {"id": "A", "name": "Project creation wizard", "status": "Not started"},
        {"id": "B", "name": "Live health strip + KPI row", "status": "Backend partial"},
        {"id": "C", "name": "Source health table with filters/badges", "status": "Spec ready"},
        {"id": "D", "name": "Crawl jobs table + retry drawer", "status": "Backend ready"},
        {"id": "E", "name": "Parser/dedupe/geocode/compliance panels", "status": "Backend pending"},
        {"id": "F", "name": "Map preview inside dashboard", "status": "Not started"},
        {"id": "G", "name": "CRM inbox summary widgets", "status": "Backend partial"},
    ]


def _roadmap_parallel_waves() -> list[dict[str, Any]]:
    """PLAN.md §9.1 — parallel roadmap waves (dependency-gated)."""
    return [
        {
            "id": "wave-a",
            "name": "Wave A",
            "summary": "Docs/rules stability, DB control plane, tier-1/2 fixture connectors, tier-3 policy/contracts, social policy/contracts.",
            "owners": ["backend_developer", "scraper_1", "scraper_t3", "scraper_sm", "debugger"],
        },
        {
            "id": "wave-b",
            "name": "Wave B",
            "summary": "DB-backed ingest runners, stats/admin expansion, auth/RBAC, tier-3 adapter stubs, frontend operator dashboard binding.",
            "owners": ["backend_developer", "scraper_1", "scraper_t3", "ux_ui_designer", "debugger"],
        },
        {
            "id": "wave-c",
            "name": "Wave C",
            "summary": "Dedupe/geo/media, map/listing/chat UI depth, publishing dry-run controls, CI hardening.",
            "owners": ["backend_developer", "ux_ui_designer", "scraper_1", "debugger"],
        },
    ]


def _operator_phases_timeline() -> list[dict[str, Any]]:
    """TASKS.md — PRIORITY EXECUTION ORDER (2026-04-09 operator wave) + parallel lanes."""
    return [
        {
            "id": "A",
            "title": "Tier-1/2 live volume",
            "subtitle": "Do first — scraper_1 + minimal backend",
            "parallel_lanes": ["scraper_1", "backend_developer"],
            "tasks": ["S1-14", "S1-15", "BD-11", "S1-18"],
        },
        {
            "id": "B",
            "title": "Backend core",
            "subtitle": "After S1-18 VERIFIED",
            "parallel_lanes": ["backend_developer"],
            "tasks": ["BD-12", "BD-13", "BD-14", "BD-15"],
        },
        {
            "id": "C",
            "title": "Debugger consolidation",
            "subtitle": "Batch verify + quality gate",
            "parallel_lanes": ["debugger", "lead_agent"],
            "tasks": ["DBG-06", "DBG-05"],
        },
        {
            "id": "D",
            "title": "Other scrapers",
            "subtitle": "Parked until S1-18 unless unblocker",
            "parallel_lanes": ["scraper_t3", "scraper_sm"],
            "tasks": ["T3-07", "T3-08", "SM-06", "…"],
        },
        {
            "id": "E",
            "title": "Frontend depth",
            "subtitle": "ux_ui_designer",
            "parallel_lanes": ["ux_ui_designer"],
            "tasks": ["UX-13", "UX-08", "UX-09", "UX-10", "UX-11"],
        },
        {
            "id": "F",
            "title": "Polish",
            "subtitle": "Map, 3D, chat, admin, smoke, security",
            "parallel_lanes": ["ux_ui_designer", "backend_developer", "debugger"],
            "tasks": ["UX-04", "UX-07", "BD-08", "UX-05", "BD-07", "UX-12", "DBG-07", "DBG-08"],
        },
        {
            "id": "G",
            "title": "Growth",
            "subtitle": "Expansion connectors + realtime + analytics",
            "parallel_lanes": ["scraper_1", "scraper_sm", "scraper_t3", "backend_developer"],
            "tasks": ["S1-16", "S1-17", "SM-06", "T3-08", "BD-16", "BD-09", "BD-10"],
        },
    ]


def _global_execution_structure() -> dict[str, Any]:
    """Single payload for dashboard “global structure” section."""
    return {
        "lanes": [
            {
                "key": "backend_developer",
                "label": "Backend / API / DB",
                "scope": "Migrations, repos, ingest, auth, deployment, map APIs",
            },
            {
                "key": "scraper_1",
                "label": "Tier-1/2 scraping",
                "scope": "Portals, classifieds, agencies — HTTP first, Playwright where needed",
            },
            {
                "key": "scraper_t3",
                "label": "Tier-3 partner/vendor",
                "scope": "Partner feeds, licensed data, official registers, auctions",
            },
            {
                "key": "scraper_sm",
                "label": "Tier-4 social",
                "scope": "Consent-gated public-channel overlays only",
            },
            {
                "key": "ux_ui_designer",
                "label": "Frontend / UX",
                "scope": "Next.js routes, map, listings, chat shell, admin",
            },
            {
                "key": "debugger",
                "label": "Verification",
                "scope": "Golden path, CI, security gates, VERIFIED promotion",
            },
            {
                "key": "lead_agent",
                "label": "Lead / orchestration",
                "scope": "Priorities, investor exports, dashboard hygiene",
            },
        ],
        "rules": [
            "One active slice per agent at a time unless operator runs GO all.",
            "Dependencies are enforced at slice level — lanes run in parallel when unblocked.",
            "Critical path until volume proof: Phase A (S1-15 + BD-11 + S1-18).",
            "Refresh this dashboard after TASKS.md or JOURNEY.md changes (`make dashboard-doc`).",
        ],
        "source_of_truth": [
            {"doc": "docs/agents/TASKS.md", "role": "Task IDs, status, dependencies"},
            {"doc": "docs/agents/README.md", "role": "Coordination protocol"},
            {"doc": "PLAN.md", "role": "Product + parallel wave definitions"},
        ],
    }


def _write_parallel_timeline_md(path: Path, generated_at: str) -> None:
    lines = [
        "# Parallel execution timeline",
        "",
        f"_Generated: {generated_at}_",
        "",
        "Aligned with `PLAN.md` §9.1 (waves) and `docs/agents/TASKS.md` priority phases.",
        "",
        "## Parallel waves (PLAN §9.1)",
        "",
    ]
    for w in _roadmap_parallel_waves():
        lines.append(f"### {w['name']}")
        lines.append("")
        lines.append(w["summary"])
        lines.append("")
        lines.append("**Typical owners:** " + ", ".join(w["owners"]) + ".")
        lines.append("")
    lines.extend(
        [
            "## Operator phases (TASKS — critical path)",
            "",
        ]
    )
    for p in _operator_phases_timeline():
        lines.append(f"### Phase {p['id']} — {p['title']}")
        lines.append("")
        lines.append(f"*{p['subtitle']}*")
        lines.append("")
        lines.append("- **Parallel lanes:** " + ", ".join(p["parallel_lanes"]))
        lines.append("- **Task IDs:** " + ", ".join(p["tasks"]))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_scraper_snapshot_md(path: Path, generated_at: str) -> None:
    """Condensed snapshot; full detail remains in each agent JOURNEY.md."""
    body = f"""# Scraper activity snapshot

_Generated: {generated_at}_

Summary of **fixture and live** work across scraper lanes. Authoritative logs: `docs/agents/scraper_1/JOURNEY.md`, `docs/agents/scraper_t3/JOURNEY.md`, `docs/agents/scraper_sm/JOURNEY.md`.

## Scraper 1 (tier-1/2 marketplaces)

- **Tier-1:** All 10 sources have fixture paths: Homes.bg, OLX.bg (API JSON), alo.bg, imot.bg, BulgarianProperties, Address.bg, SUPRIMMO, LUXIMMO, property.bg, imoti.net (legal-gated live).
- **Parser hardening:** Bulgarian keywords for intent/category; legal gate on fetch-only for `legal_review_required` sources.
- **Discovery:** `parse_discovery_html` + OLX JSON discovery; fixtures for tier-1 discovery pagination (**S1-14**).
- **Tier-2 stubs:** bazar_bg, domaza, yavlena, home2u (**S1-12**).
- **Stage-1 product types:** Coverage matrix + tests (**S1-13**); export `docs/exports/stage1-product-type-coverage.md`.
- **CLI:** `ingest-fixture`, live-safe runner tests (**S1-11**).
- **Inventory:** `make scraping-inventory` → XLSX / MD / PDF under `docs/exports/`.
- **Media:** Download/proxy pipeline, `listing_media`, `download-images` CLI (**image pipeline** — see JOURNEY Task 18).
- **Live harvest (2026-04-09):** `scripts/live_scraper.py` + `make import-scraped`; file-backed corpus for multiple sources (e.g. Bazar.bg, BulgarianProperties, imot.bg, OLX.bg, Yavlena ~250 each); repaired Address.bg, SUPRIMMO, LUXIMMO, property.bg discovery. **S1-18** still requires PostgreSQL ingest evidence (`DATABASE_URL` + `canonical_listing` counts).

## Scraper T3 (tier-3)

- Policy + tier3 fixture templates (**T3-01**).
- Licensed STR metrics parser (**T3-02**), BCPEA auctions (**T3-03**), partner feed stubs (**T3-04**), official register wrappers (**T3-05**). Status: see `TASKS.md` / verifier.

## Scraper SM (tier-4 social)

- Social ingestion contract, Telegram fixtures, redaction tests (**SM-01**).
- Telegram connector mapper (**SM-02**); X public mapper (**SM-03**) — see JOURNEY for any BLOCKED notes tied to unrelated test failures.

---
Regenerate with `make dashboard-doc` (rewrites this file).
"""
    path.write_text(body, encoding="utf-8")


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_HTML.parent.mkdir(parents=True, exist_ok=True)

    tasks_by_agent = _parse_tasks_md()
    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": generated_at,
        "roadmap": _roadmap_stats(),
        "skills": _skills(),
        "agents": _agent_data(),
        "processes": _process_progress(tasks_by_agent),
        "all_tasks": _all_tasks(tasks_by_agent),
        "sources": _source_registry_stats(),
        "progress_path": _progress_path(),
        "dashboard_backlog": _dashboard_backlog(),
        "roadmap_parallel_waves": _roadmap_parallel_waves(),
        "operator_phases": _operator_phases_timeline(),
        "global_execution_structure": _global_execution_structure(),
    }

    payload_json = json.dumps(payload, indent=2, ensure_ascii=False)
    DASHBOARD_JSON.write_text(payload_json, encoding="utf-8")
    DASHBOARD_HTML.write_text(_dashboard_html(payload_json), encoding="utf-8")
    _write_parallel_timeline_md(EXPORT_DIR / "parallel-execution-timeline.md", generated_at)
    _write_scraper_snapshot_md(EXPORT_DIR / "scraper-activity-snapshot.md", generated_at)
    print(f"generated dashboard json: {DASHBOARD_JSON}")
    print(f"dashboard html available at: {DASHBOARD_HTML}")
    print(f"wrote {EXPORT_DIR / 'parallel-execution-timeline.md'}")
    print(f"wrote {EXPORT_DIR / 'scraper-activity-snapshot.md'}")


def _dashboard_html(payload_json: str) -> str:
    template = (ROOT / "scripts" / "_dashboard_template.html").read_text(encoding="utf-8")
    return template.replace("__DASHBOARD_DATA__", payload_json, 1)


if __name__ == "__main__":
    main()
