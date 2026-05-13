#!/usr/bin/env bash
# Dispatch three Action1 OpenClaw agents (Gemma / Qwen / DeepSeek) to Telegram main channel.
# Run from repo root. Requires: openclaw (codex profile), Ollama models up, gateway healthy.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TARGET="${TELEGRAM_ACTION1_TARGET:-181488201}"
PROFILE="${OPENCLAW_PROFILE:-codex}"

REPORT="$(python3 scripts/action1_full_telegram_report.py --compact)"
# Keep agent prompts under ~6k chars for CLI stability
if [ "${#REPORT}" -gt 4000 ]; then
  REPORT="${REPORT:0:4000}"$'\n\n…(report truncated for agent prompt)'
fi

BOOTSTRAP=""
if [[ -f "$ROOT/docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md" ]]; then
  BOOTSTRAP="$(head -c 3200 "$ROOT/docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md")"$'\n\n---\n'
fi

run_agent() {
  local agent_id="$1"
  local role_block="$2"
  local msg
  msg="${BOOTSTRAP}${role_block}"$'\n\n--- DATA SNAPSHOT (Action1, 7 sources × 4 buckets) ---\n'"${REPORT}"$'\n\nReply in Telegram: ≤12 short bullets + 1 line "Next:". Do not invent counts beyond the snapshot. Never ask the operator for source URLs or CSS patterns — they are in data/source_registry.json and the repo parsers.'
  openclaw --profile "${PROFILE}" agent \
    --agent "${agent_id}" \
    --message "${msg}" \
    --deliver \
    --reply-channel telegram \
    --reply-to "${TARGET}"
}

GEMMA_ROLE="You are **action1_gemma** (ollama/gemma4:26b), **Agent 1**. Fixed role: primary **orchestration**, **description** (clear status for operators), and **management** of Action1 (S1-22B) — priorities, cadence, Telegram summaries. Do not take on implementation or deep proof work that belongs to Agent 2/3."

QWEN_ROLE="You are **action1_qwen** (ollama/qwen3-coder:30b), **Agent 2**. Fixed role: **coding and automation** — Makefile/CLI, parsers, gallery/media pipelines, scraper fixes driven by the snapshot and logs. Propose concrete repo changes; stay execution-focused."

DS_ROLE="You are **action1_deepseek** (ollama/deepseek-r1:8b), **Agent 3**. Fixed role: **reasoning and heavy logic** — QA hypotheses, policy/registry alignment (\`AGENTS.md\`, \`data/source_registry.json\`), mismatches, multi-unit and price-integrity analysis. Cite rules; do not rewrite production code unless trivial."

echo "Note: parallel runs can overload the local gateway/Ollama; this script runs agents **sequentially** for reliable Telegram delivery."

run_agent "action1_gemma" "${GEMMA_ROLE}"
run_agent "action1_qwen" "${QWEN_ROLE}"
run_agent "action1_deepseek" "${DS_ROLE}"
echo "Triad dispatch finished."
