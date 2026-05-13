# Reporter role — agent instructions (Action1 / OpenClaw / Telegram)

Use this file when the operator assigns the **reporter** skill (`agent-skills/reporter/SKILL.md`): scheduled Action1 progress, honest stats, and explicit prior-step context.

## 1. Purpose

Deliver **reliable, file-backed** status on a **5-minute default cadence** while long scrapes run. The reporter does **not** store project state in the model; state lives in **git-tracked files** and **`data/runs/`**.

## 2. Fixed settings (defaults)

| Variable | Default | Purpose |
|----------|---------|---------|
| `ACTION1_TG_INTERVAL_SEC` | **300** | Interval between Telegram sends (**5 minutes**). |
| `ACTION1_TG_FULL_TIMEOUT_SEC` | **240** | Wall clock for full `--running-line` per tick before fallback. |
| `ACTION1_REHYDRATE_REPORT_TIMEOUT_SEC` | **300** | Compact report timeout in rehydrate script. |
| `ACTION1_REHYDRATE_PREFLIGHT` | **1** | Include compact preflight in rehydrate second message (`0` to disable). |
| `ACTION1_REPORTER_LOCK_FILE` | `data/runs/action1_reporter.lock` | Single-instance lock so cron/launchd won’t double-send. |

Override on the host **before** starting the watcher, e.g.:

```bash
export ACTION1_TG_INTERVAL_SEC=300
export ACTION1_TG_FULL_TIMEOUT_SEC=600   # if you need full bad/good stats every tick on huge corpus
make action1-telegram-watch-detached
```

## 3. Canonical commands

**Periodic Telegram loop (reporter heartbeat):**

```bash
make action1-telegram-watch-detached
```

### Stop “texts while off” (hard gate)

The reporter only sends when this file exists:

- `data/runs/action1_reporter_enabled`

Control it on the host:

```bash
make action1-reporter-on     # enable + start detached watcher
make action1-reporter-stop   # stop watcher process via latest pidfile
make action1-reporter-off    # disable sending (removes enabled file)
make action1-reporter-status # inspect enabled flag + latest pidfile
```

**One-shot RUNNING line + snapshot:**

```bash
python3 scripts/action1_full_telegram_report.py --running-line --write-snapshot
```

**Quality gate (produces good/bad/grouped/rescraped_ok rollups + rescrape queue):**

```bash
python3 scripts/action1_dataset_quality_gate.py --apply
```

Smoke-safe quality gate for large local corpora:

```bash
python3 scripts/action1_dataset_quality_gate.py --limit-per-source 20 --output docs/exports/action1-dataset-quality-gate-dryrun.json
```

### If you have a cron/launchd “Action1 Progress Reporter”

Use the cron-safe wrapper so the scheduler stops spamming errors and won’t run when the reporter is off:

```bash
bash scripts/action1_progress_reporter_cron_safe.sh
```

**Checkpoint matrix (+100 net saves rule):**

```bash
make action1-matrix-snapshot
```

**Operator context reset (rules + compact metrics + preflight):**

```bash
make action1-telegram-ops-rehydrate
```

**Explicit host/task/log snapshot:**

```bash
make openclaw-preflight
# full log: data/runs/openclaw_preflight.log
```

## 4. Log artifacts (explicit prior steps)

| Artifact | Contents |
|----------|----------|
| `data/runs/action1_telegram_watch_detached_LATEST.log` | Symlink to current detached watcher log (O(1) lookup). |
| `data/runs/action1_scrape_uncapped_detached_LATEST.log` | Symlink to current detached scrape log (when using detached scrape). |
| `data/runs/openclaw_preflight.log` | Appended **openclaw-preflight** runs (TASKS grep, JOURNEYs, logs). |
| `data/runs/action1_last_running_snapshot.json` | Last RUNNING snapshot when `--write-snapshot` is used. |

Before claiming “what ran last”, **tail the LATEST log** or run **`make openclaw-preflight`**.

## 5. Context checks by problem type

| Problem | Verify |
|---------|--------|
| Empty or missing stats | Timeouts / corpus size — use `--pulse`, raise `ACTION1_TG_FULL_TIMEOUT_SEC`, read watcher `LATEST.log`. |
| “Agent forgot Action1 docs” | OpenClaw **`main` workspace** = repo root (`docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`). |
| Wrong sources in scope | `data/source_registry.json`; Action1 = **A1 seven keys** only until Action2 gate. |
| Task confusion | `docs/agents/TASKS.md` + relevant `docs/agents/*/JOURNEY.md`. |

Theory vs practice: **`docs/openclaw/memory-context-and-operational-failures.md`**.

## 6. Report layout

Telegram **RUNNING** messages must mirror **`docs/openclaw/action1-running-report-template.md`**. Data source is **`scripts/action1_full_telegram_report.py`** — not free narration.

Quality wording must be explicit:

- `accepted_good` means a single-property candidate that is not `LOST`, not grouped/development, not inactive, and not rejected by the quality gate.
- `bad_LOST` means the item is queued for rescrape or rejected because content/location/identity/fields are inconsistent.
- `grouped_development` means the source page may be useful but does not represent one sellable/rentable property unit.
- `inactive_removed` means the page appears expired, removed, inactive, unavailable, or not currently marketable.
- `media_gap` means missing local images, partial gallery, unreadable files, or suspicious one-photo rows.
- `description_gap` means absent/thin/wrong-source/wrong-language description.

Never use threshold `100` as the denominator for website completion. Use latest source/file/DB totals when available and label threshold-only views separately.

## 7. Related skills and docs

- `agent-skills/reporter/SKILL.md` — this role (short form)  
- `agent-skills/openclaw-ollama-gemma4/SKILL.md` — Gemma4 / Ollama + session logging  
- `docs/openclaw/README.md` — gateway, Ollama timeouts, Telegram CLI  
- `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md` — bootstrap paste block  

---

**Operator note:** Skills under `agent-skills/` are version-controlled. In `~/.openclaw-codex/openclaw.json`, under the **Telegram-bound agent** (e.g. `action1_gemma`), ensure the `skills` list includes the **absolute** path to the repo’s `agent-skills` tree (and keep `reporter` discoverable by adding the folder that contains `reporter/SKILL.md` — usually the repo root’s `agent-skills` is already listed; if your config lists individual skill dirs, add one entry ending with `agent-skills/reporter`).

Example fragment (replace `REPO` with your clone, e.g. `/Users/getapple/Documents/Real Estate Bulg`):

```json
"skills": [
  "REPO/agent-skills",
  "REPO/agent-skills/reporter"
]
```

Listing the parent `agent-skills` directory is enough for tools that scan all `*/SKILL.md` children; the explicit `reporter` line is optional redundancy.
