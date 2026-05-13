#!/usr/bin/env python3
"""Live scraper for Bulgarian real estate tier-1 and tier-2 sources.

Discovers listing URLs from search pages, fetches detail pages, parses with
BeautifulSoup + JSON-LD, downloads photos, and stores everything under data/scraped/.

Usage:
    python scripts/live_scraper.py [--sources homes_bg,imot_bg,...] [--max-pages 5] [--max-listings 200] [--download-photos]
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

try:
    import httpx
except ModuleNotFoundError:  # parser-only tests can run without HTTP runtime deps
    httpx = None  # type: ignore[assignment]

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from bgrealestate.services.media import download_image, ensure_media_root  # noqa: E402

try:
    from bgrealestate.scraping.source_class import (  # noqa: E402
        detail_concurrency_for_source,
        source_bucket_for_key,
    )
except ImportError:

    def source_bucket_for_key(source_key: str, *, source_display_name: str) -> str:  # type: ignore[no-redef]
        return "other"

    def detail_concurrency_for_source(source_key: str, source_display_name: str) -> int:  # type: ignore[no-redef]
        return max(1, int(os.environ.get("SCRAPER_CONCURRENCY_OTHER", "1")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(REPO / "data" / "scraper.log", mode="a"),
    ],
)
logger = logging.getLogger("live_scraper")

DELAY = float(os.getenv("SCRAPER_DELAY", "1.2"))
TIMEOUT = float(os.getenv("SCRAPER_TIMEOUT", "20"))
SCRAPED_ROOT = REPO / "data" / "scraped"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "bg,en-US;q=0.9,en;q=0.8",
}

_JSON_LD_RE = re.compile(
    r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
_PRELOADED_STATE_RE = re.compile(
    r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;</script>",
    re.DOTALL,
)
_PHONE_RE = re.compile(r"(?:\+?359|0)[\d\s\-()]{6,}\d")
_IMAGE_URL_RE = re.compile(r"(?:(?:https?:)?//[^\s\"'<>]+?\.(?:jpg|jpeg|png|webp))(?:\?[^\s\"'<>]*)?", re.IGNORECASE)
ROOM_LABELS = {
    "едностаен": 1.0,
    "гарсониера": 1.0,
    "студио": 1.0,
    "двустаен": 2.0,
    "тристаен": 3.0,
    "четиристаен": 4.0,
    "многостаен": 5.0,
    "one-bedroom": 2.0,
    "two-bedroom": 3.0,
    "three-bedroom": 4.0,
    "one bedroom": 2.0,
    "two bedroom": 3.0,
    "three bedroom": 4.0,
    "one-room": 1.0,
    "two-room": 2.0,
    "three-room": 3.0,
    "four-room": 4.0,
}
PHOTO_LIMIT = int(os.getenv("SCRAPER_MAX_PHOTOS_PER_LISTING", "0"))
PAGE_ORDER_DEFAULT = str(os.getenv("SCRAPER_PAGE_ORDER", "newest_first")).strip().lower()


def _iter_pages(max_pages: int, page_order: str) -> list[int]:
    """Return page numbers to iterate for discovery.

    Many portals default to newest-first. For long backfills we sometimes need
    oldest-first *within the scanned window* (bottom-to-top) so older inventory
    isn't starved forever.
    """

    pages = list(range(1, max(1, int(max_pages)) + 1))
    if page_order.strip().lower() in {"oldest_first", "oldest_first_within_window", "bottom_to_top"}:
        pages.reverse()
    return pages


def make_client() -> httpx.Client:
    if httpx is None:
        raise RuntimeError("httpx is required for live fetching; install scrape runtime dependencies first")
    return httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=HEADERS,
                        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2))


def _decode_response(resp: httpx.Response) -> str:
    content_type = resp.headers.get("content-type", "").lower()
    charset = None
    if "charset=" in content_type:
        charset = content_type.split("charset=", 1)[1].split(";")[0].strip()

    sample = resp.content[:4096].decode("ascii", errors="ignore")
    meta_match = re.search(r"charset=([a-zA-Z0-9_\-]+)", sample, re.IGNORECASE)
    if meta_match:
        charset = meta_match.group(1)

    candidates = [charset, "utf-8", "windows-1251", "cp1251", "iso-8859-1"]
    for encoding in candidates:
        if not encoding:
            continue
        try:
            return resp.content.decode(encoding, errors="replace")
        except LookupError:
            continue
    return resp.text


def fetch_page(client: httpx.Client, url: str, *, retries: int = 2) -> str | None:
    for attempt in range(retries + 1):
        try:
            resp = client.get(url)
            if resp.status_code == 200:
                return _decode_response(resp)
            if resp.status_code in (403, 429, 503):
                wait = DELAY * (attempt + 2)
                logger.warning("Got %d for %s — waiting %.1fs", resp.status_code, url, wait)
                time.sleep(wait)
                continue
            logger.warning("HTTP %d for %s", resp.status_code, url)
            return None
        except httpx.HTTPError as e:
            logger.warning("HTTP error fetching %s: %s", url, e)
            if attempt < retries:
                time.sleep(DELAY * 2)
    return None


def fetch_json(client: httpx.Client, url: str) -> dict | list | None:
    try:
        resp = client.get(url, headers={**HEADERS, "Accept": "application/json"})
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.warning("JSON fetch error %s: %s", url, e)
    return None


def _text_or_empty(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_number(value: Any) -> float | None:
    if value is None:
        return None
    text = _text_or_empty(value)
    if not text:
        return None
    text = (
        text.replace("\xa0", " ")
        .replace("m²", "")
        .replace("кв. м", "")
        .replace("кв.м.", "")
        .replace("кв.м", "")
        .replace("sq. m", "")
        .replace("sq.m", "")
        .replace("sq m", "")
        .strip()
    )
    match = re.search(r"-?[\d\s.,]+", text)
    if not match:
        return None
    cleaned = match.group(0).strip().replace(" ", "")
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif cleaned.count(".") > 1:
        cleaned = cleaned.replace(".", "")
    elif cleaned.count(",") > 1:
        cleaned = cleaned.replace(",", "")
    elif "." in cleaned:
        left, right = cleaned.split(".", 1)
        if right.isdigit() and len(right) == 3 and len(left) >= 1:
            cleaned = left + right
    elif "," in cleaned:
        left, right = cleaned.split(",", 1)
        if right.isdigit() and len(right) == 3 and len(left) >= 1:
            cleaned = left + right
        else:
            cleaned = left + "." + right
    try:
        return float(cleaned)
    except ValueError:
        return None


def _load_json_ld_blocks(soup: BeautifulSoup) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        payload = script.get_text(strip=True)
        if not payload:
            continue
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            blocks.append(parsed)
        elif isinstance(parsed, list):
            blocks.extend(item for item in parsed if isinstance(item, dict))
    return blocks


def _normalize_image_url(url: str) -> str:
    return f"https:{url}" if url.startswith("//") else url


def _unique_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _absolute_image_url(url: str, base_url: str) -> str:
    if not url:
        return ""
    return _normalize_image_url(urljoin(base_url, url.strip()))


def _image_urls_from_selector(soup: BeautifulSoup, selector: str, base_url: str) -> list[str]:
    urls: list[str] = []
    for img in soup.select(selector):
        for attr in ("src", "data-src", "data-lazy"):
            raw = _text_or_empty(img.get(attr))
            if raw:
                urls.append(_absolute_image_url(raw, base_url))
        srcset = _text_or_empty(img.get("srcset"))
        if srcset:
            first = srcset.split(",", 1)[0].strip().split(" ", 1)[0]
            if first:
                urls.append(_absolute_image_url(first, base_url))
    return _unique_preserve([url for url in urls if url.startswith("http")])


def _anchor_urls_from_selector(soup: BeautifulSoup, selector: str, base_url: str) -> list[str]:
    urls: list[str] = []
    for node in soup.select(selector):
        for attr in ("href", "data-src", "data-href", "src"):
            raw = _text_or_empty(node.get(attr))
            if raw:
                urls.append(_absolute_image_url(raw, base_url))
    return _unique_preserve([url for url in urls if url.startswith("http")])


def _clean_description(value: Any) -> str:
    text = unescape(_text_or_empty(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _best_description(*candidates: Any) -> str:
    cleaned = [_clean_description(candidate) for candidate in candidates if _clean_description(candidate)]
    if not cleaned:
        return ""
    return max(cleaned, key=len)[:6000]


def _extract_labeled_area_value(text: str, labels: tuple[str, ...]) -> float | None:
    label_re = "|".join(re.escape(label) for label in labels)
    for match in re.finditer(
        rf"(?:{label_re})\s*(?:[:=\-–]|</?\w+[^>]*>|\s)\s*(\d[\d\s.,]*)\s*(?:sq\.?\s*m|sq m|кв\.?\s*м|m²|м²)",
        text,
        re.IGNORECASE,
    ):
        value = _parse_number(match.group(1))
        if value is not None and value > 0:
            return value
    return None


def _extract_area_from_title(text: str) -> float | None:
    for match in re.finditer(r"(\d+(?:[.,]\d+)?)\s*(?:sq\.?\s*m|sq m|кв\.?\s*м|m²|м²)", text, re.IGNORECASE):
        value = _parse_number(match.group(1))
        if value is not None and value >= 2:
            return value
    return None


def _coordinates_in_bulgaria(latitude: Any, longitude: Any) -> bool:
    lat = _parse_number(latitude)
    lon = _parse_number(longitude)
    if lat is None or lon is None:
        return False
    lat_f = float(lat)
    lon_f = float(lon)
    if not (41.0 <= lat_f <= 44.5 and 22.0 <= lon_f <= 29.5):
        return False
    # Rough Bulgaria boundary. A bbox admits Romania/Turkey/Greece border
    # spillover; this polygon is intentionally conservative for scraper QA.
    polygon = [
        (22.35, 44.22),
        (22.90, 44.05),
        (23.80, 44.18),
        (24.80, 43.95),
        (25.30, 43.70),
        (26.05, 43.98),
        (27.30, 44.15),
        (28.60, 43.75),
        (28.60, 43.25),
        (28.20, 42.00),
        (27.50, 41.90),
        (26.30, 41.75),
        (25.25, 41.25),
        (24.00, 41.35),
        (22.90, 41.25),
        (22.35, 41.60),
    ]
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        intersects = ((yi > lat_f) != (yj > lat_f)) and (
            lon_f < (xj - xi) * (lat_f - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def _param_rows_by_label(soup: BeautifulSoup, row_selector: str, label_selector: str, value_selector: str) -> dict[str, str]:
    params: dict[str, str] = {}
    for row in soup.select(row_selector):
        label_el = row.select_one(label_selector)
        value_els = row.select(value_selector)
        if not label_el or not value_els:
            continue
        label = unescape(label_el.get_text(" ", strip=True)).strip(" :")
        value_el = value_els[-1]
        value = unescape(value_el.get_text(" ", strip=True)).strip()
        if label and value:
            params[label] = value
    return params


def _extract_phone_numbers(text: str) -> list[str]:
    return _unique_preserve([match.strip() for match in _PHONE_RE.findall(text)])


def _extract_area_values(text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"(\d[\d\s.,]*)\s*(?:sq\.?\s*m|sq m|кв\.?\s*м|кв\.?\s*м\.|m²|м²)", text, re.IGNORECASE):
        value = _parse_number(match.group(1))
        if value is not None and value > 0:
            values.append(value)
    return values


def _extract_image_urls_from_text(text: str, *, allow_domains: tuple[str, ...] = ()) -> list[str]:
    urls: list[str] = []
    for raw in _IMAGE_URL_RE.findall(text):
        url = _normalize_image_url(raw)
        lowered = url.lower()
        if allow_domains and not any(domain in lowered for domain in allow_domains):
            continue
        if any(skip in lowered for skip in ("logo", "icon", "sprite", "avatar", "flag_", "langs/", "banner", "pixel")):
            continue
        urls.append(url)
    return _unique_preserve(urls)


def _extract_js_single_quoted_value(text: str, key: str) -> str:
    patterns = [
        rf"{re.escape(key)}\s*:\s*'([^']*)'",
        rf'"{re.escape(key)}"\s*:\s*"([^"]*)"',
        rf"{re.escape(key)}\s*:\s*\"([^\"]*)\"",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return unescape(match.group(1)).strip()
    return ""


def _parse_title_city_district(title: str) -> tuple[str, str]:
    def _clean_district(value: str | None) -> str:
        district = _text_or_empty(value).strip()
        # Common Bulgarian prefixes in titles, e.g. "кв. Надежда", "м. Евксиноград".
        district = re.sub(r"^(?:кв|м)\.?\s*", "", district, flags=re.IGNORECASE).strip()
        return district

    raw = title.strip()
    match = re.search(r"гр\.\s*([^,|]+)(?:,\s*([^|]+))?", raw, re.IGNORECASE)
    if match:
        return match.group(1).strip(), _clean_district(match.group(2))
    match = re.search(r"гр\.\s*([A-ZА-Я][^\s|•]+)\s+([^|•]+)", raw, re.IGNORECASE)
    if match:
        return match.group(1).strip(), _clean_district(match.group(2))
    match = re.search(r"\bв\s+([A-ZА-Я][^,|]+?)(?:,\s*([^|]+))?(?:\s*(?:-|$))", raw)
    if match:
        return match.group(1).strip(), _clean_district(match.group(2))
    match = re.search(r"\bв\s+([A-ZА-Я][A-Za-zА-Яа-я\- ]+?)\s+\d", raw)
    if match:
        return match.group(1).strip(), ""
    return "", ""


def _extract_address_city_district_from_json_ld(blocks: list[dict[str, Any]]) -> tuple[str, str, str]:
    city = district = address_text = ""
    for block in blocks:
        address = block.get("address")
        if isinstance(address, dict):
            if not city:
                city = _text_or_empty(address.get("addressLocality"))
            if not address_text:
                address_text = _text_or_empty(address.get("streetAddress"))
        name = _text_or_empty(block.get("name"))
        if name and (not city or not district):
            title_city, title_district = _parse_title_city_district(name)
            city = city or title_city
            district = district or title_district
    return city, district, address_text


def _merge_source_result(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if key == "image_urls":
            base[key] = _unique_preserve([*_text_list(base.get(key)), *_text_list(value)])
        elif key == "phones":
            base[key] = _unique_preserve([*_text_list(base.get(key)), *_text_list(value)])
        elif key == "amenities":
            base[key] = _unique_preserve([*_text_list(base.get(key)), *_text_list(value)])
        elif key == "source_attributes":
            merged = dict(base.get("source_attributes") or {})
            merged.update(value or {})
            base[key] = merged
        elif value not in (None, "", [], {}):
            base[key] = value
    return base


def _apply_bucket_context(parsed: dict[str, Any], bucket_label: str, source_url: str = "") -> None:
    """Use the discovery route as a conservative section hint, not as detail proof.

    Detail pages remain primary, but route context prevents obvious drift such as
    rent pages being reclassified as sale because the body contains generic sales
    marketing text, or land routes being downgraded to unknown/apartment.
    """
    label = f"{bucket_label} {source_url}".lower()
    parsed["source_section_id"] = bucket_label or parsed.get("source_section_id") or "default"
    if any(token in label for token in ("rent", "rental", "naem", "naemi", "pod-naem", "под-наем")):
        parsed["listing_intent"] = "long_term_rent"
    elif any(token in label for token in ("sale", "sales", "prodazh", "prodaj", "properties_for_sale", "продаж")):
        parsed["listing_intent"] = "sale"

    if any(token in label for token in ("land", "parcel", "partsel", "parzel", "teren", "зем", "парцел")):
        parsed["property_category"] = "land"
    elif any(token in label for token in ("office", "ofisi", "офис")):
        parsed["property_category"] = "office"
    elif any(token in label for token in ("shop", "magazin", "магазин")):
        parsed["property_category"] = "shop"
    elif any(token in label for token in ("house", "houses", "kushti", "kashti", "vili", "villa", "къщ", "вил")):
        parsed["property_category"] = "house"
    elif any(token in label for token in ("apartment", "apartments", "apartamenti", "апартамент")):
        parsed["property_category"] = "apartment"


def _apply_immediate_publication_status(parsed: dict[str, Any]) -> None:
    """Persist source-publication semantics early so OpenClaw/importers can gate safely."""
    if parsed.get("suspected_multi_unit_publication"):
        parsed["source_publication_type"] = "multi_unit_or_development"
        parsed["scrape_status"] = "GROUPED_PUBLICATION"
        parsed["scrape_acceptance_status"] = "not_single_entity"
        parsed["single_entity_candidate"] = False
    else:
        parsed.setdefault("source_publication_type", "single_unit_candidate")
        parsed.setdefault("scrape_status", "PENDING_QA")
        parsed.setdefault("scrape_acceptance_status", "pending_quality_gate")
        parsed.setdefault("single_entity_candidate", True)


def _text_list(value: Any) -> list[str]:
    if not value:
        return []
    return [str(item) for item in value if item]


def _parse_address_bg(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    blocks = _load_json_ld_blocks(soup)
    city, district, address_text = _extract_address_city_district_from_json_ld(blocks)
    description = result.get("description") or ""
    description_candidates = [description]
    for block in blocks:
        block_description = _text_or_empty(block.get("description"))
        if block_description:
            description_candidates.append(block_description)
            if len(block_description) > len(description):
                description = block_description
    area_values = []
    for candidate in description_candidates:
        area_values.extend(_extract_area_values(candidate))
    if not area_values:
        area_values = _extract_area_values(html)
    exact_area_match = re.search(r"приблизително\s*(\d[\d\s.,]*)\s*кв", html, re.IGNORECASE)
    exact_area = _parse_number(exact_area_match.group(1)) if exact_area_match else None
    breadcrumb_text = " ".join(
        li.get_text(" ", strip=True)
        for li in soup.select("[itemtype*='BreadcrumbList'] li, .breadcrumbs li")
    )
    phone_urls: list[str] = []
    for link in soup.select("a[href^='tel:']"):
        href = str(link.get("href") or "")
        phone_urls.append(href.replace("tel:", ""))
    gallery_candidates = [
        *_anchor_urls_from_selector(
            soup,
            "a.image[href*='/storage/uploads/offers/'], a[href*='/storage/uploads/offers/'][href*='/1000x']",
            url,
        ),
        *_image_urls_from_selector(
            soup,
            "img[src*='/storage/uploads/offers/'], img[data-src*='/storage/uploads/offers/']",
            url,
        ),
        *_extract_image_urls_from_text(html, allow_domains=("address.bg/storage/uploads/offers/",)),
    ]
    gallery_candidates = [
        image_url
        for image_url in _unique_preserve(gallery_candidates)
        if "/storage/uploads/offers/" in image_url and not re.search(r"/(?:100x|150x|200x|250x|300x|370x200)/", image_url)
    ]
    for preferred_size in ("/1000x666/", "/764x510/"):
        sized = [image_url for image_url in gallery_candidates if preferred_size in image_url and not image_url.lower().endswith(".webp")]
        if sized:
            gallery_candidates = sized
            break
    gallery_urls = gallery_candidates
    patch = {
        "price": result.get("price"),
        "currency": result.get("currency") or "EUR",
        "city": city,
        "district": district,
        "address_text": address_text or ", ".join(part for part in [city, district] if part),
        "phones": _unique_preserve([*_extract_phone_numbers(html), *_text_list(phone_urls)]),
        "area_sqm": exact_area or (max(area_values) if area_values else None),
        "image_urls": gallery_urls or result.get("image_urls", []),
        "source_attributes": {
            "breadcrumb_text": breadcrumb_text,
        },
    }
    for block in blocks:
        offers = block.get("offers")
        if isinstance(offers, dict) and patch["price"] is None:
            patch["price"] = _parse_number(offers.get("price"))
            patch["currency"] = _text_or_empty(offers.get("priceCurrency")) or patch["currency"]
        if not patch["city"] or not patch["district"]:
            name = _text_or_empty(block.get("name"))
            title_city, title_district = _parse_title_city_district(name)
            patch["city"] = patch["city"] or title_city
            patch["district"] = patch["district"] or title_district
    if patch["price"] is None:
        price_match = re.search(r'"price"\s*:\s*([\d.,]+)', html)
        if price_match:
            patch["price"] = _parse_number(price_match.group(1))
    if not patch["city"]:
        title_city, title_district = _parse_title_city_district(result.get("title", ""))
        patch["city"] = title_city
        patch["district"] = patch["district"] or title_district
    if not patch["city"]:
        match = re.search(r"Парцел/Терен,\s*продажба,\s*([^,]+),\s*кв\.\s*([^\"<]+)", html)
        if match:
            patch["city"] = match.group(1).strip()
            patch["district"] = match.group(2).strip()
    if patch["city"] and not patch["address_text"]:
        patch["address_text"] = ", ".join(str(part) for part in [patch["city"], patch["district"]] if part)
    if patch["district"]:
        district_text = _text_or_empty(patch.get("district"))
        patch["district"] = re.sub(r"\s*-\s*код на имота.*$", "", district_text).strip()
        patch["address_text"] = ", ".join(str(part) for part in [patch["city"], patch["district"]] if part)
    merged = _merge_source_result(result, patch)
    if gallery_urls:
        merged["image_urls"] = gallery_urls
    return merged


def _parse_bulgarianproperties(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    blocks = _load_json_ld_blocks(soup)
    product = next((block for block in blocks if block.get("@type") == "Product"), {})
    h1 = soup.find("h1")
    title = _text_or_empty(h1.get_text(" ", strip=True) if h1 else "")
    data_layer_match = re.search(r"dataLayer\.push\((\{.*?listing_id:.*?\})\);", html, re.DOTALL)
    data_layer = data_layer_match.group(1) if data_layer_match else html
    property_type = _extract_js_single_quoted_value(data_layer, "property_type") or _extract_js_single_quoted_value(html, "property_type")
    town = _extract_js_single_quoted_value(data_layer, "town") or _extract_js_single_quoted_value(html, "content_city")
    region = _extract_js_single_quoted_value(data_layer, "region") or _extract_js_single_quoted_value(html, "content_region")
    image_urls = _extract_image_urls_from_text(
        html,
        allow_domains=(
            "static.bulgarianproperties.com/property-images/",
            "static.bulgarianproperties.com/floor-images/",
            "static.bulgarianproperties.com/aerial-images/",
        ),
    )
    # Keep only the current listing gallery. The page also embeds recommendation
    # cards from other properties under `/medium1/`, which should not count as
    # this listing's own media proof.
    image_urls = [image_url for image_url in image_urls if "/big/" in image_url]
    area_values = _extract_area_values(html)
    meta_description = ""
    for selector in (
        {"property": "og:description"},
        {"name": "description"},
    ):
        meta = soup.find("meta", attrs=selector)
        if meta and meta.get("content"):
            meta_description = _best_description(meta_description, meta.get("content"))
    body_description = ""
    for selector in (
        ".property-description",
        ".description",
        ".component-single-property-description",
        ".component-single-property-general-information",
        "#property-description",
    ):
        node = soup.select_one(selector)
        if node:
            body_description = _best_description(body_description, node.get_text(" ", strip=True))
    description = _best_description(
        result.get("description"),
        product.get("description") if isinstance(product, dict) else "",
        meta_description,
        body_description,
    )
    patch = {
        "title": title or _text_or_empty(product.get("name")) or result.get("title"),
        "description": description or result.get("description"),
        "price": _parse_number(_extract_js_single_quoted_value(data_layer, "price")) or result.get("price"),
        "currency": result.get("currency") or _text_or_empty(((product.get("offers") or {}).get("priceCurrency"))) or "EUR",
        "city": town,
        "region": region,
        "address_text": town,
        "property_category": _slug_to_category(property_type or title or result.get("title", "")),
        "listing_intent": "sale" if "sale" in (_extract_js_single_quoted_value(data_layer, "type").lower()) else result.get("listing_intent"),
        "area_sqm": max(area_values) if area_values else result.get("area_sqm"),
        "rooms": _rooms_from_text(property_type or title or result.get("title", "")),
        "phones": _extract_phone_numbers(html),
        "image_urls": image_urls or result.get("image_urls", []),
        "source_attributes": {
            "town": town,
            "region": region,
            "property_type": property_type,
            "refno": _extract_js_single_quoted_value(html, "content_refno"),
        },
    }
    return _merge_source_result(result, patch)


def _parse_property_family(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any], *, source_name: str) -> dict[str, Any]:
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else result.get("title", "")
    data_layer_match = re.search(r"dataLayer\.push\((\{.*?listing_id:.*?\})\);", html, re.DOTALL)
    data_layer = data_layer_match.group(1) if data_layer_match else html
    domain_map = {
        "LUXIMMO": ("static.luximmo.org/property-images/",),
        "property.bg": ("static4.superimoti.bg/property-images/",),
        "SUPRIMMO": ("static4.superimoti.bg/property-images/",),
    }
    image_urls = _extract_image_urls_from_text(html, allow_domains=domain_map.get(source_name, ()))
    area_values = _extract_area_values(html)
    preferred_area = None
    for key in ("content_area", "property_area", "built_area", "living_area", "area"):
        preferred_area = _parse_number(_extract_js_single_quoted_value(data_layer, key))
        if preferred_area is not None and preferred_area > 0:
            break
    if preferred_area is None:
        preferred_area = _extract_labeled_area_value(
            html,
            (
                "РЗП",
                "ЗП",
                "Обща площ",
                "Жилищна площ",
                "Площ",
                "Built-up area",
                "Total built-up area",
                "Area",
            ),
        )
    if preferred_area is None:
        preferred_area = _extract_area_from_title(title)
    if preferred_area is None:
        sane_area_values = [value for value in area_values if 2 <= value <= 5000]
        preferred_area = sane_area_values[0] if sane_area_values else (area_values[0] if area_values else None)
    raw_max_area = max(area_values) if area_values else None
    patch = {
        "title": title or result.get("title"),
        "price": result.get("price"),
        "currency": result.get("currency") or "EUR",
        "city": _extract_js_single_quoted_value(data_layer, "town"),
        "district": _extract_js_single_quoted_value(data_layer, "quart") or _extract_js_single_quoted_value(data_layer, "neighborhood_fb_estate"),
        "region": _extract_js_single_quoted_value(data_layer, "region"),
        "property_category": _slug_to_category(_extract_js_single_quoted_value(data_layer, "property_type") or title),
        "listing_intent": "sale" if any(word in _extract_js_single_quoted_value(data_layer, "type").lower() for word in ("sale", "sales", "продава")) else result.get("listing_intent"),
        "area_sqm": preferred_area or result.get("area_sqm"),
        "rooms": _rooms_from_text(title or _extract_js_single_quoted_value(data_layer, "property_type")),
        "address_text": ", ".join(part for part in [_extract_js_single_quoted_value(data_layer, "town"), _extract_js_single_quoted_value(data_layer, "quart") or _extract_js_single_quoted_value(data_layer, "neighborhood_fb_estate")] if part),
        "phones": _extract_phone_numbers(html),
        "image_urls": image_urls or result.get("image_urls", []),
        "source_attributes": {
            "town": _extract_js_single_quoted_value(data_layer, "town"),
            "district_raw": _extract_js_single_quoted_value(data_layer, "quart") or _extract_js_single_quoted_value(data_layer, "neighborhood_fb_estate"),
            "listing_id": _extract_js_single_quoted_value(data_layer, "listing_id"),
            "raw_max_area_sqm": raw_max_area,
        },
    }
    price_val = patch.get("price")
    intent_val = str(patch.get("listing_intent") or "")
    if price_val is None or (isinstance(price_val, (int, float)) and price_val < 1000 and intent_val == "sale"):
        patch["price"] = _parse_number(_extract_js_single_quoted_value(data_layer, "price")) or patch["price"]
    return _merge_source_result(result, patch)


def _parse_olx_bg(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    title = result.get("title") or _text_or_empty((soup.title.get_text(" ", strip=True) if soup.title else ""))
    city, district = _parse_title_city_district(title)
    if not city:
        match = re.search(r"гр\.\s*([A-ZА-Я][^\s•]+)\s+([^•]+)", _text_or_empty(soup.title.get_text(" ", strip=True) if soup.title else title), re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            district = match.group(2).replace("• OLX.bg", "").strip()
    if not city and "гр." in title:
        city = re.sub(r".*гр\.\s*", "", title).split()[0]
    description = result.get("description") or ""
    area_values = _extract_area_values(description or html)
    patch = {
        "city": city,
        "district": district,
        "address_text": ", ".join(part for part in [city, district] if part),
        "area_sqm": area_values[0] if area_values else result.get("area_sqm"),
        "rooms": _rooms_from_text(title + " " + description),
        "phones": _extract_phone_numbers(html),
    }
    return _merge_source_result(result, patch)


def _parse_bazar_bg(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else result.get("title", "")
    ad_match = re.search(r"var ad = (\{.*?\});", html, re.DOTALL)
    ad_blob = ad_match.group(1) if ad_match else html
    city, district = _parse_title_city_district(title)
    area_values = _extract_area_values(html)
    image_urls = _extract_image_urls_from_text(ad_blob, allow_domains=("imotstatic",))
    patch = {
        "title": title or result.get("title"),
        "city": city,
        "district": re.sub(r"\s*→\s*Обява.*$", "", district).strip() if district else district,
        "address_text": ", ".join(part for part in [city, re.sub(r"\s*→\s*Обява.*$", "", district).strip() if district else district] if part),
        "area_sqm": max(area_values) if area_values else result.get("area_sqm"),
        "rooms": _rooms_from_text(title),
        "phones": _extract_phone_numbers(html),
        "image_urls": image_urls or result.get("image_urls", []),
    }
    return _merge_source_result(result, patch)


def _decode_escaped_json_fragment(fragment: str) -> dict[str, Any] | None:
    try:
        decoded = fragment.encode("utf-8").decode("unicode_escape")
        return json.loads("{" + decoded + "}")
    except Exception:
        return None


def _parse_yavlena(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    start = html.find("propertyData\\\":{")
    end = html.find("},\\\"messageData\\\"", start)
    payload: dict[str, Any] | None = None
    if start != -1 and end != -1:
        fragment = html[start + len("propertyData\\\":{"):end + 1]
        payload = _decode_escaped_json_fragment(fragment)
    title = _text_or_empty(soup.title.get_text(" ", strip=True) if soup.title else result.get("title"))
    city, district = _parse_title_city_district(title)
    if district.strip().lower() in {"м", "кв"}:
        district = ""
    if not city:
        title_match = re.search(r"в\s+([A-ZА-Я][A-Za-zА-Яа-я\- ]+?)\s+\d+\s*кв", title)
        if title_match:
            city = title_match.group(1).strip()
    if not district:
        meta_desc = ""
        meta_el = soup.find("meta", attrs={"name": "description"})
        if meta_el:
            meta_desc = str(meta_el.get("content") or "")
        if meta_desc:
            district_match = re.search(r"в\s+София\s*[-–]\s*([^,]+)", meta_desc)
            if district_match:
                district = district_match.group(1).strip()
                district = re.sub(r"\s+\d+$", "", district).strip()
    description = _text_or_empty((payload or {}).get("description")) or result.get("description")
    if not description:
        description_match = re.search(r'description\\":\\"(.*?)\\",\\"constructionType', html)
        if description_match:
            description = unescape(description_match.group(1).replace("\\r\\n", " "))
    area = _parse_number((payload or {}).get("area")) or (_extract_area_values(title)[0] if _extract_area_values(title) else None)
    images = [
        f"https://userimages.yavlena.com/{item['filePath']}"
        for item in ((payload or {}).get("photos") or [])
        if isinstance(item, dict) and item.get("isImage") and item.get("filePath")
    ]
    if not images:
        images = _extract_image_urls_from_text(html, allow_domains=("userimages.yavlena.com/",))
    if not district and description:
        district_match = re.search(r"кв\.\s*([A-Za-zА-Яа-я0-9 \-]+)", description)
        if district_match:
            district = district_match.group(1).strip()
    if payload is None:
        price_match = re.search(r'price\\":\\"([^\\"]+)', html)
        ad_phone_match = re.search(r'advertisementPhoneNumber\\":\\"([^\\"]+)', html)
        broker_phone_match = re.search(r'brokerPhone\\":\\"([^\\"]+)', html)
    else:
        price_match = ad_phone_match = broker_phone_match = None
    explicit_phones = _unique_preserve(
        [
            *_text_list(
                [
                    _text_or_empty((payload or {}).get("advertisementPhoneNumber")) or (ad_phone_match.group(1) if ad_phone_match else ""),
                    _text_or_empty((payload or {}).get("brokerPhone")) or (broker_phone_match.group(1) if broker_phone_match else ""),
                ]
            ),
        ]
    )
    patch = {
        "title": title,
        "description": description,
        "price": (_parse_number((payload or {}).get("price")) if (payload or {}).get("price") is not None else None),
        "currency": "EUR" if "€" in _text_or_empty((payload or {}).get("price")) else (result.get("currency") or "EUR"),
        "area_sqm": area,
        "rooms": _rooms_from_text(title),
        "city": city,
        "district": district,
        "address_text": ", ".join(part for part in [city, district] if part),
        "phones": explicit_phones or _extract_phone_numbers(html),
        "image_urls": images or result.get("image_urls", []),
        "source_attributes": {
            "broker_name": _text_or_empty((payload or {}).get("brokerDisplayName")),
            "broker_email": _text_or_empty((payload or {}).get("brokerEmail")),
            "inner_number": _text_or_empty((payload or {}).get("innerNumber")),
        },
    }
    if patch["price"] is None and price_match:
        patch["price"] = _parse_number(price_match.group(1))
    return _merge_source_result(result, patch)


def _parse_alo_bg(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    params = _param_rows_by_label(soup, ".ads-params-row", ".ads-param-title", ".ads-params-cell")
    title_tag = soup.find("title")
    title = _text_or_empty(title_tag.get_text(" ", strip=True) if title_tag else result.get("title"))
    canonical = soup.find("link", rel="canonical")
    canonical_url = _text_or_empty(canonical.get("href") if canonical else url)
    external_match = re.search(r"-(\d{5,})(?:[/?#].*)?$", canonical_url or url)
    external_id = external_match.group(1) if external_match else _text_or_empty(params.get("Обява №"))
    image_urls = [
        url for url in _image_urls_from_selector(soup, "img", "https://www.alo.bg/")
        if "/user_files/" in url and (not external_id or f"/{external_id}_" in url)
    ]
    if not image_urls:
        image_urls = [url for url in result.get("image_urls", []) if "/user_files/" in url]

    description = result.get("description") or ""
    desc_el = soup.select_one("#description_div, .ads-description, .description")
    if desc_el:
        description = desc_el.get_text(" ", strip=True)
    if description.lower().startswith("описание "):
        description = description.split(" ", 1)[1].strip()

    price_text = params.get("Цена") or ""
    area_text = params.get("Квадратура") or ""
    type_text = params.get("Вид на имота") or title
    floor_text = params.get("Номер на етажа") or params.get("Етаж") or ""
    location_text = params.get("Местоположение") or ""
    location_blob = " ".join([location_text, title, description, canonical_url])
    district = ""
    if location_text:
        district = location_text.split(",")[0].strip()
    if not district:
        district_match = re.search(r"кв\.\s*([A-Za-zА-Яа-я0-9 .'-]+)", location_blob)
        if district_match:
            district = district_match.group(1).split(",")[0].split("-")[0].strip()
    city = "Варна" if "варна" in location_blob.lower() else result.get("city", "")

    patch = {
        "listing_url": canonical_url or url,
        "external_id": external_id or result.get("external_id"),
        "title": title or result.get("title"),
        "description": description,
        "price": _parse_number(price_text) if price_text else result.get("price"),
        "currency": "EUR" if "€" in price_text else ("BGN" if "лв" in price_text.lower() else result.get("currency") or "EUR"),
        "area_sqm": _parse_number(area_text) or result.get("area_sqm"),
        "rooms": _rooms_from_text(type_text) or _rooms_from_text(title),
        "floor": _parse_floor_value(floor_text) if floor_text else result.get("floor"),
        "city": city,
        "district": district or result.get("district", ""),
        "address_text": ", ".join(part for part in [city, district] if part),
        "listing_intent": "long_term_rent" if "imoti-naemi" in canonical_url else "sale",
        "property_category": _slug_to_category(type_text),
        "image_urls": image_urls or result.get("image_urls", []),
        "phones": _extract_phone_numbers(html),
        "source_attributes": params,
    }
    return _merge_source_result(result, patch)


def _parse_domaza(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    h1 = soup.find("h1")
    title = _text_or_empty(h1.get_text(" ", strip=True) if h1 else result.get("title"))
    canonical = soup.find("meta", property="og:url")
    canonical_url = _text_or_empty(canonical.get("content") if canonical else url)
    external_match = re.search(r"-16-(\d+)-p", canonical_url or url)
    external_id = external_match.group(1) if external_match else hashlib.sha1((canonical_url or url).encode()).hexdigest()[:12]
    content = soup.select_one(".property_content")
    content_text = content.get_text(" ", strip=True) if content else soup.get_text(" ", strip=True)
    description_el = soup.select_one("#property_description")
    description = ""
    if description_el:
        description = re.sub(r"^Описание\s*", "", description_el.get_text(" ", strip=True)).strip()
    feature_el = soup.select_one("#property_features")
    feature_text = feature_el.get_text(" ", strip=True) if feature_el else ""
    image_urls = [
        image_url for image_url in _image_urls_from_selector(soup, "#property_gallery img, .property_image_thumb img", "https://www.domaza.bg/")
        if "cdn.domaza.biz/upload/properties" in image_url and f"/{external_id}/" in image_url
    ]

    city = "Варна" if "варна" in title.lower() or "варна" in content_text.lower() else result.get("city", "")
    district = ""
    title_parts = [part.strip() for part in title.split(",") if part.strip()]
    if title_parts:
        for part in title_parts:
            if part not in {"Апартамент", "Къща", "Варна", "България"} and "гр." not in part:
                district = part
                break
    params: dict[str, str] = {}
    for label in ("Цена", "Обща площ", "Чиста площ", "Стаи"):
        match = re.search(rf"{label}\s+([^А-Яа-я]+(?:€|m\s*2|m2)?|\d+(?:[.,]\d+)?)", content_text)
        if match:
            params[label] = match.group(1).strip()
    if feature_text:
        params["Характеристики"] = feature_text

    price_match = re.search(r"(\d[\d\s.,]*)\s*€", content_text)
    area_match = re.search(r"Обща площ\s+(\d[\d\s.,]*)\s*m\s*2", content_text)
    rooms_match = re.search(r"Стаи\s+(\d+(?:[.,]\d+)?)", content_text)
    patch = {
        "listing_url": canonical_url or url,
        "external_id": external_id,
        "title": title or result.get("title"),
        "description": description or result.get("description"),
        "price": _parse_number(price_match.group(1)) if price_match else result.get("price"),
        "currency": "EUR",
        "area_sqm": _parse_number(area_match.group(1)) if area_match else result.get("area_sqm"),
        "rooms": _parse_number(rooms_match.group(1)) if rooms_match else result.get("rooms"),
        "city": city,
        "district": district,
        "address_text": ", ".join(part for part in [city, district] if part),
        "listing_intent": "long_term_rent" if " наем " in content_text.lower() else "sale",
        "property_category": _slug_to_category(title + " " + content_text),
        "image_urls": image_urls or result.get("image_urls", []),
        "phones": _extract_phone_numbers(content_text),
        "amenities": [item.strip() for item in feature_text.split() if item.strip()][:80],
        "source_attributes": params,
    }
    return _merge_source_result(result, patch)


def _parse_home2u(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    h1 = soup.find("h1")
    title = _text_or_empty(h1.get_text(" ", strip=True) if h1 else result.get("title"))
    canonical = soup.find("link", rel="canonical")
    canonical_url = _text_or_empty(canonical.get("href") if canonical else url)
    external_id = hashlib.sha1((canonical_url or url).encode()).hexdigest()[:12]
    info = soup.select_one(".section-building-info-secondary")
    info_text = info.get_text(" ", strip=True) if info else soup.get_text(" ", strip=True)
    description_el = soup.select_one(".section__content")
    description = ""
    if description_el:
        description = re.sub(r"^За имота\s*", "", description_el.get_text(" ", strip=True)).strip()
    description_status = "captured" if description else "absent_on_detail_page"
    gallery_urls = [
        image_url for image_url in _image_urls_from_selector(soup, ".section-building-gallery img, .list-gallery img", "https://home2u.bg/")
        if "/wp-content/uploads/" in image_url and not image_url.endswith(".svg")
    ]
    price_el = soup.select_one(".section__head-price")
    price_text = price_el.get_text(" ", strip=True) if price_el else info_text
    location_match = re.search(r"Местоположение\s*:?\s*([^:]+?)\s+Площ", info_text)
    location_text = location_match.group(1).strip() if location_match else ""
    city, district = _split_bg_location(location_text) if location_text else ("", "")
    if not city and "варна" in info_text.lower():
        city = "Варна"
    area_match = re.search(r"Площ(?:\s+в\s+квадратни\s+метри)?\s*:?\s*(\d[\d\s.,]*)\s*m2", info_text, re.IGNORECASE)
    floor_match = re.search(r"Етаж\s*:?\s*([A-Za-zА-Яа-я0-9 .-]+)", info_text)
    source_attrs = {
        "location": location_text,
        "floor_text": floor_match.group(1).strip() if floor_match else "",
        "description_status": description_status,
    }
    patch = {
        "listing_url": canonical_url or url,
        "external_id": external_id,
        "title": title or result.get("title"),
        "description": description or result.get("description"),
        "price": _parse_number(price_text),
        "currency": "EUR" if "€" in price_text else result.get("currency", "EUR"),
        "area_sqm": _parse_number(area_match.group(1)) if area_match else result.get("area_sqm"),
        "rooms": _rooms_from_text(title + " " + description),
        "floor": _parse_floor_value(floor_match.group(1)) if floor_match else result.get("floor"),
        "city": city,
        "district": district,
        "address_text": location_text,
        "listing_intent": "long_term_rent" if "pod-naem" in canonical_url or "под наем" in (title + " " + description).lower() else "sale",
        "property_category": _slug_to_category(title + " " + canonical_url + " " + description),
        "image_urls": gallery_urls or result.get("image_urls", []),
        "phones": _extract_phone_numbers(info_text),
        "source_attributes": source_attrs,
    }
    return _merge_source_result(result, patch)


def _slug_to_intent(url: str) -> str:
    lowered = url.lower()
    if "naem" in lowered or "rent" in lowered:
        return "long_term_rent"
    return "sale"


def _slug_to_category(text: str) -> str:
    lowered = text.lower()
    for kw, cat in [
        ("apart", "apartment"),
        ("апартамент", "apartment"),
        ("studio", "apartment"),
        ("студио", "apartment"),
        ("mezonet", "apartment"),
        ("мезонет", "apartment"),
        ("house", "house"),
        ("къща", "house"),
        ("villa", "house"),
        ("вила", "house"),
        ("parcel", "land"),
        ("парцел", "land"),
        ("land", "land"),
        ("земя", "land"),
        ("office", "office"),
        ("офис", "office"),
        ("commercial", "office"),
        ("магазин", "office"),
    ]:
        if kw in lowered:
            return cat
    return "unknown"


def _rooms_from_text(text: str) -> float | None:
    lowered = text.lower()
    for label, value in ROOM_LABELS.items():
        if label in lowered:
            return value
    match = re.search(r"(\d+(?:\.\d+)?)\s*[- ]\s*bedroom", lowered)
    if match:
        try:
            return float(match.group(1)) + 1.0
        except ValueError:
            return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*стаен", lowered)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:стаен|rooms?)", lowered)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _parse_floor_value(value: str) -> float | None:
    lowered = value.lower()
    if "партер" in lowered or "ground" in lowered:
        return 0.0
    match = re.search(r"(\d+)", value)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _split_bg_location(raw: str) -> tuple[str, str]:
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    if not parts:
        return "", ""
    if len(parts) == 2 and parts[0].lower().startswith(("град ", "гр. ", "област ")):
        city = parts[0].replace("град ", "").replace("гр. ", "").replace("област ", "").strip()
        district = parts[1]
        return city, district
    city = parts[-1]
    district = ", ".join(parts[:-1])
    if city.lower() in {"софия - град", "софия"} and district:
        return "София", district
    return city, district


def _normalize_phone_list(text: str) -> list[str]:
    phones: list[str] = []
    for part in re.split(r"[\r\n,;/]+", text):
        cleaned = part.strip()
        if cleaned and cleaned not in phones:
            phones.append(cleaned)
    return phones


def _homes_photo_url(photo: dict[str, Any]) -> str:
    path = _text_or_empty(photo.get("path"))
    name = _text_or_empty(photo.get("name"))
    if not path or not name:
        return ""
    if not path.endswith("/"):
        path += "/"
    return f"https://g1.homes.bg/{path}{name}o.jpg"


def _parse_homes_preloaded_state(html: str) -> dict[str, Any] | None:
    match = _PRELOADED_STATE_RE.search(html)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def parse_homes_detail(html: str, url: str) -> dict[str, Any] | None:
    state = _parse_homes_preloaded_state(html)
    if not state:
        return parse_listing_html(html, url, "Homes.bg")

    offer = (((state.get("data") or {}).get("offer")) or {})
    if not offer:
        return parse_listing_html(html, url, "Homes.bg")

    address = offer.get("address") or {}
    address_city = _text_or_empty(address.get("city"))
    city, district = _split_bg_location(address_city)
    coordinates = address.get("coordinates") or []
    latitude = longitude = None
    if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
        latitude = _parse_number(coordinates[0])
        longitude = _parse_number(coordinates[1])
        if latitude is not None and longitude is not None and not _coordinates_in_bulgaria(latitude, longitude):
            if _coordinates_in_bulgaria(longitude, latitude):
                latitude, longitude = longitude, latitude
            else:
                latitude = longitude = None

    attrs = offer.get("attributes") or []
    attr_map: dict[str, str] = {}
    description = ""
    floor = None
    for attr in attrs:
        label = _text_or_empty(attr.get("label"))
        value = _text_or_empty(attr.get("value"))
        if label:
            attr_map[label] = value
        if attr.get("key") == "notes" and value:
            description = value.strip("\" ")
        if attr.get("key") == "floor" and value:
            floor = _parse_floor_value(value)

    photo_urls: list[str] = []
    for photo in offer.get("photos") or []:
        if isinstance(photo, dict):
            photo_url = _homes_photo_url(photo)
            if photo_url and photo_url not in photo_urls:
                photo_urls.append(photo_url)

    phones: list[str] = []
    contacts = offer.get("contacts") or {}
    agency = contacts.get("agency") or {}
    agency_phone = ((agency.get("phone") or {}).get("number")) or ""
    phones.extend(_normalize_phone_list(agency_phone))

    title = _text_or_empty(offer.get("title"))
    property_category = _slug_to_category(url + " " + title)
    listing_intent = _slug_to_intent(url)
    rooms = _rooms_from_text(title)
    area_sqm = _extract_area_from_title(title)
    if area_sqm is None:
        for area_label in ("Квадратура", "Площ", "Area"):
            area_sqm = _parse_number(attr_map.get(area_label))
            if area_sqm is not None:
                break
    price_value = _parse_number((((offer.get("price") or {}).get("value")) or "").replace(",", ""))
    currency = _text_or_empty(((offer.get("price") or {}).get("currency"))) or "EUR"
    extras = [item.get("name") for item in offer.get("extras") or [] if isinstance(item, dict) and item.get("name")]
    full_address = " ".join(
        part for part in [
            address_city,
            _text_or_empty(address.get("address")),
            _text_or_empty(address.get("number")),
        ] if part
    ).strip()
    external_id = _text_or_empty(offer.get("id")) or hashlib.sha1(url.encode()).hexdigest()[:12]
    title_human = f"{title} - {address_city}".strip(" -")

    return {
        "source_name": "Homes.bg",
        "listing_url": url,
        "external_id": str(external_id),
        "reference_id": f"Homes.bg:{external_id}",
        "title": title_human or title or url,
        "description": description,
        "price": price_value,
        "currency": currency.upper(),
        "area_sqm": area_sqm,
        "rooms": rooms,
        "floor": floor,
        "city": city,
        "district": district,
        "address_text": full_address,
        "latitude": latitude,
        "longitude": longitude,
        "listing_intent": listing_intent,
        "property_category": property_category,
        "image_urls": photo_urls,
        "phones": phones,
        "amenities": extras,
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
        "listing_status": "active" if offer.get("status") == 1 else "inactive",
        "published_text": _text_or_empty(offer.get("published_at")),
        "agency_name": _text_or_empty(agency.get("name")),
        "agency_type": _text_or_empty(agency.get("type")),
        "agency_address": " ".join(
            part for part in [
                _text_or_empty(((agency.get("address") or {}).get("city"))),
                _text_or_empty(((agency.get("address") or {}).get("address"))),
            ] if part
        ).strip(),
        "source_attributes": attr_map,
        "photo_metadata": offer.get("photos") or [],
        "raw_offer_type": _text_or_empty(offer.get("type")),
        "view_count": offer.get("count_view"),
    }


def parse_imot_detail(html: str, url: str) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "lxml")
    result = parse_listing_html(html, url, "imot.bg") or {
        "source_name": "imot.bg",
        "listing_url": url,
        "external_id": hashlib.sha1(url.encode()).hexdigest()[:12],
        "reference_id": "",
        "title": "",
        "description": "",
        "price": None,
        "currency": "BGN",
        "area_sqm": None,
        "rooms": None,
        "floor": None,
        "city": "",
        "district": "",
        "address_text": "",
        "latitude": None,
        "longitude": None,
        "listing_intent": _slug_to_intent(url),
        "property_category": _slug_to_category(url),
        "image_urls": [],
        "phones": [],
        "amenities": [],
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
    }

    page_title = _text_or_empty(soup.title.get_text(" ", strip=True)) if soup.title else ""
    h1 = soup.find("h1")
    h1_text = _text_or_empty(h1.get_text(" ", strip=True) if h1 else "")
    title = h1_text or page_title or _text_or_empty(result.get("title"))
    if title:
        cleaned_title = re.sub(r"\s*::\s*imot\.bg.*$", "", title, flags=re.IGNORECASE).strip()
        result["title"] = cleaned_title
    canonical = soup.find("link", rel="canonical")
    canonical_url = str(canonical.get("href") or url) if canonical else url
    result["listing_intent"] = _slug_to_intent(canonical_url)
    result["property_category"] = _slug_to_category(f"{canonical_url} {title}")
    result["rooms"] = result.get("rooms") or _rooms_from_text(title) or _rooms_from_text(result.get("description") or "")

    gallery_urls: list[str] = []
    for img in soup.select("[data-src-gallery]"):
        src = _text_or_empty(img.get("data-src-gallery"))
        if src and src not in gallery_urls:
            gallery_urls.append(src)
    for img_url in result.get("image_urls") or []:
        if img_url not in gallery_urls:
            gallery_urls.append(img_url)
    result["image_urls"] = gallery_urls

    desc_el = soup.select_one(".moreInfo .text, .description")
    if desc_el:
        result["description"] = unescape(desc_el.get_text(" ", strip=True))

    location_el = soup.select_one(".info .location, .location")
    if location_el:
        location_text = unescape(location_el.get_text(" ", strip=True))
        city, district = _split_bg_location(location_text)
        if city:
            result["city"] = city
        if district:
            result["district"] = district
        if location_text:
            result["address_text"] = location_text

    price_el = soup.select_one(".price .cena, .cena")
    if price_el:
        price_text = unescape(price_el.get_text(" ", strip=True))
        price_match = re.search(r"([\d\s,.]+)\s*(EUR|BGN|ЛВ\.?|€|лв\.?)", price_text, re.IGNORECASE)
        if price_match:
            parsed_price = _parse_number(price_match.group(1))
            if parsed_price is not None:
                result["price"] = parsed_price
            currency = price_match.group(2).strip().upper()
            if currency in {"ЛВ", "ЛВ.", "BGN"}:
                result["currency"] = "BGN"
            elif currency in {"€", "EUR"}:
                result["currency"] = "EUR"

    params: dict[str, str] = {}
    for row in soup.select(".adParams > div"):
        pieces = [unescape(piece).strip() for piece in row.stripped_strings if unescape(piece).strip()]
        if pieces:
            key = pieces[0].replace(":", "").strip()
            value = " ".join(pieces[1:]).strip()
        else:
            text = unescape(row.get_text(" ", strip=True))
            if ":" in text:
                key, value = text.split(":", 1)
                key = key.strip()
                value = value.strip()
            else:
                key, value = text, ""
        if key:
            params[key] = value
    for row in soup.select(".adParams li, .adParams .param, .adParams tr"):
        text = unescape(row.get_text(" ", strip=True))
        if not text or text in params:
            continue
        if ":" in text:
            key, value = text.split(":", 1)
            params.setdefault(key.strip(), value.strip())

    area_sources = [
        params.get("Квадратура"),
        params.get("Площ"),
        params.get("ЗП"),
    ]
    title_area_match = re.search(r"(\d+(?:[.,]\d+)?)\s*кв\.?\s*м", title.lower())
    if title_area_match:
        area_sources.append(title_area_match.group(0))
    for raw_value in area_sources:
        area = _parse_number(raw_value)
        if area is not None:
            result["area_sqm"] = area
            break

    floor_sources = [
        params.get("Етаж"),
        params.get("Етажност"),
    ]
    for raw_value in floor_sources:
        floor = _parse_floor_value(_text_or_empty(raw_value))
        if floor is not None:
            result["floor"] = floor
            break

    phone_values: list[str] = []
    for phone_el in soup.select(".phone small, .phone.MT0"):
        phone_values.extend(_normalize_phone_list(phone_el.get_text(" ", strip=True)))
    if not phone_values:
        for phone_el in soup.select(".phone"):
            phone_values.extend(_normalize_phone_list(phone_el.get_text(" ", strip=True)))
    deduped_phones: list[str] = []
    for phone in phone_values:
        if not re.search(r"\d{6,}", phone):
            continue
        if phone not in deduped_phones:
            deduped_phones.append(phone)
    result["phones"] = deduped_phones

    amenities: list[str] = []
    for key, value in params.items():
        if value:
            amenities.append(f"{key}: {value}")
        else:
            amenities.append(key)
    result["amenities"] = amenities
    result["source_attributes"] = params
    result["listing_status"] = "active" if "Изтекла" not in html and "неактивна" not in html.lower() else "inactive"
    result["reference_id"] = f"imot.bg:{result['external_id']}"
    broker_box = soup.select_one(".dealer2023 .broker .name, .broker .name")
    agency_box = soup.select_one(".dealer2023 .company .name, .agency .name")
    if broker_box:
        result["contact_name"] = _text_or_empty(broker_box.get_text(" ", strip=True))
    if agency_box:
        result["agency_name"] = _text_or_empty(agency_box.get_text(" ", strip=True))
    return result


# ──────────────────────────────────────────────────────────────
# Generic listing parser (from HTML)
# ──────────────────────────────────────────────────────────────

def parse_listing_html(html: str, url: str, source_name: str) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "lxml")
    result: dict[str, Any] = {
        "source_name": source_name, "listing_url": url, "external_id": "",
        "title": "", "description": "", "price": None, "currency": "EUR",
        "area_sqm": None, "rooms": None, "floor": None,
        "city": "", "district": "", "address_text": "",
        "latitude": None, "longitude": None,
        "listing_intent": "sale", "property_category": "unknown",
        "image_urls": [], "phones": [], "amenities": [],
        "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
    }

    for item in _load_json_ld_blocks(soup):
        _apply_json_ld(item, result)

    _extract_meta(soup, result)
    if not result["title"]:
        t = soup.find("title")
        if t:
            result["title"] = t.get_text(strip=True)
    if not result["image_urls"]:
        _extract_images(soup, result)
    if result["price"] is None:
        _extract_price_html(soup, result)

    if source_name == "Address.bg":
        result = _parse_address_bg(soup, html, url, result)
    elif source_name == "BulgarianProperties":
        result = _parse_bulgarianproperties(soup, html, url, result)
    elif source_name in {"LUXIMMO", "property.bg", "SUPRIMMO"}:
        result = _parse_property_family(soup, html, url, result, source_name=source_name)
    elif source_name == "OLX.bg":
        result = _parse_olx_bg(soup, html, url, result)
    elif source_name == "Bazar.bg":
        result = _parse_bazar_bg(soup, html, url, result)
    elif source_name == "Yavlena":
        result = _parse_yavlena(soup, html, url, result)
    elif source_name == "alo.bg":
        result = _parse_alo_bg(soup, html, url, result)
    elif source_name == "Domaza":
        result = _parse_domaza(soup, html, url, result)
    elif source_name == "Home2U":
        result = _parse_home2u(soup, html, url, result)

    _apply_property_identity_flags(result)

    ext_id = result.get("external_id") or hashlib.sha1(url.encode()).hexdigest()[:12]
    result["external_id"] = ext_id
    result["reference_id"] = f"{source_name}:{ext_id}"

    blob = f"{result['title']} {result['description']}".lower()
    if "наем" in blob or "rent" in blob:
        result["listing_intent"] = "long_term_rent"
    elif "продажба" in blob or "sale" in blob or "продава" in blob:
        result["listing_intent"] = "sale"

    for kw, cat in [("апартамент", "apartment"), ("apartment", "apartment"), ("студио", "apartment"),
                     ("къща", "house"), ("house", "house"), ("вила", "house"),
                     ("парцел", "land"), ("земя", "land"), ("land", "land"),
                     ("офис", "office"), ("office", "office")]:
        if kw in blob:
            result["property_category"] = cat
            break

    if result["title"] or result["image_urls"] or result["price"] is not None:
        return result
    return None


_MULTI_UNIT_PUBLICATION_RE = re.compile(
    r"\b\d+\s*[-–/]\s*\d+\s*(bedroom|bed|room|спалн|стайн|стаен)\b"
    r"|apartments\s*\(various\s*types\)|various_types|different apartments|apartments available|units available"
    r"|selection of|choice of|prices?\s+from|starting\s+from|цени\s+от|цена\s+от"
    r"|new development|project development|whole residential building|entire residential building"
    r"|жилищна сграда\s+(?:с|предлага|включва|разполага)|новострояща\s+се\s+жилищна\s+сграда"
    r"|комплекс\s+от\s+\d+|вилно\s+селище|проект\s+с\s+\d+",
    re.IGNORECASE,
)

_ON_REQUEST_PRICE_RE = re.compile(r"по\s+запитване|при\s+запитване|on\s+request|upon\s+request|price\s+on\s+request", re.IGNORECASE)


def _apply_property_identity_flags(result: dict[str, Any]) -> None:
    warnings = list(result.get("scrape_warnings") or [])
    provenance = dict(result.get("crawl_provenance") or {})
    text = "\n".join(str(result.get(key) or "") for key in ("title", "description", "listing_url"))

    if _MULTI_UNIT_PUBLICATION_RE.search(text):
        result["suspected_multi_unit_publication"] = True
        warnings.append("suspected_multi_unit_publication")
        provenance["identity_status"] = "source_publication_requires_unit_level_review"
    else:
        result["suspected_multi_unit_publication"] = False
        provenance.setdefault("identity_status", "single_publication_candidate")

    if result.get("price") == 0:
        result["price"] = None
        provenance["price_status"] = "undefined"
        warnings.append("zero_price_normalized_to_undefined")
    elif result.get("price") is None and _ON_REQUEST_PRICE_RE.search(text):
        provenance["price_status"] = "on_request"
    elif result.get("price") is None:
        provenance.setdefault("price_status", "undefined")
    else:
        provenance.setdefault("price_status", "numeric")

    area = result.get("area_sqm")
    if isinstance(area, (int, float)) and 0 < float(area) < 2:
        title_area_values = [value for value in _extract_area_values(str(result.get("title") or "")) if value >= 2]
        title_area = title_area_values[0] if title_area_values else None
        if title_area and title_area >= 2:
            result["area_sqm"] = title_area
            warnings.append("area_decimal_parse_corrected_from_title")
        else:
            provenance["area_status"] = "suspicious_decimal_parse"
            warnings.append("suspicious_area_decimal_parse")

    latitude = result.get("latitude")
    longitude = result.get("longitude")
    if latitude is not None and longitude is not None and not _coordinates_in_bulgaria(latitude, longitude):
        if _coordinates_in_bulgaria(longitude, latitude):
            result["latitude"], result["longitude"] = longitude, latitude
            warnings.append("coordinate_order_corrected")
        else:
            result["latitude"] = None
            result["longitude"] = None
            provenance["geo_status"] = "outside_bulgaria_coordinates_rejected"
            warnings.append("outside_bulgaria_coordinates_rejected")

    result["crawl_provenance"] = provenance
    if warnings:
        result["scrape_warnings"] = sorted(set(warnings))


def _apply_json_ld(ld: dict, r: dict):
    if ld.get("name") and not r["title"]:
        r["title"] = str(ld["name"])
    if ld.get("description"):
        r["description"] = str(ld["description"])[:2000]
    imgs = ld.get("image")
    if imgs:
        if isinstance(imgs, str):
            r["image_urls"].append(imgs)
        elif isinstance(imgs, list):
            for img in imgs:
                u = img if isinstance(img, str) else (img.get("url") or img.get("contentUrl") or "") if isinstance(img, dict) else ""
                if u:
                    r["image_urls"].append(u)
    offers = ld.get("offers")
    if isinstance(offers, dict) and r["price"] is None:
        try:
            r["price"] = float(str(offers.get("price", "")).replace(",", "").replace(" ", ""))
        except ValueError:
            pass
        if offers.get("priceCurrency"):
            r["currency"] = str(offers["priceCurrency"]).upper()
    geo = ld.get("geo")
    if isinstance(geo, dict) and r["latitude"] is None:
        try:
            latitude = float(geo.get("latitude", 0))
            longitude = float(geo.get("longitude", 0))
            if _coordinates_in_bulgaria(latitude, longitude):
                r["latitude"] = latitude
                r["longitude"] = longitude
        except (ValueError, TypeError):
            pass
    addr = ld.get("address")
    if isinstance(addr, dict):
        if addr.get("addressLocality") and not r["city"]:
            r["city"] = addr["addressLocality"]
    area = ld.get("floorSize")
    if isinstance(area, dict) and r["area_sqm"] is None:
        try:
            r["area_sqm"] = float(str(area.get("value", "")).replace(",", ""))
        except ValueError:
            pass
    if ld.get("numberOfRooms") and r["rooms"] is None:
        try:
            r["rooms"] = float(str(ld["numberOfRooms"]))
        except ValueError:
            pass
    for key in ("identifier", "sku", "productID"):
        if ld.get(key) and not r["external_id"]:
            r["external_id"] = str(ld[key])


def _extract_meta(soup, r):
    for m in soup.find_all("meta"):
        prop = m.get("property", "") or m.get("name", "")
        c = m.get("content", "")
        if not c:
            continue
        if prop == "og:title" and not r["title"]:
            r["title"] = c
        elif prop in {"og:description", "description"} and not r["description"]:
            r["description"] = c[:2000]
        elif prop == "og:image" and c not in r["image_urls"]:
            r["image_urls"].append(c)


def _extract_images(soup, r):
    seen = set(r["image_urls"])
    for sel in ["div[class*='gallery'] img", "div[class*='slider'] img", "div[class*='photo'] img",
                "div[class*='image'] img", "figure img", "div[class*='swiper'] img",
                "a[data-fancybox] img", ".property-gallery img", ".listing-photos img"]:
        for img in soup.select(sel):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy") or ""
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("http") and src not in seen:
                seen.add(src)
                r["image_urls"].append(src)
    if len(r["image_urls"]) < 3:
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            if src.startswith("//"):
                src = "https:" + src
            if not src.startswith("http"):
                continue
            if any(skip in src.lower() for skip in ("logo", "icon", "avatar", "banner", "sprite", "pixel", "1x1", "tracking")):
                continue
            if src not in seen:
                seen.add(src)
                r["image_urls"].append(src)
            if len(r["image_urls"]) >= 30:
                break


def _extract_price_html(soup, r):
    price_re = re.compile(r"([\d\s,.]+)\s*(EUR|€|лв\.?|BGN|USD|\$)", re.IGNORECASE)
    for sel in ["span[class*='price']", "div[class*='price']", ".price", "strong[class*='price']"]:
        el = soup.select_one(sel)
        if el:
            m = price_re.search(el.get_text(strip=True))
            if m:
                parsed = _parse_number(m.group(1))
                if parsed is not None:
                    r["price"] = parsed
                    cmap = {"€": "EUR", "лв": "BGN", "лв.": "BGN", "$": "USD"}
                    r["currency"] = cmap.get(m.group(2).strip(), m.group(2).strip().upper())
                    return


# ──────────────────────────────────────────────────────────────
# Stats tracker
# ──────────────────────────────────────────────────────────────

@dataclass
class ScrapeStats:
    source_key: str = ""
    source_name: str = ""
    discovery_pages_fetched: int = 0
    listing_urls_discovered: int = 0
    listing_pages_fetched: int = 0
    listing_pages_parsed: int = 0
    listing_pages_failed: int = 0
    photos_found: int = 0
    photos_downloaded: int = 0
    photos_failed: int = 0
    with_price: int = 0
    with_geo: int = 0
    with_address: int = 0
    with_area: int = 0
    with_rooms: int = 0
    with_description: int = 0
    intents: dict[str, int] = field(default_factory=dict)
    categories: dict[str, int] = field(default_factory=dict)
    product_breakdown: dict[str, int] = field(default_factory=dict)
    sample_reference_ids: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    duration_seconds: float = 0.0
    detail_concurrency_used: int = 1
    source_bucket: str = ""
    _stats_lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


def scrape_stats_to_dict(stats: ScrapeStats) -> dict[str, Any]:
    """JSON-serializable stats (excludes threading.Lock)."""
    return {f.name: getattr(stats, f.name) for f in fields(stats) if f.name != "_stats_lock"}


def _thread_local_client_factory(
    download_photos: bool,
) -> Callable[[], tuple[httpx.Client, httpx.Client | None]]:
    tls = threading.local()

    def get_clients() -> tuple[httpx.Client, httpx.Client | None]:
        if getattr(tls, "http", None) is None:
            tls.http = make_client()
            tls.photo = make_client() if download_photos else None
        return tls.http, tls.photo

    return get_clients


def _run_bounded_listing_details(
    stats: ScrapeStats,
    log_label: str,
    source_key: str,
    source_display_name: str,
    urls: list[str],
    max_listings: int,
    download_photos: bool,
    detail_fn: Callable[[int, str, httpx.Client, httpx.Client | None], None],
) -> None:
    """Detail phase: bounded parallel fetches; one httpx client (and optional photo client) per worker thread."""
    stats.source_bucket = source_bucket_for_key(source_key, source_display_name=source_display_name)
    workers = detail_concurrency_for_source(source_key, source_display_name)
    stats.detail_concurrency_used = workers
    to_process = list(enumerate(urls[:max_listings]))
    total = len(to_process)
    get_clients = _thread_local_client_factory(download_photos)

    def _execute(job: tuple[int, str]) -> None:
        i, url = job
        if i > 0 and i % 25 == 0:
            with stats._stats_lock:
                fetched = stats.listing_pages_fetched
                parsed = stats.listing_pages_parsed
            logger.info(
                "[%s] Progress: %d/%d fetched=%d parsed=%d",
                log_label,
                i,
                total,
                fetched,
                parsed,
            )
        time.sleep(DELAY)
        http, photo = get_clients()
        detail_fn(i, url, http, photo)

    def _safe(job: tuple[int, str]) -> None:
        try:
            _execute(job)
        except Exception:
            logger.exception("[%s] Unhandled error for %s", log_label, job[1])
            with stats._stats_lock:
                stats.listing_pages_failed += 1

    if workers <= 1:
        for item in to_process:
            _safe(item)
        return

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(_safe, to_process))


def _append_scrape_metrics(stats: ScrapeStats) -> None:
    runs_dir = REPO / "data" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": stats.end_time or stats.start_time,
        "source_key": stats.source_key,
        "source_name": stats.source_name,
        "source_bucket": stats.source_bucket,
        "detail_concurrency_used": stats.detail_concurrency_used,
        "duration_seconds": stats.duration_seconds,
        "listing_urls_discovered": stats.listing_urls_discovered,
        "listing_pages_fetched": stats.listing_pages_fetched,
        "listing_pages_parsed": stats.listing_pages_parsed,
        "listing_pages_failed": stats.listing_pages_failed,
        "photos_found": stats.photos_found,
        "photos_downloaded": stats.photos_downloaded,
        "photos_failed": stats.photos_failed,
        "errors_count": len(stats.errors),
    }
    payload = json.dumps(line, ensure_ascii=False)
    path = runs_dir / "scrape_metrics.jsonl"
    with path.open("a", encoding="utf-8") as wf:
        wf.write(payload + "\n")
    (runs_dir / "scrape_metrics_latest.json").write_text(
        json.dumps(line, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _save_listing(stats: ScrapeStats, parsed: dict, html: str, source_key: str,
                  *, download_photos: bool = False, photo_client: httpx.Client | None = None,
                  product_label: str | None = None, extra_fields: dict[str, Any] | None = None):
    ref_id = parsed["reference_id"]
    safe_ref = re.sub(r'[/:*?"<>|\\]', '_', ref_id)
    if extra_fields:
        parsed.update(extra_fields)
    _apply_immediate_publication_status(parsed)

    listing_dir = SCRAPED_ROOT / source_key / "listings"
    raw_dir = SCRAPED_ROOT / source_key / "raw"
    media_root = ensure_media_root()
    if not media_root.is_absolute():
        media_root = (REPO / media_root).resolve()
    listing_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    imgs = parsed.get("image_urls", [])
    # Normalize protocol-relative URLs
    imgs = [("https:" + u if u.startswith("//") else u) for u in imgs]
    parsed["image_urls"] = imgs
    media_dir = media_root / safe_ref
    if media_dir.exists():
        existing_files = sorted(p for p in media_dir.iterdir() if p.is_file())
        parsed["local_image_files"] = [str(path.resolve().relative_to(REPO)) for path in existing_files]
        parsed["local_image_storage_keys"] = [f"{safe_ref}/{path.name}" for path in existing_files]
    else:
        parsed["local_image_files"] = []
        parsed["local_image_storage_keys"] = []
    try:
        parsed["local_media_dir"] = str(media_dir.resolve().relative_to(REPO))
    except Exception:
        parsed["local_media_dir"] = str(media_dir.resolve())
    parsed["photo_count_remote"] = len(imgs)

    with stats._stats_lock:
        stats.listing_pages_parsed += 1
        if parsed.get("price") is not None:
            stats.with_price += 1
        if parsed.get("latitude") is not None:
            stats.with_geo += 1
        if parsed.get("city") or parsed.get("address_text"):
            stats.with_address += 1
        if parsed.get("area_sqm") is not None:
            stats.with_area += 1
        if parsed.get("rooms") is not None:
            stats.with_rooms += 1
        if parsed.get("description"):
            stats.with_description += 1

        intent = parsed.get("listing_intent", "unknown")
        stats.intents[intent] = stats.intents.get(intent, 0) + 1
        cat = parsed.get("property_category", "unknown")
        stats.categories[cat] = stats.categories.get(cat, 0) + 1
        if product_label:
            stats.product_breakdown[product_label] = stats.product_breakdown.get(product_label, 0) + 1
            parsed["pattern_bucket_label"] = product_label
        if ref_id not in stats.sample_reference_ids and len(stats.sample_reference_ids) < 8:
            stats.sample_reference_ids.append(ref_id)
        stats.photos_found += len(imgs)

    if download_photos and imgs and photo_client:
        photo_urls = imgs if PHOTO_LIMIT <= 0 else imgs[:PHOTO_LIMIT]
        for idx, photo_url in enumerate(photo_urls):
            try:
                dr = download_image(photo_url, reference_id=safe_ref, ordering=idx, client=photo_client)
                with stats._stats_lock:
                    if dr.status == "downloaded":
                        stats.photos_downloaded += 1
                    else:
                        stats.photos_failed += 1
            except Exception:
                with stats._stats_lock:
                    stats.photos_failed += 1

    if media_dir.exists():
        stored_files = sorted(p for p in media_dir.iterdir() if p.is_file())
        parsed["local_image_files"] = [str(path.relative_to(REPO)) for path in stored_files]
        parsed["local_image_storage_keys"] = [f"{safe_ref}/{path.name}" for path in stored_files]
    parsed["photo_count_local"] = len(parsed.get("local_image_files") or [])
    # Partial galleries are normal mid-run (failed downloads, rate limits, or `--download-photos` off).
    # `action1_full_telegram_report.py` flags gallery_gap until local catches up to remote — not always a parser bug.
    parsed["full_gallery_downloaded"] = bool(
        parsed["photo_count_remote"] > 0 and parsed["photo_count_local"] >= parsed["photo_count_remote"]
    )
    # Normalize to four operator buckets used throughout the repo.
    # This is intentionally coarse and derived from parsed intent + category so the
    # dashboard and quality audits can reason about coverage even when a source's
    # own search routes are mixed.
    listing_intent = str(parsed.get("listing_intent") or "sale").lower()
    property_category = str(parsed.get("property_category") or "other").lower()
    deal = "rent" if listing_intent in {"rent", "long_term_rent", "short_term_rent", "short_term_rental"} else "buy"
    commercial = property_category in {"office", "shop", "land", "garage"}
    space = "commercial" if commercial else "personal"
    parsed["bucket_key"] = f"{deal}_{space}"
    parsed["segment_key"] = parsed["bucket_key"]
    if parsed["photo_count_remote"] <= 0:
        parsed["photo_download_status"] = "no_remote_gallery"
    elif parsed["photo_count_local"] <= 0:
        parsed["photo_download_status"] = "no_local_files"
    elif parsed["photo_count_local"] >= parsed["photo_count_remote"]:
        parsed["photo_download_status"] = "full_gallery"
    else:
        parsed["photo_download_status"] = "partial_gallery"

    (listing_dir / f"{safe_ref}.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (raw_dir / f"{safe_ref}.html").write_text(html, encoding="utf-8")


# ──────────────────────────────────────────────────────────────
# Source-specific scrapers
# ──────────────────────────────────────────────────────────────

def _scrape_homes_bg(stats: ScrapeStats, client: httpx.Client, max_pages: int, max_listings: int,
                     download_photos: bool, photo_client: httpx.Client | None,
                     *, page_order: str = "newest_first",
                     api_templates: list[tuple[str, str]] | None = None,
                     accept_parsed: Callable[[dict[str, Any], str, str, str], bool] | None = None,
                     save_context_builder: Callable[[dict[str, Any], str, str, str], dict[str, Any] | None] | None = None):
    """Homes.bg: uses JSON API for discovery, HTML for detail."""
    search_types = [
        ("sale-sofia", "1", "sofia"),
        ("sale-varna", "1", "varna"),
        ("sale-burgas", "1", "burgas"),
        ("sale-plovdiv", "1", "plovdiv"),
        ("rent-sofia", "2", "sofia"),
        ("rent-varna", "2", "varna"),
        ("sale-all", "1", ""),
        ("rent-all", "2", ""),
    ]
    all_urls: list[str] = []
    seen: set[str] = set()
    url_to_bucket: dict[str, str] = {}

    if api_templates:
        template_defs: list[tuple[str, str]] = api_templates
    else:
        template_defs = []
        for intent_label, offer_type, city in search_types:
            template = f"https://www.homes.bg/api/offers?currPage={{page}}&lang=bg&offerType={offer_type}"
            if city:
                template += f"&city={city}"
            template_defs.append((intent_label, template))

    for intent_label, api_template in template_defs:
        for page in _iter_pages(max_pages, page_order):
            if len(all_urls) >= max_listings:
                break
            api_url = api_template.format(page=page)
            data = fetch_json(client, api_url)
            if not data or not isinstance(data, dict):
                break
            results = data.get("result", [])
            if not results:
                break
            stats.discovery_pages_fetched += 1

            for item in results:
                href = item.get("viewHref", "")
                if href:
                    full = f"https://www.homes.bg{href}" if href.startswith("/") else href
                    if full not in seen:
                        seen.add(full)
                        all_urls.append(full)
                        url_to_bucket[full] = intent_label
            logger.info("[homes_bg] API page %d (%s): %d items, total: %d", page, intent_label, len(results), len(all_urls))
            time.sleep(DELAY * 0.5)

    stats.listing_urls_discovered = len(all_urls)
    logger.info("[homes_bg] Discovery: %d unique URLs from %d API pages", len(all_urls), stats.discovery_pages_fetched)

    def _detail_homes(
        _i: int, url: str, http: httpx.Client, photo: httpx.Client | None,
    ) -> None:
        html = fetch_page(http, url)
        if not html:
            with stats._stats_lock:
                stats.listing_pages_failed += 1
            return
        with stats._stats_lock:
            stats.listing_pages_fetched += 1
        parsed = parse_homes_detail(html, url)
        if parsed:
            bucket_label = url_to_bucket.get(url, "default")
            _apply_bucket_context(parsed, bucket_label, url)
            if accept_parsed and not accept_parsed(parsed, url, html, bucket_label):
                return
            _save_listing(
                stats,
                parsed,
                html,
                "homes_bg",
                download_photos=download_photos,
                photo_client=photo,
                product_label=bucket_label or f"{parsed.get('listing_intent', 'unknown')}:{parsed.get('property_category', 'unknown')}",
                extra_fields=save_context_builder(parsed, url, html, bucket_label) if save_context_builder else None,
            )
        else:
            with stats._stats_lock:
                stats.listing_pages_failed += 1

    _run_bounded_listing_details(
        stats,
        "homes_bg",
        "homes_bg",
        "Homes.bg",
        all_urls,
        max_listings,
        download_photos,
        _detail_homes,
    )


def _scrape_imot_bg(stats: ScrapeStats, client: httpx.Client, max_pages: int, max_listings: int,
                    download_photos: bool, photo_client: httpx.Client | None,
                    *, page_order: str = "newest_first",
                    search_routes: list[tuple[str, str]] | None = None,
                    accept_parsed: Callable[[dict[str, Any], str, str, str], bool] | None = None,
                    save_context_builder: Callable[[dict[str, Any], str, str, str], dict[str, Any] | None] | None = None):
    """imot.bg: server-rendered search with /obiava-... URLs."""
    search_urls = [
        "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya",
        "https://www.imot.bg/obiavi/prodazhbi/grad-varna",
        "https://www.imot.bg/obiavi/prodazhbi/grad-burgas",
        "https://www.imot.bg/obiavi/prodazhbi/grad-plovdiv",
        "https://www.imot.bg/obiavi/naemi/grad-sofiya",
        "https://www.imot.bg/obiavi/naemi/grad-varna",
        "https://www.imot.bg/obiavi/prodazhbi/grad-ruse",
        "https://www.imot.bg/obiavi/prodazhbi/grad-stara-zagora",
    ]
    all_urls: list[str] = []
    seen: set[str] = set()
    url_to_bucket: dict[str, str] = {}
    obiava_re = re.compile(r'href="(//www\.imot\.bg/obiava-[^"]+)"')

    if search_routes:
        route_defs = search_routes
    else:
        route_defs = []
        for search_url in search_urls:
            intent_label = "rent" if "/naemi/" in search_url else "sale"
            city_label = search_url.rsplit("/", 1)[-1].replace("grad-", "")
            route_defs.append((f"{intent_label}_{city_label}", search_url))

    for bucket_label, search_url in route_defs:
        for page in _iter_pages(max_pages, page_order):
            if len(all_urls) >= max_listings:
                break
            paged_url = search_url if page == 1 else f"{search_url}/p-{page}"
            html = fetch_page(client, paged_url)
            if not html:
                break
            stats.discovery_pages_fetched += 1
            matches = obiava_re.findall(html)
            new_count = 0
            for m in matches:
                full = "https:" + m if m.startswith("//") else m
                full = full.split("#")[0]
                slug = full.lower()
                if any(skip in slug for skip in ("zhilishten-kompleks", "zhilishtna-sgrada")):
                    continue
                if full not in seen:
                    seen.add(full)
                    all_urls.append(full)
                    url_to_bucket[full] = bucket_label
                    new_count += 1
            logger.info("[imot_bg] %s p%d: %d URLs (%d new), total: %d", bucket_label, page, len(matches), new_count, len(all_urls))
            if not new_count:
                break
            time.sleep(DELAY)

    stats.listing_urls_discovered = len(all_urls)
    logger.info("[imot_bg] Discovery: %d unique URLs", len(all_urls))

    def _detail_imot(
        _i: int, url: str, http: httpx.Client, photo: httpx.Client | None,
    ) -> None:
        html = fetch_page(http, url)
        if not html:
            with stats._stats_lock:
                stats.listing_pages_failed += 1
            return
        with stats._stats_lock:
            stats.listing_pages_fetched += 1
        parsed = parse_imot_detail(html, url)
        if parsed:
            bucket_label = url_to_bucket.get(url, "default")
            _apply_bucket_context(parsed, bucket_label, url)
            if accept_parsed and not accept_parsed(parsed, url, html, bucket_label):
                return
            _save_listing(
                stats,
                parsed,
                html,
                "imot_bg",
                download_photos=download_photos,
                photo_client=photo,
                product_label=bucket_label or f"{parsed.get('listing_intent', 'unknown')}:{parsed.get('property_category', 'unknown')}",
                extra_fields=save_context_builder(parsed, url, html, bucket_label) if save_context_builder else None,
            )
        else:
            with stats._stats_lock:
                stats.listing_pages_failed += 1

    _run_bounded_listing_details(
        stats,
        "imot_bg",
        "imot_bg",
        "imot.bg",
        all_urls,
        max_listings,
        download_photos,
        _detail_imot,
    )


def _scrape_generic_html(stats: ScrapeStats, client: httpx.Client, source_key: str, source_name: str,
                         search_urls: list[str], listing_pattern: re.Pattern, base_url: str,
                         max_pages: int, max_listings: int, download_photos: bool, photo_client: httpx.Client | None,
                         *, page_suffix: str = "?page={}", buckets: list[dict[str, Any]] | None = None,
                         page_order: str = "newest_first",
                         accept_parsed: Callable[[dict[str, Any], str, str, str], bool] | None = None,
                         save_context_builder: Callable[[dict[str, Any], str, str, str], dict[str, Any] | None] | None = None):
    """Generic HTML scraper for sources with standard pagination."""
    all_urls: list[str] = []
    seen: set[str] = set()
    url_to_bucket: dict[str, str] = {}

    bucket_defs = buckets or [{"label": "default", "search_urls": search_urls, "page_suffix": page_suffix}]

    for bucket in bucket_defs:
        bucket_label = bucket.get("label", "default")
        bucket_urls = bucket.get("search_urls") or []
        bucket_suffix = bucket.get("page_suffix", page_suffix)
        for search_url in bucket_urls:
            for page in _iter_pages(max_pages, page_order):
                if len(all_urls) >= max_listings:
                    break
                if page == 1:
                    paged = search_url
                elif "{}" in bucket_suffix:
                    paged = search_url + bucket_suffix.format(page)
                else:
                    paged = search_url + bucket_suffix + str(page)

                html = fetch_page(client, paged)
                if not html:
                    break
                stats.discovery_pages_fetched += 1

                soup = BeautifulSoup(html, "lxml")
                new_count = 0
                for a in soup.find_all("a", href=True):
                    href = str(a.get("href") or "")
                    full = urljoin(base_url, href)
                    if listing_pattern.search(full) and full not in seen:
                        seen.add(full)
                        all_urls.append(full)
                        url_to_bucket[full] = bucket_label
                        new_count += 1
                logger.info(
                    "[%s] %s p%d: %d new URLs, total: %d",
                    source_key,
                    bucket_label,
                    page,
                    new_count,
                    len(all_urls),
                )
                if not new_count:
                    break
                time.sleep(DELAY)

    stats.listing_urls_discovered = len(all_urls)
    logger.info("[%s] Discovery: %d URLs from %d pages", source_key, len(all_urls), stats.discovery_pages_fetched)

    def _detail_generic(
        _i: int, url: str, http: httpx.Client, photo: httpx.Client | None,
    ) -> None:
        html = fetch_page(http, url)
        if not html:
            with stats._stats_lock:
                stats.listing_pages_failed += 1
            return
        with stats._stats_lock:
            stats.listing_pages_fetched += 1
        parsed = parse_listing_html(html, url, source_name)
        if parsed:
            bucket_label = url_to_bucket.get(url, "default")
            _apply_bucket_context(parsed, bucket_label, url)
            if accept_parsed and not accept_parsed(parsed, url, html, bucket_label):
                return
            _save_listing(
                stats,
                parsed,
                html,
                source_key,
                download_photos=download_photos,
                photo_client=photo,
                product_label=bucket_label,
                extra_fields=save_context_builder(parsed, url, html, bucket_label) if save_context_builder else None,
            )
        else:
            with stats._stats_lock:
                stats.listing_pages_failed += 1

    _run_bounded_listing_details(
        stats,
        source_key,
        source_key,
        source_name,
        all_urls,
        max_listings,
        download_photos,
        _detail_generic,
    )


# ──────────────────────────────────────────────────────────────
# Source dispatch table
# ──────────────────────────────────────────────────────────────

SOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "homes_bg": {"name": "Homes.bg", "func": "_scrape_homes_bg"},
    "imot_bg": {"name": "imot.bg", "func": "_scrape_imot_bg"},
    "alo_bg": {
        "name": "alo.bg", "func": "generic",
        "base_url": "https://www.alo.bg",
        "buckets": [
            {
                "label": "sale_apartments",
                "search_urls": ["https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/?region_id=3&location_ids=554"],
            },
            {
                "label": "sale_houses",
                "search_urls": ["https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/?region_id=3&location_ids=554"],
            },
            {
                "label": "sale_land",
                "search_urls": [
                    "https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/?region_id=3&location_ids=554",
                    "https://www.alo.bg/obiavi/imoti-prodajbi/zemedelska-zemia-gradini-lozia-gora/?region_id=3&location_ids=554",
                ],
            },
            {
                "label": "rent_apartments",
                "search_urls": ["https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/?region_id=3&location_ids=554"],
            },
        ],
        "listing_pattern": re.compile(r"alo\.bg/.+-\d{5,}(?:[/?#].*)?$"),
        "page_suffix": "?page={}",
    },
    "address_bg": {
        "name": "Address.bg", "func": "generic",
        "base_url": "https://address.bg",
        "buckets": [
            {
                "label": "sale_all",
                "search_urls": ["https://address.bg/sale"],
            },
            {
                "label": "rent_all",
                "search_urls": ["https://address.bg/rent"],
            },
            {
                "label": "sale_sofia",
                "search_urls": ["https://address.bg/sale/sofia/l4451"],
            },
            {
                "label": "sale_varna",
                "search_urls": ["https://address.bg/sale/varna/l4694"],
            },
            {
                "label": "rent_sofia",
                "search_urls": ["https://address.bg/rent/sofia/l4451"],
            },
        ],
        "listing_pattern": re.compile(r"address\.bg/.+-offer\d{5,}(?:[/?#].*)?$"),
        "page_suffix": "?page={}",
    },
    "bulgarianproperties": {
        "name": "BulgarianProperties", "func": "generic",
        "base_url": "https://www.bulgarianproperties.com",
        "buckets": [
            {
                "label": "sale_all",
                "search_urls": ["https://www.bulgarianproperties.com/properties_for_sale_in_Bulgaria/index.html"],
            },
            {
                "label": "rent_all",
                "search_urls": ["https://www.bulgarianproperties.com/properties_for_rent_in_Bulgaria/index.html"],
            },
            {
                "label": "sale_land",
                "search_urls": ["https://www.bulgarianproperties.com/land_for_sale_in_Bulgaria/index.html"],
            },
            {
                "label": "sale_apartment_1br",
                "search_urls": ["https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html"],
            },
            {
                "label": "sale_apartment_2br",
                "search_urls": ["https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html"],
            },
            {
                "label": "sale_apartment_3br",
                "search_urls": ["https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html"],
            },
            {
                "label": "sale_houses",
                "search_urls": ["https://www.bulgarianproperties.com/houses_in_Bulgaria/index.html"],
            },
        ],
        "listing_pattern": re.compile(r"bulgarianproperties\.com/.+AD\d+BG"),
        "page_suffix": "?page={}",
    },
    "suprimmo": {
        "name": "SUPRIMMO", "func": "generic",
        "base_url": "https://www.suprimmo.bg",
        "buckets": [
            {
                "label": "sale_apartments",
                "search_urls": ["https://www.suprimmo.bg/bulgaria/apartamenti/"],
                "page_suffix": "/page/{}/",
            },
            {
                "label": "sale_houses",
                "search_urls": ["https://www.suprimmo.bg/bulgaria/kushti-vili/"],
                "page_suffix": "/page/{}/",
            },
            {
                "label": "sale_land",
                "search_urls": ["https://www.suprimmo.bg/bulgaria/partseli/"],
                "page_suffix": "/page/{}/",
            },
            {
                "label": "sale_selection",
                "search_urls": ["https://www.suprimmo.bg/prodajba/bulgaria/selectsya/"],
                "page_suffix": "/page/{}/",
            },
            {
                "label": "rent_selection",
                "search_urls": ["https://www.suprimmo.bg/naem/bulgaria/selectsya/"],
                "page_suffix": "/page/{}/",
            },
        ],
        "listing_pattern": re.compile(r"suprimmo\.bg/imot-\d{5,}(?:[-/][^\"'<> ]*)?"),
        "page_suffix": "/page/{}/",
    },
    "luximmo": {
        "name": "LUXIMMO", "func": "generic",
        "base_url": "https://www.luximmo.bg",
        "buckets": [
            {
                "label": "sale_apartments",
                "search_urls": ["https://www.luximmo.bg/apartamenti/"],
                "page_suffix": "index{}.html",
            },
        ],
        "listing_pattern": re.compile(r"luximmo\.bg/.+-\d{5,}-[^\"'<> ]+\.html(?:[?#][^\"'<> ]*)?$"),
        "page_suffix": "index{}.html",
    },
    "property_bg": {
        "name": "property.bg", "func": "generic",
        "base_url": "https://www.property.bg",
        "buckets": [
            {
                "label": "sale_apartments",
                "search_urls": ["https://www.property.bg/bulgaria/apartments/"],
                "page_suffix": "/page/{}/",
            },
            {
                "label": "sale_selection",
                "search_urls": ["https://www.property.bg/sales/bulgaria/selection/"],
                "page_suffix": "/page/{}/",
            },
            {
                "label": "rent_selection",
                "search_urls": ["https://www.property.bg/rentals/bulgaria/selection/"],
                "page_suffix": "/page/{}/",
            },
        ],
        "listing_pattern": re.compile(r"property\.bg/property-\d{5,}(?:[-/][^\"'<> ]*)?"),
        "page_suffix": "/page/{}/",
    },
    "bazar_bg": {
        "name": "Bazar.bg", "func": "generic",
        "base_url": "https://bazar.bg",
        "buckets": [
            {
                "label": "sale_apartments",
                "search_urls": ["https://bazar.bg/obiavi/apartamenti"],
            },
            {
                "label": "sale_houses",
                "search_urls": ["https://bazar.bg/obiavi/kashti-i-vili"],
            },
            {
                "label": "sale_land",
                "search_urls": ["https://bazar.bg/obiavi/zemya"],
            },
            {
                "label": "sale_garages",
                "search_urls": ["https://bazar.bg/obiavi/garazhi-i-parkoingi"],
            },
        ],
        "listing_pattern": re.compile(r"bazar\.bg/obiava-\d{5,}"),
        "page_suffix": "?page={}",
    },
    "domaza": {
        "name": "Domaza", "func": "generic",
        "base_url": "https://www.domaza.bg",
        "search_urls": [
            "https://www.domaza.bg/недвижими_имоти_във_варна_за_продажба/",
            "https://www.domaza.bg/недвижими_имоти_във_варна_под_наем/",
        ],
        "listing_pattern": re.compile(r"domaza\.bg/.+-16-\d+-p/"),
        "page_suffix": "?page={}",
    },
    "yavlena": {
        "name": "Yavlena", "func": "generic",
        "base_url": "https://www.yavlena.com",
        "buckets": [
            {
                "label": "sale_all",
                "search_urls": ["https://www.yavlena.com/bg/sales"],
            },
            {
                "label": "rent_all",
                "search_urls": ["https://www.yavlena.com/bg/rentals"],
            },
        ],
        "listing_pattern": re.compile(r"yavlena\.com/bg/\d{5,}"),
        "page_suffix": "?page={}",
    },
    "home2u": {
        "name": "Home2U", "func": "generic",
        "base_url": "https://home2u.bg",
        "search_urls": [
            "https://home2u.bg/partseli-i-teren-varna/",
            "https://home2u.bg/ofisi-pod-naem-varna/",
            "https://home2u.bg/magazini-pod-naem-varna/",
            "https://home2u.bg/apartamenti-pod-naem-varna/",
        ],
        "listing_pattern": re.compile(r"home2u\.bg/property/[^\"'<> ]+/?(?:[?#].*)?$"),
        "page_suffix": "?page={}",
    },
    "olx_bg": {
        "name": "OLX.bg", "func": "generic",
        "base_url": "https://www.olx.bg",
        "buckets": [
            {
                "label": "all_real_estate",
                "search_urls": ["https://www.olx.bg/nedvizhimi-imoti/"],
            },
        ],
        "listing_pattern": re.compile(r"olx\.bg/d/ad/"),
        "page_suffix": "?page={}",
    },
}


def scrape_source(key: str, *, download_photos: bool = False,
                  max_pages: int = 12, max_listings: int = 500,
                  page_order: str | None = None,
                  config_override: dict[str, Any] | None = None,
                  accept_parsed: Callable[[dict[str, Any], str, str, str], bool] | None = None,
                  save_context_builder: Callable[[dict[str, Any], str, str, str], dict[str, Any] | None] | None = None) -> ScrapeStats:
    cfg = {**SOURCE_CONFIGS[key], **(config_override or {})}
    stats = ScrapeStats(source_key=key, source_name=cfg["name"])
    stats.start_time = datetime.now(tz=timezone.utc).isoformat()
    t0 = time.time()

    client = make_client()
    photo_client = make_client() if download_photos else None

    logger.info("=== Starting scrape: %s ===", cfg["name"])

    try:
        func_name = cfg["func"]
        effective_page_order = str(page_order or cfg.get("page_order") or PAGE_ORDER_DEFAULT or "newest_first").strip().lower()
        if func_name == "_scrape_homes_bg":
            _scrape_homes_bg(
                stats, client, max_pages, max_listings, download_photos, photo_client,
                page_order=effective_page_order,
                api_templates=cfg.get("api_templates"),
                accept_parsed=accept_parsed,
                save_context_builder=save_context_builder,
            )
        elif func_name == "_scrape_imot_bg":
            _scrape_imot_bg(
                stats, client, max_pages, max_listings, download_photos, photo_client,
                page_order=effective_page_order,
                search_routes=cfg.get("search_routes"),
                accept_parsed=accept_parsed,
                save_context_builder=save_context_builder,
            )
        elif func_name == "generic":
            _scrape_generic_html(
                stats, client, key, cfg["name"],
                cfg.get("search_urls", []), cfg["listing_pattern"], cfg["base_url"],
                max_pages, max_listings, download_photos, photo_client,
                page_suffix=cfg.get("page_suffix", "?page={}"),
                buckets=cfg.get("buckets"),
                page_order=effective_page_order,
                accept_parsed=accept_parsed,
                save_context_builder=save_context_builder,
            )
    except Exception:
        logger.exception("Error scraping %s", key)
        stats.errors.append(traceback.format_exc())
    finally:
        client.close()
        if photo_client:
            photo_client.close()

    stats.end_time = datetime.now(tz=timezone.utc).isoformat()
    stats.duration_seconds = round(time.time() - t0, 1)

    stats_dir = SCRAPED_ROOT / key
    stats_dir.mkdir(parents=True, exist_ok=True)
    (stats_dir / "scrape_stats.json").write_text(json.dumps(scrape_stats_to_dict(stats), ensure_ascii=False, indent=2), encoding="utf-8")

    _append_scrape_metrics(stats)

    logger.info(
        "[%s] DONE in %.1fs — discovered=%d fetched=%d parsed=%d photos=%d/%d",
        key, stats.duration_seconds, stats.listing_urls_discovered,
        stats.listing_pages_fetched, stats.listing_pages_parsed,
        stats.photos_found, stats.photos_downloaded,
    )
    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Live scraper for BG real estate")
    parser.add_argument("--sources", type=str, default="all")
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--max-listings", type=int, default=500)
    parser.add_argument("--download-photos", action="store_true")
    parser.add_argument("--list-sources", action="store_true")
    args = parser.parse_args()

    if args.list_sources:
        for k, v in sorted(SOURCE_CONFIGS.items()):
            print(f"  {k:25s} — {v['name']}")
        return

    (REPO / "data").mkdir(exist_ok=True)
    SCRAPED_ROOT.mkdir(parents=True, exist_ok=True)
    ensure_media_root()

    keys = list(SOURCE_CONFIGS.keys()) if args.sources == "all" else [k.strip() for k in args.sources.split(",")]
    all_stats: list[ScrapeStats] = []

    for key in keys:
        if key not in SOURCE_CONFIGS:
            logger.error("Unknown source: %s", key)
            continue
        try:
            s = scrape_source(key, download_photos=args.download_photos,
                            max_pages=args.max_pages, max_listings=args.max_listings)
            all_stats.append(s)
        except Exception:
            logger.exception("Fatal error: %s", key)

    combined = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sources_scraped": len(all_stats),
        "total_discovered": sum(s.listing_urls_discovered for s in all_stats),
        "total_fetched": sum(s.listing_pages_fetched for s in all_stats),
        "total_parsed": sum(s.listing_pages_parsed for s in all_stats),
        "total_photos_found": sum(s.photos_found for s in all_stats),
        "total_photos_downloaded": sum(s.photos_downloaded for s in all_stats),
        "per_source": [scrape_stats_to_dict(s) for s in all_stats],
    }
    (SCRAPED_ROOT / "scrape_summary.json").write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 70)
    print("SCRAPE SUMMARY")
    print("=" * 70)
    for s in all_stats:
        print(f"\n{s.source_name}:")
        print(f"  Discovered: {s.listing_urls_discovered:>6}  Fetched: {s.listing_pages_fetched:>6}  Parsed: {s.listing_pages_parsed:>6}")
        print(f"  Photos:     {s.photos_found:>6} found, {s.photos_downloaded:>6} downloaded")
        print(f"  Price: {s.with_price:>4}  Geo: {s.with_geo:>4}  Addr: {s.with_address:>4}  Area: {s.with_area:>4}  Rooms: {s.with_rooms:>4}")
        if s.product_breakdown:
            breakdown = ", ".join(f"{k}={v}" for k, v in sorted(s.product_breakdown.items()))
            print(f"  Products:   {breakdown}")
        print(f"  Duration: {s.duration_seconds:.1f}s")
    print(f"\nTOTAL: {combined['total_discovered']} discovered, {combined['total_parsed']} parsed, {combined['total_photos_found']} photos")


if __name__ == "__main__":
    main()
