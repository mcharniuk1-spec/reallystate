from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import SourceRegistryEntry
from .source_registry import SourceRegistry


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def tier4_sources(registry: SourceRegistry) -> list[SourceRegistryEntry]:
    return [entry for entry in registry.all() if entry.tier == 4]


def collect_tier4_links(registry: SourceRegistry) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in tier4_sources(registry):
        urls: list[str] = []
        if entry.primary_url:
            urls.append(entry.primary_url)
        urls.extend(entry.related_urls or [])
        for idx, url in enumerate(dict.fromkeys(urls)):
            rows.append(
                {
                    "source_name": entry.source_name,
                    "tier": entry.tier,
                    "source_family": entry.source_family.value,
                    "access_mode": entry.access_mode.value,
                    "legal_mode": entry.legal_mode,
                    "risk_mode": entry.risk_mode.value,
                    "freshness_target": entry.freshness_target.value,
                    "url": url,
                    "url_kind": "primary" if idx == 0 else "related",
                    "requires_consent": entry.legal_mode in {"consent_or_manual_only", "official_partner_or_vendor_only"},
                }
            )
    return rows


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_tier4_posts() -> list[dict[str, Any]]:
    """Collect fixture-backed tier-4 posts/messages as one-row-per-message dataset."""
    root = _repo_root() / "tests" / "fixtures"
    rows: list[dict[str, Any]] = []

    # Telegram posts (existing fixture cases)
    telegram_root = root / "telegram_public"
    if telegram_root.exists():
        from .connectors.social_parser import extract_social_lead

        for case_dir in sorted(telegram_root.iterdir()):
            if not case_dir.is_dir():
                continue
            raw_path = case_dir / "raw.json"
            if not raw_path.exists():
                continue
            raw = _load_json(raw_path)
            extracted = extract_social_lead(raw)
            rows.append(
                {
                    "platform": "telegram",
                    "source_name": raw.get("source_name"),
                    "channel_or_account": raw.get("channel_id"),
                    "message_id": str(raw.get("message_id")),
                    "posted_at": raw.get("posted_at"),
                    "raw_text": raw.get("raw_text"),
                    "media_urls": raw.get("media_urls", []),
                    "redaction_applied": bool(raw.get("redaction_applied", False)),
                    "consent_status": raw.get("consent_status"),
                    "intent": extracted.get("intent"),
                    "property_type": extracted.get("property_type"),
                    "city": extracted.get("city"),
                    "district": extracted.get("district"),
                    "price": extracted.get("price"),
                    "currency": extracted.get("currency"),
                    "is_noise": extracted.get("is_noise"),
                }
            )

    # X posts (fixture cases)
    x_root = root / "x_public"
    if x_root.exists():
        from .connectors.social_parser import extract_social_lead

        for case_dir in sorted(x_root.iterdir()):
            if not case_dir.is_dir():
                continue
            raw_path = case_dir / "raw.json"
            if not raw_path.exists():
                continue
            raw = _load_json(raw_path)
            extracted = extract_social_lead(raw)
            rows.append(
                {
                    "platform": "x",
                    "source_name": raw.get("source_name"),
                    "channel_or_account": raw.get("account_id"),
                    "message_id": str(raw.get("message_id")),
                    "posted_at": raw.get("posted_at"),
                    "raw_text": raw.get("raw_text"),
                    "media_urls": raw.get("media_urls", []),
                    "redaction_applied": bool(raw.get("redaction_applied", False)),
                    "consent_status": raw.get("consent_status"),
                    "intent": extracted.get("intent"),
                    "property_type": extracted.get("property_type"),
                    "city": extracted.get("city"),
                    "district": extracted.get("district"),
                    "price": extracted.get("price"),
                    "currency": extracted.get("currency"),
                    "is_noise": extracted.get("is_noise"),
                }
            )

    return rows


def write_tier4_exports(
    registry: SourceRegistry,
    *,
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    links = collect_tier4_links(registry)
    posts = collect_tier4_posts()

    links_json = out_dir / "tier4-social-links.json"
    links_csv = out_dir / "tier4-social-links.csv"
    posts_json = out_dir / "tier4-social-posts.json"
    posts_csv = out_dir / "tier4-social-posts.csv"

    links_json.write_text(json.dumps(links, ensure_ascii=False, indent=2), encoding="utf-8")
    posts_json.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")

    if links:
        with links_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(links[0].keys()))
            writer.writeheader()
            writer.writerows(links)
    else:
        links_csv.write_text("", encoding="utf-8")

    if posts:
        with posts_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(posts[0].keys()))
            writer.writeheader()
            writer.writerows(posts)
    else:
        posts_csv.write_text("", encoding="utf-8")

    return {
        "tier4_sources": len(tier4_sources(registry)),
        "links": len(links),
        "posts": len(posts),
        "files": {
            "links_json": str(links_json),
            "links_csv": str(links_csv),
            "posts_json": str(posts_json),
            "posts_csv": str(posts_csv),
        },
    }

