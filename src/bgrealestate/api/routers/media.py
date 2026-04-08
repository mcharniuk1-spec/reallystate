"""Image serving and proxy endpoints.

Serves locally-stored listing images and proxies external URLs that
haven't been downloaded yet.
"""

from __future__ import annotations

import logging
import re
from typing import Annotated, Any
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ...db.repositories import ListingMediaRepository
from ...services.media import get_image_path, proxy_external_image
from ..deps import get_db

router = APIRouter(tags=["media"])
logger = logging.getLogger(__name__)

_SAFE_URL_RE = re.compile(r"^https?://")
_CACHE_MAX_AGE = 86400 * 7  # 7 days


@router.get("/media/proxy")
def proxy_image(
    url: str = Query(..., description="External image URL to proxy"),
) -> Response:
    """Proxy an external image URL for the frontend.

    Used when images haven't been downloaded yet. The frontend sends
    the external URL through this endpoint to bypass hotlink protection.
    """
    decoded = unquote(url)
    if not _SAFE_URL_RE.match(decoded):
        raise HTTPException(status_code=400, detail="invalid_url")

    try:
        data, ct = proxy_external_image(decoded)
    except Exception as exc:
        logger.warning("Proxy request failed for %s: %s", decoded, exc)
        raise HTTPException(status_code=502, detail="image_proxy_failed") from exc

    return Response(
        content=data,
        media_type=ct,
        headers={
            "Cache-Control": f"public, max-age={_CACHE_MAX_AGE}",
            "Content-Length": str(len(data)),
        },
    )


@router.get("/media/{media_id}")
def serve_media(
    media_id: str,
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    """Serve a stored listing image by its media_id."""
    repo = ListingMediaRepository(session)
    media = repo.get(media_id)
    if media is None:
        raise HTTPException(status_code=404, detail="media_not_found")

    if media.storage_key:
        local = get_image_path(media.storage_key)
        if local is not None:
            data = local.read_bytes()
            return Response(
                content=data,
                media_type=media.mime_type or "image/jpeg",
                headers={
                    "Cache-Control": f"public, max-age={_CACHE_MAX_AGE}",
                    "Content-Length": str(len(data)),
                },
            )

    if media.url and _SAFE_URL_RE.match(media.url):
        try:
            data, ct = proxy_external_image(media.url)
            return Response(
                content=data,
                media_type=ct,
                headers={"Cache-Control": f"public, max-age={_CACHE_MAX_AGE}"},
            )
        except Exception as exc:
            logger.warning("Proxy failed for %s: %s", media.url, exc)
            raise HTTPException(status_code=502, detail="image_proxy_failed") from exc

    raise HTTPException(status_code=404, detail="image_not_available")


@router.get("/listings/{reference_id}/images")
def list_listing_images(
    reference_id: str,
    session: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    """Return all images for a listing with serving URLs."""
    repo = ListingMediaRepository(session)
    media_rows = repo.list_for_listing(reference_id)
    items = []
    for m in media_rows:
        serve_url = f"/media/{m.media_id}" if m.storage_key else f"/media/proxy?url={m.url}"
        items.append({
            "media_id": m.media_id,
            "url": m.url,
            "serve_url": serve_url,
            "storage_key": m.storage_key,
            "mime_type": m.mime_type,
            "width": m.width,
            "height": m.height,
            "file_size": m.file_size,
            "ordering": m.ordering,
            "download_status": m.download_status,
        })
    return {"reference_id": reference_id, "count": len(items), "images": items}
