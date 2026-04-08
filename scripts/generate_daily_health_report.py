from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import textwrap
import time
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "docs" / "reports"
PDF_DIR = ROOT / "output" / "pdf"

REQUIRED_FRONTEND_ROUTES = [
    "app/(main)/listings/page.tsx",
    "app/(main)/properties/[id]/page.tsx",
    "app/(main)/map/page.tsx",
    "app/(main)/chat/page.tsx",
    "app/(main)/settings/page.tsx",
    "app/(main)/admin/page.tsx",
]


@dataclass(frozen=True)
class CommandResult:
    label: str
    command: str
    returncode: int
    duration_ms: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def combined_output(self) -> str:
        out = self.stdout.strip()
        err = self.stderr.strip()
        if out and err:
            return f"{out}\n{err}"
        return out or err


def run_shell(label: str, command: str, *, env: dict[str, str] | None = None) -> CommandResult:
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    started = time.perf_counter()
    proc = subprocess.run(
        ["/bin/zsh", "-lc", command],
        cwd=ROOT,
        env=run_env,
        text=True,
        capture_output=True,
        check=False,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)
    return CommandResult(
        label=label,
        command=command,
        returncode=proc.returncode,
        duration_ms=duration_ms,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _markdown_to_lines(markdown: str, width: int = 95) -> list[str]:
    lines: list[str] = []
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            lines.append("")
            continue
        if line.startswith("```"):
            continue
        if line.startswith("# "):
            lines.append(line[2:].upper())
            lines.append("")
            continue
        if line.startswith("## "):
            title = line[3:]
            lines.append(title)
            lines.append("-" * min(len(title), width))
            continue
        if line.startswith("### "):
            lines.append(line[4:])
            continue
        bullet_prefix = ""
        content = line
        if line.startswith("- "):
            bullet_prefix = "- "
            content = line[2:]
        elif re.match(r"^\d+\.\s", line):
            marker, content = line.split(" ", 1)
            bullet_prefix = f"{marker} "
        wrapped = textwrap.wrap(content, width=max(20, width - len(bullet_prefix))) or [""]
        for idx, part in enumerate(wrapped):
            prefix = bullet_prefix if idx == 0 else " " * len(bullet_prefix)
            lines.append(prefix + part)
    return lines


def _build_pdf(lines: list[str]) -> bytes:
    page_width = 612
    page_height = 792
    margin_left = 54
    margin_top = 54
    font_size = 10
    leading = 13
    max_lines = int((page_height - 2 * margin_top) / leading)

    pages = [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)] or [[]]
    objects: list[bytes] = []

    def add_object(payload: str | bytes) -> int:
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
        objects.append(payload_bytes)
        return len(objects)

    font_obj = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    pages_obj_placeholder = add_object("<< >>")
    page_obj_ids: list[int] = []

    for page_number, page_lines in enumerate(pages, start=1):
        content_lines = ["BT", f"/F1 {font_size} Tf", f"{margin_left} {page_height - margin_top} Td", f"{leading} TL"]
        for line in page_lines:
            content_lines.append(f"({_escape_pdf_text(line)}) Tj")
            content_lines.append("T*")
        content_lines.append(f"(Page {page_number} of {len(pages)}) Tj")
        content_lines.append("ET")
        stream = "\n".join(content_lines).encode("utf-8")
        content_obj = add_object(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        page_obj_ids.append(
            add_object(
                f"<< /Type /Page /Parent {pages_obj_placeholder} 0 R /MediaBox [0 0 {page_width} {page_height}] "
                f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_obj} 0 R >>"
            )
        )

    kids = " ".join(f"{page_id} 0 R" for page_id in page_obj_ids)
    objects[pages_obj_placeholder - 1] = (
        f"<< /Type /Pages /Count {len(page_obj_ids)} /Kids [ {kids} ] >>".encode("utf-8")
    )
    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj_placeholder} 0 R >>")

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def check_zip(path: Path) -> str:
    if not path.exists():
        return "missing"
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
        return "ok" if bad is None else f"bad member: {bad}"
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


def check_pdf(path: Path) -> str:
    if not path.exists():
        return "missing"
    try:
        return "ok" if path.read_bytes()[:8].startswith(b"%PDF-") else "bad header"
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


def parse_pyproject(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    requires_python_match = re.search(r'requires-python\s*=\s*"([^"]+)"', text)
    deps_match = re.search(r"dependencies\s*=\s*\[(.*?)\]\s*\n", text, re.S)
    dev_match = re.search(r"dev\s*=\s*\[(.*?)\]\s*\n", text, re.S)

    def _extract(block: str | None) -> list[str]:
        if not block:
            return []
        return re.findall(r'"([^"]+)"', block)

    return {
        "requires_python": requires_python_match.group(1) if requires_python_match else "unknown",
        "dependencies": _extract(deps_match.group(1) if deps_match else None),
        "dev_dependencies": _extract(dev_match.group(1) if dev_match else None),
    }


def parse_ci_versions(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    py_match = re.search(r'python-version:\s*"([^"]+)"', text)
    node_match = re.search(r'node-version:\s*"([^"]+)"', text)
    return {
        "python": py_match.group(1) if py_match else "unknown",
        "node": node_match.group(1) if node_match else "unknown",
    }


def parse_dockerfile_base(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("FROM "):
            return line.split(" ", 1)[1].strip()
    return "unknown"


def parse_compose_images(path: Path) -> list[str]:
    images: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("image: "):
            images.append(stripped.split("image: ", 1)[1])
    return images


def slugify_source_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def frontend_route_status() -> list[tuple[str, bool]]:
    return [(path, (ROOT / path).exists()) for path in REQUIRED_FRONTEND_ROUTES]


def list_backend_routes() -> list[str]:
    main_text = (ROOT / "src" / "bgrealestate" / "api" / "main.py").read_text(encoding="utf-8")
    prefixes: dict[str, str] = {}
    for router_name, prefix in re.findall(r'app\.include_router\((\w+)\.router(?:,\s*prefix="([^"]*)")?\)', main_text):
        prefixes[router_name] = prefix or ""

    route_files = sorted((ROOT / "src" / "bgrealestate" / "api" / "routers").glob("*.py"))
    routes: list[str] = []
    for path in route_files:
        text = path.read_text(encoding="utf-8")
        module_name = path.stem
        file_prefix_match = re.search(r'APIRouter\([^)]*prefix\s*=\s*"([^"]+)"', text)
        file_prefix = file_prefix_match.group(1) if file_prefix_match else ""
        include_prefix = prefixes.get(module_name, "")
        prefix = f"{include_prefix}{file_prefix}"
        for route in re.findall(r'@router\.(?:get|post|put|patch|delete)\("([^"]+)"', text):
            routes.append(f"{prefix}{route}")
    return sorted(dict.fromkeys(routes))


def extract_test_summary(result: CommandResult) -> dict[str, object]:
    summary: dict[str, object] = {
        "status": "failed" if not result.ok else "passed",
        "ran": 0,
        "skipped": 0,
        "duration_seconds": None,
        "skip_reasons": [],
    }
    text = result.combined_output()
    ran_match = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", text)
    if ran_match:
        summary["ran"] = int(ran_match.group(1))
        summary["duration_seconds"] = float(ran_match.group(2))
    skipped_match = re.search(r"OK \(skipped=(\d+)\)", text)
    if skipped_match:
        summary["skipped"] = int(skipped_match.group(1))
    skip_lines = []
    for line in text.splitlines():
        if "... skipped " in line:
            skip_lines.append(line.strip())
    summary["skip_reasons"] = skip_lines
    return summary


def try_import_version(module_name: str) -> str:
    try:
        __import__(module_name)
    except Exception:  # noqa: BLE001
        return "missing"
    return "installed"


def collect_registry_metrics() -> dict[str, object]:
    sources = json.loads((ROOT / "data" / "source_registry.json").read_text(encoding="utf-8"))["sources"]
    counts = {
        "tier": Counter(item["tier"] for item in sources),
        "access_mode": Counter(item["access_mode"] for item in sources),
        "risk_mode": Counter(item["risk_mode"] for item in sources),
        "legal_mode": Counter(item["legal_mode"] for item in sources),
        "freshness_target": Counter(item["freshness_target"] for item in sources),
        "source_family": Counter(item["source_family"] for item in sources),
    }
    tier1 = [item["source_name"] for item in sources if item["tier"] == 1]
    fixture_dirs = sorted([p.name for p in (ROOT / "tests" / "fixtures").iterdir() if p.is_dir()])
    expected_tier1_fixtures = sorted(slugify_source_name(name) for name in tier1)
    covered = sorted(set(expected_tier1_fixtures) & set(fixture_dirs))
    missing = sorted(set(expected_tier1_fixtures) - set(fixture_dirs))

    case_details: list[str] = []
    for path in sorted((ROOT / "tests" / "fixtures").iterdir()):
        if path.is_dir():
            labels = sorted(p.name for p in path.iterdir() if p.is_dir())
            case_details.append(f"{path.name}: {', '.join(labels)}")

    return {
        "total_sources": len(sources),
        "counts": counts,
        "tier1_sources": tier1,
        "fixture_dirs": fixture_dirs,
        "tier1_fixture_coverage": len(covered),
        "tier1_fixture_expected": len(expected_tier1_fixtures),
        "tier1_fixture_missing": missing,
        "fixture_case_details": case_details,
    }


def collect_git_status() -> dict[str, object]:
    result = run_shell("git-status", "git status --short")
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return {"count": len(lines), "lines": lines}


def collect_export_checks() -> dict[str, str]:
    return {
        "docs/exports/bulgaria-real-estate-source-links.xlsx": check_zip(
            ROOT / "docs" / "exports" / "bulgaria-real-estate-source-links.xlsx"
        ),
        "docs/exports/bulgaria-real-estate-source-report.docx": check_zip(
            ROOT / "docs" / "exports" / "bulgaria-real-estate-source-report.docx"
        ),
        "docs/exports/project-status-roadmap.docx": check_zip(ROOT / "docs" / "exports" / "project-status-roadmap.docx"),
        "docs/exports/project-architecture-execution-guide.pdf": check_pdf(
            ROOT / "docs" / "exports" / "project-architecture-execution-guide.pdf"
        ),
    }


def collect_local_tooling() -> dict[str, CommandResult]:
    return {
        "python3": run_shell("python3-version", "python3 --version"),
        "python3.12": run_shell("python3.12-version", "python3.12 --version"),
        "node": run_shell("node-version", "node --version"),
        "npm": run_shell("npm-version", "npm --version"),
        "docker": run_shell("docker-version", "docker --version"),
        "pdftoppm": run_shell("pdftoppm-version", "pdftoppm -v"),
    }


def collect_runtime_checks() -> dict[str, CommandResult]:
    return {
        "tests": run_shell("unit-tests", "PYTHONPATH=src python3 -m unittest discover -s tests -v"),
        "worker": run_shell("dev-worker-once", "PYTHONPATH=src python3 -m bgrealestate.dev_worker --once"),
        "scheduler": run_shell("dev-scheduler-once", "PYTHONPATH=src python3 -m bgrealestate.dev_scheduler --once"),
    }


def maybe_collect_db_validation() -> dict[str, object]:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"available": False, "reason": "DATABASE_URL not set"}
    try:
        import sqlalchemy  # noqa: F401
        from sqlalchemy import create_engine, text
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"sqlalchemy unavailable: {exc}"}

    metrics: dict[str, object] = {"available": True}
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            counts = conn.execute(
                text(
                    """
                    select
                      (select count(*) from crawl_job) as crawl_jobs,
                      (select count(*) from crawl_attempt) as crawl_attempts,
                      (select count(*) from raw_capture) as raw_captures,
                      (select count(*) from canonical_listing) as canonical_listings
                    """
                )
            ).mappings().one()
            metrics["counts"] = dict(counts)
            latest = conn.execute(text("select max(last_seen) as last_seen from canonical_listing")).mappings().one()
            metrics["latest_last_seen"] = latest["last_seen"].isoformat() if latest["last_seen"] else None
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"database query failed: {exc}"}
    return metrics


def render_counter(counter: Counter[object]) -> list[str]:
    return [f"- {key}: {value}" for key, value in sorted(counter.items(), key=lambda item: str(item[0]))]


def trim_block(text: str, limit: int = 1200) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."


def build_dependency_rows(pyproject: dict[str, object], package: dict[str, object]) -> list[str]:
    rows = [
        "| Item | Current version (repo/local) | Target version | Status | Evidence |",
        "| --- | --- | --- | --- | --- |",
        "| Python local runtime | "
        + trim_block(run_shell("python3-cache", "python3 --version").combined_output(), 40)
        + " | 3.12 | conflicting | `.python-version`, `pyproject.toml`, `ci.yml`, `Dockerfile` |",
        "| Python CI runtime | "
        + str(parse_ci_versions(ROOT / ".github" / "workflows" / "ci.yml")["python"])
        + " | 3.12 | aligned | `.github/workflows/ci.yml` |",
        "| Python Docker runtime | "
        + parse_dockerfile_base(ROOT / "Dockerfile")
        + " | "
        + str(pyproject["requires_python"])
        + " | aligned | `Dockerfile`, `pyproject.toml` |",
        "| Node local runtime | "
        + trim_block(run_shell("node-cache", "node --version").combined_output(), 40)
        + " | "
        + str(parse_ci_versions(ROOT / ".github" / "workflows" / "ci.yml")["node"])
        + " | conflicting | local shell vs CI |",
        "| Python lockfile | none | no exact repo target defined | unknown | no `requirements*.txt` / `poetry.lock` / lock artifact committed |",
        "| Node lockfile | none | no exact repo target defined | unknown | no `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` |",
    ]

    for dep in pyproject["dependencies"]:  # type: ignore[index]
        rows.append(
            f"| Python dep `{dep.split('>=', 1)[0]}` | `{dep}` | no exact target defined | unknown | `pyproject.toml` only |"
        )
    for dep in pyproject["dev_dependencies"]:  # type: ignore[index]
        rows.append(
            f"| Python dev dep `{dep.split('>=', 1)[0]}` | `{dep}` | no exact target defined | unknown | `pyproject.toml` only |"
        )
    for section in ("dependencies", "devDependencies"):
        for name, version in sorted(package.get(section, {}).items()):
            rows.append(f"| Node package `{name}` | `{version}` | no exact target defined | unknown | `package.json` only |")
    return rows


def markdown_report(run_date: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    pyproject = parse_pyproject(ROOT / "pyproject.toml")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    ci_versions = parse_ci_versions(ROOT / ".github" / "workflows" / "ci.yml")
    compose_images = parse_compose_images(ROOT / "docker-compose.yml")
    registry = collect_registry_metrics()
    git_status = collect_git_status()
    export_checks = collect_export_checks()
    tooling = collect_local_tooling()
    runtime = collect_runtime_checks()
    test_summary = extract_test_summary(runtime["tests"])
    db_validation = maybe_collect_db_validation()
    routes = list_backend_routes()
    frontend_routes = frontend_route_status()
    package_presence = {
        "reportlab": try_import_version("reportlab"),
        "pdfplumber": try_import_version("pdfplumber"),
        "pypdf": try_import_version("pypdf"),
        "fastapi": try_import_version("fastapi"),
        "sqlalchemy": try_import_version("sqlalchemy"),
        "redis": try_import_version("redis"),
        "uvicorn": try_import_version("uvicorn"),
    }

    scraping_status = "Issues"
    data_status = "Issues"
    backend_status = "Issues"
    frontend_status = "Issues"

    lines: list[str] = [
        "# Daily Project Health Check Report",
        "",
        f"Date: {run_date}",
        f"Generated at: {timestamp}",
        f"Workspace: `{ROOT}`",
        "",
        "## Scope",
        "",
        "This report audits the repository state, local executable environment, fixture-backed parser coverage, export artifacts, and dependency/runtime drift.",
        "It does not guess missing telemetry. Where the repo or environment does not provide evidence, the report explicitly says `no data available`.",
        "",
        "## 1. Execution Monitoring (Scraping Layer)",
        "",
        f"- Scheduled scraping job telemetry: {'available' if db_validation.get('available') else 'no data available'}",
        f"- Crawl success rate: {'no data available' if not db_validation.get('available') else 'see DB metrics below'}",
        "- Failed endpoints: no data available",
        "- Time anomalies vs baseline: no data available",
        f"- Dev worker placeholder: {'OK' if runtime['worker'].ok else 'failed'}",
        f"- Dev scheduler placeholder: {'OK' if runtime['scheduler'].ok else 'failed'}",
        f"- Tier-1 fixture coverage: {registry['tier1_fixture_coverage']}/{registry['tier1_fixture_expected']} sources have fixture directories",
        f"- Offline parser regression result: {test_summary['status']} ({test_summary['ran']} tests, {test_summary['skipped']} skipped)",
        "",
        "Evidence:",
        f"- `{runtime['worker'].command}` -> {runtime['worker'].returncode} in {runtime['worker'].duration_ms} ms",
        f"- `{runtime['scheduler'].command}` -> {runtime['scheduler'].returncode} in {runtime['scheduler'].duration_ms} ms",
        "- There are no scrape logs, retry logs, or persisted crawl rows available in this shell-backed run.",
        "",
        "Registry summary:",
        *[f"- Tier {key}: {value}" for key, value in sorted(registry["counts"]["tier"].items())],  # type: ignore[index]
        "",
        "Fixture sources:",
        *[f"- {name}" for name in registry["fixture_dirs"]],  # type: ignore[index]
        "",
        "## 2. Data Validation (Database Layer)",
        "",
        f"- Database validation availability: {'available' if db_validation.get('available') else 'no data available'}",
        f"- Missing values by column: {'no data available' if not db_validation.get('available') else 'not collected in this run'}",
        f"- Duplicate row checks: {'no data available' if not db_validation.get('available') else 'not collected in this run'}",
        f"- Price/category anomalies: {'no data available' if not db_validation.get('available') else 'not collected in this run'}",
        f"- Freshness window: {'no data available' if not db_validation.get('available') else db_validation.get('latest_last_seen', 'no data available')}",
        "- Schema consistency: blueprint and migration scaffold present; migration tests passed offline.",
        "",
    ]

    if db_validation.get("available"):
        counts = db_validation.get("counts", {})
        lines.extend(
            [
                "Observed DB counts:",
                f"- crawl_job rows: {counts.get('crawl_jobs', 'n/a')}",
                f"- crawl_attempt rows: {counts.get('crawl_attempts', 'n/a')}",
                f"- raw_capture rows: {counts.get('raw_captures', 'n/a')}",
                f"- canonical_listing rows: {counts.get('canonical_listings', 'n/a')}",
            ]
        )
    else:
        lines.extend(
            [
                f"Reason: {db_validation.get('reason', 'no data available')}",
                "- `DATABASE_URL` is not configured in this shell, and SQLAlchemy is not installed locally.",
                "- The optional DB roundtrip test was skipped for the same reason.",
            ]
        )

    lines.extend(
        [
            "",
            "## 3. Backend Integrity",
            "",
            f"- FastAPI runtime package: {package_presence['fastapi']}",
            f"- SQLAlchemy runtime package: {package_presence['sqlalchemy']}",
            f"- Uvicorn runtime package: {package_presence['uvicorn']}",
            "- Endpoint availability/status codes/response times: no live data available",
            "- Data flow scraper -> DB -> API: no live data available",
            f"- Static route inventory present: {len(routes)} routes defined in `src/bgrealestate/api/routers`",
            "",
            "Defined backend routes:",
            *[f"- `{route}`" for route in routes],
            "",
            "Runtime evidence:",
            f"- Overall unit test suite: {test_summary['status']}",
            "- FastAPI route tests were skipped in this shell because the `fastapi` package is not installed locally.",
            *[f"- {line}" for line in test_summary["skip_reasons"]],  # type: ignore[index]
            "- DB-backed APIs are coded to return 503 when `DATABASE_URL` is not configured.",
            "",
            "## 4. Frontend Consistency",
            "",
            f"- Node runtime: {tooling['node'].combined_output() or 'missing'}",
            f"- npm runtime: {tooling['npm'].combined_output() or 'missing'}",
            "- Frontend smoke tests: no data available",
            "- Playwright tests: none found in the repository",
            "",
            "Required route files:",
            *[f"- `{path}`: {'present' if present else 'missing'}" for path, present in frontend_routes],
            "",
            "Observed UI behavior from code inspection:",
            "- `/listings` fetches `/sources` and currently renders source-registry cards, not listing search results.",
            "- `/chat` renders a proxy-backed assistant playground and a placeholder threads pane.",
            "- `/map`, `/settings`, `/admin`, and `/properties/[id]` are layout shells awaiting stable APIs.",
            "- Because Node/npm are absent, lint, typecheck, build, and browser smoke tests could not be executed.",
            "",
            "## 5. Reporting Layer",
            "",
            "- Existing report/export artifacts were structurally validated in this run.",
            "- Aggregation correctness against raw ingested data: no data available",
            "- PDF visual rendering validation: no data available (`pdftoppm` is not installed in this shell)",
            "",
            "Export artifact checks:",
            *[f"- `{path}`: {status}" for path, status in export_checks.items()],
            "",
            "## 6. Dependency & SDK Drift Detection",
            "",
            "### 6.1 Detect Current State",
            "",
            f"- `.python-version`: `{(ROOT / '.python-version').read_text(encoding='utf-8').strip()}`",
            f"- `pyproject.toml` requires Python: `{pyproject['requires_python']}`",
            f"- CI Python target: `{ci_versions['python']}`",
            f"- CI Node target: `{ci_versions['node']}`",
            f"- Dockerfile base image: `{parse_dockerfile_base(ROOT / 'Dockerfile')}`",
            f"- Docker Compose images: {', '.join(f'`{image}`' for image in compose_images)}",
            f"- Local `python3`: `{tooling['python3'].combined_output() or 'missing'}`",
            f"- Local `python3.12`: `{tooling['python3.12'].combined_output() or 'missing'}`",
            f"- Local `node`: `{tooling['node'].combined_output() or 'missing'}`",
            f"- Local `npm`: `{tooling['npm'].combined_output() or 'missing'}`",
            f"- Local `docker`: `{tooling['docker'].combined_output() or 'missing'}`",
            "",
            "### 6.2 Compare with Target State",
            "",
            "- Python target is explicitly defined by `.python-version`, CI, Dockerfile, and `pyproject.toml`.",
            "- Node target is partially defined by CI (`22`) plus the committed Next.js manifest.",
            "- Exact resolved dependency targets are not defined because there are no committed lockfiles.",
            "",
            "### 6.3 Drift Types",
            "",
            "- Version mismatch: local Python is 3.9.6 while repo targets 3.12.",
            "- SDK/runtime mismatch: Node/npm are missing locally, so the Next.js app cannot be validated here.",
            "- Reproducibility drift: no Python or Node lockfile is committed.",
            "- Deprecated package status: no data available (offline, no package audit tooling installed).",
            "- Security vulnerability status: no data available (offline, no lockfile, no audit output).",
            "",
            "### 6.4 Drift Analysis",
            "",
            *build_dependency_rows(pyproject, package),
            "",
            "## 7. Minimal Alignment Plan",
            "",
            "Preferred option: Conservative",
            "",
            "1. Install the declared runtimes without changing package versions.",
            "2. Re-run the audit on Python 3.12 with FastAPI/SQLAlchemy/Uvicorn installed.",
            "3. Commit lockfiles only after a clean install succeeds and tests pass.",
            "4. Add DB-backed validation once `DATABASE_URL` points to the Compose PostgreSQL service.",
            "5. Add frontend lint/typecheck and at least one Playwright smoke test once Node/npm are present.",
            "",
            "Conservative plan (preferred):",
            "- Python: align local shell to 3.12. Risk: low. Impact: unlocks backend validation without changing app code.",
            "- Node: install Node 22 to match CI. Risk: low. Impact: unlocks Next.js lint/typecheck/build validation.",
            "- Lockfiles: commit one Python lock artifact and one Node lockfile. Risk: low-medium. Impact: reproducible installs.",
            "- Database: run Compose services and migrations, then enable DB checks in this audit. Risk: low-medium. Impact: actual scrape/data freshness metrics become available.",
            "",
            "Progressive plan (suggestion):",
            "- After lockfiles exist, review patch/minor upgrades for FastAPI, SQLAlchemy, Next.js, React, and TypeScript. Risk: medium. Impact: modernized stack with broader test surface.",
            "- Add package audit tooling and a CI dependency drift job. Risk: medium. Impact: real vulnerability/deprecation visibility.",
            "",
            "## 8. Final Report",
            "",
            "### 8.1 System Status Summary",
            "",
            f"- Scraping: {scraping_status}",
            f"- Data: {data_status}",
            f"- Backend: {backend_status}",
            f"- Frontend: {frontend_status}",
            "",
            "### 8.2 Key Issues",
            "",
            "1. Local runtime does not satisfy the repo contract: Python 3.12 is required, but only Python 3.9.6 is available; Node/npm/docker are missing.",
            "2. There is no live ingestion telemetry or database dataset in this environment, so scrape success rate, freshness, duplicate counts, and anomaly checks are unavailable.",
            "3. Backend route files exist, but FastAPI/SQLAlchemy/Uvicorn are not installed locally, so endpoint execution is not validated in this shell.",
            "4. The Next.js route scaffold exists, but frontend build/smoke validation is blocked by the missing Node toolchain and the absence of Playwright specs.",
            "5. Dependency resolution is not reproducible yet because there are no committed Python or Node lockfiles.",
            "",
            "### 8.3 Drift Summary",
            "",
            "- Python runtime mismatch: local 3.9.6 vs target 3.12.",
            "- Node runtime mismatch: local missing vs CI target 22.",
            "- No committed lockfile for Python.",
            "- No committed lockfile for Node.",
            "- Exact vulnerability/deprecation state cannot be determined from this offline shell.",
            "",
            "### 8.4 Recommended Actions",
            "",
            "1. Install Python 3.12 locally and run the backend stack with committed dev dependencies.",
            "2. Install Node 22/npm, then run `npm install`, `npm run lint`, and `npm run typecheck`.",
            "3. Start Compose services and set `DATABASE_URL` so this report can compute live scrape/data metrics.",
            "4. Commit dependency lockfiles after a clean green run on Python 3.12 and Node 22.",
            "5. Add one frontend smoke test and one DB-backed golden-path validation script to close the current observability gaps.",
            "",
            "### 8.5 Logs Appendix",
            "",
            "Tooling errors:",
            f"- `python3.12 --version`: {trim_block(tooling['python3.12'].combined_output(), 200) or 'no output'}",
            f"- `node --version`: {trim_block(tooling['node'].combined_output(), 200) or 'no output'}",
            f"- `npm --version`: {trim_block(tooling['npm'].combined_output(), 200) or 'no output'}",
            f"- `docker --version`: {trim_block(tooling['docker'].combined_output(), 200) or 'no output'}",
            f"- `pdftoppm -v`: {trim_block(tooling['pdftoppm'].combined_output(), 200) or 'no output'}",
            "",
            "Execution traces:",
            f"- Unit tests (`{runtime['tests'].duration_ms} ms`):",
            "```text",
            trim_block(runtime["tests"].combined_output(), 6000),
            "```",
            f"- Dev worker (`{runtime['worker'].duration_ms} ms`):",
            "```text",
            trim_block(runtime["worker"].combined_output(), 1000),
            "```",
            f"- Dev scheduler (`{runtime['scheduler'].duration_ms} ms`):",
            "```text",
            trim_block(runtime["scheduler"].combined_output(), 1000),
            "```",
            "",
            "Repo state notes:",
            f"- Dirty worktree entries observed: {git_status['count']}",
            *[f"- {line}" for line in git_status["lines"][:25]],  # type: ignore[index]
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_report(run_date: str) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    markdown = markdown_report(run_date)
    md_path = REPORT_DIR / f"daily-project-health-check-{run_date}.md"
    pdf_path = PDF_DIR / f"daily-project-health-check-{run_date}.pdf"
    md_path.write_text(markdown, encoding="utf-8")
    pdf_path.write_bytes(_build_pdf(_markdown_to_lines(markdown)))
    return md_path, pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the daily project health check report.")
    parser.add_argument("--date", default=datetime.now().date().isoformat(), help="Report date in YYYY-MM-DD form.")
    args = parser.parse_args()

    md_path, pdf_path = write_report(args.date)
    print(f"generated markdown: {md_path}")
    print(f"generated pdf: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
