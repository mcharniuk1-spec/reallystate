from __future__ import annotations

import hashlib
from typing import Any


def stable_evidence_id(prefix: str, *parts: object) -> str:
    raw = "::".join(str(part or "") for part in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]}"


def import_eligibility_from_provenance(provenance: dict[str, Any]) -> tuple[bool, str, str | None]:
    status = str(provenance.get("scrape_status") or "").strip()
    acceptance = str(provenance.get("scrape_acceptance_status") or "").strip()
    publication_type = str(provenance.get("source_publication_type") or "").strip()
    listing_status = str(provenance.get("listing_status") or "").strip().lower()
    price_status = str(provenance.get("price_status") or "").strip().lower()

    if status in {"", "PENDING_QA", "UNKNOWN"}:
        return False, "blocked", "unreviewed_quality_state"
    if status == "LOST" or provenance.get("needs_rescrape") is True:
        return False, "blocked", "lost_rescrape_required"
    if acceptance == "not_single_entity" or publication_type == "multi_unit_or_development":
        return False, "blocked", "grouped_publication_not_single_entity"
    if listing_status in {"inactive", "removed", "expired", "sold", "rented", "stale_review"}:
        return False, "blocked", "inactive_source_listing"
    if provenance.get("price_zero_coerced_to_null") and price_status not in {"on_request", "undefined"}:
        return False, "blocked", "invalid_zero_price_state"
    if status == "SCRAPED_OK" and acceptance == "accepted_single_entity_candidate":
        return True, "accepted_single_entity_candidate", None
    return False, "blocked", "unsupported_acceptance_state"
