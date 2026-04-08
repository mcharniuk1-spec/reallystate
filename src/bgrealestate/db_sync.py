from __future__ import annotations

from sqlalchemy.engine import Engine

from .connectors.factory import marketplace_sources
from .connectors.legal import default_primary_endpoint, derive_default_legal_rule
from .db.repositories import SourceRegistryRepository
from .db.session import session_scope
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
