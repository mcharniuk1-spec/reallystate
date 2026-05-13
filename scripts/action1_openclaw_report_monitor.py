#!/usr/bin/env python3
"""
Every INTERVAL seconds: generate Action1 --running-line report, send via OpenClaw to Telegram,
log results. Exit after STOP_AFTER_SUCCESS_STREAK consecutive successful sends (openclaw JSON ok=true).

Uses subprocess timeout so openclaw cannot hang indefinitely (macOS has no GNU timeout by default).

Usage:
  cd repo && python3 scripts/action1_openclaw_report_monitor.py
  ACTION1_TG_INTERVAL_SEC=300 STOP_AFTER_SUCCESS_STREAK=5 python3 scripts/action1_openclaw_report_monitor.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PY = ROOT / "scripts" / "action1_full_telegram_report.py"
LOG_PATH = ROOT / "data" / "runs" / "action1_report_monitor.log"
STATE_PATH = ROOT / "data" / "runs" / "action1_report_monitor_state.json"
ENABLED_FILE = Path(
    os.environ.get("ACTION1_REPORTER_ENABLED_FILE", str(ROOT / "data" / "runs" / "action1_reporter_enabled"))
)
LOCK_FILE = Path(
    os.environ.get("ACTION1_REPORTER_LOCK_FILE", str(ROOT / "data" / "runs" / "action1_reporter.lock"))
)

INTERVAL = int(os.environ.get("ACTION1_TG_INTERVAL_SEC", "300"))
STOP_STREAK = int(os.environ.get("STOP_AFTER_SUCCESS_STREAK", "5"))
PROFILE = os.environ.get("OPENCLAW_PROFILE", "codex")
TARGET = os.environ.get("OPENCLAW_TARGET", "181488201")
OPENCLAW_TIMEOUT = int(os.environ.get("OPENCLAW_SEND_TIMEOUT_SEC", "180"))
DRY_RUN = os.environ.get("DRY_RUN", "").strip() not in ("", "0", "false")

TOTAL_RE = re.compile(r"Total\(7\)=(\d+)")


def log(msg: str) -> None:
    ts = datetime.now(tz=timezone.utc).isoformat()
    line = f"[{ts}] {msg}\n"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)
    print(line, end="")


def build_report() -> str | None:
    try:
        r = subprocess.run(
            [sys.executable, str(REPORT_PY), "--running-line", "--write-snapshot"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        log("ERROR build_report: subprocess timeout")
        return None
    if r.returncode != 0:
        log(f"ERROR build_report exit={r.returncode} stderr={r.stderr[:800]!s}")
        return None
    return r.stdout.strip()



def parse_total(report: str) -> int | None:
    m = TOTAL_RE.search(report)
    if not m:
        return None
    return int(m.group(1))


def send_telegram(message: str) -> tuple[bool, str]:
    if not ENABLED_FILE.exists():
        # Allow cron/launchd to run safely without spamming: treat disabled reporter as success.
        log(f"reporter disabled (missing {ENABLED_FILE}); skipping openclaw send")
        return True, '{"skipped": "reporter_disabled"}'
    # Single-instance lock: if a detached watcher is active, a cron/launchd monitor should not also send.
    try:
        if LOCK_FILE.exists():
            pid_text = LOCK_FILE.read_text(encoding="utf-8").strip()
            if pid_text.isdigit():
                pid = int(pid_text)
                # kill(pid, 0) equivalent without importing signal: rely on os.kill
                import os as _os

                try:
                    _os.kill(pid, 0)
                    log(f"reporter lock present (pid={pid}); skipping openclaw send")
                    return True, '{"skipped": "reporter_locked"}'
                except OSError:
                    pass
    except Exception:
        pass
    if DRY_RUN:
        log("DRY_RUN: skip openclaw send")
        return True, '{"dryRun": true}'
    try:
        proc = subprocess.run(
            [
                "openclaw",
                "--profile",
                PROFILE,
                "message",
                "send",
                "--channel",
                "telegram",
                "--target",
                TARGET,
                "--message",
                message,
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=OPENCLAW_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, f"openclaw timeout after {OPENCLAW_TIMEOUT}s"

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        hint = ""
        if "EPERM" in combined or "operation not permitted" in combined.lower():
            hint = (
                " HINT: openclaw needs write access to ~/.openclaw-codex — run this monitor "
                "from Terminal.app (full macOS permissions), not a restricted sandbox."
            )
        return False, (combined[-3500:] + hint)

    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return False, combined[-3500:]
    payload = data.get("payload") or {}
    ok = payload.get("ok") is True
    return ok, proc.stdout or ""


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"success_streak": 0, "last_total": None}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"success_streak": 0, "last_total": None}


def save_state(st: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(st, indent=2), encoding="utf-8")


def run_loop(*, once: bool = False) -> None:
    log(
        f"start interval={INTERVAL}s stop_after_streak={STOP_STREAK} "
        f"profile={PROFILE} target={TARGET} openclaw_timeout={OPENCLAW_TIMEOUT}s dry={DRY_RUN} once={once}"
    )
    st = load_state()

    while True:
        report = build_report()
        if not report:
            st["success_streak"] = 0
            save_state(st)
            if once:
                break
            time.sleep(INTERVAL)
            continue
        total = parse_total(report)
        ok, detail = send_telegram(report)
        prev = st.get("last_total")
        if ok:
            st["success_streak"] = int(st.get("success_streak") or 0) + 1
            log(
                f"SEND_OK streak={st['success_streak']}/{STOP_STREAK} total(7)={total} "
                f"(prev_total={prev}) payload_tail={detail[:200]!s}"
            )
        else:
            st["success_streak"] = 0
            log(f"SEND_FAIL reset streak total(7)={total} detail={detail[-1200:]!s}")

        st["last_total"] = total
        st["last_ok"] = ok
        st["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        save_state(st)

        if ok and int(st["success_streak"]) >= STOP_STREAK:
            log(f"STOP: reached {STOP_STREAK} consecutive successful Telegram sends.")
            break

        if once:
            break

        time.sleep(INTERVAL)


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Action1 OpenClaw Telegram report monitor")
    p.add_argument(
        "--once",
        action="store_true",
        help="Send one report and exit (for testing from a full-permission shell).",
    )
    args = p.parse_args()
    run_loop(once=args.once)


if __name__ == "__main__":
    main()
