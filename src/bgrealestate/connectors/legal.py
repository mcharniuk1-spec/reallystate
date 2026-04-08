from __future__ import annotations

from dataclasses import dataclass

from ..enums import AccessMode, SourceFamily
from ..models import SourceRegistryEntry


class LegalGateError(RuntimeError):
    """Raised when a connector operation violates source legal gates."""


@dataclass(frozen=True)
class DerivedLegalRule:
    rule_id: str
    allowed_for_ingestion: bool
    allowed_for_publishing: bool
    requires_contract: bool
    requires_consent: bool
    blocks_live_scrape: bool
    reason: str


def derive_default_legal_rule(entry: SourceRegistryEntry) -> DerivedLegalRule:
    """Map registry legal_mode to a default row for ``source_legal_rule`` (fail-safe)."""
    rule_id = f"{entry.source_name}:default"
    pub = bool(entry.publish_capable)
    lm = entry.legal_mode

    if lm == "official_partner_or_vendor_only":
        return DerivedLegalRule(
            rule_id=rule_id,
            allowed_for_ingestion=True,
            allowed_for_publishing=pub,
            requires_contract=True,
            requires_consent=False,
            blocks_live_scrape=True,
            reason="Ingestion only via official partner, vendor API, or licensed feed — not public HTML scrape.",
        )
    if lm == "licensing_required":
        return DerivedLegalRule(
            rule_id=rule_id,
            allowed_for_ingestion=False,
            allowed_for_publishing=pub,
            requires_contract=True,
            requires_consent=False,
            blocks_live_scrape=True,
            reason="Commercial data use requires explicit license; automated crawl disabled until authorized.",
        )
    if lm == "consent_or_manual_only":
        return DerivedLegalRule(
            rule_id=rule_id,
            allowed_for_ingestion=False,
            allowed_for_publishing=pub,
            requires_contract=False,
            requires_consent=True,
            blocks_live_scrape=True,
            reason="Official or consent-driven access only; no bulk automated crawl.",
        )
    if lm == "legal_review_required":
        return DerivedLegalRule(
            rule_id=rule_id,
            allowed_for_ingestion=True,
            allowed_for_publishing=pub,
            requires_contract=False,
            requires_consent=False,
            blocks_live_scrape=True,
            reason="Elevated legal/anti-bot risk; live crawl paused until operator legal review.",
        )
    if lm in {"public_crawl_with_review", "public_or_contract_review"}:
        return DerivedLegalRule(
            rule_id=rule_id,
            allowed_for_ingestion=True,
            allowed_for_publishing=pub,
            requires_contract=False,
            requires_consent=False,
            blocks_live_scrape=False,
            reason="Public pages may be crawled conservatively with operator review and rate limits.",
        )
    if lm == "official_api_allowed":
        return DerivedLegalRule(
            rule_id=rule_id,
            allowed_for_ingestion=True,
            allowed_for_publishing=pub,
            requires_contract=False,
            requires_consent=False,
            blocks_live_scrape=False,
            reason="Prefer official API for ingestion; HTTP used only where documented as allowed.",
        )
    return DerivedLegalRule(
        rule_id=rule_id,
        allowed_for_ingestion=False,
        allowed_for_publishing=pub,
        requires_contract=True,
        requires_consent=False,
        blocks_live_scrape=True,
        reason=f"Unknown legal_mode={lm!r}; blocked until registry policy is explicit.",
    )


def assert_live_http_allowed(entry: SourceRegistryEntry) -> None:
    """Block general HTTP fetches for gated sources and all social/messenger families."""
    if entry.source_family in (SourceFamily.SOCIAL_PUBLIC_CHANNEL, SourceFamily.PRIVATE_MESSENGER):
        raise LegalGateError("source family is social/messenger — not a marketplace crawl target")
    rule = derive_default_legal_rule(entry)
    if rule.blocks_live_scrape:
        raise LegalGateError(f"live HTTP crawl blocked for {entry.source_name}: {rule.reason}")


def endpoint_slug(source_name: str) -> str:
    safe = []
    for ch in source_name.lower():
        if ch.isalnum():
            safe.append(ch)
        elif ch in " .-/":
            safe.append("_")
    out = "".join(safe).strip("_")
    return out or "source"


def default_primary_endpoint(entry: SourceRegistryEntry) -> dict | None:
    """Build a ``source_endpoint`` row from registry planning fields."""
    base = (entry.primary_url or "").strip()
    if not base:
        return None
    headless = entry.access_mode == AccessMode.HEADLESS
    ft = entry.freshness_target.value if hasattr(entry.freshness_target, "value") else str(entry.freshness_target)
    return {
        "endpoint_id": f"{endpoint_slug(entry.source_name)}:site_root",
        "source_name": entry.source_name,
        "endpoint_kind": "site_root",
        "base_url": base,
        "params_template": {},
        "method": "GET",
        "requires_headless": headless,
        "requires_auth": False,
        "rate_limit_policy": {"freshness_target": ft, "access_mode": entry.access_mode.value},
    }
