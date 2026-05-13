#!/usr/bin/env bash
# One-shot OpenClaw Agent 3 (DeepSeek R1) → Telegram. Usage:
#   ./scripts/openclaw_agent3_deepseek.sh "your prompt"
set -euo pipefail
TARGET="${TELEGRAM_ACTION1_TARGET:-181488201}"
PROFILE="${OPENCLAW_PROFILE:-codex}"
MSG="${1:?usage: $0 \"prompt for reasoning / mismatch analysis\"}"
openclaw --profile "${PROFILE}" agent \
  --agent action1_deepseek \
  --message "${MSG}" \
  --deliver \
  --reply-channel telegram \
  --reply-to "${TARGET}" \
  --timeout 1800
