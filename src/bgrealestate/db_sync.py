from __future__ import annotations

from sqlalchemy.engine import Engine

from .connectors.factory import marketplace_sources
from .connectors.legal import default_primary_endpoint, derive_default_legal_rule, endpoint_slug
from .db.repositories import SourceRegistryRepository
from .db.session import session_scope
from .social_tier4 import collect_tier4_links
from .source_registry import SourceRegistry


def sync_marketplace_sources_to_db(engine: Engine, registry: SourceRegistry) -> dict[str, int]:
    """Persist all non-social sources: registry rows, default legal rules, primary site endpoints."""
    endpoints = 0
    with session_scope(engine) as session:
        repo = SourceRegistryRepository(session)
        entries = marketplace_sources(registry)
        for entry in entries:
            repo.upsert_source(entry)
            rule = derive_default_legal_rule(entry)
            repo.upsert_legal_rule(rule, source_name=entry.source_name)
            ep = default_primary_endpoint(entry)
            if ep:
                repo.upsert_endpoint(**ep)
                endpoints += 1
        return {
            "marketplace_sources": len(entries),
            "legal_rules": len(entries),
            "primary_endpoints": endpoints,
        }


def sync_social_sources_to_db(engine: Engine, registry: SourceRegistry) -> dict[str, int]:
    """Persist tier-4 social/messenger sources, legal rules, and all known URLs as endpoints."""
    links = collect_tier4_links(registry)
    endpoints = 0
    with session_scope(engine) as session:
        repo = SourceRegistryRepository(session)
        for entry in [e for e in registry.all() if e.tier == 4]:
            repo.upsert_source(entry)
            rule = derive_default_legal_rule(entry)
            repo.upsert_legal_rule(rule, source_name=entry.source_name)
        for idx, link in enumerate(links):
            source_name = str(link["source_name"])
            url = str(link["url"])
            repo.upsert_endpoint(
                endpoint_id=f"{endpoint_slug(source_name)}:social:{idx+1}",
                source_name=source_name,
                endpoint_kind="social_channel",
                base_url=url,
                params_template={"url_kind": link["url_kind"]},
                method="GET",
                requires_headless=False,
                requires_auth=bool(link["requires_consent"]),
                rate_limit_policy={
                    "freshness_target": link["freshness_target"],
                    "access_mode": link["access_mode"],
                    "legal_mode": link["legal_mode"],
                },
            )
            endpoints += 1
    return {
        "tier4_sources": len([e for e in registry.all() if e.tier == 4]),
        "legal_rules": len([e for e in registry.all() if e.tier == 4]),
        "social_endpoints": endpoints,
    }
