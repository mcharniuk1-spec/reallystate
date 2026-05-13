#!/usr/bin/env python3
"""
Build Action1 (7 sources × 4 buckets) Markdown report for Telegram / OpenClaw.

Reads:
  - data/scraped/<source>/listings/*.json
  - data/source_registry.json (primary_url for --running-line headings)
  - docs/exports/website-inventory-analysis.json (website totals for **% progress** in --running-line; compact mode)

No network. Output to stdout (pipe to openclaw message send).
Template contract: ``docs/openclaw/action1-running-report-template.md``.
"""

from __future__ import annotations

import json
import os
import re
import string
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRAPED = ROOT / "data" / "scraped"
INV = ROOT / "docs" / "exports" / "website-inventory-analysis.json"
CKPT_LISTINGS = ROOT / "data" / "runs" / "action1_listing_json_total.txt"
RUN_SNAPSHOT = ROOT / "data" / "runs" / "action1_last_running_snapshot.json"
QUALITY_CACHE = ROOT / "data" / "runs" / "action1_quality_rollup_latest.json"

SOURCES = [
    ("address_bg", "Address.bg"),
    ("bulgarianproperties", "BulgarianProperties"),
    ("homes_bg", "Homes.bg"),
    ("imot_bg", "imot.bg"),
    ("luximmo", "LUXIMMO"),
    ("property_bg", "property.bg"),
    ("suprimmo", "SUPRIMMO"),
]
BUCKETS = ["buy_personal", "buy_commercial", "rent_personal", "rent_commercial"]

REGISTRY_PATH = ROOT / "data" / "source_registry.json"

MIN_DESC_WORDS = 25


def load_primary_urls() -> dict[str, str]:
    """Map ``source_name`` → ``primary_url`` from ``data/source_registry.json``."""
    if not REGISTRY_PATH.exists():
        return {}
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for row in data.get("sources", []):
        name = row.get("source_name")
        url = row.get("primary_url")
        if name and url:
            u = str(url).strip()
            if u and not u.endswith("/"):
                u += "/"
            out[str(name)] = u
    return out


def classify_deal(row: dict[str, Any]) -> str:
    """Coarse buy vs rent (fallback when segment/bucket missing)."""
    bk = (row.get("bucket_key") or row.get("segment_key") or "").strip()
    if bk.startswith("buy_"):
        return "buy"
    if bk.startswith("rent_"):
        return "rent"
    intent = (row.get("listing_intent") or "").strip().lower()
    if intent in ("sale", "auction"):
        return "buy"
    if intent in ("long_term_rent", "short_term_rent"):
        return "rent"
    return "unknown"

def _word_count(row: dict[str, Any]) -> int:
    desc = (row.get("description") or "").strip()
    return len(desc.split()) if desc else 0


def _is_zero_price(row: dict[str, Any]) -> bool:
    pr = row.get("price")
    return pr == 0 or pr == "0"


def _is_multi_unit(row: dict[str, Any]) -> bool:
    return bool(row.get("suspected_multi_unit_publication") or row.get("suspected_multi_unit"))


def _gallery_gap(row: dict[str, Any]) -> bool:
    # "Bad/previously-wrong" proxy: not full-gallery, but remote gallery exists.
    if row.get("full_gallery_downloaded"):
        return False
    remote = int(row.get("photo_count_remote") or len(row.get("image_urls") or []))
    local = int(row.get("photo_count_local") or len(row.get("local_image_files") or []))
    return remote > max(local, 0) and remote > 0


def is_bad_listing(row: dict[str, Any]) -> bool:
    """
    "Bad" = likely previously scraped incorrectly / not properly complete for product use.
    This is file-backed QA (no live fetch) and is intentionally conservative.
    """
    wc = _word_count(row)
    if wc < MIN_DESC_WORDS:
        return True
    if _is_zero_price(row):
        return True
    if _is_multi_unit(row):
        return True
    if _gallery_gap(row):
        return True
    return False


def format_source_heading(label: str, urls: dict[str, str]) -> str:
    u = urls.get(label)
    if u:
        # Normalize display: ensure trailing slash for canonical portal links (matches operator examples)
        display = u if u.endswith("/") else u + "/"
        return f"**{label}** ({display})"
    return f"**{label}**"

STOP = frozenset(
    "the a an and or for of in on at to from with by as is are was were be been being "
    "this that these those it its we you your our their they not no yes bg bgp bgm bgk "
    "продава наем апартамент къща имот имоти за от в на по до при със без много една един "
    "двустаен тристаен четиристаен панорамен изглед цена кв м euro eur лв bgn".split()
)


def load_inventory() -> dict[str, dict]:
    if not INV.exists():
        return {}
    data = json.loads(INV.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for row in data.get("sources", []):
        name = row.get("source_name")
        if not name:
            continue
        out[name] = row
    return out


def _site_progress_line(inv_row: dict | None, items: int) -> str:
    """One-line saved-vs-portal total from ``website-inventory-analysis.json`` (not DB)."""
    if not inv_row:
        return "  - vs portal inventory total: _n/a (no row in website-inventory-analysis.json)_"
    wt = inv_row.get("website_total") or {}
    raw = wt.get("value")
    kind = wt.get("kind") or "unknown"
    if raw is None:
        return "  - vs portal inventory total: _n/a (no website_total.value)_"
    try:
        denom = float(raw)
    except (TypeError, ValueError):
        return "  - vs portal inventory total: _n/a (invalid website_total.value)_"
    if denom <= 0:
        return "  - vs portal inventory total: _n/a (denominator 0)_"
    pct = round(items / denom * 100, 2)
    note = ""
    if items > denom:
        note = " _(saved JSON files exceed denominator — mixed methodology / category-bound total)_"
    return (
        f"  - vs portal inventory total: **{items}** / **{int(denom)}** ≈ **{pct}%** "
        f"(total kind: `{kind}`; see `docs/exports/website-inventory-analysis.json`){note}"
    )


def tokenize(text: str) -> list[str]:
    t = text.lower()
    t = re.sub(r"[^\w\s\u0400-\u04ff]", " ", t, flags=re.UNICODE)
    parts = []
    for w in t.split():
        w = w.strip(string.punctuation)
        if len(w) < 3 or w in STOP:
            continue
        parts.append(w)
    return parts


def bucket_stats(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {
            "items": 0,
            "full_pct": 0.0,
            "avg_desc_words": 0.0,
            "avg_remote": 0.0,
            "avg_local": 0.0,
            "multi_unit": 0,
            "zero_price": 0,
            "thin_desc": 0,
            "gallery_gap": 0,
            "bad_items": 0,
        }
    full = sum(1 for r in rows if r.get("full_gallery_downloaded"))
    words = []
    rem = []
    loc = []
    multi = 0
    zprice = 0
    thin = 0
    gap = 0
    bad = 0
    for r in rows:
        wc = _word_count(r)
        words.append(wc)
        rem.append(int(r.get("photo_count_remote") or len(r.get("image_urls") or [])))
        loc.append(int(r.get("photo_count_local") or len(r.get("local_image_files") or [])))
        if _is_multi_unit(r):
            multi += 1
        if _is_zero_price(r):
            zprice += 1
        if wc < MIN_DESC_WORDS:
            thin += 1
        if _gallery_gap(r):
            gap += 1
        if is_bad_listing(r):
            bad += 1
    return {
        "items": n,
        "full_pct": round(full / n * 100, 1),
        "avg_desc_words": round(sum(words) / n, 1),
        "avg_remote": round(sum(rem) / n, 2),
        "avg_local": round(sum(loc) / n, 2),
        "multi_unit": multi,
        "zero_price": zprice,
        "thin_desc": thin,
        "gallery_gap": gap,
        "bad_items": bad,
    }


def top_words_for_source(rows_flat: list[dict], k: int = 12) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for r in rows_flat:
        c.update(tokenize(r.get("description") or ""))
        c.update(tokenize(r.get("title") or ""))
    return c.most_common(k)


def _scan_one_source(sk: str, label: str) -> dict[str, Any]:
    """Read one portal's ``listings/*.json`` tree (used by ``scan_metrics``; may run in a thread)."""
    nested_local = {b: [] for b in BUCKETS}
    extras_local: list[dict] = []
    flat_local: list[dict] = []
    cat_local: Counter[str] = Counter()
    deal_local: Counter[str] = Counter()
    segment_local: Counter[str] = Counter()
    ps: dict[str, Any] = {
        "items": 0,
        "words_sum": 0,
        "local_images_sum": 0,
        "remote_refs_sum": 0,
        "deal_counts": Counter(),
        "segment_counts": Counter(),
        "categories": Counter(),
    }
    bd = {"thin": 0, "zero": 0, "multi": 0, "gap": 0, "bad": 0}
    qa = {"total": 0, "good_single_unit": 0, "bad_lost": 0, "grouped_publication": 0, "rescraped_ok": 0}
    bad_total_local = 0
    tw_local = 0
    d = SCRAPED / sk / "listings"
    if not d.is_dir():
        return {
            "sk": sk,
            "label": label,
            "nested_local": nested_local,
            "extras_local": extras_local,
            "flat_local": flat_local,
            "cat_local": cat_local,
            "deal_local": deal_local,
            "segment_local": segment_local,
            "bad_detail": {label: bd},
            "bad_total": 0,
            "total_words": 0,
            "total_files": 0,
            "per_source_out": {
                label: {
                    "items": 0,
                    "avg_words": 0.0,
                    "avg_remote_img": 0.0,
                    "avg_local_img": 0.0,
                    "local_images_total": 0,
                    "categories": ps["categories"],
                    "deal_counts": ps["deal_counts"],
                    "segment_counts": ps["segment_counts"],
                }
            },
        }

    for p in d.glob("*.json"):
        try:
            row = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        flat_local.append(row)
        ps["items"] += 1
        qa["total"] += 1

        bk = (row.get("bucket_key") or row.get("segment_key") or "").strip()
        if bk in BUCKETS:
            nested_local[bk].append(row)
            segment_local[bk] += 1
            ps["segment_counts"][bk] += 1
        else:
            extras_local.append(row)

        cat = (row.get("property_category") or row.get("product_type") or "unknown").strip() or "unknown"
        cat_local[cat] += 1
        ps["categories"][cat] += 1
        deal = classify_deal(row)
        deal_local[deal] += 1
        ps["deal_counts"][deal] += 1

        desc = (row.get("description") or "").strip()
        wc = len(desc.split()) if desc else 0
        ps["words_sum"] += wc
        tw_local += wc

        loc = row.get("local_image_files") or []
        loc_n = len(loc) if isinstance(loc, list) else int(row.get("photo_count_local") or 0)
        rem_n = int(row.get("photo_count_remote") or len(row.get("image_urls") or []))
        ps["local_images_sum"] += loc_n
        ps["remote_refs_sum"] += rem_n

        if wc < MIN_DESC_WORDS:
            bd["thin"] += 1
        if _is_zero_price(row):
            bd["zero"] += 1
        if _is_multi_unit(row):
            bd["multi"] += 1
        if _gallery_gap(row):
            bd["gap"] += 1
        if is_bad_listing(row):
            bd["bad"] += 1
            bad_total_local += 1

        # Prefer persisted quality gate state when present; fallback to conservative heuristics otherwise.
        a1q = row.get("action1_quality") or {}
        st = str(a1q.get("status") or "").strip()
        good_single_unit = bool(a1q.get("good_single_unit")) if a1q else False
        if st:
            if st == "SCRAPED_OK" and good_single_unit:
                qa["good_single_unit"] += 1
            elif st == "GROUPED_PUBLICATION":
                qa["grouped_publication"] += 1
            else:
                qa["bad_lost"] += 1
            res = (a1q.get("rescrape") or {}) if isinstance(a1q, dict) else {}
            if res.get("rescraped_ok_at"):
                qa["rescraped_ok"] += 1
        else:
            # No applied quality gate yet — approximate.
            if _is_multi_unit(row):
                qa["grouped_publication"] += 1
            elif is_bad_listing(row):
                qa["bad_lost"] += 1
            else:
                qa["good_single_unit"] += 1

    n = int(ps["items"])
    ws = int(ps["words_sum"])
    loc_imgs = int(ps["local_images_sum"])
    rem_refs = int(ps["remote_refs_sum"])
    per_source_out = {
        label: {
            "items": n,
            "avg_words": round(ws / n, 1) if n else 0.0,
            "avg_remote_img": round(rem_refs / n, 2) if n else 0.0,
            "avg_local_img": round(loc_imgs / n, 2) if n else 0.0,
            "local_images_total": loc_imgs,
            "categories": ps["categories"],
            "deal_counts": ps["deal_counts"],
            "segment_counts": ps["segment_counts"],
            "quality": qa,
        }
    }
    return {
        "sk": sk,
        "label": label,
        "nested_local": nested_local,
        "extras_local": extras_local,
        "flat_local": flat_local,
        "cat_local": cat_local,
        "deal_local": deal_local,
        "segment_local": segment_local,
        "bad_detail": {label: bd},
        "bad_total": bad_total_local,
        "total_words": tw_local,
        "total_files": n,
        "per_source_out": per_source_out,
        "quality": qa,
    }


def scan_metrics() -> dict[str, Any]:
    """
    One read pass per listing JSON **per source**, merged here.

    Sources are scanned in parallel (default 7 threads) so Action1 Telegram cadence
    stays within a few minutes on large corpora. Override with ``ACTION1_REPORT_THREADS=1``.
    """
    nested: dict[str, dict[str, list[dict]]] = {sk: {b: [] for b in BUCKETS} for sk, _ in SOURCES}
    extras: dict[str, list[dict]] = defaultdict(list)
    total = 0
    cat_global: Counter[str] = Counter()
    deal_global: Counter[str] = Counter()
    segment_global: Counter[str] = Counter()
    flat_all: list[dict] = []
    bad_total = 0
    total_words = 0
    quality_rollup: dict[str, int] = {"total": 0, "good_single_unit": 0, "bad_lost": 0, "grouped_publication": 0, "rescraped_ok": 0}
    bad_detail: dict[str, dict[str, int]] = {
        label: {"thin": 0, "zero": 0, "multi": 0, "gap": 0, "bad": 0} for _, label in SOURCES
    }
    per_source: dict[str, dict[str, Any]] = {}

    workers = int(os.environ.get("ACTION1_REPORT_THREADS", "7") or "7")
    workers = max(1, min(workers, len(SOURCES)))
    pairs = list(SOURCES)
    if workers <= 1:
        chunks = [_scan_one_source(sk, lab) for sk, lab in pairs]
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            chunks = list(ex.map(lambda t: _scan_one_source(*t), pairs))

    for ch in chunks:
        sk = ch["sk"]
        label = ch["label"]
        for b in BUCKETS:
            nested[sk][b].extend(ch["nested_local"][b])
        extras[sk].extend(ch["extras_local"])
        flat_all.extend(ch["flat_local"])
        cat_global.update(ch["cat_local"])
        deal_global.update(ch["deal_local"])
        segment_global.update(ch["segment_local"])
        bad_total += int(ch["bad_total"])
        total_words += int(ch["total_words"])
        total += int(ch["total_files"])
        bad_detail[label] = ch["bad_detail"][label]
        per_source.update(ch["per_source_out"])
        q = ch.get("quality") or {}
        for k in quality_rollup:
            quality_rollup[k] += int(q.get(k) or 0)

    return {
        "total_listings": total,
        "categories_global": cat_global,
        "deal_global": deal_global,
        "segment_global": segment_global,
        "per_source": per_source,
        "nested": nested,
        "extras": extras,
        "flat_rows": flat_all,
        "bad_total": bad_total,
        "total_words": total_words,
        "bad_detail": bad_detail,
        "quality_rollup": quality_rollup,
    }


def count_listing_json_files() -> tuple[dict[str, int], int]:
    """Count ``*.json`` per portal without parsing (fast PULSE when full scan times out)."""
    by_label: dict[str, int] = {}
    total = 0
    for sk, label in SOURCES:
        d = SCRAPED / sk / "listings"
        if not d.is_dir():
            by_label[label] = 0
            continue
        n = sum(1 for _ in d.glob("*.json"))
        by_label[label] = n
        total += n
    return by_label, total


def format_pulse_line() -> str:
    """Minimal Telegram line: file counts + deltas; no JSON body reads."""
    by_label, total = count_listing_json_files()
    snap = _load_run_snapshot()
    prev = int(snap.get("listing_json_total") or 0) if snap else 0
    delta = total - prev
    parts = [f"{label[:11]}:{by_label[label]}" for _, label in SOURCES]
    ckpt = _read_ckpt_listings()
    lines: list[str] = []
    if ckpt is not None:
        lines.append(
            f"⚡ Action1 PULSE (glob-only). Total JSON files={total} (Δsnapshot {delta:+d}; vs ckpt +{total - ckpt})"
        )
    else:
        lines.append(f"⚡ Action1 PULSE (glob-only). Total JSON files={total} (Δsnapshot {delta:+d})")

    # Fast, explicit 4-stat rollup (requires quality gate cache).
    if QUALITY_CACHE.exists():
        try:
            qc = json.loads(QUALITY_CACHE.read_text(encoding="utf-8"))
        except Exception:
            qc = {}
        q = qc.get("quality_rollup") or {}
        lines.append(
            "• quality (cached): "
            f"total={int(q.get('total') or 0)} | "
            f"proper(good_single_unit)={int(q.get('good_single_unit') or 0)} | "
            f"bad(bad_lost)={int(q.get('bad_lost') or 0)} | "
            f"rescraped_ok={int(q.get('rescraped_ok') or 0)}"
        )
        psq = qc.get("per_source_quality_rollup") or {}
        # Keep short: only totals per platform.
        parts_q = []
        for sk, label in SOURCES:
            qsrc = psq.get(sk) or {}
            parts_q.append(
                f"{label[:11]}:"
                f"{int(qsrc.get('total') or 0)}/"
                f"{int(qsrc.get('good_single_unit') or 0)}/"
                f"{int(qsrc.get('bad_lost') or 0)}/"
                f"{int(qsrc.get('rescraped_ok') or 0)}"
            )
        lines.append("• per-source (total/proper/bad/rescraped): " + " | ".join(parts_q))
        lines.append(f"• quality_cache generated_at: {qc.get('generated_at','n/a')}")
    else:
        lines.append("• quality (cached): n/a (run `python3 scripts/action1_dataset_quality_gate.py --apply`)")
    lines.append("• by source: " + " | ".join(parts))
    lines.append(f"• last full snapshot `updated_at`: {snap.get('updated_at', 'n/a')}")
    lines.append(
        "• _Full quality lines (bad/good, segments, gallery) need a completed `--running-line` scan._ "
        "If you always see PULSE, raise `ACTION1_TG_FULL_TIMEOUT_SEC` on the host or run overnight: "
        "`ACTION1_REPORT_THREADS=7 python3 scripts/action1_full_telegram_report.py --running-line --write-snapshot`"
    )
    return "\n".join(lines)


def _read_ckpt_listings() -> int | None:
    if not CKPT_LISTINGS.exists():
        return None
    try:
        return int(CKPT_LISTINGS.read_text(encoding="utf-8").strip() or "0")
    except (OSError, ValueError):
        return None


def _load_run_snapshot() -> dict[str, Any]:
    if not RUN_SNAPSHOT.exists():
        return {}
    try:
        return json.loads(RUN_SNAPSHOT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_run_snapshot(total_listings: int, total_local_images: int, total_words: int, bad_listings: int) -> None:
    from datetime import datetime, timezone

    RUN_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    RUN_SNAPSHOT.write_text(
        json.dumps(
            {
                "listing_json_total": total_listings,
                "bad_listing_total": bad_listings,
                "local_image_files_total": total_local_images,
                "total_words": total_words,
                "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def format_running_line(*, write_snapshot: bool = False) -> str:
    urls = load_primary_urls()
    inv = load_inventory()
    m = scan_metrics()
    total = m["total_listings"]
    flat_rows: list[dict] = m["flat_rows"]
    bad_total = int(m["bad_total"])
    tw = int(m["total_words"])
    bad_detail: dict[str, dict[str, int]] = m["bad_detail"]
    ckpt = _read_ckpt_listings()
    if ckpt is not None:
        head = f"📈 Action1 RUNNING. Total(7)={total} (+{total - ckpt} vs last Telegram checkpoint file)"
    else:
        head = f"📈 Action1 RUNNING. Total(7)={total} (+? vs checkpoint — no action1_listing_json_total.txt yet)"

    snap = _load_run_snapshot()
    prev_l = int(snap.get("listing_json_total") or 0)
    prev_i = int(snap.get("local_image_files_total") or 0)
    tw_prev = int(snap.get("total_words") or 0) if snap else 0
    prev_bad = int(snap.get("bad_listing_total") or 0) if snap else 0
    sum_local = sum(int(x["local_images_total"]) for x in m["per_source"].values())
    if snap:
        snap_note_list = f"(+{total - prev_l})"
        snap_note_img = f"(+{sum_local - prev_i})"
    else:
        snap_note_list = "(baseline — run with --write-snapshot)"
        snap_note_img = snap_note_list

    avg_words_all = round(tw / len(flat_rows), 1) if flat_rows else 0.0
    tw_delta = tw - tw_prev if snap else 0
    q = m.get("quality_rollup") or {}
    good_total = int(q.get("good_single_unit") or max(0, total - bad_total))
    bad_total_q = int(q.get("bad_lost") or bad_total)
    grouped_total = int(q.get("grouped_publication") or 0)
    rescraped_ok = int(q.get("rescraped_ok") or 0)

    dg = m["deal_global"]
    sglob = m["segment_global"]
    cg = m["categories_global"]
    top_cats = cg.most_common(8)
    cat_bits = ", ".join(f"{k}:{n}" for k, n in top_cats) if top_cats else "n/a"
    seg_bits_all = " | ".join(f"{b}:{sglob.get(b, 0)}" for b in BUCKETS)

    lines: list[str] = []
    lines.append(head)
    if snap:
        bad_delta = bad_total - prev_bad
        lines.append(
            f"• Since last report snapshot: listings {snap_note_list}, bad {bad_total} ({bad_delta:+}), local imgs {snap_note_img}"
        )
    else:
        lines.append(f"• Since last report snapshot: listings {snap_note_list}, bad {bad_total}, local imgs {snap_note_img}")
    lines.append(
        f"• Quality (all 7): total={total} | **good_single_unit={good_total}** | bad_lost={bad_total_q} | grouped={grouped_total} | rescraped_ok={rescraped_ok}"
    )
    lines.append(
        f"• By deal type (all 7): buy:{dg.get('buy', 0)} | rent:{dg.get('rent', 0)} | unknown:{dg.get('unknown', 0)}"
    )
    lines.append(f"• By segment key (all 7): {seg_bits_all}")
    lines.append(f"• By property_category (all 7): {cat_bits}")
    if snap:
        lines.append(f"• Avg descr words (all items): {avg_words_all} [total words {tw} (+{tw_delta})]")
    else:
        lines.append(f"• Avg descr words (all items): {avg_words_all} [total words {tw}]")
    lines.append(
        f"• Images: avg local/img/property {round(sum_local / total, 2) if total else 0} | local imgs total {sum_local} {snap_note_img}"
    )
    lines.append(
        "• Progress % = saved listing JSON files ÷ portal total from "
        "`docs/exports/website-inventory-analysis.json` (`website_total`; may be exact, estimate, or lower_bound — not always whole-site)."
    )
    lines.append("**By source**")
    for sk, label in SOURCES:
        ps = m["per_source"].get(label, {})
        if not ps.get("items"):
            lines.append(f"• {format_source_heading(label, urls)}")
            lines.append("  - _no listing JSON files_")
            lines.append(_site_progress_line(inv.get(label), 0))
            continue
        dc = ps["deal_counts"]
        sc = ps["segment_counts"]
        seg_src = " | ".join(f"{b}:{sc.get(b, 0)}" for b in BUCKETS)
        cats = ps["categories"].most_common(4)
        cat_s = ", ".join(f"{a}:{b}" for a, b in cats)
        # Source-local "bad" breakdown (same rules, but per source).
        bd = bad_detail.get(label, {"thin": 0, "zero": 0, "multi": 0, "gap": 0, "bad": 0})
        bad_src = int(bd["bad"])
        bad_multi = int(bd["multi"])
        bad_zero = int(bd["zero"])
        bad_thin = int(bd["thin"])
        bad_gap = int(bd["gap"])
        lines.append(f"• {format_source_heading(label, urls)}")
        lines.append(
            f"  - buy:{dc.get('buy', 0)} | rent:{dc.get('rent', 0)} | unknown:{dc.get('unknown', 0)}"
        )
        lines.append(f"  - segments: {seg_src}")
        lines.append(
            f"  - items:{ps['items']} | rem̄{ps['avg_remote_img']} | loc̄{ps['avg_local_img']} | locΣ{ps['local_images_total']} | words̄{ps['avg_words']}"
        )
        qsrc = ps.get("quality") or {}
        if qsrc:
            lines.append(
                "  - quality: "
                f"good_single_unit:{int(qsrc.get('good_single_unit') or 0)} | "
                f"bad_lost:{int(qsrc.get('bad_lost') or 0)} | "
                f"grouped:{int(qsrc.get('grouped_publication') or 0)} | "
                f"rescraped_ok:{int(qsrc.get('rescraped_ok') or 0)}"
            )
        lines.append(
            f"  - bad:{bad_src} (thin:{bad_thin} | $0:{bad_zero} | multi:{bad_multi} | gallery_gap:{bad_gap})"
        )
        lines.append(_site_progress_line(inv.get(label), int(ps["items"])))
        lines.append(f"  - top property_category: {cat_s}")

    if write_snapshot:
        _write_run_snapshot(total, sum_local, tw, bad_total)

    out = "\n".join(lines)
    if len(out) > 5500:
        out = out[:5200] + "\n…(truncated)"
    return out


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--compact", action="store_true", help="One row per source + totals (fits Telegram)")
    ap.add_argument(
        "--running-line",
        action="store_true",
        help="Action1 RUNNING Telegram/OpenClaw template: bullets, buy/rent, segments, per-source blocks (see docs/openclaw/action1-running-report-template.md).",
    )
    ap.add_argument(
        "--write-snapshot",
        action="store_true",
        help="With --running-line: write data/runs/action1_last_running_snapshot.json for next-run deltas.",
    )
    ap.add_argument(
        "--skip-top-tokens",
        action="store_true",
        help="With --compact: omit expensive title/description token rollups (faster for Telegram rehydrate).",
    )
    ap.add_argument(
        "--pulse",
        action="store_true",
        help="Glob-only file counts per source (instant). Use when full --running-line times out.",
    )
    args = ap.parse_args()
    if args.pulse:
        print(format_pulse_line())
        return
    if args.running_line:
        print(format_running_line(write_snapshot=args.write_snapshot))
        return

    inv = load_inventory()
    m = scan_metrics()
    nested, total, extras = m["nested"], m["total_listings"], m["extras"]
    lines: list[str] = []
    lines.append("**Action1 checkpoint** (7×4 + quality)")
    lines.append(f"- **Saved listing JSON files (7 sources)**: {total}")
    lines.append("")
    if args.compact:
        lines.append("### Per source (all buckets)")
        lines.append("| source | items | good | bad | full% | words | R/L | multi | $0 | thin | gap | vs site |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for sk, label in SOURCES:
            flat = [r for b in BUCKETS for r in nested[sk][b]] + extras.get(sk, [])
            st = bucket_stats(flat)
            good = max(0, st["items"] - st["bad_items"])
            inv_row = inv.get(label, {})
            wt = inv_row.get("website_total") or {}
            site = ""
            if wt.get("value") is not None:
                site = f"{wt['value']} ({wt.get('kind', '')})"
            elif inv_row.get("analysis_estimate"):
                site = f"~{inv_row['analysis_estimate']}"
            rl = f"{st['avg_remote']:.1f}/{st['avg_local']:.1f}"
            lines.append(
                f"| {label} | {st['items']} | {good} | {st['bad_items']} | {st['full_pct']} | {st['avg_desc_words']} | {rl} | "
                f"{st['multi_unit']} | {st['zero_price']} | {st['thin_desc']} | {st['gallery_gap']} | {site} |"
            )
        lines.append("")
        if not args.skip_top_tokens:
            lines.append("### Top tokens (all titles+descriptions, 7 sources)")
            top = top_words_for_source(m["flat_rows"], 15)
            lines.append("- " + ", ".join(f"`{w}`×{n}" for w, n in top))
            lines.append("")
        lines.append("### Bucket quick view (counts only)")
        for sk, label in SOURCES:
            parts = [f"`{b}`:{len(nested[sk][b])}" for b in BUCKETS]
            exn = len(extras.get(sk, []))
            suf = f" unbucketed:{exn}" if exn else ""
            lines.append(f"- **{label}**: " + " ".join(parts) + suf)
    else:
        lines.append("### Matrix: items | full-gallery % | avg desc words | avg remote/local photos | multi-unit | zero-price | thin-desc")
        lines.append("")
        lines.append("| source | bucket | n | full% | words | R/L ph | multi | $0 | thin | vs site |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for sk, label in SOURCES:
            inv_row = inv.get(label, {})
            wt = inv_row.get("website_total") or {}
            site_note = ""
            if wt.get("value") is not None:
                site_note = f"{wt.get('value')} ({wt.get('kind', '')})"
            elif inv_row.get("analysis_estimate"):
                site_note = f"~{inv_row['analysis_estimate']} (est.)"
            for b in BUCKETS:
                rows = nested[sk][b]
                st = bucket_stats(rows)
                rl = f"{st['avg_remote']:.1f}/{st['avg_local']:.1f}"
                lines.append(
                    f"| {label[:14]} | `{b}` | {st['items']} | {st['full_pct']} | {st['avg_desc_words']} | {rl} | "
                    f"{st['multi_unit']} | {st['zero_price']} | {st['thin_desc']} | {site_note if b == 'buy_personal' else ''} |"
                )
            ex = extras.get(sk, [])
            if ex:
                lines.append(f"| {label[:14]} | _(unbucketed)_ | {len(ex)} | — | — | — | — | — | — | |")
        lines.append("")
        if not args.skip_top_tokens:
            lines.append("### Top tokens (title+description) per source")
            for sk, label in SOURCES:
                flat = [r for b in BUCKETS for r in nested[sk][b]] + extras.get(sk, [])
                if not flat:
                    continue
                top = top_words_for_source(flat, 10)
                lines.append(f"- **{label}**: " + ", ".join(f"`{w}`×{n}" for w, n in top))
    lines.append("")
    lines.append("### Mismatch / risk hints")
    lines.append("- **multi-unit**: suspected_multi_unit* flags")
    lines.append("- **zero-price**: numeric 0 (invalid per AGENTS.md)")
    lines.append("- **thin-desc**: description words < 25")
    lines.append("- **gallery gap**: remote ≫ local without full_gallery_downloaded")
    lines.append("")
    lines.append("_`python3 scripts/action1_full_telegram_report.py --compact`_")
    out = "\n".join(lines)
    if len(out) > 3900:
        out = out[:3850] + "\n\n…(truncated for Telegram 4k cap)"
    print(out)


if __name__ == "__main__":
    main()
