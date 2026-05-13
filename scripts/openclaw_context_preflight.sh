#!/usr/bin/env bash
# Emit an explicit "where we are" snapshot for OpenClaw ops: repo, git head, TASKS lines,
# recent JOURNEY tails, latest Telegram watcher log tail, optional gateway probe.
# Append full output to data/runs/openclaw_preflight.log (UTC timestamps).
#
# Usage:
#   ./scripts/openclaw_context_preflight.sh
#   FOCUS=telegram ./scripts/openclaw_context_preflight.sh    # shorter: logs + snapshot only
#   OPENCLAW_PROFILE=codex PROBE=1 ./scripts/openclaw_context_preflight.sh
#
# FOCUS: all (default) | tasks | scrape | telegram

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Avoid shell globs and broad glob.glob() over data/runs (can stall with huge directories).
_pick_latest_run_log() {
  python3 -c '
import os, sys
root = sys.argv[1]
prefix, suffix = sys.argv[2], sys.argv[3]
d = os.path.join(root, "data", "runs")
best_p, best_t = "", -1.0
try:
    with os.scandir(d) as it:
        for e in it:
            if not e.is_file(follow_symlinks=False):
                continue
            n = e.name
            if not (n.startswith(prefix) and n.endswith(suffix)):
                continue
            try:
                t = e.stat().st_mtime
            except OSError:
                continue
            if t > best_t:
                best_t, best_p = t, e.path
except FileNotFoundError:
    pass
print(best_p)
' "$ROOT" "$1" "$2"
}

# Short block for Telegram / rehydrate (keep under ~2.2k chars). All Python: avoids pipe buffering stalls.
if [[ "${1:-}" == "--compact" ]]; then
  export OPENCLAW_PREFLIGHT_ROOT="$ROOT"
  python3 - <<'PY'
import os, subprocess
from datetime import datetime, timezone

root = os.environ.get("OPENCLAW_PREFLIGHT_ROOT", os.getcwd())
max_len = 2200
buf = []
def out(s: str) -> None:
    buf.append(s)

out("Preflight (compact) " + datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
out("ROOT=" + root)
try:
    h = subprocess.check_output(
        ["git", "-C", root, "rev-parse", "--short", "HEAD"],
        timeout=3,
        stderr=subprocess.DEVNULL,
    ).decode().strip()
    out(h)
except Exception:
    out("(git n/a)")
out("--- TASKS (grep, first 400 lines only) ---")
tasks_p = os.path.join(root, "docs/agents/TASKS.md")
try:
    with open(tasks_p, encoding="utf-8", errors="replace") as f:
        chunk = []
        for i, line in enumerate(f):
            if i >= 400:
                break
            chunk.append(line)
    text = "".join(chunk)
    matches = [
        ln for ln in text.splitlines()
        if any(k in ln for k in ("IN_PROGRESS", "TODO", "BLOCKED", "PENDING"))
    ]
    for line in matches[:24]:
        out(line)
except Exception as e:
    out("(TASKS read failed: " + str(e) + ")")
out("--- watcher log tail ---")
wl = os.path.join(root, "data/runs/action1_telegram_watch_detached_LATEST.log")

def tail_lines(path, n, read_chunk=65536):
    try:
        size = os.path.getsize(path)
    except OSError:
        return []
    try:
        with open(path, "rb") as f:
            if size > read_chunk:
                f.seek(max(0, size - read_chunk))
            data = f.read().decode("utf-8", errors="replace")
        return data.splitlines()[-n:]
    except OSError:
        return []

if os.path.isfile(wl):
    out("file=" + wl)
    for line in tail_lines(wl, 10):
        out(line)
else:
    out("(no action1_telegram_watch_detached_LATEST.log — run: make action1-telegram-watch-detached)")
out("--- scraper_1 JOURNEY (tail 8) ---")
jp = os.path.join(root, "docs/agents/scraper_1/JOURNEY.md")
try:
    if os.path.isfile(jp) and os.path.getsize(jp) > 512_000:
        for line in tail_lines(jp, 8, read_chunk=256_000):
            out(line)
    elif os.path.isfile(jp):
        with open(jp, encoding="utf-8", errors="replace") as f:
            jlines = f.readlines()
        for line in jlines[-8:]:
            out(line.rstrip("\n"))
    else:
        out("(missing JOURNEY)")
except Exception:
    out("(missing JOURNEY)")
body = "\n".join(buf)
print(body[:max_len] + ("\n" if len(body) > max_len else ""))
PY
  exit 0
fi

LOG="${OPENCLAW_PREFLIGHT_LOG:-$ROOT/data/runs/openclaw_preflight.log}"
FOCUS="${FOCUS:-all}"
PROBE="${PROBE:-0}"
PROFILE="${OPENCLAW_PROFILE:-codex}"
STAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$(dirname "$LOG")"

section() { printf '\n── %s ──\n' "$1"; }

emit_tasks() {
  section "TASKS (status lines)"
  if [[ -f "$ROOT/docs/agents/TASKS.md" ]]; then
    head -n 2000 "$ROOT/docs/agents/TASKS.md" 2>/dev/null | grep -E 'IN_PROGRESS|TODO|PENDING|BLOCKED|VERIFIED|DONE|slice|S1-22' 2>/dev/null | head -50 || true
  else
    echo "(missing docs/agents/TASKS.md)"
  fi
}

emit_journeys() {
  section "JOURNEY tails (last 18 lines each)"
  for j in "$ROOT/docs/agents/backend_developer/JOURNEY.md" \
           "$ROOT/docs/agents/scraper_1/JOURNEY.md" \
           "$ROOT/docs/agents/debugger/JOURNEY.md"; do
    if [[ -f "$j" ]]; then
      echo ">>> $j"
      tail -n 18 "$j"
    fi
  done
}

emit_scrape_runs() {
  section "Latest scrape metrics tail"
  if [[ -f "$ROOT/data/runs/scrape_metrics_latest.json" ]]; then
    tail -c 4000 "$ROOT/data/runs/scrape_metrics_latest.json" 2>/dev/null || true
  else
    echo "(no data/runs/scrape_metrics_latest.json)"
  fi
  section "Latest action1 uncapped log (tail 12)"
  latest="$ROOT/data/runs/action1_scrape_uncapped_detached_LATEST.log"
  if [[ -f "$latest" ]]; then
    echo "file=$latest"
    tail -n 12 "$latest"
  else
    fb="$(_pick_latest_run_log "action1_scrape_uncapped_detached_" ".log")"
    fb="${fb:-$(_pick_latest_run_log "action1_scrape_uncapped_" ".log")}"
    if [[ -n "${fb:-}" ]]; then
      echo "file=$fb (no LATEST symlink; consider restarting detached runner)"
      tail -n 12 "$fb"
    else
      echo "(no scrape uncapped log)"
    fi
  fi
}

emit_telegram() {
  section "Telegram watcher log (tail 20)"
  latest="$ROOT/data/runs/action1_telegram_watch_detached_LATEST.log"
  if [[ -f "$latest" ]]; then
    echo "file=$latest"
    tail -n 20 "$latest"
  else
    fb="$(_pick_latest_run_log "action1_telegram_watch_detached_" ".log")"
    if [[ -n "${fb:-}" ]]; then
      echo "file=$fb (no LATEST symlink)"
      tail -n 20 "$fb"
    else
      echo "(no watcher log; run: make action1-telegram-watch-detached)"
    fi
  fi
  section "Last RUNNING snapshot file (head)"
  snap="$ROOT/data/runs/action1_last_running_snapshot.json"
  if [[ -f "$snap" ]]; then
    head -c 2500 "$snap"
    echo ""
    [[ $(wc -c <"$snap") -gt 2500 ]] && echo "…(truncated)"
  else
    echo "(no action1_last_running_snapshot.json)"
  fi
}

emit_probe() {
  section "openclaw gateway probe"
  if command -v openclaw >/dev/null 2>&1; then
    openclaw --profile "$PROFILE" gateway probe 2>&1 || true
  else
    echo "(openclaw not on PATH)"
  fi
}

body() {
  echo "OpenClaw context preflight — $STAMP"
  section "REPO"
  echo "ROOT=$ROOT"
  (cd "$ROOT" && git rev-parse --short HEAD 2>/dev/null && git status -sb 2>/dev/null | head -5) || echo "(not a git repo or git unavailable)"

  case "$FOCUS" in
    tasks)
      emit_tasks
      ;;
    scrape)
      emit_scrape_runs
      ;;
    telegram)
      emit_telegram
      ;;
    all|*)
      emit_tasks
      emit_journeys
      emit_scrape_runs
      emit_telegram
      ;;
  esac

  if [[ "$PROBE" == "1" ]]; then
    emit_probe
  fi

  section "Hints"
  echo "Problem: wrong source scope → data/source_registry.json + docs/openclaw/scrape-taxonomy-a1-a12.md"
  echo "Problem: empty stats → scripts/action1_full_telegram_report.py (--pulse if timeouts)"
  echo "Problem: agent can't see repo → docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md (workspace path)"
}

OUT="$(body)"
printf '%s\n' "$OUT"
printf '\n[%s] --- preflight ---\n%s\n' "$STAMP" "$OUT" >>"$LOG"
