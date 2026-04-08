from __future__ import annotations

import uuid


def new_id(prefix: str) -> str:
    # Stable, URL-safe, sortable-enough for MVP debugging.
    return f"{prefix}_{uuid.uuid4().hex}"

