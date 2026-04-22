"""Image download, storage, and serving service.

Handles downloading listing photos from external URLs, storing them on the
local filesystem (or S3 when configured), and recording metadata in the
listing_media + media_asset tables.

Storage layout (local):
    MEDIA_ROOT/<reference_id>/<ordering>_<hash8>.<ext>

Environment:
    MEDIA_STORAGE_PATH  – local directory for cached images (default: data/media)
"""

from __future__ import annotations

import hashlib
import logging
import mimetypes
import os
import shlex
import subprocess
from io import BytesIO
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

MEDIA_ROOT = Path(os.getenv("MEDIA_STORAGE_PATH", "data/media"))

_ALLOWED_CONTENT_TYPES = frozenset({
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
    "image/svg+xml",
})

_EXT_MAP: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
    "image/svg+xml": ".svg",
}

_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per image
_DOWNLOAD_TIMEOUT = 15.0


def _guess_ext(content_type: str | None, url: str) -> str:
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if ct in _EXT_MAP:
            return _EXT_MAP[ct]
    guessed = mimetypes.guess_type(url.split("?")[0])[0]
    if guessed and guessed in _EXT_MAP:
        return _EXT_MAP[guessed]
    return ".jpg"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download_with_curl(url: str) -> tuple[bytes, str | None]:
    """Fallback downloader for environments where httpx DNS resolution is flaky."""
    cmd = f"curl -L --fail --max-time 20 -sS {shlex.quote(url)}"
    proc = subprocess.run(
        ["/bin/zsh", "-lc", cmd],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="ignore").strip() or f"curl exit {proc.returncode}")
    content_type = mimetypes.guess_type(url.split("?")[0])[0]
    return proc.stdout, content_type


def ensure_media_root() -> Path:
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    return MEDIA_ROOT


class DownloadResult:
    __slots__ = ("url", "storage_key", "local_path", "content_hash", "mime_type",
                 "width", "height", "file_size", "status", "error")

    def __init__(
        self,
        *,
        url: str,
        storage_key: str = "",
        local_path: Path | None = None,
        content_hash: str = "",
        mime_type: str = "",
        width: int | None = None,
        height: int | None = None,
        file_size: int = 0,
        status: str = "pending",
        error: str | None = None,
    ):
        self.url = url
        self.storage_key = storage_key
        self.local_path = local_path
        self.content_hash = content_hash
        self.mime_type = mime_type
        self.width = width
        self.height = height
        self.file_size = file_size
        self.status = status
        self.error = error


def download_image(
    url: str,
    *,
    reference_id: str,
    ordering: int = 0,
    client: httpx.Client | None = None,
) -> DownloadResult:
    """Download a single image and store it under MEDIA_ROOT.

    Returns a DownloadResult with status='downloaded' on success or
    status='failed' with an error message.
    """
    result = DownloadResult(url=url)
    own_client = client is None
    http_client = client
    if own_client:
        http_client = httpx.Client(
            timeout=_DOWNLOAD_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "BulgariaRealEstate/0.1 MediaFetcher"},
        )
    if http_client is None:
        result.status = "failed"
        result.error = "HTTP client initialization failed"
        return result

    try:
        resp = http_client.get(url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Image download failed for %s via httpx, trying curl fallback: %s", url, exc)
        try:
            data, guessed_content_type = _download_with_curl(url)
            content_type = guessed_content_type or ""
        except Exception as curl_exc:
            result.status = "failed"
            result.error = f"HTTP error: {exc}; curl fallback: {curl_exc}"
            logger.warning("Image download failed for %s: %s", url, curl_exc)
            return result
    finally:
        if own_client:
            http_client.close()
    if "data" not in locals():
        content_type = resp.headers.get("content-type", "")
        data = resp.content
    ct_base = content_type.split(";")[0].strip().lower() if content_type else ""
    if not ct_base:
        ct_base = mimetypes.guess_type(url.split("?")[0])[0] or "image/jpeg"
    if ct_base not in _ALLOWED_CONTENT_TYPES:
        result.status = "failed"
        result.error = f"Unsupported content type: {ct_base}"
        return result

    if len(data) > _MAX_FILE_SIZE:
        result.status = "failed"
        result.error = f"File too large: {len(data)} bytes"
        return result

    if len(data) == 0:
        result.status = "failed"
        result.error = "Empty response body"
        return result

    sha = _sha256_bytes(data)
    ext = _guess_ext(ct_base, url)
    hash8 = sha[:8]

    listing_dir = ensure_media_root() / reference_id
    listing_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{ordering:04d}_{hash8}{ext}"
    local_path = listing_dir / filename
    local_path.write_bytes(data)

    storage_key = f"{reference_id}/{filename}"

    width, height = None, None
    try:
        from PIL import Image
        with Image.open(BytesIO(data)) as img:
            width, height = img.size
    except Exception:
        pass

    result.storage_key = storage_key
    result.local_path = local_path
    result.content_hash = sha
    result.mime_type = ct_base
    result.width = width
    result.height = height
    result.file_size = len(data)
    result.status = "downloaded"
    return result


def download_listing_images(
    image_urls: list[str],
    *,
    reference_id: str,
    client: httpx.Client | None = None,
) -> list[DownloadResult]:
    """Download all images for a listing. Returns a list of DownloadResults."""
    if not image_urls:
        return []

    own_client = client is None
    http_client = client
    if own_client:
        http_client = httpx.Client(
            timeout=_DOWNLOAD_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "BulgariaRealEstate/0.1 MediaFetcher"},
        )
    if http_client is None:
        return []

    results: list[DownloadResult] = []
    try:
        for i, url in enumerate(image_urls):
            result = download_image(url, reference_id=reference_id, ordering=i, client=http_client)
            results.append(result)
    finally:
        if own_client:
            http_client.close()

    return results


def get_image_path(storage_key: str) -> Path | None:
    """Resolve a storage key to a local file path. Returns None if not found."""
    path = MEDIA_ROOT / storage_key
    if path.is_file():
        return path
    return None


def proxy_external_image(url: str, *, client: httpx.Client | None = None) -> tuple[bytes, str]:
    """Fetch an external image URL and return (bytes, content_type).

    Used as a live proxy for images not yet downloaded.
    Raises httpx.HTTPError on failure.
    """
    own_client = client is None
    http_client = client
    if own_client:
        http_client = httpx.Client(
            timeout=_DOWNLOAD_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "BulgariaRealEstate/0.1 ImageProxy"},
        )
    if http_client is None:
        raise RuntimeError("HTTP client initialization failed")
    try:
        resp = http_client.get(url)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        return resp.content, ct
    finally:
        if own_client:
            http_client.close()
