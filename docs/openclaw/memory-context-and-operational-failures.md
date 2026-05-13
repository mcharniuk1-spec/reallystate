# Why OpenClaw “loses memory”, drops tasks, or shows empty stats

This document separates **facts** (observable in this repo and runtime) from **interpretations** (likely causes) so operators and agents stop confusing LLM behavior with project state.

## FACT — What project memory actually is

| Store | Role |
|--------|------|
| **`docs/agents/TASKS.md`** | Single queue of slices and statuses — authoritative for “what is next”. |
| **`docs/agents/*/JOURNEY.md`** | Append-only execution logs per agent — authoritative for “what already happened”. |
| **`data/runs/*.log`, `*.pid`, snapshots** | Host process and reporting artifacts (Telegram watcher, scrapers, `action1_last_running_snapshot.json`). |
| **Telegram thread** | Human-visible history only; the model does not automatically reload every file each turn. |
| **OpenClaw agent config** (`~/.openclaw-codex/openclaw.json`) | Routes inbound Telegram to an **agent id**, model id, skills paths — not a copy of TASKS.md. |

The **LLM** does not have a durable database of your tasks. Each completion is bounded by **context window**, **which files were read this turn**, and **whether the gateway/session restarted**. Anything not loaded from disk or pasted into the prompt is **not** guaranteed to persist in the model’s head across turns.

## FACT — Symptom classes seen in this project

1. **“No stats” / timeout lines in Telegram**  
   Reporting scripts walked **very large** `data/scraped/**/listings/*.json` trees; subprocess or compact paths hit **time limits** before producing output. That is **not** OpenClaw forgetting — it is **compute + I/O** finishing too late. Mitigations: faster report path (`--pulse`), higher timeouts, parallel scan (see `scripts/action1_full_telegram_report.py`).

2. **`main` workspace ≠ repo root**  
   If OpenClaw **`main`** uses `~/.openclaw/workspace-codex`, tools cannot read `AGENTS.md`, `docs/exports/taskforgema.md`, etc. The model may **hallucinate** missing docs or URLs. Fix: workspace = `/Users/getapple/Documents/Real Estate Bulg` (see `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`).

3. **`openclaw message send` fails with EPERM / plugin errors**  
   CLI writes under **`~/.openclaw-codex/`**. Sandboxed or locked-down environments block that — sends fail even though the repo is fine. Fix: run sends from a full-permission shell on the host.

4. **Ollama timeouts / “couldn’t generate”**  
   Local model calls exceed provider timeout or GPU stalls. Fix: raise `models.providers.ollama.timeoutSeconds`, restart gateway (`docs/openclaw/README.md`).

5. **Operator expects continuity across days**  
   New chat, cleared thread, or different **agent id** ⇒ no automatic inheritance of yesterday’s reasoning. **TASKS.md / JOURNEY.md** still hold truth; the model must **read them again**.

## INTERPRETATION — Why it *feels* like memory loss

- **Confusing “assistant recall” with “git truth”**: The assistant may summarize incorrectly unless it **re-reads** TASKS and the relevant JOURNEY tail this session.
- **Implicit tasks**: If work exists only in chat, it is **not** in TASKS.md → the next run has no durable anchor.
- **Large corpus + short timeouts**: Empty or partial Telegram body reads as “forgot to report” instead of “report subprocess timed out”.

## INTERPRETATION — OpenClaw-specific gaps

- **Delivery vs understanding**: `message send` can succeed while the **inbound** agent never received the same text as structured memory — two different paths.
- **Long `agent --deliver` / deliver hangs**: Ops moved to **message send** + file-backed reports for reliability (`action1_telegram_ops_rehydrate.sh`).
- **Skills list ≠ loaded context**: Listing `agent-skills/` in config does not inject full file contents; agents still need **explicit read** of contracts (`taskforgema.md`, bootstrap).

## Operational protocol — explicit steps and checks

1. **Before narrating scrape progress**  
   Run file-backed metrics (host):  
   `python3 scripts/action1_full_telegram_report.py --running-line`  
   or, if the corpus is huge and timeboxed: `--pulse` or raise `ACTION1_TG_FULL_TIMEOUT_SEC`.  
   **Do not** freestyle counts.

2. **Before claiming task status**  
   Open **`docs/agents/TASKS.md`** and the owning agent’s **`JOURNEY.md`** and cite the current slice / last entry.

3. **After meaningful work**  
   Append to **`JOURNEY.md`** and update **TASKS.md** status — same activation checklist as `AGENTS.md`.

4. **When debugging “lost context”**  
   Run **`make openclaw-preflight`** (or `scripts/openclaw_context_preflight.sh`) and paste or Telegram the output so **previous steps** and **host logs** are explicit.

5. **Problem-shaped checks** (which artifact to trust)

   | Problem | Read first | Verify |
   |---------|------------|--------|
   | Wrong scope / illegal sources | `data/source_registry.json`, `docs/openclaw/scrape-taxonomy-a1-a12.md` | `legal_mode` / Action1 = A1 only |
   | Bad listing stats | `scripts/action1_full_telegram_report.py`, `data/runs/action1_*` | Timeout? Use `--pulse` |
   | “Agent forgot Action1 docs” | Workspace path, `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md` | `main` workspace |
   | Queue drift | `docs/agents/TASKS.md` | Slice owner + dependency |

## Related docs

- `docs/openclaw/README.md` — gateway, Ollama, Telegram patterns  
- `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md` — workspace + seven sources  
- `agent-skills/openclaw-ollama-gemma4/SKILL.md` — session continuity + step logging  

---

*GAP — Unknown without your host: OpenClaw plugin version, exact gateway restart schedule, and whether multiple clones of the repo exist (wrong path silences file reads).*
