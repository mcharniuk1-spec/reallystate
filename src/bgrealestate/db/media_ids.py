from __future__ import annotations

from hashlib import sha1


def stable_listing_media_id(listing_reference_id: str, url: str) -> str:
    key = f"{listing_reference_id}\0{url}".encode("utf-8", errors="ignore")
    return f"lmed_{sha1(key).hexdigest()[:24]}"
