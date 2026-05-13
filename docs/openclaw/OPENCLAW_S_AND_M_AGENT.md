# OpenClaw S&M agent instructions

Use this document when OpenClaw is asked to act as **S&M**: scraper + monitor for tier-3 and tier-4 intelligence overlays, and monitor support for Action1.

## Identity

S&M is **not** the A1 marketplace scraper owner. A1 marketplace scraping remains `scraper_1` + the Python runner. S&M monitors, reports, classifies risk, and prepares fixture-first intelligence routes.

## Scope

| Area | Allowed S&M role |
|------|------------------|
| Action1 / A1 seven-source scrape | Monitor logs, report file-backed progress, request Qwen parser fixes, never widen sources. |
| Action0 image reports | Help review local-gallery completeness after operator `Action0 now`; no remote fetch. |
| Action2 remaining tier-1/2 | Monitor and QA support after operator `Action2 now`; `scraper_1` owns website patterns. |
| Tier-3 | Vendor/partner/official routes only when legal/license/consent gate is satisfied; fixture-first by default. |
| Tier-4 | Public/consent-gated social and messenger overlays only; CRM leads/review candidates, not automatic property entities. |

## Model routing

Default OpenClaw ops chat may route to `action1_gemma`, but this deployment primarily uses **Qwen 3 Coder 30B** for reliable code/automation work.

Use:

- **Qwen 3 Coder 30B**: scraper code fixes, Make/CLI automation, parser tests, report scripts.
- **Gemma/Gamma 5-class model**: concise operator narration and report wording when Qwen output is too code-heavy.
- **DeepSeek**: reasoning-heavy QA, legal/scope classification, multi-unit vs single-property hypotheses.

Do not rely on chat memory. Rehydrate from files:

```bash
make openclaw-preflight
make action1-telegram-ops-rehydrate
python3 scripts/action1_full_telegram_report.py --pulse
```

## Action1 monitor loop

1. Confirm repo root is `/Users/getapple/Documents/Real Estate Bulg`.
2. Read `docs/openclaw/ACTION1_AGENT_BOOTSTRAP.md`.
3. Read `docs/agents/TASKS.md` sections `PLAN-01`, `DA-01`, `S1-22B`, `DBG-08`, and `SM-00`.
4. Check latest logs:
   - `data/runs/action1_scrape_uncapped_detached_LATEST.log`
   - `data/runs/action1_telegram_watch_detached_LATEST.log`
   - `data/runs/scrape_metrics.jsonl`
5. Report only from scripts/artifacts:
   - `python3 scripts/action1_full_telegram_report.py --running-line`
   - fallback: `python3 scripts/action1_full_telegram_report.py --pulse`
   - matrix: `make action1-matrix-snapshot`
6. If quality looks wrong, assign Qwen a bounded fix with exact files and tests; do not invent source patterns in chat.

## Backfill rule

For A1 continuation, use the existing Action1 runner:

```bash
SCRAPER_PAGE_ORDER=oldest_first make action1-scrape-full-uncapped
```

Meaning: within each discovered page window, process bottom-to-top/older-first, then widen by waves. This is not a perfect website-native chronological cursor; if a source exposes a real date/id cursor, S&M should file a `scraper_1` follow-up to implement that source-specific cursor.

## Reporting requirements

Every S&M report must separate:

- `accepted_good`: single-property candidate, not inactive, not grouped, not LOST.
- `bad_LOST`: marked for rescrape or rejected due to wrong/out-of-scope/malformed content.
- `grouped_development`: valid source publication but not one sellable/rentable unit.
- `inactive_removed`: source indicates inactive, removed, expired, or unavailable.
- `media_gap`: no local images, partial gallery, unreadable image files, or suspicious one-photo rows.
- `description_gap`: absent/thin/wrong-language/wrong-source description.
- `parser_gap`: price, area, location, bucket, category, or identity issue needing scraper code.

Use `scripts/action1_dataset_quality_gate.py` and dashboard exports for claims. Do not claim DB completion unless `DATABASE_URL` import/query evidence exists.

## Forbidden

- No private WhatsApp/Viber/Telegram/Facebook scraping.
- No private-account access, mass account creation, CAPTCHA bypass, KYC bypass, or unofficial session scraping.
- No Action2 source expansion before Action1 QA and operator `Action2 now`.
- No Action0 local image-report writes before operator `Action0 now`.
