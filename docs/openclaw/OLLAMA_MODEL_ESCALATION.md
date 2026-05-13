# Ollama model escalation (OpenClaw — Bulgaria RE)

**Default (Agent 1):** **`ollama/gemma4:26b`** — orchestration, status, management, Telegram narration *when configured that way*.

**Operator override (this deployment):** the Telegram-bound agent id **`action1_gemma`** is configured in `~/.openclaw-codex/openclaw.json` to run **`ollama/qwen3-coder:30b`** so inbound ops chat stays on the coding/automation model without handoffs. Triad docs still describe roles; the **local model id** is authoritative in `openclaw.json`.

**Escalate to Agent 2 — Qwen (`ollama/qwen3-coder:30b`)** when the work is **coding or automation**: patches, parsers, Makefile/CLI, scraper modules, refactors, multi-file edits, or “write the command/script” requests.

**Escalate to Agent 3 — DeepSeek (`ollama/deepseek-r1:8b`)** when you need **heavy reasoning**: logic mismatches, policy/registry interpretation, multi-unit vs single-unit judgment, contradiction hunting, formal QA hypotheses — especially when Gemma’s first pass is uncertain.

## How to invoke (host CLI)

Gemma is the **default** for Telegram on the ops peer when `bindings` in `~/.openclaw-codex/openclaw.json` route that chat to `action1_gemma`. For explicit one-shot turns:

```bash
# Agent 1 (default voice)
openclaw --profile codex agent --agent action1_gemma --message "…" --deliver --reply-channel telegram --reply-to "${TELEGRAM_ACTION1_TARGET:-181488201}"

# Agent 2 — coding
openclaw --profile codex agent --agent action1_qwen --message "…" --deliver --reply-channel telegram --reply-to "${TELEGRAM_ACTION1_TARGET:-181488201}"

# Agent 3 — deep analysis
openclaw --profile codex agent --agent action1_deepseek --message "…" --deliver --reply-channel telegram --reply-to "${TELEGRAM_ACTION1_TARGET:-181488201}"
```

Shortcut: `./scripts/action1_openclaw_triad.sh` runs **all three in order** with the same data snapshot (use after milestones, not every message).

**Default inbound Telegram (ops chat):** OpenClaw `bindings` route the main Telegram peer to **`action1_gemma`**. The **model string** for that agent id is whatever is set under `agents.list` (here: **`ollama/qwen3-coder:30b`**). For ad-hoc **separate** coding or reasoning turns from the host shell, use `./scripts/openclaw_agent2_qwen.sh "…"` and `./scripts/openclaw_agent3_deepseek.sh "…"`.

## Gemma (Agent 1) behaviour

- Answer first; keep replies actionable and short for Telegram.
- If you would need to **edit repo files** or **design non-trivial code**, stop and either ask the operator to run the **Qwen** line above or state: **“Handoff: Agent 2 (Qwen) required for coding.”**
- If the question is **why two metrics disagree**, **whether a page violates AGENTS.md**, or **root-cause of a logic mismatch**, state: **“Handoff: Agent 3 (DeepSeek) suggested for reasoning.”** Then optionally wait for a follow-up invocation of DeepSeek with the same context.

## Config reference

- Agents: `~/.openclaw-codex/openclaw.json` → `agents.list` (`action1_gemma`, `action1_qwen`, `action1_deepseek`).
- Telegram → Gemma: `bindings` with `match.channel: "telegram"` and `match.peer` for the ops chat. **Positive numeric IDs** are **direct-message threads** with the bot: use `peer.kind: "dm"` (or `"direct"`) and `id: "181488201"`. **Supergroups** use negative IDs (often `-100…`): use `peer.kind: "group"`. A common failure mode is binding `181488201` as `group`, which routes **no inbound** messages to `action1_gemma`. Add `channels.telegram.dmPolicy` + `allowFrom` if DMs are not open. Verify with `openclaw agents list --bindings` (use `gateway probe --timeout 30000 --token …` if the default probe times out while the gateway is busy).
- Repo contract: `docs/openclaw/action1-multi-agent.md`, `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`.
