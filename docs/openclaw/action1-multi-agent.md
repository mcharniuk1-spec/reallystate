# Action1 parallel OpenClaw agents (Ollama triad)

Use after operator **`Action1 ACCEPT`**. All three agents post to the **same Telegram main channel** (`181488201` by default).

Roles are **fixed in repo text only** (no diagram image in the repository). This matches the OpenClaw operating conclusion:

- **Agent 1 — `action1_gemma` (`ollama/gemma4:26b` or configured ops model)**: **orchestration**, **status/description** for operators, and **management** of cadence, priorities, and Telegram-facing summaries.
- **Agent 2 — `action1_qwen` (`ollama/qwen3-coder:30b`)**: primary **coding and automation** model — parsers, Makefile/CLI hooks, scraper/worker changes, concrete fixes implied by metrics and logs. Prefer Qwen for most implementation/continuation tasks.
- **Agent 3 — `action1_deepseek` (`ollama/deepseek-r1:8b`)**: **reasoning and heavy logic** — QA hypotheses, policy and registry alignment, mismatch and multi-unit analysis, price-integrity reasoning; cite `AGENTS.md` and `data/source_registry.json`.

## Model mapping (Codex profile `agents.list`)

| Agent id | Model | Role (summary) |
|----------|--------|------------------|
| `action1_gemma` | configured in `~/.openclaw-codex/openclaw.json` | Orchestration, descriptions, management / ops voice; current ops chat may use Qwen |
| `action1_qwen` | `ollama/qwen3-coder:30b` | Coding and automation |
| `action1_deepseek` | `ollama/deepseek-r1:8b` | Reasoning and heavy logic |

## One-shot dispatch (host)

**Inbound Telegram** to the ops chat (`181488201`) is routed to **`action1_gemma`** (Gemma4) via `bindings` in `~/.openclaw-codex/openclaw.json` — **Agent 1** responds first.

From repo root (batch snapshot to all three — use sparingly; agents run **sequentially**):

```bash
./scripts/action1_openclaw_triad.sh
```

**Selective handoffs** (same channel, different local model):

```bash
./scripts/openclaw_agent2_qwen.sh "Implement / fix: …"
./scripts/openclaw_agent3_deepseek.sh "Analyse mismatch / logic: …"
```

Escalation rules: `docs/openclaw/OLLAMA_MODEL_ESCALATION.md`.

If **`main`** (Telegram) lost context, fix is documented in `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md` (wrong OpenClaw workspace). Recovery turn:

```bash
make action1-openclaw-main-resume
```

Or manually: build the compact report (`make action1-telegram-report`), paste into three `openclaw --profile codex agent` runs with `--agent … --deliver --reply-channel telegram --reply-to 181488201`.

## +100 Telegram checkpoints

After live scrapes, poll (cron or scrape wrapper):

```bash
make action1-checkpoint-notify EXTRA_ARGS='--send --profile codex --target 181488201'
```

Uses `data/runs/action1_listing_json_total.txt` and `scripts/action1_full_telegram_report.py --compact`.

## References

- `docs/exports/taskforgema.md` — Action1 contract
- `docs/agents/TASKS.md` — `S1-22B`
- `scripts/action1_full_telegram_report.py` — matrix + quality stats
