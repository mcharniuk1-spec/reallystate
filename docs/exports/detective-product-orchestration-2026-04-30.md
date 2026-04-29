# Detective pass — product, stack, and agent orchestration (2026-04-30)

This document consolidates what **Codex / Cursor agents**, **OpenClaw + Gemma4 (Ollama)**, and prior **Claude-style planning** artifacts actually produced in-repo, and defines the **efficient next path** for a buyer-first Bulgarian marketplace.

## 1) Evidence trail (what exists vs what is claimed)

| Area | FACT (repo) | GAP / RISK |
|------|-------------|------------|
| **Scraping** | `scripts/live_scraper.py`, `make scrape-all-full`, `data/scraped/*/listings/*.json`, `bucket_key` backfill for four-bucket reporting | File-backed volume ≠ `canonical_listing` until **BD-11** ingest is proven; several sources have **remote ≫ local** photos (partial galleries). |
| **Quality** | `scripts/generate_s1_21_quality_audit.py`, `docs/exports/s1-21-tier12-quality-audit-2026-04-29.*`, `suspected_multi_unit_publication` rules | Mixed-unit pages and parser edge cases (Homes area decimals, Yavlena zero-price) need continuous repair, not one-off audits. |
| **Frontend** | Next.js 15 app; `MainExplorer` reads `/data/scraped-listings.json`; `/properties/[id]` tries **FastAPI** `getApiBaseUrl()` then falls back to file-backed `readScrapedListings()` | Client-side listing browse is **not** wired to `/api/backend/...` yet for dynamic DB mode; detail page is hybrid (good for demos, confusing for “single API truth”). |
| **API bridge** | `app/api/backend/[...path]/route.ts` proxies to `API_BASE_URL` with optional `X-Api-Key` | Operators on LAN must set `API_BASE_URL` to a reachable host; see **Local public hosting** in `README.md`. |
| **OpenClaw** | `docs/openclaw/*`, `agent-skills/openclaw-ollama-gemma4/SKILL.md` | Agents must not improvise “waiting for URLs”; patterns live in code + exports. Long runs need **detached** scrapers + explicit Telegram cadence. |

## 2) Customer + reliability lens (current market)

- **Buyers** want: trustworthy **single-unit** listings, **full galleries**, clear **price status** (not fake zeros), fast **map + filters**, and **explainable** duplicates — not raw portal noise.
- **Operators** need: **per-source / per-bucket** metrics, **legal_mode** enforcement, and **dashboards** that separate “rows saved” from “gallery complete” from “semantic image reports (Action0)”.
- **Efficiency** means: fix **connector + media backfill** bottlenecks before widening source count; ship **BD-11** so counts are DB-auditable; keep Gemma4 on **offline report drafting** unless explicitly driving narrated runs.

## 3) Backend ↔ attribute map (contract health)

Canonical listing fields used in UI and exports should stay aligned with:

- `sql/schema.sql` → `canonical_listing` and related tables (when DB path is active).
- `src/bgrealestate/api/routers/listings.py` (list/detail JSON shape).
- `lib/types/listing.ts` and `lib/server/scraped-listings.ts` (file-backed bridge).

**Next hardening**: document a single **OpenAPI or Zod** shared contract (even if generated from Python models) so `/listings/{id}` and `readScrapedListings()` cannot drift.

## 4) Widened per-source scraping approach (priority seven)

For each of **Address.bg, BulgarianProperties, Homes.bg, imot.bg, LUXIMMO, property.bg, SUPRIMMO**:

1. **Discovery**: category/city entry URLs from `data/source_registry.json` + `src/bgrealestate/scraping/section_catalog.py` — never “homepage wander”.
2. **Pagination**: exhaust listing index pages within legal rate limits; log HTTP failures per bucket.
3. **Detail**: JSON-LD + structured selectors; preserve **raw HTML hash** or capture key when useful for regression.
4. **Classification**: derive `bucket_key` from **detail evidence**, not URL alone, when routes are mixed.
5. **Media**: enumerate gallery; download **all** reachable images; set `full_gallery_downloaded` only when local count matches remote policy.
6. **Promotion rule**: keep `suspected_multi_unit_publication` until unit-level evidence exists (per `AGENTS.md`).
7. **Exports**: after each batch, refresh `docs/exports/source-item-photo-coverage.json` + `make dashboard-doc`.

## 5) OpenClaw + Gemma4 (Ollama) — operator gate + Telegram

- Every OpenClaw prompt should **load** Action0 + Action1 + Action2 contracts from `docs/exports/taskforgema.md`.
- **Execution rule**: no Action0 or Action2 **execution** until the operator sends **`Action1 ACCEPT`** (then run Action1). After Action1 is accepted and running, send Telegram **every +100 net new saved listings** with a **7 sources × 4 buckets** bullet matrix (counts + errors + full-gallery %).

## 6) Strategic next steps (ordered)

1. **Finish Action1** with detached runner + periodic matrix pings; refresh dashboards.
2. **Media backfill** for BulgarianProperties / Homes / imot where remote ≫ local.
3. **BD-11**: land file-backed rows into Postgres for real completion metrics (**S1-18**).
4. **Unify listing fetch** in UI: one code path via `/api/backend/listings` when `NEXT_PUBLIC_USE_API=1` (future slice).
5. **BD-06 / UX-04**: nationwide geo API + map contract hardening.

## 7) Agent goal refresh (one line each)

| Agent | Goal |
|-------|------|
| **backend_developer** | Postgres + APIs are the system of record; ingest and contracts beat file-only demos. |
| **scraper_1** | Full-gallery, legally gated, bucket-accurate corpuses with honest failure logs. |
| **scraper_t3** | Partner/official feeds only with explicit contracts. |
| **scraper_sm** | Consent-gated overlays only. |
| **ux_ui_designer** | Buyer-trust UI: honest loading, map fallback, liquid-glass polish without hiding data gaps. |
| **debugger** | Verify gates: fixtures, legal blocks, dashboard numbers, and OpenClaw output contracts. |

This file is the **detective index**; day-to-day sequencing remains in `docs/agents/TASKS.md`.
