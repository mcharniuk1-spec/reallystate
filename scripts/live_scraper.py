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


def make_client() -> httpx.Client:
    return httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers=HEADERS,
                        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2))


def fetch_page(client: httpx.Client, url: str, *, retries: int = 2) -> str | None:
    for attempt in range(retries + 1):
        try:
            resp = client.get(url)
            if resp.status_code == 200:
                return resp.text
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

    for block_text in _JSON_LD_RE.findall(html):
        try:
            ld = json.loads(block_text.strip())
            items = ld if isinstance(ld, list) else [ld]
            for item in items:
                if isinstance(item, dict):
                    _apply_json_ld(item, result)
        except (json.JSONDecodeError, ValueError):
            pass

    _extract_meta(soup, result)
    if not result["title"]:
        t = soup.find("title")
        if t:
            result["title"] = t.get_text(strip=True)
    if not result["image_urls"]:
        _extract_images(soup, result)
    if result["price"] is None:
        _extract_price_html(soup, result)

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
                try:
                    r["price"] = float(m.group(1).replace(" ", "").replace(",", ""))
                    cmap = {"€": "EUR", "лв": "BGN", "лв.": "BGN", "$": "USD"}
                    r["currency"] = cmap.get(m.group(2).strip(), m.group(2).strip().upper())
                    return
                except ValueError:
                    pass


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
    errors: list[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    duration_seconds: float = 0.0


def _save_listing(stats: ScrapeStats, parsed: dict, html: str, source_key: str,
                  *, download_photos: bool = False, photo_client: httpx.Client | None = None):
    ref_id = parsed["reference_id"]
    safe_ref = re.sub(r'[/:*?"<>|\\]', '_', ref_id)

    listing_dir = SCRAPED_ROOT / source_key / "listings"
    raw_dir = SCRAPED_ROOT / source_key / "raw"
    listing_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    (listing_dir / f"{safe_ref}.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (raw_dir / f"{safe_ref}.html").write_text(html, encoding="utf-8")

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

    imgs = parsed.get("image_urls", [])
    # Normalize protocol-relative URLs
    imgs = [("https:" + u if u.startswith("//") else u) for u in imgs]
    parsed["image_urls"] = imgs
    stats.photos_found += len(imgs)

    if download_photos and imgs and photo_client:
        for idx, photo_url in enumerate(imgs[:15]):
            try:
                dr = download_image(photo_url, reference_id=safe_ref, ordering=idx, client=photo_client)
                if dr.status == "downloaded":
                    stats.photos_downloaded += 1
                else:
                    stats.photos_failed += 1
            except Exception:
                stats.photos_failed += 1


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
        parsed = parse_listing_html(html, url, "Homes.bg")
        if parsed:
            _save_listing(stats, parsed, html, "homes_bg", download_photos=download_photos, photo_client=photo_client)
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
        parsed = parse_listing_html(html, url, "imot.bg")
        if parsed:
            _save_listing(stats, parsed, html, "imot_bg", download_photos=download_photos, photo_client=photo_client)
        else:
            stats.listing_pages_failed += 1


def _scrape_generic_html(stats: ScrapeStats, client: httpx.Client, source_key: str, source_name: str,
                         search_urls: list[str], listing_pattern: re.Pattern, base_url: str,
                         max_pages: int, max_listings: int, download_photos: bool, photo_client: httpx.Client | None,
                         *, page_suffix: str = "?page={}"):
    """Generic HTML scraper for sources with standard pagination."""
    all_urls: list[str] = []
    seen: set[str] = set()

    for search_url in search_urls:
        for page in range(1, max_pages + 1):
            if len(all_urls) >= max_listings:
                break
            if page == 1:
                paged = search_url
            elif "{}" in page_suffix:
                paged = search_url + page_suffix.format(page)
            else:
                paged = search_url + page_suffix + str(page)

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
                    new_count += 1
            logger.info("[%s] %s p%d: %d new URLs, total: %d", source_key, search_url.split("/")[-1][:30], page, new_count, len(all_urls))
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
            _save_listing(stats, parsed, html, source_key, download_photos=download_photos, photo_client=photo_client)
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
        "search_urls": [
            "https://www.alo.bg/obiavi/imoti-prodajbi/",
            "https://www.alo.bg/obiavi/imoti-naemi/",
            "https://www.alo.bg/obiavi/imoti-prodajbi/apartamenti-stai/",
            "https://www.alo.bg/obiavi/imoti-prodajbi/kashti-vili/",
        ],
        "listing_pattern": re.compile(r"alo\.bg/obiavi/\d{5,}"),
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
        "listing_pattern": re.compile(r"address\.bg/.+/p\d{4,}"),
        "page_suffix": "?page={}",
    },
    "bulgarianproperties": {
        "name": "BulgarianProperties", "func": "generic",
        "base_url": "https://www.bulgarianproperties.com",
        "search_urls": [
            "https://www.bulgarianproperties.com/properties_for_sale_in_Bulgaria/index.html",
            "https://www.bulgarianproperties.com/properties_for_rent_in_Bulgaria/index.html",
            "https://www.bulgarianproperties.com/land_for_sale_in_Bulgaria/index.html",
            "https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/index.html",
            "https://www.bulgarianproperties.com/2-bedroom_apartments_in_Bulgaria/index.html",
            "https://www.bulgarianproperties.com/3-bedroom_apartments_in_Bulgaria/index.html",
            "https://www.bulgarianproperties.com/houses_in_Bulgaria/index.html",
        ],
        "listing_pattern": re.compile(r"bulgarianproperties\.com/.+AD\d+BG"),
        "page_suffix": "?page={}",
    },
    "suprimmo": {
        "name": "SUPRIMMO", "func": "generic",
        "base_url": "https://www.suprimmo.bg",
        "search_urls": [
            "https://www.suprimmo.bg/",
            "https://www.suprimmo.bg/bulgaria/imoti-na-moreto/",
            "https://www.suprimmo.bg/bulgaria/imoti-v-morski-kurort/",
            "https://www.suprimmo.bg/bulgaria/imoti-v-planinata/",
        ],
        "listing_pattern": re.compile(r"suprimmo\.bg/.+/\d{4,}"),
        "page_suffix": "?page={}",
    },
    "luximmo": {
        "name": "LUXIMMO", "func": "generic",
        "base_url": "https://www.luximmo.bg",
        "search_urls": [
            "https://www.luximmo.bg/",
        ],
        "listing_pattern": re.compile(r"luximmo\.bg/.+/\d{4,}"),
        "page_suffix": "?page={}",
    },
    "property_bg": {
        "name": "property.bg", "func": "generic",
        "base_url": "https://www.property.bg",
        "search_urls": [
            "https://www.property.bg/bg/",
            "https://www.property.bg/",
        ],
        "listing_pattern": re.compile(r"property\.bg/.+/\d{4,}"),
        "page_suffix": "?page={}",
    },
    "bazar_bg": {
        "name": "Bazar.bg", "func": "generic",
        "base_url": "https://bazar.bg",
        "search_urls": [
            "https://bazar.bg/obiavi/apartamenti",
            "https://bazar.bg/obiavi/kashti-i-vili",
            "https://bazar.bg/obiavi/zemya",
            "https://bazar.bg/obiavi/garazhi-i-parkoingi",
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
        "search_urls": [
            "https://www.yavlena.com/bg/sales",
            "https://www.yavlena.com/bg/rentals",
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
        "search_urls": [
            "https://www.olx.bg/nedvizhimi-imoti/",
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
                cfg["search_urls"], cfg["listing_pattern"], cfg["base_url"],
                max_pages, max_listings, download_photos, photo_client,
                page_suffix=cfg.get("page_suffix", "?page={}"),
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
        print(f"  Duration: {s.duration_seconds:.1f}s")
    print(f"\nTOTAL: {combined['total_discovered']} discovered, {combined['total_parsed']} parsed, {combined['total_photos_found']} photos")


if __name__ == "__main__":
    main()
