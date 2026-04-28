"""Persist manifest sections + layered patterns into PostgreSQL (operator-triggered)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from ..db.ids import new_id
from ..db.session import session_scope
from .manifest import SectionManifestEntry, iter_sections
from .pattern_layers import PATTERN_LAYERS


def upsert_sections_from_manifest(engine: Engine, sections: list[SectionManifestEntry]) -> dict[str, int]:
    """Upsert ``source_section``, ``source_section_pattern``, ``segment_fulfillment`` rows."""
    now = datetime.now(tz=timezone.utc)
    sec_count = 0
    pat_count = 0
    ful_count = 0
    with session_scope(engine) as session:
        for sec in sections:
            session.execute(
                text(
                    """
                    insert into source_section (
                        section_id, source_name, region_key, segment_key, vertical_key,
                        section_label, entry_urls, active, legal_notes, varna_filter, created_at, updated_at
                    ) values (
                        :section_id, :source_name, :region_key, :segment_key, :vertical_key,
                        :section_label, cast(:entry_urls as jsonb), :active, :legal_notes, cast(:varna_filter as jsonb), :created_at, :updated_at
                    )
                    on conflict (source_name, region_key, segment_key, vertical_key) do update set
                        section_label = excluded.section_label,
                        entry_urls = excluded.entry_urls,
                        active = excluded.active,
                        legal_notes = excluded.legal_notes,
                        varna_filter = excluded.varna_filter,
                        updated_at = excluded.updated_at
                    """
                ),
                {
                    "section_id": sec.section_id,
                    "source_name": sec.source_name,
                    "region_key": sec.region_key,
                    "segment_key": sec.segment_key,
                    "vertical_key": sec.vertical_key,
                    "section_label": sec.section_label,
                    "entry_urls": json.dumps(sec.entry_urls),
                    "active": sec.active,
                    "legal_notes": sec.patterns.get("legal_notes"),
                    "varna_filter": json.dumps(sec.patterns.get("varna_enforcement") or {}),
                    "created_at": now,
                    "updated_at": now,
                },
            )
            sec_count += 1

            for layer in PATTERN_LAYERS:
                spec = sec.patterns.get(layer)
                if spec is None:
                    continue
                pid = new_id("spat")
                session.execute(
                    text(
                        """
                        insert into source_section_pattern (
                            pattern_id, section_id, pattern_layer, schema_version, parser_profile, spec_jsonb, created_at
                        ) values (
                            :pattern_id, :section_id, :pattern_layer, :schema_version, :parser_profile, cast(:spec as jsonb), :created_at
                        )
                        on conflict (section_id, pattern_layer, schema_version) do update set
                            parser_profile = excluded.parser_profile,
                            spec_jsonb = excluded.spec_jsonb
                        """
                    ),
                    {
                        "pattern_id": pid,
                        "section_id": sec.section_id,
                        "pattern_layer": layer,
                        "schema_version": 1,
                        "parser_profile": str((spec or {}).get("parser_profile") or "generic_html_v1"),
                        "spec": json.dumps(spec or {}),
                        "created_at": now,
                    },
                )
                pat_count += 1

            fid = f"fulfill__{sec.section_id}"
            session.execute(
                text(
                    """
                    insert into segment_fulfillment (
                        fulfillment_id, section_id, target_valid_listings, current_valid_listings, current_total_listings, last_status, incremental_ready
                    ) values (
                        :fulfillment_id, :section_id, :target, 0, 0, 'planned', false
                    )
                    on conflict (section_id) do update set
                        target_valid_listings = excluded.target_valid_listings
                    """
                ),
                {
                    "fulfillment_id": fid,
                    "section_id": sec.section_id,
                    "target": int(sec.patterns.get("target_valid_listings") or 100),
                },
            )
            ful_count += 1
    return {"sections_upserted": sec_count, "patterns_upserted": pat_count, "fulfillment_touched": ful_count}


def sync_manifest_to_db(engine: Engine, manifest: dict[str, Any]) -> dict[str, int]:
    rows = iter_sections(manifest)
    return upsert_sections_from_manifest(engine, rows)
