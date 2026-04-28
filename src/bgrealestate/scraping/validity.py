"""Validity policy for Stage 2 threshold counting."""

from __future__ import annotations

VALIDITY_POLICY: dict[str, object] = {
    "region_key": "varna",
    "requires_source_identity": True,
    "requires_section_identity": True,
    "requires_segment_identity": True,
    "requires_detail_parse": True,
    "requires_location_signal": True,
    "requires_text_signal": True,
    "requires_minimal_structured_signal": True,
    "media_required_for_threshold": False,
    "media_gap_flag": "media_incomplete",
}


def valid_listing_where(alias: str = "cl") -> str:
    """Return the SQL predicate used for threshold counting.

    The policy is intentionally strict on identity, region, detail parse, and
    text/location coverage, while allowing media gaps to be tracked separately.
    """
    return f"""
        {alias}.removed_at is null
        and coalesce({alias}.region_key, '') = 'varna'
        and (
            nullif(trim(coalesce({alias}.source_section_id, '')), '') is not null
            or (
                nullif(trim(coalesce({alias}.source_name, '')), '') is not null
                and nullif(trim(coalesce({alias}.segment_key, '')), '') is not null
            )
        )
        and nullif(trim(coalesce({alias}.reference_id, '')), '') is not null
        and nullif(trim(coalesce({alias}.external_id, '')), '') is not null
        and nullif(trim(coalesce({alias}.detail_url_canonical, {alias}.listing_url, '')), '') is not null
        and (
            nullif(trim(coalesce({alias}.city, '')), '') is not null
            or nullif(trim(coalesce({alias}.address_text, '')), '') is not null
        )
        and nullif(trim(coalesce({alias}.combined_text, {alias}.description, {alias}.raw_text_fallback, '')), '') is not null
        and (
            {alias}.price is not null
            or {alias}.area_sqm is not null
            or {alias}.rooms is not null
            or {alias}.structured_extra <> '{{}}'::jsonb
        )
    """


def media_present_where(alias: str = "cl") -> str:
    return f"jsonb_array_length(coalesce({alias}.image_urls, '[]'::jsonb)) > 0"


__all__ = ["VALIDITY_POLICY", "valid_listing_where", "media_present_where"]
