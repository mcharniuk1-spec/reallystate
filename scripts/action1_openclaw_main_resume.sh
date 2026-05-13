#!/usr/bin/env bash
# One-shot: OpenClaw `main` with repo workspace + Action1 bootstrap (after fixing openclaw.json).
# Posts reply to Telegram main channel. Use when a session "lost" taskforgema context.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TARGET="${TELEGRAM_ACTION1_TARGET:-181488201}"
PROFILE="${OPENCLAW_PROFILE:-codex}"

BOOT="$(head -c 4000 "$ROOT/docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md" 2>/dev/null || true)"
TASK="$(grep -n 'Action1' "$ROOT/docs/exports/taskforgema.md" | head -3 || true)"

MSG="${BOOT}

---
**Operator directive**: Continue Action1 per prior instructions. You must NOT ask for Address.bg / LUXIMMO / property.bg / SUPRIMMO URLs or scraper patterns — \`primary_url\` values live in \`data/source_registry.json\`; execution is \`make scrape-all-full\` with the seven sources after \`Action1 ACCEPT\`.

If scrape is already running, only: (1) \`tail\` the latest \`data/runs/action1_*.log\`, (2) \`make action1-telegram-report\` or \`make action1-checkpoint-notify EXTRA_ARGS='--send'\` on +100 milestones, (3) report blockers from logs — no invented \"deep-scraper\".

taskforgema.md pointers:
${TASK}"

openclaw --profile "${PROFILE}" agent \
  --agent main \
  --message "${MSG}" \
  --deliver \
  --reply-channel telegram \
  --reply-to "${TARGET}" \
  --timeout 900
