from __future__ import annotations

import argparse
from pathlib import Path

from .connectors.factory import marketplace_sources
from .exporters import export_matrices
from .source_registry import SourceRegistry


def _default_registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "source_registry.json"


def _skills_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "agent-skills"


def _discover_skills(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        return []
    names: list[str] = []
    for path in sorted(skills_dir.iterdir()):
        if path.is_dir() and (path / "SKILL.md").exists():
            names.append(path.name)
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulgaria real estate ingestion toolkit")
    parser.add_argument("--registry", type=Path, default=_default_registry_path(), help="Path to the source registry JSON file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-sources", help="Print seeded sources.")
    subparsers.add_parser("list-skills", help="Print available project agent skills.")
    export_parser = subparsers.add_parser("export-matrices", help="Export source and legal matrices.")
    export_parser.add_argument("--out-dir", type=Path, default=Path("artifacts"))

    ingest_parser = subparsers.add_parser(
        "ingest-fixture",
        help="Parse a fixture HTML file and insert it into the database (offline, no network).",
    )
    ingest_parser.add_argument("source_name", help="Registry source name (e.g. Homes.bg)")
    ingest_parser.add_argument("fixture_dir", type=Path, help="Path to fixture case dir (must contain raw.html and expected.json)")
    ingest_parser.add_argument("--dry-run", action="store_true", help="Parse and print canonical listing; do not touch the database.")

    sync_parser = subparsers.add_parser(
        "sync-database",
        help="Upsert marketplace sources (excluding social/messenger), legal rules, and primary URLs into PostgreSQL.",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print counts only; do not connect to the database.",
    )
    sync_social_parser = subparsers.add_parser(
        "sync-social-database",
        help="Upsert tier-4 social sources, legal rules, and all known social links into PostgreSQL.",
    )
    sync_social_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print counts only; do not connect to the database.",
    )
    export_tier4_parser = subparsers.add_parser(
        "export-tier4",
        help="Export tier-4 social links and per-message fixture dataset to JSON/CSV.",
    )
    export_tier4_parser.add_argument("--out-dir", type=Path, default=Path("docs/exports"))
    seed_social_parser = subparsers.add_parser(
        "seed-social-fixtures",
        help="Insert fixture-backed tier-4 social threads/messages into PostgreSQL.",
    )
    seed_social_parser.add_argument("--account-id", default="acct_tier4_seed")
    seed_social_parser.add_argument("--dry-run", action="store_true")

    dl_img_parser = subparsers.add_parser(
        "download-images",
        help="Download images for listings already in DB (or from fixtures).",
    )
    dl_img_parser.add_argument("--reference-id", help="Download images for a specific listing reference_id.")
    dl_img_parser.add_argument("--source-name", help="Download images for all listings from this source.")
    dl_img_parser.add_argument("--limit", type=int, default=50, help="Max listings to process (default 50).")
    dl_img_parser.add_argument("--dry-run", action="store_true", help="Show URLs without downloading.")

    bcpea_parser = subparsers.add_parser(
        "scrape-bcpea",
        help="Scrape BCPEA property auction listings (public register, legal to crawl).",
    )
    bcpea_parser.add_argument("--pages", type=int, default=3, help="Max pages to scrape (default 3).")
    bcpea_parser.add_argument("--perpage", type=int, default=36, help="Results per page (default 36).")
    bcpea_parser.add_argument("--rate-limit", type=float, default=1.5, help="Seconds between requests (default 1.5).")
    bcpea_parser.add_argument("--fetch-details", action="store_true", help="Also fetch individual detail pages.")
    bcpea_parser.add_argument("--out-dir", type=Path, default=Path("output/bcpea"), help="Output directory for scraped data.")
    bcpea_parser.add_argument("--dry-run", action="store_true", help="Print discovery results only, don't write files.")

    args = parser.parse_args()
    registry = SourceRegistry.from_file(args.registry)

    if args.command == "list-sources":
        for entry in registry.all():
            print(f"{entry.tier} | {entry.source_name} | {entry.source_family.value} | {entry.access_mode.value}")
        return 0

    if args.command == "list-skills":
        for name in _discover_skills(_skills_dir()):
            print(name)
        return 0

    if args.command == "ingest-fixture":
        import json
        from datetime import datetime, timezone
        from .connectors.factory import build_connector

        source = registry.by_name(args.source_name)
        if not source:
            print(f"error: source {args.source_name!r} not found in registry")
            return 1
        raw_path = args.fixture_dir / "raw.html"
        if not raw_path.exists():
            raw_path = args.fixture_dir / "raw.json"
        if not raw_path.exists():
            print(f"error: no raw.html or raw.json in {args.fixture_dir}")
            return 1
        html = raw_path.read_text(encoding="utf-8")
        expected_path = args.fixture_dir / "expected.json"
        expected = json.loads(expected_path.read_text(encoding="utf-8")) if expected_path.exists() else {}
        url = expected.get("listing_url", f"https://fixture/{args.source_name}/{args.fixture_dir.name}")
        seed_path = args.fixture_dir / "seed.json"
        seed = json.loads(seed_path.read_text(encoding="utf-8")) if seed_path.exists() else None

        connector = build_connector(args.source_name, registry)
        now = datetime.now(tz=timezone.utc)

        if hasattr(connector, "parse_and_normalize_from_html"):
            out = connector.parse_and_normalize_from_html(url=url, html=html, discovered_at=now, seed=seed)
        elif hasattr(connector, "parse_api_response"):
            out = connector.parse_api_response(url=url, json_text=html, fetched_at=now, seed=seed)
        else:
            print(f"error: connector for {args.source_name} has no parse method")
            return 1

        canonical = out["canonical_listing"]
        if args.dry_run:
            from dataclasses import asdict
            print(json.dumps({k: str(v) if isinstance(v, datetime) else v for k, v in asdict(canonical).items()}, indent=2, ensure_ascii=False, default=str))
            return 0

        from .connectors.ingest import ingest_listing_detail_html
        from .db.session import create_db_engine

        engine = create_db_engine()
        ingest_result = ingest_listing_detail_html(
            engine=engine, source=source, url=url, html=html,
            discovered_at=now, download_images=not args.dry_run,
        )
        print(f"ingested: {ingest_result}")
        return 0

    if args.command == "download-images":
        from .db.session import create_db_engine, session_scope
        from .db.repositories import CanonicalListingRepository, ListingMediaRepository
        from .db.ids import new_id
        from .services.media import download_image

        engine = create_db_engine()
        with session_scope(engine) as session:
            repo = CanonicalListingRepository(session)
            listings = repo.list_recent(
                limit=args.limit,
                source_name=args.source_name,
            )
            if args.reference_id:
                m = repo.get(args.reference_id)
                listings = [m] if m else []

            total_dl = 0
            for listing in listings:
                urls = list(listing.image_urls or [])
                if not urls:
                    continue
                if args.dry_run:
                    print(f"{listing.reference_id}: {len(urls)} images")
                    for u in urls:
                        print(f"  {u}")
                    continue

                media_repo = ListingMediaRepository(session)
                for i, url in enumerate(urls):
                    result = download_image(url, reference_id=listing.reference_id, ordering=i)
                    media_id = new_id("lmed")
                    media_repo.upsert_media(
                        media_id=media_id,
                        listing_reference_id=listing.reference_id,
                        url=url,
                        ordering=i,
                        content_hash=result.content_hash if result.status == "downloaded" else None,
                        storage_key=result.storage_key if result.status == "downloaded" else None,
                        mime_type=result.mime_type if result.status == "downloaded" else None,
                        width=result.width,
                        height=result.height,
                        file_size=result.file_size if result.status == "downloaded" else None,
                        download_status=result.status,
                    )
                    status_icon = "ok" if result.status == "downloaded" else "FAIL"
                    print(f"  [{status_icon}] {url}")
                    total_dl += 1 if result.status == "downloaded" else 0

            if not args.dry_run:
                print(f"\nDownloaded {total_dl} images for {len(listings)} listings.")
        return 0

    if args.command == "export-matrices":
        export_matrices(registry.all(), args.out_dir)
        print(f"exported matrices to {args.out_dir}")
        return 0

    if args.command == "sync-database":
        market = marketplace_sources(registry)
        if args.dry_run:
            print(f"would upsert {len(market)} marketplace sources (tier 1–3 + registers/OTAs; social/messenger skipped)")
            print("run alembic upgrade head (or make migrate) before writing if the database is new")
            return 0
        from .db.session import create_db_engine
        from .db_sync import sync_marketplace_sources_to_db

        engine = create_db_engine()
        stats = sync_marketplace_sources_to_db(engine, registry)
        print(f"synced: {stats}")
        return 0

    if args.command == "sync-social-database":
        from .social_tier4 import collect_tier4_links, tier4_sources

        t4 = tier4_sources(registry)
        links = collect_tier4_links(registry)
        if args.dry_run:
            print(f"would upsert {len(t4)} tier-4 social sources and {len(links)} social endpoints")
            print("run alembic upgrade head (or make migrate) before writing if the database is new")
            return 0
        from .db.session import create_db_engine
        from .db_sync import sync_social_sources_to_db

        engine = create_db_engine()
        stats = sync_social_sources_to_db(engine, registry)
        print(f"synced: {stats}")
        return 0

    if args.command == "export-tier4":
        from .social_tier4 import write_tier4_exports

        stats = write_tier4_exports(registry, out_dir=args.out_dir)
        print(f"exported tier-4 dataset: {stats}")
        return 0

    if args.command == "seed-social-fixtures":
        from .social_seed import build_social_seed_payloads

        payloads = build_social_seed_payloads(account_id=args.account_id)
        if args.dry_run:
            print(f"would seed {len(payloads)} tier-4 fixture messages for account_id={args.account_id}")
            return 0
        from .db.session import create_db_engine
        from .social_seed import seed_social_fixtures_to_db

        engine = create_db_engine()
        stats = seed_social_fixtures_to_db(engine, account_id=args.account_id)
        print(f"seeded: {stats}")
        return 0

    if args.command == "scrape-bcpea":
        return _scrape_bcpea(args, registry)

    return 1


def _scrape_bcpea(args: argparse.Namespace, registry: SourceRegistry) -> int:
    import json as _json
    import logging
    from dataclasses import asdict
    from datetime import datetime, timezone

    from .connectors.tier3 import BcpeaAuctionConnector

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    connector = BcpeaAuctionConnector(
        registry,
        perpage=args.perpage,
        rate_limit=args.rate_limit,
    )

    out_dir: Path = args.out_dir
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    all_items: list[dict] = []
    detail_results: list[dict] = []
    total_pages = min(args.pages, 200)

    for page in range(1, total_pages + 1):
        print(f"[BCPEA] Fetching discovery page {page}/{total_pages}...")
        try:
            discovery_page = connector.discover_page(page)
        except Exception as e:
            print(f"[BCPEA] Error on page {page}: {e}")
            break

        for discovery_item in discovery_page.listings:
            all_items.append(asdict(discovery_item))

        print(f"[BCPEA] Page {page}: {len(discovery_page.listings)} items (total so far: {len(all_items)})")

        if discovery_page.next_page is None or page >= total_pages:
            break

    print(f"\n[BCPEA] Discovery complete: {len(all_items)} auction listings found")

    if args.dry_run:
        for item_dict in all_items[:5]:
            print(_json.dumps(item_dict, indent=2, ensure_ascii=False))
        if len(all_items) > 5:
            print(f"... and {len(all_items) - 5} more")
        return 0

    discovery_path = out_dir / "discovery.json"
    discovery_path.write_text(
        _json.dumps(all_items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[BCPEA] Discovery saved to {discovery_path}")

    if args.fetch_details:
        now = datetime.now(tz=timezone.utc)
        for i, item_dict in enumerate(all_items):
            url = item_dict["url"]
            print(f"[BCPEA] Fetching detail {i + 1}/{len(all_items)}: {url}")
            try:
                raw = connector.fetch_listing_detail(url=url, fetched_at=now)
                parsed = connector.parse_detail_html(html=raw.body, url=url)
                detail_results.append(parsed)
            except Exception as e:
                print(f"[BCPEA] Error fetching {url}: {e}")
                continue

        details_path = out_dir / "details.json"
        details_path.write_text(
            _json.dumps(detail_results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[BCPEA] {len(detail_results)} detail records saved to {details_path}")

    return 0

