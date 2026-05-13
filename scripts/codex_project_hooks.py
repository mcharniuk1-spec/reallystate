#!/usr/bin/env python3
"""Project guard hooks for Codex/Cursor agents.

The hooks are intentionally repo-local and dependency-free. They can be run as
one full preflight (`make codex-hooks`) or as a pre-command guard:

    python3 scripts/codex_project_hooks.py --command "make scrape-all-full"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


REPO = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Hook:
    hook_id: str
    owner: str
    title: str
    check: Callable[[], list[str]]


@dataclass(frozen=True)
class CommandRule:
    hook_id: str
    owner: str
    title: str
    pattern: re.Pattern[str]
    env_override: str
    message: str
    allow_if: Callable[[str], bool] | None = None


def _read(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


def _exists(path: str) -> bool:
    return (REPO / path).exists()


def _git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git_changed_files() -> list[str]:
    names: set[str] = set()
    for args in (["git", "diff", "--name-only"], ["git", "diff", "--cached", "--name-only"]):
        result = subprocess.run(args, cwd=REPO, text=True, capture_output=True, check=False)
        if result.returncode == 0:
            names.update(line.strip() for line in result.stdout.splitlines() if line.strip())
    return sorted(names)


def _git_staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _contains_all(path: str, required: Iterable[str]) -> list[str]:
    if not _exists(path):
        return [f"missing required file: {path}"]
    text = _read(path)
    return [f"{path} missing required text: {needle}" for needle in required if needle not in text]


def _staged_forbidden_files() -> list[str]:
    forbidden_patterns = (
        re.compile(r"(^|/)\.env($|\.)"),
        re.compile(r"^\.openclaw/"),
        re.compile(r"^data/scraped/.*/raw/"),
        re.compile(r"\.(dump|backup|sqlite|sqlite3|zip)$"),
    )
    allowed_names = {".env.example"}
    errors: list[str] = []
    for name in _git_staged_files():
        if name in allowed_names:
            continue
        if any(pattern.search(name) for pattern in forbidden_patterns):
            errors.append(f"staged forbidden file: {name}")
    return errors


def _scan_secret_literals(paths: Iterable[str]) -> list[str]:
    secret_patterns = (
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bAIza[0-9A-Za-z_-]{20,}"),
        re.compile(r"\bghp_[0-9A-Za-z]{20,}"),
        re.compile(r"\bglpat-[0-9A-Za-z_-]{20,}"),
        re.compile(r"BEGIN (RSA |OPENSSH |EC |DSA |)?PRIVATE KEY"),
        re.compile(r"(?i)\b(authorization:\s*bearer|x-api-key|api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}"),
    )
    allowed_fragments = ("example", "placeholder", "changeme", "${", "<", "your_", "REDACTED")
    skipped_prefixes = (
        "node_modules/",
        ".git/",
        "data/scraped/",
        "data/media/",
        "docs/exports/",
    )
    skipped_suffixes = ("/JOURNEY.md",)
    errors: list[str] = []
    for name in paths:
        if not name or name.startswith(skipped_prefixes) or name.endswith(skipped_suffixes):
            continue
        path = REPO / name
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lower = text.lower()
        if any(fragment.lower() in lower for fragment in allowed_fragments):
            # Still scan obvious private keys even in example files.
            key_patterns = secret_patterns[-2:-1]
            patterns = key_patterns
        else:
            patterns = secret_patterns
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                errors.append(f"{name}: suspicious secret literal near {match.group(0)[:32]}")
                break
    return errors


def hook_planner_dependency_integrity() -> list[str]:
    required = (
        "data_analyst` is the active evidence owner",
        "`BD-18` depends on `DA-01` plus unresolved `BD-11`",
        "Action1 ACCEPT",
        "Action0 now",
        "Action2 now",
    )
    return _contains_all("docs/agents/TASKS.md", required)


def hook_backend_accepted_only_import() -> list[str]:
    required = (
        "def _skip_reason(",
        "PENDING_QA",
        "UNKNOWN",
        "scrape_status\") == \"LOST\"",
        "scrape_acceptance_status\") == \"not_single_entity\"",
        "inactive",
        "crawl_provenance",
        "local_image_storage_keys",
    )
    return _contains_all("scripts/import_scraped_listings.py", required)


def hook_data_denominator_truth() -> list[str]:
    errors = []
    errors.extend(_contains_all("docs/agents/TASKS.md", ("### DA-02: Dashboard metric contract repair", "bad_and_grouped")))
    errors.extend(_contains_all("/Users/getapple/core/wiki/projects/real-estate-bulgaria/insights.md", ("Count Denominators Are Separate Product States",)))
    return errors


def hook_scraper_scope_and_identity() -> list[str]:
    errors = []
    errors.extend(_contains_all("data/source_registry.json", ("legal_mode", "risk_mode", "access_mode")))
    errors.extend(_contains_all("scripts/live_scraper.py", ("GROUPED_PUBLICATION", "not_single_entity", "PENDING_QA")))
    errors.extend(_contains_all("scripts/action1_dataset_quality_gate.py", ("accepted_single_entity_candidate",)))
    errors.extend(_contains_all("docs/agents/TASKS.md", ("Address.bg", "BulgarianProperties", "Homes.bg", "imot.bg", "LUXIMMO", "property.bg", "SUPRIMMO")))
    return errors


def hook_scraper_sm_consent_routes() -> list[str]:
    errors = []
    errors.extend(_contains_all("data/source_registry.json", ("consent_or_manual_only", "official_partner_or_vendor_only", "manual_consent_only")))
    if _exists("data/social_media_intelligence_candidates.json"):
        errors.extend(_contains_all("data/social_media_intelligence_candidates.json", ("consent", "blocked", "official_api")))
    errors.extend(_contains_all("docs/agents/scraper_sm/JOURNEY.md", ("No private/social/messenger scraping was added",)))
    return errors


def hook_ux_accepted_only_public_export() -> list[str]:
    return _contains_all(
        "scripts/generate_frontend_scraped_listings.py",
        (
            "def is_public_listing",
            "scrape_status\") == \"LOST\"",
            "needs_rescrape",
            "not_single_entity",
            "inactive",
            "removed",
            "expired",
        ),
    )


def hook_debugger_verifier_queue() -> list[str]:
    required = ("DBG-16", "DBG-20", "DBG-21", "DBG-22", "DBG-23")
    return _contains_all("docs/agents/TASKS.md", required)


def hook_ops_release_hygiene() -> list[str]:
    errors = []
    errors.extend(_contains_all(".gitignore", (".env", ".openclaw/", "data/scraped/**/raw/", "data/runs/*.log", "*.dump", "*.sqlite")))
    errors.extend(_staged_forbidden_files())
    changed = _git_changed_files()
    if changed:
        errors.extend(_scan_secret_literals(changed))
    return errors


def hook_infra_db_safety() -> list[str]:
    errors = []
    errors.extend(_contains_all("Makefile", ("backup-db:", "restore-db:", "verify-db-counts:")))
    errors.extend(_contains_all("docs/runbooks/server-db-migration.md", ("DATABASE_URL", "REMOTE_DATABASE_URL", "DB_DUMP", "No DB dump")))
    return errors


def hook_market_claim_gate() -> list[str]:
    return _contains_all(
        "docs/exports/market-intelligence-2026-05-13.md",
        ("Avoid complete-market", "95% coverage", "accepted-only DB counts"),
    )


def hook_user_analytics_privacy() -> list[str]:
    return _contains_all(
        "docs/analytics/user-event-taxonomy.md",
        (
            "No external analytics SDKs",
            "No raw chat messages",
            "No raw query text",
            "No image URLs",
            "unknown fields are rejected or dropped",
        ),
    )


def hook_vision_action0_gate() -> list[str]:
    return _contains_all(
        "docs/agents/TASKS.md",
        ("VM-02", "operator `Action0 now`", "Use only `local_image_files`", "no remote fetch"),
    )


def hook_entity_resolution_no_auto_merge() -> list[str]:
    return _contains_all(
        "docs/exports/entity-resolution-queue-plan-2026-05-13.md",
        ("accepted source publications first", "does not promote any record to `property_entity`", "grouped/development", "must not treat raw scrape volume"),
    )


def hook_knowledge_wiki_closeout() -> list[str]:
    errors = []
    errors.extend(_contains_all("docs/agents/knowledge_context_agent/JOURNEY.md", ("wiki", "memory", "insight")))
    errors.extend(_contains_all("/Users/getapple/core/wiki/projects/real-estate-bulgaria/log.md", ("[2026-05-13]",)))
    return errors


def hook_codex_hook_inventory() -> list[str]:
    errors = []
    errors.extend(_contains_all("codex-hooks/bgrealestate-hooks.json", ("planner.dependency_integrity", "knowledge.wiki_closeout")))
    errors.extend(_contains_all("docs/agents/codex-hooks.md", ("Hook Matrix", "Pre-Command Guard")))
    return errors


HOOKS: tuple[Hook, ...] = (
    Hook("planner.dependency_integrity", "planner", "task dependency and action-order integrity", hook_planner_dependency_integrity),
    Hook("backend.accepted_only_import", "backend_developer", "accepted-only import and provenance preservation", hook_backend_accepted_only_import),
    Hook("data.denominator_truth", "data_analyst", "count denominator separation", hook_data_denominator_truth),
    Hook("scraper_1.scope_identity", "scraper_1", "legal scope and source-publication identity", hook_scraper_scope_and_identity),
    Hook("scraper_sm.consent_routes", "scraper_sm", "consent/official route separation", hook_scraper_sm_consent_routes),
    Hook("ux.accepted_only_public_export", "ux_ui_designer", "public UI accepted-only export", hook_ux_accepted_only_public_export),
    Hook("debugger.verifier_queue", "debugger", "verifier queue and handoff coverage", hook_debugger_verifier_queue),
    Hook("ops.release_hygiene", "ops_release_manager", "secret/path release hygiene", hook_ops_release_hygiene),
    Hook("infra.db_safety", "infra_db_operator", "DB backup/restore/count safety", hook_infra_db_safety),
    Hook("market.claim_gate", "market_intelligence_analyst", "market claim evidence gate", hook_market_claim_gate),
    Hook("analytics.privacy", "user_analytics_agent", "first-party privacy-safe analytics", hook_user_analytics_privacy),
    Hook("vision.action0_gate", "vision_media_agent", "Action0 local-media-only gate", hook_vision_action0_gate),
    Hook("entity.no_auto_merge", "entity_resolution_agent", "accepted-only no-auto-merge contract", hook_entity_resolution_no_auto_merge),
    Hook("knowledge.wiki_closeout", "knowledge_context_agent", "wiki run/log/memory/insight closeout", hook_knowledge_wiki_closeout),
    Hook("codex.inventory", "knowledge_context_agent", "Codex hook inventory exists", hook_codex_hook_inventory),
)


def _allowed_dry_command(command: str) -> bool:
    lowered = command.lower()
    return "--dry-run" in lowered or "-dry" in lowered or " dry" in lowered


def _literal_secret_command(command: str) -> bool:
    patterns = (
        r"\bsk-[A-Za-z0-9_-]{20,}",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\bAIza[0-9A-Za-z_-]{20,}",
        r"(?i)\b(API_KEY|TOKEN|PASSWORD|SECRET|DATABASE_URL)\s*=\s*['\"]?[A-Za-z0-9_./:@+=-]{16,}",
        r"(?i)Authorization:\s*Bearer\s+[A-Za-z0-9_./+=-]{16,}",
        r"(?i)x-api-key:\s*[A-Za-z0-9_./+=-]{16,}",
    )
    allowed = ("${", "<", "REDACTED", "example", "placeholder")
    if any(fragment in command for fragment in allowed):
        return False
    return any(re.search(pattern, command) for pattern in patterns)


COMMAND_RULES: tuple[CommandRule, ...] = (
    CommandRule(
        "scraper_1.live_scrape_operator_gate",
        "scraper_1",
        "live scraping requires explicit operator env gate",
        re.compile(r"(make\s+(scrape-all-full|scrape-varna-full|action1-scrape-full-uncapped|scrape-bcpea)\b|scripts/live_scraper\.py|\bbgrealestate\s+scrape-(all|varna)-full\b)"),
        "CODEX_ALLOW_LIVE_SCRAPE",
        "live scrape command blocked; set CODEX_ALLOW_LIVE_SCRAPE=1 only after operator approval",
        allow_if=_allowed_dry_command,
    ),
    CommandRule(
        "scraper_1.media_backfill_gate",
        "scraper_1",
        "media backfill requires explicit operator env gate",
        re.compile(r"(make\s+backfill-scraped-media\b|backfill_scraped_media\.py)"),
        "CODEX_ALLOW_MEDIA_BACKFILL",
        "media backfill can download/write many files; set CODEX_ALLOW_MEDIA_BACKFILL=1 after approval",
        allow_if=_allowed_dry_command,
    ),
    CommandRule(
        "vision.action0_operator_gate",
        "vision_media_agent",
        "Action0 image reports require operator gate",
        re.compile(r"(property-image-reports|apartment-image-reports|Action0 now|s1-21-gemma-action0-eligible)"),
        "CODEX_ALLOW_ACTION0",
        "Action0 semantic media execution blocked until operator sends Action0 now",
        allow_if=lambda command: any(word in command for word in ("sed ", "rg ", "cat ", "tail ", "--help")),
    ),
    CommandRule(
        "scraper_1.action2_operator_gate",
        "scraper_1",
        "Action2 source expansion requires operator gate",
        re.compile(r"(Action2 now|S1-22C|remaining legal tier-1/2|Action2)"),
        "CODEX_ALLOW_ACTION2",
        "Action2 expansion blocked until operator sends Action2 now and Action1 QA passes",
        allow_if=lambda command: any(word in command for word in ("sed ", "rg ", "cat ", "tail ", "--help")),
    ),
    CommandRule(
        "backend.unsafe_import_flags",
        "backend_developer",
        "unsafe import include flags require explicit override",
        re.compile(r"import_scraped_listings\.py.*--include-(lost|grouped|inactive|unreviewed)"),
        "CODEX_ALLOW_UNSAFE_IMPORT",
        "unsafe import include flag blocked; default import must stay accepted-only",
    ),
    CommandRule(
        "ops.no_broad_git_add",
        "ops_release_manager",
        "broad git add is blocked",
        re.compile(r"\bgit\s+add\s+(-A|\.|:/)\b"),
        "CODEX_ALLOW_BROAD_GIT_ADD",
        "broad git add blocked; stage explicit safe files only",
    ),
    CommandRule(
        "ops.no_sensitive_git_add",
        "ops_release_manager",
        "sensitive path staging is blocked",
        re.compile(r"\bgit\s+add\b.*(\.env|\.openclaw|data/scraped/.*/raw|data/runs/|data/scraper\.log|\.dump|\.backup|\.sqlite|\.zip)"),
        "CODEX_ALLOW_SENSITIVE_STAGE",
        "sensitive path staging blocked; use release manager and explicit review",
    ),
    CommandRule(
        "infra.no_db_dump_commit",
        "infra_db_operator",
        "DB dumps/backups cannot be staged",
        re.compile(r"\bgit\s+add\b.*\.(dump|backup|sqlite|sqlite3)\b"),
        "CODEX_ALLOW_DB_ARTIFACT_STAGE",
        "DB artifact staging blocked",
    ),
)


def evaluate_command(command: str, *, env: dict[str, str] | None = None) -> list[str]:
    env = env or dict(os.environ)
    errors: list[str] = []
    if _literal_secret_command(command):
        errors.append("api_keys.literal_command_secret: command appears to contain a literal API key/token/password; use env vars or secret manager references")
    for rule in COMMAND_RULES:
        if not rule.pattern.search(command):
            continue
        if rule.allow_if and rule.allow_if(command):
            continue
        if env.get(rule.env_override) == "1":
            continue
        errors.append(f"{rule.hook_id}: {rule.message}")
    return errors


def run_hooks(selected: set[str] | None = None) -> dict[str, list[str]]:
    output: dict[str, list[str]] = {}
    for hook in HOOKS:
        if selected and hook.hook_id not in selected and hook.owner not in selected:
            continue
        output[hook.hook_id] = hook.check()
    return output


def _manifest() -> list[dict[str, str]]:
    return [
        {"id": hook.hook_id, "owner": hook.owner, "title": hook.title}
        for hook in HOOKS
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Bulgaria real estate Codex project hooks.")
    parser.add_argument("--hook", action="append", help="Run one hook id or owner. Repeatable.")
    parser.add_argument("--command", help="Evaluate a shell command as a pre-command guard.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--list", action="store_true", help="List hook inventory.")
    args = parser.parse_args(argv)

    if args.list:
        payload = _manifest()
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for item in payload:
                print(f"{item['id']} [{item['owner']}] - {item['title']}")
        return 0

    command_errors: list[str] = []
    if args.command:
        command_errors = evaluate_command(args.command)

    selected = set(args.hook or [])
    results = run_hooks(selected or None)
    failed = {hook_id: errors for hook_id, errors in results.items() if errors}

    if args.json:
        print(
            json.dumps(
                {
                    "command_errors": command_errors,
                    "hook_results": results,
                    "status": "FAIL" if command_errors or failed else "PASS",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for hook in HOOKS:
            if hook.hook_id not in results:
                continue
            errors = results[hook.hook_id]
            status = "FAIL" if errors else "PASS"
            print(f"{status} {hook.hook_id} [{hook.owner}] - {hook.title}")
            for error in errors:
                print(f"  - {error}")
        for error in command_errors:
            print(f"FAIL {error}")

    return 2 if command_errors or failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
