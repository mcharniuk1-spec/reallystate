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
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from bgrealestate.services.media import download_image, ensure_media_root  # noqa: E402

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


def make_client() -> httpx.Client:
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
    raw = title.strip()
    match = re.search(r"гр\.\s*([^,|]+)(?:,\s*([^|]+))?", raw, re.IGNORECASE)
    if match:
        return match.group(1).strip(), _text_or_empty(match.group(2))
    match = re.search(r"гр\.\s*([A-ZА-Я][^\s|•]+)\s+([^|•]+)", raw, re.IGNORECASE)
    if match:
        return match.group(1).strip(), _text_or_empty(match.group(2)).strip()
    match = re.search(r"\bв\s+([A-ZА-Я][^,|]+?)(?:,\s*([^|]+))?(?:\s*(?:-|$))", raw)
    if match:
        return match.group(1).strip(), _text_or_empty(match.group(2))
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
    breadcrumb_text = " ".join(li.get_text(" ", strip=True) for li in soup.select("[itemtype*='BreadcrumbList'] li, .breadcrumbs li"))
    phone_urls = [link.get("href", "").replace("tel:", "") for link in soup.select("a[href^='tel:']")]
    patch = {
        "price": result.get("price"),
        "currency": result.get("currency") or "EUR",
        "city": city,
        "district": district,
        "address_text": address_text or ", ".join(part for part in [city, district] if part),
        "phones": _unique_preserve([*_extract_phone_numbers(html), *_text_list(phone_urls)]),
        "area_sqm": exact_area or (max(area_values) if area_values else None),
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
        patch["address_text"] = ", ".join(part for part in [patch["city"], patch["district"]] if part)
    if patch["district"]:
        patch["district"] = re.sub(r"\s*-\s*код на имота.*$", "", patch["district"]).strip()
        patch["address_text"] = ", ".join(part for part in [patch["city"], patch["district"]] if part)
    return _merge_source_result(result, patch)


def _parse_bulgarianproperties(soup: BeautifulSoup, html: str, url: str, result: dict[str, Any]) -> dict[str, Any]:
    blocks = _load_json_ld_blocks(soup)
    product = next((block for block in blocks if block.get("@type") == "Product"), {})
    title = _text_or_empty((soup.find("h1") or {}).get_text(" ", strip=True) if soup.find("h1") else "")
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
    patch = {
        "title": title or _text_or_empty(product.get("name")) or result.get("title"),
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
    patch = {
        "title": title or result.get("title"),
        "price": result.get("price"),
        "currency": result.get("currency") or "EUR",
        "city": _extract_js_single_quoted_value(data_layer, "town"),
        "district": _extract_js_single_quoted_value(data_layer, "quart") or _extract_js_single_quoted_value(data_layer, "neighborhood_fb_estate"),
        "region": _extract_js_single_quoted_value(data_layer, "region"),
        "property_category": _slug_to_category(_extract_js_single_quoted_value(data_layer, "property_type") or title),
        "listing_intent": "sale" if any(word in _extract_js_single_quoted_value(data_layer, "type").lower() for word in ("sale", "sales", "продава")) else result.get("listing_intent"),
        "area_sqm": area_values[0] if area_values else result.get("area_sqm"),
        "rooms": _rooms_from_text(title or _extract_js_single_quoted_value(data_layer, "property_type")),
        "address_text": ", ".join(part for part in [_extract_js_single_quoted_value(data_layer, "town"), _extract_js_single_quoted_value(data_layer, "quart") or _extract_js_single_quoted_value(data_layer, "neighborhood_fb_estate")] if part),
        "phones": _extract_phone_numbers(html),
        "image_urls": image_urls or result.get("image_urls", []),
        "source_attributes": {
            "town": _extract_js_single_quoted_value(data_layer, "town"),
            "district_raw": _extract_js_single_quoted_value(data_layer, "quart") or _extract_js_single_quoted_value(data_layer, "neighborhood_fb_estate"),
            "listing_id": _extract_js_single_quoted_value(data_layer, "listing_id"),
        },
    }
    if patch["price"] is None or (patch["price"] and patch["price"] < 1000 and patch["listing_intent"] == "sale"):
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
    if not city:
        title_match = re.search(r"в\s+([A-ZА-Я][A-Za-zА-Яа-я\- ]+?)\s+\d+\s*кв", title)
        if title_match:
            city = title_match.group(1).strip()
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
    area_sqm = _parse_number(title)
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
    h1_text = _text_or_empty((soup.find("h1") or {}).get_text(" ", strip=True) if soup.find("h1") else "")
    title = h1_text or page_title or _text_or_empty(result.get("title"))
    if title:
        cleaned_title = re.sub(r"\s*::\s*imot\.bg.*$", "", title, flags=re.IGNORECASE).strip()
        result["title"] = cleaned_title
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical.get("href") if canonical else url
    result["listing_intent"] = _slug_to_intent(canonical_url)
    result["property_category"] = _slug_to_category(canonical_url + " " + title)
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
    for value in area_sources:
        area = _parse_number(value)
        if area is not None:
            result["area_sqm"] = area
            break

    floor_sources = [
        params.get("Етаж"),
        params.get("Етажност"),
    ]
    for value in floor_sources:
        floor = _parse_floor_value(_text_or_empty(value))
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
            r["latitude"] = float(geo.get("latitude", 0))
            r["longitude"] = float(geo.get("longitude", 0))
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
        elif prop == "og:description" and not r["description"]:
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


def _save_listing(stats: ScrapeStats, parsed: dict, html: str, source_key: str,
                  *, download_photos: bool = False, photo_client: httpx.Client | None = None,
                  product_label: str | None = None):
    ref_id = parsed["reference_id"]
    safe_ref = re.sub(r'[/:*?"<>|\\]', '_', ref_id)

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
    if ref_id not in stats.sample_reference_ids and len(stats.sample_reference_ids) < 8:
        stats.sample_reference_ids.append(ref_id)
    stats.photos_found += len(imgs)

    if download_photos and imgs and photo_client:
        photo_urls = imgs if PHOTO_LIMIT <= 0 else imgs[:PHOTO_LIMIT]
        for idx, photo_url in enumerate(photo_urls):
            try:
                dr = download_image(photo_url, reference_id=safe_ref, ordering=idx, client=photo_client)
                if dr.status == "downloaded":
                    stats.photos_downloaded += 1
                else:
                    stats.photos_failed += 1
            except Exception:
                stats.photos_failed += 1

        if media_dir.exists():
            stored_files = sorted(p for p in media_dir.iterdir() if p.is_file())
            parsed["local_image_files"] = [str(path.relative_to(REPO)) for path in stored_files]
            parsed["local_image_storage_keys"] = [f"{safe_ref}/{path.name}" for path in stored_files]

    (listing_dir / f"{safe_ref}.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (raw_dir / f"{safe_ref}.html").write_text(html, encoding="utf-8")


# ──────────────────────────────────────────────────────────────
# Source-specific scrapers
# ──────────────────────────────────────────────────────────────

def _scrape_homes_bg(stats: ScrapeStats, client: httpx.Client, max_pages: int, max_listings: int,
                     download_photos: bool, photo_client: httpx.Client | None):
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

    for intent_label, offer_type, city in search_types:
        for page in range(1, max_pages + 1):
            if len(all_urls) >= max_listings:
                break
            api_url = f"https://www.homes.bg/api/offers?currPage={page}&lang=bg&offerType={offer_type}"
            if city:
                api_url += f"&city={city}"
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
            logger.info("[homes_bg] API page %d (%s): %d items, total: %d", page, intent_label, len(results), len(all_urls))
            time.sleep(DELAY * 0.5)

    stats.listing_urls_discovered = len(all_urls)
    logger.info("[homes_bg] Discovery: %d unique URLs from %d API pages", len(all_urls), stats.discovery_pages_fetched)

    for i, url in enumerate(all_urls[:max_listings]):
        if i > 0 and i % 25 == 0:
            logger.info("[homes_bg] Progress: %d/%d fetched (%d parsed)", i, len(all_urls), stats.listing_pages_parsed)
        time.sleep(DELAY)
        html = fetch_page(client, url)
        if not html:
            stats.listing_pages_failed += 1
            continue
        stats.listing_pages_fetched += 1
        parsed = parse_homes_detail(html, url)
        if parsed:
            _save_listing(
                stats,
                parsed,
                html,
                "homes_bg",
                download_photos=download_photos,
                photo_client=photo_client,
                product_label=f"{parsed.get('listing_intent', 'unknown')}:{parsed.get('property_category', 'unknown')}",
            )
        else:
            stats.listing_pages_failed += 1


def _scrape_imot_bg(stats: ScrapeStats, client: httpx.Client, max_pages: int, max_listings: int,
                    download_photos: bool, photo_client: httpx.Client | None):
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
    obiava_re = re.compile(r'href="(//www\.imot\.bg/obiava-[^"]+)"')

    for search_url in search_urls:
        for page in range(1, max_pages + 1):
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
                    new_count += 1
            logger.info("[imot_bg] %s p%d: %d URLs (%d new), total: %d", search_url.split("/")[-1], page, len(matches), new_count, len(all_urls))
            if not new_count:
                break
            time.sleep(DELAY)

    stats.listing_urls_discovered = len(all_urls)
    logger.info("[imot_bg] Discovery: %d unique URLs", len(all_urls))

    for i, url in enumerate(all_urls[:max_listings]):
        if i > 0 and i % 25 == 0:
            logger.info("[imot_bg] Progress: %d/%d", i, stats.listing_pages_parsed)
        time.sleep(DELAY)
        html = fetch_page(client, url)
        if not html:
            stats.listing_pages_failed += 1
            continue
        stats.listing_pages_fetched += 1
        parsed = parse_imot_detail(html, url)
        if parsed:
            _save_listing(
                stats,
                parsed,
                html,
                "imot_bg",
                download_photos=download_photos,
                photo_client=photo_client,
                product_label=f"{parsed.get('listing_intent', 'unknown')}:{parsed.get('property_category', 'unknown')}",
            )
        else:
            stats.listing_pages_failed += 1


def _scrape_generic_html(stats: ScrapeStats, client: httpx.Client, source_key: str, source_name: str,
                         search_urls: list[str], listing_pattern: re.Pattern, base_url: str,
                         max_pages: int, max_listings: int, download_photos: bool, photo_client: httpx.Client | None,
                         *, page_suffix: str = "?page={}", buckets: list[dict[str, Any]] | None = None):
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
            for page in range(1, max_pages + 1):
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
                    href = a["href"]
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

    for i, url in enumerate(all_urls[:max_listings]):
        if i > 0 and i % 25 == 0:
            logger.info("[%s] Progress: %d/%d parsed", source_key, stats.listing_pages_parsed, i)
        time.sleep(DELAY)
        html = fetch_page(client, url)
        if not html:
            stats.listing_pages_failed += 1
            continue
        stats.listing_pages_fetched += 1
        parsed = parse_listing_html(html, url, source_name)
        if parsed:
            _save_listing(
                stats,
                parsed,
                html,
                source_key,
                download_photos=download_photos,
                photo_client=photo_client,
                product_label=url_to_bucket.get(url),
            )
        else:
            stats.listing_pages_failed += 1


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
                "search_urls": ["https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/"],
            },
            {
                "label": "sale_houses",
                "search_urls": ["https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/"],
            },
            {
                "label": "sale_land",
                "search_urls": [
                    "https://www.alo.bg/obiavi/imoti-prodajbi/parzeli-za-zastroiavane-investicionni-proekti/",
                    "https://www.alo.bg/obiavi/imoti-prodajbi/zemedelska-zemia-gradini-lozia-gora/",
                ],
            },
            {
                "label": "rent_apartments",
                "search_urls": ["https://www.alo.bg/obiavi/imoti-naemi/apartamenti-stai/"],
            },
        ],
        "listing_pattern": re.compile(r"alo\.bg/.+-\d{5,}(?:[/?#].*)?$"),
        "page_suffix": "?page={}",
    },
    "address_bg": {
        "name": "Address.bg", "func": "generic",
        "base_url": "https://address.bg",
        "search_urls": [
            "https://address.bg/sale",
            "https://address.bg/rent",
            "https://address.bg/sale/sofia/l4451",
            "https://address.bg/sale/varna/l4694",
            "https://address.bg/rent/sofia/l4451",
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
            "https://www.domaza.bg/property/index/search/1/s/572da6146f10beb4bf6333d75039731a4d2b9902",
            "https://www.domaza.bg/property/index/search/1/s/c8a3ad4db8f37d4e8b31fe9db66bc4d1f537ba5a",
            "https://www.domaza.bg/property/index/search/1/s/e8780bcda8fa201940f1ce87e404f870d0c5c3fc",
        ],
        "listing_pattern": re.compile(r"domaza\.(bg|biz)/.+ID\d+"),
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
            "https://home2u.bg/nedvizhimi-imoti-sofia/",
            "https://home2u.bg/nedvizhimi-imoti-varna/",
            "https://home2u.bg/nedvizhimi-imoti-burgas/",
            "https://home2u.bg/nedvizhimi-imoti-plovdiv/",
            "https://home2u.bg/apartamenti-pod-naem-sofia/",
            "https://home2u.bg/apartamenti-pod-naem-varna/",
        ],
        "listing_pattern": re.compile(r"home2u\.bg/.+-[a-z0-9]{5,}"),
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
                  max_pages: int = 12, max_listings: int = 500) -> ScrapeStats:
    cfg = SOURCE_CONFIGS[key]
    stats = ScrapeStats(source_key=key, source_name=cfg["name"])
    stats.start_time = datetime.now(tz=timezone.utc).isoformat()
    t0 = time.time()

    client = make_client()
    photo_client = make_client() if download_photos else None

    logger.info("=== Starting scrape: %s ===", cfg["name"])

    try:
        func_name = cfg["func"]
        if func_name == "_scrape_homes_bg":
            _scrape_homes_bg(stats, client, max_pages, max_listings, download_photos, photo_client)
        elif func_name == "_scrape_imot_bg":
            _scrape_imot_bg(stats, client, max_pages, max_listings, download_photos, photo_client)
        elif func_name == "generic":
            _scrape_generic_html(
                stats, client, key, cfg["name"],
                cfg.get("search_urls", []), cfg["listing_pattern"], cfg["base_url"],
                max_pages, max_listings, download_photos, photo_client,
                page_suffix=cfg.get("page_suffix", "?page={}"),
                buckets=cfg.get("buckets"),
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
    (stats_dir / "scrape_stats.json").write_text(json.dumps(asdict(stats), ensure_ascii=False, indent=2), encoding="utf-8")

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
        "per_source": [asdict(s) for s in all_stats],
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
