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

    for line in text.splitlines():
        line_s = line.strip()

        if line_s.startswith("## ") and not line_s.startswith("## Dependency"):
            agent_name = line_s[3:].strip()
            paren = agent_name.find("(")
            if paren > 0:
                agent_name = agent_name[:paren].strip()
            current_agent = agent_name.lower().replace(" ", "_")
            agents.setdefault(current_agent, [])
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
            for s in ["VERIFIED", "DONE_AWAITING_VERIFY", "IN_PROGRESS", "TODO", "BLOCKED"]:
                if s in status_text.upper():
                    current_task["status"] = s
                    break
            current_task["details"] = status_text
            continue

    return agents


def _parse_journey_tasks(path: Path) -> list[dict[str, str]]:
    """Extract completed tasks from a JOURNEY.md file."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    tasks: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in text.splitlines():
        line_s = line.strip()
        if line_s.startswith("### ") and "task backlog" not in line_s.lower() and "scope" not in line_s.lower() and "review comments" not in line_s.lower():
            heading = line_s[4:].strip()
            if heading.startswith("After "):
                continue
            current = {"title": heading, "summary": ""}
            tasks.append(current)
        elif current and line_s.startswith("**Goal"):
            goal = line_s.split(":", 1)
            if len(goal) > 1:
                current["summary"] = goal[1].strip().rstrip("*")

    return tasks


def _agent_data() -> list[dict[str, Any]]:
    mapping: dict[str, tuple[str, Path]] = {
        "debugger": ("Debugger", AGENTS_DIR / "debugger" / "JOURNEY.md"),
        "backend_developer": ("Backend Developer", AGENTS_DIR / "backend_developer" / "JOURNEY.md"),
        "ux_ui_designer": ("UX/UI Designer", AGENTS_DIR / "ux_ui_designer" / "JOURNEY.md"),
        "scraper_1": ("Scraper 1 (Marketplaces)", AGENTS_DIR / "scraper_1" / "JOURNEY.md"),
        "scraper_t3": ("Scraper T3 (Vendor/Partner)", AGENTS_DIR / "scraper_t3" / "JOURNEY.md"),
        "scraper_sm": ("Scraper SM (Social)", AGENTS_DIR / "scraper_sm" / "JOURNEY.md"),
    }
    tasks_by_agent = _parse_tasks_md()
    result: list[dict[str, Any]] = []

    for key, (display_name, journey_path) in mapping.items():
        completed_tasks = _parse_journey_tasks(journey_path)
        agent_tasks = tasks_by_agent.get(key, [])
        verified = [t for t in agent_tasks if t["status"] == "VERIFIED"]
        todo = [t for t in agent_tasks if t["status"] == "TODO"]
        in_progress = [t for t in agent_tasks if t["status"] == "IN_PROGRESS"]
        blocked = [t for t in agent_tasks if t["status"] == "BLOCKED"]

        result.append({
            "key": key,
            "display_name": display_name,
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
                "journal_entries": len(completed_tasks),
            },
        })
    return result


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

        slug = s["source_name"].lower().replace(".", "_").replace(" ", "_").replace("-", "_")
        fixture_dir = fixtures_root / slug
        cases = 0
        if fixture_dir.exists():
            cases = sum(1 for d in fixture_dir.iterdir() if d.is_dir())
        if cases > 0:
            fixture_count += 1

        source_list.append({
            "name": s["source_name"],
            "tier": s.get("tier"),
            "access_mode": am,
            "legal_mode": lm,
            "risk_mode": s.get("risk_mode", ""),
            "publish_capable": s.get("publish_capable", False),
            "fixture_cases": cases,
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


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_HTML.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap": _roadmap_stats(),
        "skills": _skills(),
        "agents": _agent_data(),
        "sources": _source_registry_stats(),
        "progress_path": _progress_path(),
        "dashboard_backlog": _dashboard_backlog(),
    }

    DASHBOARD_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    DASHBOARD_HTML.write_text(_dashboard_html(), encoding="utf-8")
    print(f"generated dashboard json: {DASHBOARD_JSON}")
    print(f"dashboard html available at: {DASHBOARD_HTML}")


def _dashboard_html() -> str:
    return (ROOT / "scripts" / "_dashboard_template.html").read_text(encoding="utf-8")


if __name__ == "__main__":
    main()
