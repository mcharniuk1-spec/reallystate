"""Generate the four operator dashboards from task and analyst artifacts.

The dashboards are intentionally file-backed: they summarize agent execution,
scrape/database quality, website readiness, and support operations without
touching the scraped corpus or live database.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "docs/agents/TASKS.md"
EXPORTS_DIR = ROOT / "docs/exports"
DASHBOARD_DIR = ROOT / "docs/dashboard"
APP_DIR = ROOT / "app"
COMPONENTS_DIR = ROOT / "components"

AGENT_BY_PREFIX = {
    "PLAN": "planner",
    "CONST": "planner",
    "OPS": "ops_release_manager",
    "INFRA": "infra_db_operator",
    "MI": "market_intelligence_analyst",
    "UA": "user_analytics_agent",
    "VM": "vision_media_agent",
    "ER": "entity_resolution_agent",
    "KCA": "knowledge_context_agent",
    "DA": "data_analyst",
    "BD": "backend_developer",
    "S1": "scraper_1",
    "SM": "scraper_sm",
    "T3": "scraper_t3",
    "UX": "ux_ui_designer",
    "DBG": "debugger",
    "LEAD": "lead_agent",
}

AGENT_LABELS = {
    "planner": "Planner",
    "backend_developer": "Backend Developer",
    "data_analyst": "Data Analyst",
    "scraper_1": "Scraper 1",
    "scraper_sm": "S&M / Social + Vendor",
    "scraper_t3": "Scraper T3 (historical)",
    "ux_ui_designer": "UX/UI Designer",
    "debugger": "Debugger",
    "ops_release_manager": "Ops Release Manager",
    "infra_db_operator": "Infra DB Operator",
    "market_intelligence_analyst": "Market Intelligence",
    "user_analytics_agent": "User Analytics",
    "vision_media_agent": "Vision Media",
    "entity_resolution_agent": "Entity Resolution",
    "knowledge_context_agent": "Knowledge Context",
    "lead_agent": "Lead Agent",
}


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as exc:
        return {"_error": f"{path.name}: {exc}"}


def clean_md(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    return " ".join(value.strip().split())


def first_field(block: str, name: str) -> str:
    match = re.search(rf"^- \*\*{re.escape(name)}\*\*:\s*(.+)$", block, re.M)
    return clean_md(match.group(1)) if match else ""


def list_after_do(block: str, limit: int = 3) -> list[str]:
    match = re.search(r"^- \*\*Do\*\*:(.*?)(?:\n- \*\*|\Z)", block, re.S | re.M)
    if not match:
        return []
    section = match.group(1)
    items = re.findall(r"^\s*(?:\d+\.|-)\s+(.+)$", section, re.M)
    return [clean_md(item) for item in items[:limit]]


def infer_agent(task_id: str) -> str:
    prefix = task_id.split("-")[0]
    if prefix == "S1":
        return "scraper_1"
    return AGENT_BY_PREFIX.get(prefix, "planner")


def parse_tasks() -> list[dict[str, Any]]:
    text = TASKS_PATH.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^### ([A-Z0-9]+-\d+[A-Z]?):\s*(.+)$", text, re.M))
    tasks: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        task_id = match.group(1)
        status = first_field(block, "Status") or "UNKNOWN"
        priority = first_field(block, "Priority") or ""
        verifier = first_field(block, "Verifier") or ""
        depends_on = first_field(block, "Depends on") or ""
        output = first_field(block, "Output") or ""
        acceptance = first_field(block, "Acceptance gate") or ""
        tasks.append(
            {
                "id": task_id,
                "title": clean_md(match.group(2)),
                "agent": infer_agent(task_id),
                "status": status,
                "status_key": normalize_status(status),
                "priority": priority,
                "verifier": verifier,
                "depends_on": depends_on,
                "output": output,
                "acceptance": acceptance,
                "next_actions": list_after_do(block),
            }
        )
    return tasks


def normalize_status(status: str) -> str:
    status = status.upper()
    if "VERIFIED" in status:
        return "VERIFIED"
    if "DONE_AWAITING_VERIFY" in status:
        return "DONE_AWAITING_VERIFY"
    if "IN_PROGRESS" in status:
        return "IN_PROGRESS"
    if "BLOCKED" in status:
        return "BLOCKED"
    if "TODO" in status:
        return "TODO"
    return "UNKNOWN"


def latest_journey_entry(agent: str) -> str:
    path = ROOT / "docs/agents" / agent / "JOURNEY.md"
    if not path.exists():
        return "No journey log yet."
    text = path.read_text(encoding="utf-8").strip()
    headings = list(re.finditer(r"^#{2,3}\s+(.+)$", text, re.M))
    if not headings:
        return clean_md(text[-300:])
    start = headings[-1].start()
    return clean_md(text[start : start + 700])


def count_files(path: Path, suffixes: tuple[str, ...]) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file() and item.suffix in suffixes)


def route_paths() -> list[str]:
    if not APP_DIR.exists():
        return []
    routes = []
    for path in APP_DIR.rglob("page.tsx"):
        routes.append("/" + str(path.relative_to(APP_DIR).parent).replace("(main)/", "").replace(".", ""))
    for path in APP_DIR.rglob("route.ts"):
        routes.append("/" + str(path.relative_to(APP_DIR).parent).replace("(main)/", "").replace(".", ""))
    return sorted(set(route.replace("/.", "/").replace("//", "/") for route in routes))


def summarize_agents(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        by_agent[task["agent"]].append(task)
    rows = []
    for agent, label in AGENT_LABELS.items():
        agent_tasks = by_agent.get(agent, [])
        counts = Counter(task["status_key"] for task in agent_tasks)
        active = [
            task
            for task in agent_tasks
            if task["status_key"] in {"IN_PROGRESS", "TODO", "BLOCKED", "DONE_AWAITING_VERIFY"}
        ][:4]
        rows.append(
            {
                "agent": agent,
                "label": label,
                "counts": dict(counts),
                "open_count": sum(counts[key] for key in ("IN_PROGRESS", "TODO", "BLOCKED", "DONE_AWAITING_VERIFY")),
                "latest": latest_journey_entry(agent),
                "active_tasks": active,
            }
        )
    return rows


def source_rows(scrape_status: dict[str, Any], audit: dict[str, Any], gate: dict[str, Any]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for item in scrape_status.get("sources", []):
        key = item.get("source_key") or item.get("registry_key") or item.get("name") or "unknown"
        rows[key] = {
            "source": item.get("name") or key,
            "tier": item.get("tier", ""),
            "saved": item.get("saved_listings", 0),
            "description": item.get("with_description", 0),
            "photo_urls": item.get("with_photo_urls", 0),
            "local_photos": item.get("with_readable_local_photos", 0),
            "accepted": item.get("accepted_single_entity_candidates", 0),
            "lost": item.get("lost_items", 0),
            "grouped": item.get("grouped_publications", 0),
        }
    audit_sources = audit.get("sources", [])
    if isinstance(audit_sources, dict):
        audit_sources = [dict(value, source_key=key) for key, value in audit_sources.items() if isinstance(value, dict)]
    for item in audit_sources:
        if not isinstance(item, dict):
            continue
        key = item.get("source_key") or item.get("source") or "unknown"
        row = rows.setdefault(key, {"source": key})
        estimated = item.get("estimated_quality", {})
        row.update(
            {
                "audit_rows": item.get("rows", item.get("total_rows", "")),
                "audit_action1_rows": item.get("action1_rows", ""),
                "audit_lost": item.get("estimated_lost", item.get("lost", estimated.get("LOST", ""))),
                "audit_grouped": item.get("estimated_grouped", item.get("grouped", "")),
            }
        )
    gate_sources = gate.get("sources", [])
    if isinstance(gate_sources, dict):
        gate_sources = [dict(value, source_key=key) for key, value in gate_sources.items() if isinstance(value, dict)]
    for item in gate_sources:
        if not isinstance(item, dict):
            continue
        key = item.get("source_key") or item.get("source") or "unknown"
        row = rows.setdefault(key, {"source": key})
        quality = item.get("quality_rollup") or item.get("quality") or item
        row.update(
            {
                "gate_total": quality.get("total", item.get("items", "")),
                "gate_good": quality.get("good_single_unit", ""),
                "gate_lost": quality.get("bad_lost", item.get("LOST", "")),
                "gate_grouped": quality.get("grouped_publication", ""),
            }
        )
    return sorted(rows.values(), key=lambda row: str(row.get("source", "")).lower())


def fmt_int(value: Any) -> str:
    if value in (None, ""):
        return "n/a"
    if isinstance(value, (int, float)):
        return f"{int(value):,}"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return escape(str(value))


def page_shell(title: str, subtitle: str, body: str, generated_at: str) -> str:
    nav = """
      <nav>
        <a href="index.html">Hub</a>
        <a href="project-progress.html">Project Progress</a>
        <a href="properties-database.html">Properties Database</a>
        <a href="website.html">Website</a>
        <a href="support.html">Support</a>
        <a href="data-quality-dashboard.html">Deep Data Quality</a>
        <a href="scrape-status.html">Source Matrix</a>
      </nav>
    """
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | Bulgaria Real Estate Ops</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fa;
      --panel: #ffffff;
      --ink: #17212f;
      --muted: #5d6b7d;
      --line: #d9e0e8;
      --accent: #0f766e;
      --warn: #b45309;
      --bad: #b91c1c;
      --good: #047857;
      --info: #1d4ed8;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.45; }}
    header {{ padding: 28px min(5vw, 56px) 20px; background: #ffffff; border-bottom: 1px solid var(--line); }}
    h1 {{ margin: 0 0 6px; font-size: clamp(28px, 4vw, 44px); letter-spacing: 0; }}
    h2 {{ margin: 32px 0 12px; font-size: 22px; letter-spacing: 0; }}
    h3 {{ margin: 0 0 8px; font-size: 16px; letter-spacing: 0; }}
    p {{ margin: 0 0 10px; }}
    a {{ color: var(--info); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }}
    nav a {{ border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; color: var(--ink); background: #f8fafc; font-size: 14px; }}
    main {{ padding: 24px min(5vw, 56px) 56px; }}
    .muted {{ color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }}
    .wide-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 12px; }}
    details.stat, .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    details.stat summary {{ cursor: pointer; list-style: none; display: grid; gap: 4px; }}
    details.stat summary::-webkit-details-marker {{ display: none; }}
    .label {{ color: var(--muted); font-size: 13px; }}
    .value {{ font-size: 28px; font-weight: 750; line-height: 1.15; }}
    .tag {{ display: inline-flex; align-items: center; border: 1px solid var(--line); border-radius: 999px; padding: 2px 8px; font-size: 12px; color: var(--muted); background: #f8fafc; }}
    .good {{ color: var(--good); }}
    .warn {{ color: var(--warn); }}
    .bad {{ color: var(--bad); }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); vertical-align: top; text-align: left; font-size: 14px; }}
    th {{ background: #eef3f8; font-size: 12px; text-transform: uppercase; letter-spacing: .02em; color: #435166; }}
    tr:last-child td {{ border-bottom: 0; }}
    .nowrap {{ white-space: nowrap; }}
    footer {{ color: var(--muted); padding: 0 min(5vw, 56px) 32px; font-size: 13px; }}
  </style>
</head>
<body>
  <header>
    <p class="tag">Generated {escape(generated_at)}</p>
    <h1>{escape(title)}</h1>
    <p class="muted">{escape(subtitle)}</p>
    {nav}
  </header>
  <main>
    {body}
  </main>
  <footer>File-backed operator dashboards. DB-backed claims remain blocked until BD-18 + INFRA-02 verification.</footer>
</body>
</html>
"""
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def stat(label: str, value: Any, insight: str, details: str, action: str = "") -> str:
    action_html = f"<p><strong>Action:</strong> {escape(action)}</p>" if action else ""
    return f"""
    <details class="stat" open>
      <summary><span class="label">{escape(label)}</span><span class="value">{fmt_int(value)}</span></summary>
      <p><strong>Insight:</strong> {escape(insight)}</p>
      <p><strong>Details:</strong> {escape(details)}</p>
      {action_html}
    </details>
    """


def task_table(tasks: list[dict[str, Any]], limit: int = 40) -> str:
    rows = []
    for task in tasks[:limit]:
        action = "; ".join(task.get("next_actions") or [])[:260]
        rows.append(
            "<tr>"
            f"<td class=\"nowrap\">{escape(task['id'])}</td>"
            f"<td>{escape(task['title'])}</td>"
            f"<td>{escape(AGENT_LABELS.get(task['agent'], task['agent']))}</td>"
            f"<td>{escape(task['status_key'])}</td>"
            f"<td>{escape(task.get('depends_on') or '-')}</td>"
            f"<td>{escape(action or task.get('acceptance') or '-')}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>ID</th><th>Slice</th><th>Owner</th><th>Status</th><th>Depends</th><th>Next evidence/action</th></tr></thead><tbody>"
        + "\n".join(rows)
        + "</tbody></table>"
    )


def build_project_dashboard(tasks: list[dict[str, Any]], agents: list[dict[str, Any]], generated_at: str) -> str:
    counts = Counter(task["status_key"] for task in tasks)
    active = [task for task in tasks if task["status_key"] in {"IN_PROGRESS", "BLOCKED", "TODO", "DONE_AWAITING_VERIFY"}]
    priority = sorted(
        active,
        key=lambda task: (
            {"IN_PROGRESS": 0, "BLOCKED": 1, "DONE_AWAITING_VERIFY": 2, "TODO": 3}.get(task["status_key"], 9),
            task["id"],
        ),
    )
    stat_grid = '<section class="grid">' + "".join(
        [
            stat("Total slices", len(tasks), "The task board is now the project operating plan.", "Counts include active, historic, recurring, and support-lane slices.", "Keep new work as verifier-gated slices, not chat-only requests."),
            stat("Verified slices", counts["VERIFIED"], "Verified work is the only completed state usable for downstream claims.", "DONE_AWAITING_VERIFY still needs debugger or assigned verifier promotion."),
            stat("Awaiting verifier", counts["DONE_AWAITING_VERIFY"], "There is a large verification queue from concluded agent execution.", "Debugger should batch similar documentation-only gates, then isolate runtime/DB gates."),
            stat("Blocked slices", counts["BLOCKED"], "The main blockers are DB credentials/import proof and operator-gated media execution.", "Do not unblock public UI or release claims until the named gates clear."),
            stat("Open active slices", len(active), "The project has many open slices, but only a few are critical path.", "Critical path: DA-02/DA-03 -> BD-18/BD-19 -> INFRA-02 -> UX-16/18 -> release."),
            stat("Agent lanes", len([a for a in agents if a["open_count"] or a["counts"]]), "All current specialist lanes are represented.", "The dashboard includes new support lanes absent from the legacy progress view."),
        ]
    ) + "</section>"
    agent_blocks = []
    for agent in agents:
        counts_txt = ", ".join(f"{key}: {value}" for key, value in sorted(agent["counts"].items())) or "No task slices"
        active_txt = "; ".join(f"{task['id']} {task['status_key']}" for task in agent["active_tasks"]) or "No open slice"
        agent_blocks.append(
            f"""
            <details class="stat" open>
              <summary><span class="label">{escape(agent['label'])}</span><span class="value">{fmt_int(agent['open_count'])}</span></summary>
              <p><strong>Insight:</strong> {escape(agent['latest'][:360])}</p>
              <p><strong>Details:</strong> {escape(counts_txt)}</p>
              <p><strong>Action:</strong> {escape(active_txt)}</p>
            </details>
            """
        )
    body = f"""
      {stat_grid}
      <h2>Critical Path</h2>
      <div class="panel">
        <p><strong>FACT:</strong> Data analyst remains evidence owner for Action1 accepted/LOST/grouped/media counts. DA-01 is file-backed; DB-backed proof is still blocked.</p>
        <p><strong>INTERPRETATION:</strong> The next whole-project move is denominator repair and accepted-only import proof, then admin/UI truth surfaces.</p>
        <p><strong>GAP:</strong> No public completeness, DB count, or release claim is valid until DA-02/DA-03, BD-18/BD-19, INFRA-02, and debugger gates complete.</p>
      </div>
      <h2>Agent Subsections</h2>
      <section class="wide-grid">{''.join(agent_blocks)}</section>
      <h2>Execution Queue</h2>
      {task_table(priority, 60)}
    """
    return page_shell("Project Progress Dashboard", "Whole-project execution state with all agent lanes and verifier gates.", body, generated_at)


def build_properties_dashboard(
    audit: dict[str, Any], gate: dict[str, Any], scrape_status: dict[str, Any], rows: list[dict[str, Any]], generated_at: str
) -> str:
    audit_totals = audit.get("totals", {})
    gate_rollup = gate.get("quality_rollup", {})
    scrape_totals = scrape_status.get("totals", {})
    source_table_rows = []
    for row in rows:
        source_table_rows.append(
            "<tr>"
            f"<td>{escape(str(row.get('source', 'unknown')))}</td>"
            f"<td>{escape(str(row.get('tier', '')))}</td>"
            f"<td>{fmt_int(row.get('saved'))}</td>"
            f"<td>{fmt_int(row.get('accepted') or row.get('gate_good'))}</td>"
            f"<td>{fmt_int(row.get('lost') or row.get('gate_lost') or row.get('audit_lost'))}</td>"
            f"<td>{fmt_int(row.get('grouped') or row.get('gate_grouped') or row.get('audit_grouped'))}</td>"
            f"<td>{fmt_int(row.get('description'))}</td>"
            f"<td>{fmt_int(row.get('local_photos'))}</td>"
            "</tr>"
        )
    body = f"""
      <section class="grid">
        {stat("Audit rows", audit_totals.get("rows"), "DA-01 is the current file-backed quality audit.", "This is not a verified live database count.", "Keep DB claims blocked until BD-18 + INFRA-02.")}
        {stat("Action1 rows", audit_totals.get("action1_rows"), "Action1 is the current marketplace evidence scope.", "Seven sources x four buckets remain the controlled scope.", "Do not widen Action2 until Action1 QA repair is verified.")}
        {stat("DB import candidates", audit_totals.get("db_import_default_candidate_rows"), "Default import must be accepted-only.", "Candidate count excludes pending/missing QA, LOST, grouped/development, and inactive rows where the audit can identify them.", "Backend should preserve QA state before canonical promotion.")}
        {stat("Pending or missing QA", audit_totals.get("pending_or_missing_qa_rows"), "This is the largest data-risk queue.", "Rows without clear QA state cannot enter public property views.", "DA-02 and scraper repair waves must reduce or classify this queue.")}
        {stat("Quality-gate total", gate_rollup.get("total"), "The quality gate uses its own denominator.", "DA-02 must reconcile this with audit/importer/dashboard semantics.", "Keep bad/grouped overlap visible.")}
        {stat("Good single-unit", gate_rollup.get("good_single_unit"), "These rows are closest to buyer-facing property candidates.", "They still need accepted-only import/read-model proof before public claims.", "Use for internal QA, not public coverage language.")}
        {stat("LOST rows", gate_rollup.get("bad_lost"), "LOST means rescrape/repair or quarantine, not a valid property.", "Do not import by default.", "Scraper_1 should consume the LOST queue for bounded repairs.")}
        {stat("Grouped publications", gate_rollup.get("grouped_publication"), "Grouped/development rows are source publications, not single units.", "Split only when unit-level URL, price/status, area, and media evidence exist.", "Entity resolution and UX must keep these out of single-property flows.")}
        {stat("Saved listings", scrape_totals.get("saved_listings"), "Scrape-status saved rows are operational capture counts.", "They are useful for source health but not equivalent to accepted properties.", "Display alongside accepted and LOST counts, never as market coverage.")}
        {stat("Description coverage", scrape_totals.get("with_description"), "Description presence is improving but must be source-scoped.", "Thin/mojibake descriptions still require parser repair.", "UX should expose missing/weak description as QA state in admin only.")}
        {stat("Readable local photos", scrape_totals.get("with_readable_local_photos"), "Local media is a trust prerequisite.", "Remote URL counts alone are insufficient for durable gallery evidence.", "Vision/media work waits for Action0 operator gate.")}
        {stat("Patterned sources", scrape_totals.get("patterned_sources"), "Pattern status is source-pattern readiness, not market completion.", "Patterned must still prove accepted rows and full media by bucket.", "Keep pattern and count readiness separate.")}
      </section>
      <h2>Source Detail</h2>
      <table>
        <thead><tr><th>Source</th><th>Tier</th><th>Saved</th><th>Accepted/good</th><th>LOST</th><th>Grouped</th><th>Description</th><th>Readable local photos</th></tr></thead>
        <tbody>{''.join(source_table_rows)}</tbody>
      </table>
    """
    return page_shell("Properties Database Dashboard", "Scraping, QA, description, media, and accepted-only import readiness.", body, generated_at)


def build_website_dashboard(tasks: list[dict[str, Any]], generated_at: str) -> str:
    routes = route_paths()
    ux_tasks = [task for task in tasks if task["agent"] == "ux_ui_designer" and task["status_key"] in {"TODO", "IN_PROGRESS", "DONE_AWAITING_VERIFY", "BLOCKED"}]
    backend_ui = [task for task in tasks if task["id"] in {"BD-19", "BD-20", "BD-21"}]
    route_rows = "".join(f"<tr><td>{escape(route)}</td><td>Next.js app route</td></tr>" for route in routes[:80])
    body = f"""
      <section class="grid">
        {stat("App routes", len(routes), "The app shell exists across buyer, map, chat, settings, admin, and dashboard routes.", "Route count is structural readiness, not data trust.", "Keep public property routes accepted-only.")}
        {stat("React components", count_files(COMPONENTS_DIR, (".tsx", ".ts")), "Reusable UI components exist for the platform.", "Dashboard and admin surfaces still need DA/BD read-model contracts.", "UX-16/18 should implement only verified metric labels.")}
        {stat("UX open slices", len(ux_tasks), "Frontend work is waiting on data-count and import truth.", "UX-15 completed requirements; UX-16/17/18/19/20 remain contract-driven.", "Do not invent counts in UI while DA-02 and BD-19 are pending.")}
        {stat("Backend UI contracts", len(backend_ui), "Website dashboards depend on backend read models.", "BD-19/20/21 are the API/data contracts for QA, analytics, and entity-resolution review.", "Prioritize BD-19 after BD-18 proof.")}
      </section>
      <h2>Route Inventory</h2>
      <table><thead><tr><th>Route</th><th>Insight</th></tr></thead><tbody>{route_rows}</tbody></table>
      <h2>Website Execution Queue</h2>
      {task_table(ux_tasks + backend_ui, 30)}
      <h2>Buyer-Facing Rule</h2>
      <div class="panel">
        <p><strong>FACT:</strong> Public website views must not consume LOST, grouped/development, inactive, pending-QA, or missing-status rows.</p>
        <p><strong>INTERPRETATION:</strong> Admin queues can show raw quality work, but public pages need accepted single-unit proof plus media/description state.</p>
        <p><strong>GAP:</strong> DB-backed accepted-only read model is pending BD-19 and verifier sign-off.</p>
      </div>
    """
    return page_shell("Website Dashboard", "Frontend route readiness, UX gates, and public-data safety.", body, generated_at)


def build_support_dashboard(tasks: list[dict[str, Any]], agents: list[dict[str, Any]], generated_at: str) -> str:
    support_agents = {
        "ops_release_manager",
        "infra_db_operator",
        "market_intelligence_analyst",
        "user_analytics_agent",
        "vision_media_agent",
        "entity_resolution_agent",
        "knowledge_context_agent",
        "scraper_sm",
        "debugger",
    }
    support_tasks = [task for task in tasks if task["agent"] in support_agents and task["status_key"] in {"TODO", "IN_PROGRESS", "BLOCKED", "DONE_AWAITING_VERIFY"}]
    counts = Counter(task["status_key"] for task in support_tasks)
    agent_rows = []
    for agent in agents:
        if agent["agent"] not in support_agents:
            continue
        agent_rows.append(
            "<tr>"
            f"<td>{escape(agent['label'])}</td>"
            f"<td>{fmt_int(agent['open_count'])}</td>"
            f"<td>{escape(agent['latest'][:260])}</td>"
            "</tr>"
        )
    body = f"""
      <section class="grid">
        {stat("Support open slices", len(support_tasks), "Operational assistance now has explicit owners.", "This includes release, infra, market, analytics, vision, entity resolution, knowledge, S&M, and verification.", "Keep support work evidence-backed and verifier-gated.")}
        {stat("Awaiting verification", counts["DONE_AWAITING_VERIFY"], "Several concluded planning outputs need debugger promotion.", "Most are docs/contracts, not runtime execution.", "Debugger should batch verify low-risk docs, then queue runtime gates separately.")}
        {stat("Blocked support gates", counts["BLOCKED"], "Blocked work is mostly credential/operator gated.", "INFRA-02 needs DB URLs; VM-02 needs operator Action0 now.", "Do not substitute file-backed evidence for DB/operator proof.")}
        {stat("Todo support slices", counts["TODO"], "Support roadmap is now visible.", "Next work should convert contracts into implementation only after upstream evidence exists.", "Prioritize DA/BD/DBG handoffs before adding new scope.")}
      </section>
      <h2>Operational Lanes</h2>
      <table><thead><tr><th>Lane</th><th>Open</th><th>Latest insight</th></tr></thead><tbody>{''.join(agent_rows)}</tbody></table>
      <h2>Support Execution Queue</h2>
      {task_table(support_tasks, 50)}
    """
    return page_shell("Support Dashboard", "Operational assistance, release, infra, analytics, media, and verification lanes.", body, generated_at)


def build_hub(generated_at: str, tasks: list[dict[str, Any]], scrape_status: dict[str, Any]) -> str:
    counts = Counter(task["status_key"] for task in tasks)
    scrape_totals = scrape_status.get("totals", {})
    body = f"""
      <section class="wide-grid">
        <div class="panel">
          <h3><a href="project-progress.html">Project Progress Dashboard</a></h3>
          <p class="muted">All-agent execution plan, verifier queue, active blockers, and critical path.</p>
          <p><strong>{fmt_int(len(tasks))}</strong> task slices, <strong>{fmt_int(counts['DONE_AWAITING_VERIFY'])}</strong> awaiting verification.</p>
        </div>
        <div class="panel">
          <h3><a href="properties-database.html">Properties Database Dashboard</a></h3>
          <p class="muted">Scraping, description/media coverage, accepted/LOST/grouped evidence, and import-readiness warnings.</p>
          <p><strong>{fmt_int(scrape_totals.get('saved_listings'))}</strong> saved rows, <strong>{fmt_int(scrape_totals.get('accepted_single_entity_candidates'))}</strong> accepted candidates in scrape-status export.</p>
          <p><a href="data-quality-dashboard.html">Open deep data-quality drilldown</a></p>
        </div>
        <div class="panel">
          <h3><a href="website.html">Website Dashboard</a></h3>
          <p class="muted">Frontend routes, UX work queue, public-data safety, and dashboard implementation gates.</p>
          <p><strong>{fmt_int(len(route_paths()))}</strong> app routes detected.</p>
        </div>
        <div class="panel">
          <h3><a href="support.html">Support Dashboard</a></h3>
          <p class="muted">Release, infra, analytics, media, entity-resolution, knowledge, S&M, and debugger lanes.</p>
          <p>DB-backed claims stay blocked until BD-18 and INFRA-02.</p>
        </div>
      </section>
    """
    return page_shell("Operations Dashboard Hub", "Four explicit dashboards for project, properties database, website, and support operations.", body, generated_at)


def write_plan_export(tasks: list[dict[str, Any]], agents: list[dict[str, Any]], generated_at: str) -> None:
    lines = [
        "# All-Agent Execution Plan",
        "",
        f"Generated: {generated_at}",
        "",
        "## Critical Path",
        "",
        "- FACT: `data_analyst` owns current Action1 evidence and dashboard denominator truth.",
        "- INTERPRETATION: execute `DA-02`/`DA-03` before public dashboard claims, then `BD-18`/`BD-19`, then `INFRA-02`, then UX/admin/public surfaces.",
        "- GAP: DB-backed proof and operator-gated media execution remain unavailable.",
        "",
        "## Agent Next Actions",
        "",
    ]
    by_agent = {agent["agent"]: agent for agent in agents}
    for agent, label in AGENT_LABELS.items():
        active = by_agent.get(agent, {}).get("active_tasks", [])
        lines.extend([f"### {label}", ""])
        if not active:
            lines.append("- No open task slice currently parsed.")
        for task in active[:4]:
            action = "; ".join(task.get("next_actions") or []) or task.get("acceptance") or "Follow task acceptance gate."
            lines.append(f"- `{task['id']}` ({task['status_key']}): {task['title']} — {action}")
        lines.append("")
    (EXPORTS_DIR / "all-agent-execution-plan-2026-05-13.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    tasks = parse_tasks()
    agents = summarize_agents(tasks)
    audit = read_json(EXPORTS_DIR / "scrape-database-quality-audit-2026-05-13.json", {})
    gate = read_json(EXPORTS_DIR / "action1-dataset-quality-gate.json", {})
    scrape_status = read_json(EXPORTS_DIR / "scrape-status-dashboard.json", {})
    rows = source_rows(scrape_status, audit, gate)

    pages = {
        "index.html": build_hub(generated_at, tasks, scrape_status),
        "project-progress.html": build_project_dashboard(tasks, agents, generated_at),
        "properties-database.html": build_properties_dashboard(audit, gate, scrape_status, rows, generated_at),
        "website.html": build_website_dashboard(tasks, generated_at),
        "support.html": build_support_dashboard(tasks, agents, generated_at),
    }
    for name, html in pages.items():
        (DASHBOARD_DIR / name).write_text(html, encoding="utf-8")

    payload = {
        "generated_at": generated_at,
        "dashboards": {
            "project_progress": "docs/dashboard/project-progress.html",
            "properties_database": "docs/dashboard/properties-database.html",
            "website": "docs/dashboard/website.html",
            "support": "docs/dashboard/support.html",
        },
        "task_counts": dict(Counter(task["status_key"] for task in tasks)),
        "agents": agents,
        "properties_database": {
            "audit_totals": audit.get("totals", {}),
            "quality_rollup": gate.get("quality_rollup", {}),
            "scrape_totals": scrape_status.get("totals", {}),
            "sources": rows,
        },
        "website": {
            "routes": route_paths(),
            "component_count": count_files(COMPONENTS_DIR, (".tsx", ".ts")),
        },
    }
    (EXPORTS_DIR / "operational-dashboards.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_plan_export(tasks, agents, generated_at)
    print(f"Wrote {len(pages)} dashboard pages and operational-dashboards.json")


if __name__ == "__main__":
    main()
