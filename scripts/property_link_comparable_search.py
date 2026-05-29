#!/usr/bin/env python3
"""Scrape one property link and search comparable saved publications.

Default behavior is fixture/offline-safe: pass ``--html-file`` to parse a saved
detail page. Use ``--fetch-live`` only for a single operator-approved URL; this
does not start discovery, queues, or broad crawling.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from bgrealestate.matching import (  # noqa: E402
    MatchResult,
    classify_source_publication,
    fingerprint_from_mapping,
    rank_comparable_properties,
)
from bgrealestate.source_registry import SourceRegistry  # noqa: E402


REGISTRY_PATH = REPO / "data" / "source_registry.json"
SCRAPED_ROOT = REPO / "data" / "scraped"
EXPORT_ROOT = REPO / "docs" / "exports"
LIVE_ALLOWED_LEGAL_MODES = {"public_crawl_with_review", "official_api_allowed"}


def _source_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _host_key(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""


def _load_source_configs() -> dict[str, dict[str, Any]]:
    try:
        import live_scraper  # type: ignore

        return dict(live_scraper.SOURCE_CONFIGS)
    except Exception:
        return {}


def _registry_lookup(registry: SourceRegistry) -> tuple[dict[str, Any], dict[str, str]]:
    entries = {entry.source_name: entry for entry in registry.all()}
    by_key: dict[str, str] = {}
    for entry in registry.all():
        by_key[_source_key(entry.source_name)] = entry.source_name
    return entries, by_key


def infer_source_name(url: str, registry: SourceRegistry, *, source_hint: str | None = None) -> str:
    entries, by_key = _registry_lookup(registry)
    if source_hint:
        direct = entries.get(source_hint)
        if direct is not None:
            return direct.source_name
        keyed = by_key.get(_source_key(source_hint))
        if keyed and keyed in entries:
            return entries[keyed].source_name
        raise SystemExit(f"unknown source hint {source_hint!r}; expected a source name from data/source_registry.json")

    host = _host_key(url)
    candidates: list[tuple[int, str]] = []
    source_configs = _load_source_configs()
    for entry in registry.all():
        urls = [entry.primary_url, *entry.related_urls]
        cfg = next((cfg for cfg in source_configs.values() if cfg.get("name") == entry.source_name), {})
        urls.extend([cfg.get("base_url"), *cfg.get("search_urls", [])])
        for candidate_url in urls:
            if not candidate_url:
                continue
            candidate_host = _host_key(str(candidate_url))
            if not candidate_host:
                continue
            if host == candidate_host:
                candidates.append((100 + len(candidate_host), entry.source_name))
            elif host.endswith("." + candidate_host):
                candidates.append((80 + len(candidate_host), entry.source_name))
            elif candidate_host in host:
                candidates.append((40 + len(candidate_host), entry.source_name))

    if not candidates:
        raise SystemExit(f"could_not_infer_source_from_url host={host!r}; pass --source")
    candidates.sort(reverse=True)
    return candidates[0][1]


def _assert_live_allowed(source_name: str, registry: SourceRegistry, allowed_tiers: set[int]) -> None:
    source = registry.by_name(source_name)
    if source is None:
        raise SystemExit(f"source {source_name!r} not found in data/source_registry.json")
    if source.tier not in allowed_tiers:
        raise SystemExit(f"source {source.source_name!r} is tier {source.tier}; allowed tiers are {sorted(allowed_tiers)}")
    if source.legal_mode not in LIVE_ALLOWED_LEGAL_MODES:
        raise SystemExit(
            f"live intake blocked for {source.source_name!r}: legal_mode={source.legal_mode!r}. "
            "Use a saved fixture/partner import/manual route."
        )


def parse_query_link(
    *,
    url: str,
    source_name: str,
    html: str,
) -> dict[str, Any]:
    import live_scraper  # type: ignore

    if source_name == "Homes.bg":
        parsed = live_scraper.parse_homes_detail(html, url)
    elif source_name == "imot.bg":
        parsed = live_scraper.parse_imot_detail(html, url)
    else:
        parsed = live_scraper.parse_listing_html(html, url, source_name)
    if not parsed:
        raise SystemExit(f"parser produced no property candidate for {source_name}: {url}")
    return parsed


def fetch_query_html(url: str) -> str:
    import live_scraper  # type: ignore

    client = live_scraper.make_client()
    try:
        html = live_scraper.fetch_page(client, url)
    finally:
        client.close()
    if not html:
        raise SystemExit(f"failed_to_fetch_query_url: {url}")
    return html


def _iter_saved_listing_files(scraped_root: Path) -> Iterable[Path]:
    for source_dir in sorted(scraped_root.iterdir()):
        listings_dir = source_dir / "listings"
        if listings_dir.exists():
            yield from sorted(listings_dir.glob("*.json"))


def _is_accepted_candidate(row: dict[str, Any]) -> bool:
    provenance = dict(row.get("crawl_provenance") or {})
    for key in ("scrape_status", "scrape_acceptance_status", "source_publication_type", "listing_status"):
        if key in row:
            provenance[key] = row.get(key)
    if str(provenance.get("scrape_status") or "").upper() != "SCRAPED_OK":
        return False
    if provenance.get("scrape_acceptance_status") != "accepted_single_entity_candidate":
        return False
    if provenance.get("source_publication_type") != "single_unit_candidate":
        return False
    if str(provenance.get("listing_status") or "active").lower() in {"inactive", "removed", "expired"}:
        return False
    return True


def load_comparable_corpus(
    *,
    registry: SourceRegistry,
    scraped_root: Path,
    allowed_tiers: set[int],
    accepted_only: bool,
    max_corpus_files: int = 0,
) -> tuple[list[Any], int]:
    entries, by_key = _registry_lookup(registry)
    out = []
    scanned = 0
    for path in _iter_saved_listing_files(scraped_root):
        if max_corpus_files > 0 and scanned >= max_corpus_files:
            break
        scanned += 1
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        source_name = str(row.get("source_name") or "")
        if not source_name:
            source_name = by_key.get(_source_key(path.parent.parent.name), "")
        source = entries.get(source_name)
        if source is None or source.tier not in allowed_tiers:
            continue
        if accepted_only and not _is_accepted_candidate(row):
            continue
        fp = fingerprint_from_mapping(row, source_tier=source.tier, source_name=source.source_name)
        out.append(fp)
    return out, scanned


def _result_to_dict(result: MatchResult) -> dict[str, Any]:
    candidate = result.candidate
    return {
        "score": result.score,
        "match_class": result.match_class,
        "source_name": candidate.source_name,
        "source_tier": candidate.source_tier,
        "reference_id": candidate.reference_id,
        "listing_url": candidate.listing_url,
        "title": candidate.title,
        "city": candidate.city,
        "district": candidate.district,
        "price": candidate.price,
        "currency": candidate.currency,
        "area_sqm": candidate.area_sqm,
        "rooms": candidate.rooms,
        "score_components": dict(result.score_components),
        "evidence": list(result.evidence),
        "conflicts": list(result.conflicts),
    }


def write_output(payload: dict[str, Any], output_path: Path | None) -> Path:
    if output_path is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = EXPORT_ROOT / f"property-link-comparable-search-{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape one property link and rank comparable saved properties.")
    parser.add_argument("--url", required=True, help="Property detail URL to intake.")
    parser.add_argument("--source", help="Optional source display name or source key when URL inference is ambiguous.")
    parser.add_argument("--html-file", type=Path, help="Parse this saved HTML file instead of fetching live.")
    parser.add_argument("--fetch-live", action="store_true", help="Fetch exactly the provided URL live; no discovery crawl is started.")
    parser.add_argument("--tiers", default="1,2,3", help="Comma-separated source tiers to search. Default: 1,2,3.")
    parser.add_argument("--include-same-source", action="store_true", help="Do not exclude same-source candidates.")
    parser.add_argument("--include-unreviewed", action="store_true", help="Search all saved rows, not only accepted single-unit candidates.")
    parser.add_argument("--min-score", type=float, default=0.25)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-corpus-files", type=int, default=0, help="Optional smoke-test cap. Default 0 scans all saved rows.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    allowed_tiers = {int(part.strip()) for part in args.tiers.split(",") if part.strip()}
    registry = SourceRegistry.from_file(REGISTRY_PATH)
    source_name = infer_source_name(args.url, registry, source_hint=args.source)

    if args.html_file:
        html = args.html_file.read_text(encoding="utf-8")
    elif args.fetch_live:
        _assert_live_allowed(source_name, registry, allowed_tiers)
        html = fetch_query_html(args.url)
    else:
        raise SystemExit("provide --html-file for offline parsing or --fetch-live for one approved live URL")

    parsed = parse_query_link(url=args.url, source_name=source_name, html=html)
    source = registry.by_name(source_name)
    query = fingerprint_from_mapping(parsed, source_tier=source.tier if source else None, source_name=source_name)
    decision = classify_source_publication(query)
    corpus, scanned_files = load_comparable_corpus(
        registry=registry,
        scraped_root=SCRAPED_ROOT,
        allowed_tiers=allowed_tiers,
        accepted_only=not args.include_unreviewed,
        max_corpus_files=args.max_corpus_files,
    )
    matches = rank_comparable_properties(
        query,
        corpus,
        include_same_source=args.include_same_source,
        min_score=args.min_score,
        limit=args.limit,
    )
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": {
            "source_name": query.source_name,
            "source_tier": query.source_tier,
            "listing_url": query.listing_url,
            "reference_id": query.reference_id,
            "title": query.title,
            "city": query.city,
            "district": query.district,
            "price": query.price,
            "currency": query.currency,
            "price_status": query.price_status,
            "area_sqm": query.area_sqm,
            "rooms": query.rooms,
            "classification": decision.classification,
            "is_single_unit_candidate": decision.is_single_unit_candidate,
            "classification_blockers": list(decision.blockers),
        },
        "search_policy": {
            "searched_tiers": sorted(allowed_tiers),
            "accepted_only": not args.include_unreviewed,
            "include_same_source": args.include_same_source,
            "min_score": args.min_score,
            "candidate_count": len(corpus),
            "corpus_files_scanned": scanned_files,
            "max_corpus_files": args.max_corpus_files,
            "live_fetch_used": bool(args.fetch_live and not args.html_file),
        },
        "summary": {
            "matches_returned": len(matches),
            "same_property_candidates": sum(1 for item in matches if item.match_class == "same_property_candidate"),
            "comparable_properties": sum(1 for item in matches if item.match_class == "comparable_property"),
            "weak_candidates": sum(1 for item in matches if item.match_class == "weak_candidate"),
        },
        "matches": [_result_to_dict(item) for item in matches],
    }
    output_path = write_output(payload, args.output)
    try:
        display_path = str(output_path.relative_to(REPO))
    except ValueError:
        display_path = str(output_path)
    print(f"output={display_path}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    if decision.blockers:
        print("query_classification_blockers=" + ",".join(decision.blockers))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
