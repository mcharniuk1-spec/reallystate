# OpenClaw / Action1 fresh review — 2026-05-05

## FACT

- Active Action1 scrape is running detached from `scripts/action1_scrape_full_uncapped.sh`.
- Process evidence: `python3.12 -m bgrealestate scrape-all-full --parallel-sources 7 --max-pages 24 --max-waves 12 --target-per-source 0 --refresh-dashboard --download-photos --sources Address.bg,BulgarianProperties,Homes.bg,imot.bg,LUXIMMO,property.bg,SUPRIMMO`.
- Latest scrape log: `data/runs/action1_scrape_uncapped_detached_20260504_161536.log`.
- Current file-backed A1 listing JSON counts:
  - `Address.bg`: 6473
  - `BulgarianProperties`: 2289
  - `Homes.bg`: 144
  - `imot.bg`: 9937
  - `LUXIMMO`: 2512
  - `property.bg`: 3094
  - `SUPRIMMO`: 4948
  - Total: 29397
- The scrape log is currently dominated by SUPRIMMO/property.bg detail and image fetches with HTTP 200 responses.
- `DATABASE_URL` is not set in this shell, so DB-backed import/query verification was not run.
- OpenClaw gateway status is healthy: LaunchAgent loaded, gateway running on `127.0.0.1:18789`, probe OK.
- Ollama service is running.
- `qwen3-coder:30b` failed to load with `500 Internal Server Error: model runner has unexpectedly stopped`, likely resource pressure.
- `qwen3-vl:8b` loaded successfully and is visible in `ollama ps`.
- Telegram/OpenClaw send from Codex was rejected by the approval reviewer as external data transfer to Telegram.
- Reporter was therefore stopped and disabled from Codex after the rejection: `make action1-reporter-stop && make action1-reporter-off`.

## INTERPRETATION

- Action1 is not complete. High file volume proves continued harvesting, not accepted property quality.
- The critical remaining work is A1 corpus QA: accepted/good vs `LOST` vs grouped/development vs inactive vs media/description/parser gaps.
- Reporting failure in the screenshot is consistent with stale long-running `action1_full_telegram_report.py` subprocesses and a fallback that spawned another report subprocess.
- OpenClaw is operational as a gateway, but Telegram reporting should be run from a trusted host Terminal or after explicit operator approval for external send.
- Qwen 30B should remain the preferred code model when host resources allow it; current live fallback is smaller Qwen.

## HYPOTHESIS

- `qwen3-coder:30b` failed because current host memory/GPU pressure is high while Action1 scrape is still active and downloading media.
- Full `--running-line` scans time out because the corpus is now large and JSON/media metadata reads are slow under active scrape load.
- Homes.bg remains the weakest A1 source by count and should be prioritized in DA-01 / scraper_1 gap analysis.

## GAP

- No DB verification because `DATABASE_URL` was unavailable.
- No full quality scan completed in this run; only cached/screenshot quality evidence exists.
- No Telegram send was completed from Codex due external-transfer rejection.

## Changes made in this review

- Hardened `scripts/action1_telegram_watch.sh`:
  - timeboxed report subprocesses now run in their own process group
  - timeouts kill the full process group
  - fallback pulse is now inline file-count logic, so it cannot leak another report subprocess
- Hardened `scripts/action1_telegram_ops_rehydrate.sh` similarly.
- Fixed `scripts/action1_telegram_watch_detached.sh` symlink update with `ln -sfn` to avoid same-second restart failure.

## Next operational state

1. Keep Action1 scrape running.
2. Run DA-01 corpus consistency audit from files first.
3. Import/query DB only when `DATABASE_URL` is available.
4. Restart Telegram reporting only after explicit operator approval for external Telegram transfer or from a non-sandbox host Terminal:
   - `make action1-reporter-on`
   - `ACTION1_TG_INTERVAL_SEC=300 make action1-telegram-watch-detached`
5. Do not run Action0 or Action2 until Action1 QA is accepted and the operator gives the next gate.
