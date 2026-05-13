# Action1 RUNNING report — OpenClaw / Telegram template

Canonical generator (always match this structure when narrating Action1 progress):

```bash
python3 scripts/action1_full_telegram_report.py --running-line
python3 scripts/action1_full_telegram_report.py --running-line --write-snapshot   # persist deltas for next run
make action1-running-report
```

**Fast PULSE** (glob counts only — use if full scan is too slow for Telegram):

```bash
python3 scripts/action1_full_telegram_report.py --pulse
```

The detached watcher (`make action1-telegram-watch-detached`) runs `--running-line --write-snapshot` with **`ACTION1_TG_FULL_TIMEOUT_SEC`** (default **240**); on timeout it sends **`--pulse`** so the channel never goes silent. Raise the timeout on the host for full stats every tick.

**Notify OpenClaw/Telegram** (running report + mandatory reporting instructions for Gemma4):

```bash
make action1-openclaw-continue
# same as: ./scripts/action1_openclaw_continue.sh
```

**Reliable ops context reset** (short rules + compact snapshot; uses `openclaw message send` — not `agent --deliver`). Two Telegram messages: rules, then `--compact` (timeout/size-capped). Full `--running-line` stays on the **5‑minute watcher** or the host.

```bash
make action1-telegram-ops-rehydrate
# same as: ./scripts/action1_telegram_ops_rehydrate.sh
# Optional: ACTION1_REHYDRATE_REPORT_TIMEOUT_SEC=180 ACTION1_REHYDRATE_MAX_CHARS=3800
```

## Output shape (required sections)

1. **Header** — `📈 Action1 RUNNING. Total(7)=N (+Δ vs last Telegram checkpoint file)`  
   - Checkpoint file: `data/runs/action1_listing_json_total.txt` (updated when `action1_checkpoint_notify.py --send` succeeds).

2. **Snapshot deltas** — bullet includes **bad** rows and local images:  
   - `• Since last report snapshot: listings (+A), bad B (+Δbad), local imgs (+C)`  
   - Baseline: `data/runs/action1_last_running_snapshot.json` (from `--write-snapshot`).

3. **Quality rollup (all 7 sources)**  
   - `• Quality (all 7): good=... = total ... − bad ...`  

4. **Global rollups (all 7 sources)**  
   - `• By deal type … buy | rent | unknown` (from `segment_key` / `listing_intent`).  
   - `• By segment key … buy_personal | buy_commercial | rent_personal | rent_commercial`.  
   - `• By property_category …`  
   - `• Avg descr words … [total words … (+Δ)]`  
   - `• Images: avg local/img/property … | local imgs total …`

5. **`**By source**`** — one block per portal (fixed order: Address.bg → … → SUPRIMMO):  
   - `• **SourceName** (primary_url from data/source_registry.json)`  
   - `- buy:… | rent:… | unknown:…`  
   - `- segments: buy_personal:… | …`  
   - `- items:… | rem̄… | loc̄… | locΣ… | words̄…`  
   - `- bad:... (thin:... | $0:... | multi:... | gallery_gap:...)`  
   - `- vs portal inventory total: N / D ≈ X%` (from `docs/exports/website-inventory-analysis.json` `website_total`; see `kind` for exact / estimate / lower_bound)  
   - `- top property_category: …`

6. **Global line** (before **By source**): short explanation that progress % = saved files ÷ portal total from the inventory file.

Do **not** invent totals; re-run the script on the host repo after scrape waves.

## Related

- Operator bootstrap: `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`  
- Continue ping script: `scripts/action1_openclaw_continue.sh` / `make action1-openclaw-continue`
