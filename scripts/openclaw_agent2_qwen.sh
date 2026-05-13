#!/usr/bin/env bash
# One-shot OpenClaw Agent 2 (Qwen3 coder) → Telegram. Usage:
#   ./scripts/openclaw_agent2_qwen.sh "your prompt"
set -euo pipefail
TARGET="${TELEGRAM_ACTION1_TARGET:-181488201}"
PROFILE="${OPENCLAW_PROFILE:-codex}"
MSG="${1:?usage: $0 \"prompt for coding/automation\"}"
openclaw --profile "${PROFILE}" agent \
  --agent action1_qwen \
  --message "${MSG}" \
  --deliver \
  --reply-channel telegram \
  --reply-to "${TARGET}" \
  --timeout 1800
