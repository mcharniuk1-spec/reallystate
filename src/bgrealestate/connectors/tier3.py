from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from ..models import RawCapture, SourceRegistryEntry
from ..source_registry import SourceRegistry
from .legal import assert_live_http_allowed
from .protocol import Connector, DiscoveryResult

log = logging.getLogger(__name__)

PARTNER_PARSER_VERSION = "tier3_partner_template_v1"
LICENSED_PARSER_VERSION = "tier3_licensed_template_v1"
OFFICIAL_REGISTER_PARSER_VERSION = "tier3_official_register_template_v1"
BCPEA_PARSER_VERSION = "tier3_public_auction_template_v1"
BCPEA_LIVE_PARSER_VERSION = "bcpea_live_v1"

BCPEA_BASE_URL = "https://sales.bcpea.org"
BCPEA_DEFAULT_PERPAGE = 36
BCPEA_DEFAULT_RATE_LIMIT = 1.5

DATE_RANGE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})")
BG_DATE_RE = re.compile(r"от\s+(\d{2}\.\d{2}\.\d{4})\s+до\s+(\d{2}\.\d{2}\.\d{4})")
BG_PRICE_RE = re.compile(r"([\d\s]+(?:[.,]\d+)?)\s*(EUR|лв\.?)", re.IGNORECASE)


class PartnerContractRequired(RuntimeError):
    """Raised when partner-feed source is used without an active contract."""


class OperatorConsentRequired(RuntimeError):
    """Raised when consent/manual source is queried without explicit operator approval."""


@dataclass(frozen=True)
class StrMarketMetrics:
    source_name: str
    market: str
    period: str
    occupancy_rate: float | None
    adr_eur: float | None
    revpar_eur: float | None
    active_listings: int | None
    parser_version: str = LICENSED_PARSER_VERSION


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _source_entry(registry: SourceRegistry, source_name: str) -> SourceRegistryEntry:
    source = registry.by_name(source_name)
    if not source:
        raise RuntimeError(f"source not found in registry: {source_name}")
    return source


class PartnerFeedStubConnector(Connector):
    """Fixture-first connector for partner-feed sources until contracts are active."""

    def __init__(
        self,
        source_name: str,
        registry: SourceRegistry,
        *,
        contract_id: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.source_name = source_name
        self._registry = registry
        self._contract_id = contract_id
        self._client = client

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        return DiscoveryResult(urls=[], next_cursor=cursor, discovered_at=_utc_now())

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        _ = fetched_at
        if not self._contract_id:
            raise PartnerContractRequired(
                f"{self.source_name} requires an active partner contract before live feed access."
            )
        source = _source_entry(self._registry, self.source_name)
        # Even with contract present, generic web crawling is not permitted for partner-only sources.
        assert_live_http_allowed(source)
        raise PartnerContractRequired(
            f"{self.source_name} live partner feed not configured; use official contract feed client."
        )

    def parse_partner_payload(self, *, json_text: str) -> dict[str, Any]:
        payload = json.loads(json_text)
        listing = payload.get("listing") or {}
        external_id = str(listing.get("external_id", ""))
        lat = (listing.get("coordinates") or {}).get("lat")
        lon = (listing.get("coordinates") or {}).get("lon")
        nightly = listing.get("nightly_price") or {}
        return {
            "source_name": self.source_name,
            "external_id": external_id,
            "reference_id": f"{self.source_name}:{external_id}" if external_id else None,
            "listing_intent": "short_term_rent",
            "property_category": "apartment",
            "city": listing.get("city"),
            "price": float(nightly["amount"]) if nightly.get("amount") is not None else None,
            "currency": nightly.get("currency"),
            "latitude": lat,
            "longitude": lon,
            "listing_url": listing.get("url"),
            "image_urls": listing.get("images") or [],
            "parser_version": PARTNER_PARSER_VERSION,
        }


class LicensedStrDataConnector:
    """Parser for licensed STR analytics payloads (fixture-first)."""

    def __init__(self, source_name: str, registry: SourceRegistry) -> None:
        self.source_name = source_name
        self._registry = registry

    def parse_metrics_payload(self, *, json_text: str) -> StrMarketMetrics:
        _ = _source_entry(self._registry, self.source_name)
        payload = json.loads(json_text)
        metrics = payload.get("metrics") or {}
        return StrMarketMetrics(
            source_name=self.source_name,
            market=str(payload.get("market", "")),
            period=str(payload.get("period", "")),
            occupancy_rate=float(metrics["occupancy_rate"]) if metrics.get("occupancy_rate") is not None else None,
            adr_eur=float(metrics["adr_eur"]) if metrics.get("adr_eur") is not None else None,
            revpar_eur=float(metrics["revpar_eur"]) if metrics.get("revpar_eur") is not None else None,
            active_listings=int(metrics["active_listings"]) if metrics.get("active_listings") is not None else None,
        )

    @staticmethod
    def metrics_to_dict(metrics: StrMarketMetrics) -> dict[str, Any]:
        return {
            "source_name": metrics.source_name,
            "dataset_type": "short_term_rent_metrics",
            "market": metrics.market,
            "period": metrics.period,
            "metrics": {
                "occupancy_rate": metrics.occupancy_rate,
                "adr_eur": metrics.adr_eur,
                "revpar_eur": metrics.revpar_eur,
                "active_listings": metrics.active_listings,
            },
            "parser_version": metrics.parser_version,
        }


class OfficialRegisterWrapper:
    """Manual/consent wrapper for Property Register and KAIS flows."""

    def __init__(self, source_name: str, registry: SourceRegistry, *, operator_approval_id: str | None = None) -> None:
        self.source_name = source_name
        self._registry = registry
        self._operator_approval_id = operator_approval_id

    def query_live(self, *, query: dict[str, Any]) -> dict[str, Any]:
        _ = query
        if not self._operator_approval_id:
            raise OperatorConsentRequired(
                f"{self.source_name} requires explicit operator approval for live official-service queries."
            )
        raise OperatorConsentRequired(
            f"{self.source_name} live wrapper requires operator-driven workflow and is not auto-enabled."
        )

    def parse_official_response(self, *, json_text: str) -> dict[str, Any]:
        payload = json.loads(json_text)
        query = payload.get("query") or {}
        response = payload.get("response") or {}
        reference_id = query.get("parcel_or_property_id")
        verification_type = "parcel_validation" if self.source_name == "KAIS Cadastre" else "ownership_verification"
        return {
            "source_name": self.source_name,
            "verification_type": verification_type,
            "reference_id": f"{self.source_name}:{reference_id}" if reference_id else None,
            "query_status": response.get("status"),
            "encumbrance_flag": bool(response.get("encumbrance_flag", False)),
            "consent_mode": "operator_approved" if payload.get("operator_approval_id") else "manual_only",
            "parser_version": OFFICIAL_REGISTER_PARSER_VERSION,
        }


@dataclass(frozen=True)
class BcpeaDiscoveryItem:
    external_id: str
    url: str
    property_type: str | None
    area_sqm: float | None
    price: float | None
    currency: str | None
    city: str | None
    address: str | None
    court: str | None
    bailiff: str | None
    auction_start_date: str | None
    auction_end_date: str | None
    announcement_date: str | None
    has_image: bool


@dataclass(frozen=True)
class BcpeaDiscoveryPage:
    total_results: int | None
    listings: list[BcpeaDiscoveryItem]
    next_page: int | None
    last_page: int | None


def _parse_bg_price(text: str | None) -> tuple[float | None, str | None]:
    if not text:
        return None, None
    cleaned = text.replace("\xa0", " ").replace("&nbsp;", " ")
    m = BG_PRICE_RE.search(cleaned)
    if not m:
        return None, None
    raw_num = m.group(1).replace(" ", "").replace(",", ".")
    currency = "EUR" if "EUR" in m.group(2).upper() else "BGN"
    try:
        return float(raw_num), currency
    except ValueError:
        return None, currency


def _parse_bg_area(text: str | None) -> float | None:
    if not text:
        return None
    cleaned = text.replace("\xa0", " ").replace("&nbsp;", " ")
    m = re.search(r"([\d\s]+(?:[.,]\d+)?)\s*кв\.?\s*м", cleaned)
    if not m:
        return None
    raw = m.group(1).replace(" ", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _bg_date_to_iso(dd_mm_yyyy: str) -> str | None:
    try:
        parts = dd_mm_yyyy.strip().split(".")
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    except (IndexError, ValueError):
        return None


def _bg_datetime_to_iso(raw: str) -> str | None:
    raw = raw.strip()
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})", raw)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}T{m.group(4)}"
    return None


def parse_bcpea_discovery_html(html: str) -> BcpeaDiscoveryPage:
    """Parse a BCPEA /properties listing page into structured discovery items."""
    total_m = re.search(r"от\s+\d+\s+до\s+<b>(\d+)</b>\s+от\s+<b>(\d+)</b>", html)
    if not total_m:
        total_m = re.search(r"до\s+<b>\d+</b>.*?<b>(\d+)</b>", html)
    total_results = int(total_m.group(2)) if total_m and total_m.lastindex and total_m.lastindex >= 2 else None

    items: list[BcpeaDiscoveryItem] = []
    group_starts = [m.start() for m in re.finditer(r'<div class="item__group">', html)]
    for idx, start in enumerate(group_starts):
        end = group_starts[idx + 1] if idx + 1 < len(group_starts) else len(html)
        block = html[start:end]

        prop_type = _tag_text(r'<div class="title">([^<]+)</div>', block)
        area_text = _tag_text(r'<div class="category">([^<]+)</div>', block)
        area_sqm = _parse_bg_area(area_text)

        price_text = _tag_text(r'<div class="price">([^<]+)</div>', block)
        price, currency = _parse_bg_price(price_text)

        city = _label_info("НАСЕЛЕНО МЯСТО", block)
        address = _label_info("Адрес", block)
        court = _label_info("ОКРЪЖЕН СЪД", block)
        bailiff = _label_info("ЧАСТЕН СЪДЕБЕН ИЗПЪЛНИТЕЛ", block)

        term_text = _label_info("СРОК", block) or ""
        date_m = BG_DATE_RE.search(term_text)
        start_date = date_m.group(1) if date_m else None
        end_date = date_m.group(2) if date_m else None

        announce = _label_info("ОБЯВЯВАНЕ НА", block)

        link_m = re.search(r'href="(/properties/(\d+))"', block)
        if not link_m:
            continue
        ext_id = link_m.group(2)
        url = urljoin(BCPEA_BASE_URL, link_m.group(1))

        has_image = "photo-placeholder" not in block and "/upload/" in block

        items.append(BcpeaDiscoveryItem(
            external_id=ext_id,
            url=url,
            property_type=prop_type,
            area_sqm=area_sqm,
            price=price,
            currency=currency,
            city=city,
            address=address,
            court=court,
            bailiff=bailiff,
            auction_start_date=start_date,
            auction_end_date=end_date,
            announcement_date=announce,
            has_image=has_image,
        ))

    next_page, last_page = _parse_bcpea_pagination(html)

    return BcpeaDiscoveryPage(
        total_results=total_results,
        listings=items,
        next_page=next_page,
        last_page=last_page,
    )


def _parse_bcpea_pagination(html: str) -> tuple[int | None, int | None]:
    pag_m = re.search(r'<div class="pagination">(.*?)</div>', html, re.DOTALL)
    if not pag_m:
        return None, None
    pag_html = pag_m.group(1)

    active_m = re.search(r'<li class="active"><a [^>]*>(\d+)</a></li>', pag_html)
    current_page = int(active_m.group(1)) if active_m else 1

    page_nums = [int(x) for x in re.findall(r'&amp;p=(\d+)', pag_html)]
    last_page = max(page_nums) if page_nums else current_page

    next_page = current_page + 1 if current_page < last_page else None
    return next_page, last_page


def parse_bcpea_detail_html(html: str, url: str) -> dict[str, Any]:
    """Parse a BCPEA /properties/<id> detail page."""
    id_m = re.search(r"/properties/(\d+)", url)
    external_id = id_m.group(1) if id_m else None

    expanded_m = re.search(r'<div class="item__expanded">(.*?)(Подобни обяви|</body>)', html, re.DOTALL)
    block = expanded_m.group(1) if expanded_m else html

    person_start = block.find('class="person_info"')
    info_block = block[:person_start] if person_start > 0 else block

    wrapper_m = re.search(
        r'<div class="item__wrapper">.*?<div class="title">([^<]+)</div>',
        html, re.DOTALL | re.IGNORECASE,
    )
    prop_type = wrapper_m.group(1).strip() if wrapper_m else None
    area_text = _label_info("ПЛОЩ", info_block)
    area_sqm = _parse_bg_area(area_text)
    construction = _label_info("ТИП СТРОИТЕЛСТВО", info_block)
    amenities_raw = _label_info("Екстри", info_block)
    amenities = [a.strip() for a in amenities_raw.split(",") if a.strip()] if amenities_raw else []

    city = _label_info("Населено място", info_block) or _label_info("НАСЕЛЕНО МЯСТО", info_block)
    court = _label_info("ОКРЪЖЕН СЪД", info_block)
    bailiff = _label_info("ЧАСТЕН СЪДЕБЕН ИЗПЪЛНИТЕЛ", info_block)

    reg_num = _label_info("РЕГ. № ЧСИ", block)

    term_text = _label_info("СРОК", info_block) or ""
    date_m = BG_DATE_RE.search(term_text)
    start_date = _bg_date_to_iso(date_m.group(1)) if date_m else None
    end_date = _bg_date_to_iso(date_m.group(2)) if date_m else None

    announce_raw = _label_info("ОБЯВЯВАНЕ НА", info_block)
    announce_iso = _bg_datetime_to_iso(announce_raw) if announce_raw else None

    desc_m = re.search(
        r'<div class="label__group label__group-description">.*?<div class="info">(.*?)</div>',
        info_block, re.DOTALL | re.IGNORECASE,
    )
    description = ""
    if desc_m:
        raw_desc = re.sub(r"<[^>]+>", "", desc_m.group(1)).strip()
        description = raw_desc[:500] if raw_desc else ""

    image_urls: list[str] = []
    for img_m in re.finditer(r'<a class="item-image" href="([^"]+)"', block):
        href = img_m.group(1)
        if href.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            image_urls.append(urljoin(BCPEA_BASE_URL, href))

    doc_urls: list[str] = []
    scan_section = re.search(r"Сканирани обявления.*?<ul>(.*?)</ul>", block, re.DOTALL | re.IGNORECASE)
    if scan_section:
        for doc_m in re.finditer(r'href="([^"]+)"', scan_section.group(1)):
            doc_urls.append(urljoin(BCPEA_BASE_URL, doc_m.group(1)))

    phone = _label_info("Телефон", block)
    mobile = _label_info("Мобилен телефон", block)

    return {
        "source_name": "BCPEA property auctions",
        "external_id": external_id,
        "listing_url": url if url.startswith("http") else urljoin(BCPEA_BASE_URL, url),
        "property_type": prop_type,
        "listing_intent": "auction_sale",
        "construction_type": construction,
        "amenities": amenities,
        "area_sqm": area_sqm,
        "city": city,
        "court": court,
        "bailiff": bailiff,
        "bailiff_reg_number": reg_num,
        "auction_start_date": start_date,
        "auction_end_date": end_date,
        "announcement_datetime": announce_iso,
        "description_snippet": description[:200] if description else None,
        "image_urls": image_urls,
        "scanned_documents": doc_urls,
        "bailiff_phone": phone,
        "bailiff_mobile": mobile,
        "parser_version": BCPEA_LIVE_PARSER_VERSION,
    }


def _tag_text(pattern: str, html: str) -> str | None:
    m = re.search(pattern, html, flags=re.IGNORECASE)
    if not m:
        return None
    return m.group(1).replace("&nbsp;", " ").replace("\xa0", " ").strip()


def _label_info(label: str, html: str) -> str | None:
    pattern = (
        r'<div class="label">\s*' + re.escape(label) + r'\s*</div>\s*'
        r'<div class="info">\s*(.*?)\s*</div>'
    )
    m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if not m:
        return None
    raw = re.sub(r"<[^>]+>", "", m.group(1)).replace("&nbsp;", " ").replace("\xa0", " ").strip()
    return raw or None


class BcpeaAuctionConnector(Connector):
    source_name = "BCPEA property auctions"

    def __init__(
        self,
        registry: SourceRegistry,
        *,
        client: Any | None = None,
        perpage: int = BCPEA_DEFAULT_PERPAGE,
        rate_limit: float = BCPEA_DEFAULT_RATE_LIMIT,
    ) -> None:
        self._registry = registry
        self._client = client
        self._perpage = perpage
        self._rate_limit = rate_limit
        self._last_request_at: float = 0.0

    def _entry(self) -> SourceRegistryEntry:
        return _source_entry(self._registry, self.source_name)

    def _ensure_client(self) -> Any:
        if self._client is None:
            import httpx  # type: ignore
            self._client = httpx.Client(
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": "bgrealestate-mvp/0.1 (public auction register crawler)"},
            )
        return self._client

    def _throttle(self) -> None:
        if self._rate_limit <= 0:
            return
        elapsed = time.monotonic() - self._last_request_at
        wait = self._rate_limit - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_at = time.monotonic()

    def _get(self, url: str) -> Any:
        client = self._ensure_client()
        self._throttle()
        resp = client.get(url)
        resp.raise_for_status()
        return resp

    def discover_listing_urls(self, *, cursor: dict[str, Any] | None = None) -> DiscoveryResult:
        source = self._entry()
        assert_live_http_allowed(source)
        page = (cursor or {}).get("page", 1)
        url = f"{BCPEA_BASE_URL}/properties?perpage={self._perpage}&p={page}"
        log.info("BCPEA discovery page=%d url=%s", page, url)
        resp = self._get(url)
        result = parse_bcpea_discovery_html(resp.text)
        urls = [item.url for item in result.listings]
        next_cursor: dict[str, Any] | None = {"page": result.next_page} if result.next_page else None
        return DiscoveryResult(urls=urls, next_cursor=next_cursor, discovered_at=_utc_now())

    def discover_page(self, page: int = 1) -> BcpeaDiscoveryPage:
        """Fetch and parse a single discovery page, returning structured items."""
        source = self._entry()
        assert_live_http_allowed(source)
        url = f"{BCPEA_BASE_URL}/properties?perpage={self._perpage}&p={page}"
        log.info("BCPEA discover_page page=%d", page)
        resp = self._get(url)
        return parse_bcpea_discovery_html(resp.text)

    def discover_page_from_html(self, html: str) -> BcpeaDiscoveryPage:
        """Parse discovery HTML without network access (for fixtures/tests)."""
        return parse_bcpea_discovery_html(html)

    def fetch_listing_detail(self, *, url: str, fetched_at: datetime) -> RawCapture:
        source = self._entry()
        assert_live_http_allowed(source)
        log.info("BCPEA fetch detail url=%s", url)
        resp = self._get(url)
        return RawCapture(
            source_name=source.source_name,
            url=url,
            content_type=resp.headers.get("content-type", "text/html"),
            body=resp.text,
            fetched_at=fetched_at,
            parser_version=BCPEA_LIVE_PARSER_VERSION,
            metadata={"http_status": resp.status_code, "headers": dict(resp.headers)},
        )

    def parse_detail_html(self, *, html: str, url: str) -> dict[str, Any]:
        """Parse a BCPEA detail page into a structured dict."""
        return parse_bcpea_detail_html(html, url)

    def parse_auction_html(self, *, html: str) -> dict[str, Any]:
        """Legacy template parser — kept for backward compat with T3-03 fixtures."""
        ext_id = _tag_text(r'<div class="auction-id">([^<]+)</div>', html)
        price_text = _tag_text(r'<div class="price">([^<]+)</div>', html)
        area_text = _tag_text(r'<div class="area">([^<]+)</div>', html)
        address_text = _tag_text(r'<div class="address">([^<]+)</div>', html)
        court = _tag_text(r'<div class="court">([^<]+)</div>', html)
        bailiff = _tag_text(r'<div class="bailiff">([^<]+)</div>', html)
        dates = _tag_text(r'<div class="dates">([^<]+)</div>', html)
        match = DATE_RANGE_RE.search(dates or "")
        start_date = match.group(1) if match else None
        end_date = match.group(2) if match else None
        city, district = self._split_city_district(address_text)
        return {
            "source_name": self.source_name,
            "external_id": ext_id,
            "listing_intent": "auction_sale",
            "price": self._extract_float(price_text),
            "currency": "EUR" if "EUR" in (price_text or "").upper() else None,
            "area_sqm": self._extract_float(area_text),
            "city": city,
            "district": district,
            "court": court.replace("Court: ", "") if court else None,
            "bailiff": bailiff.replace("Bailiff: ", "") if bailiff else None,
            "auction_start_date": start_date,
            "auction_end_date": end_date,
            "parser_version": BCPEA_PARSER_VERSION,
        }

    @staticmethod
    def _extract_float(text: str | None) -> float | None:
        if not text:
            return None
        m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", "."))
        return float(m.group(1)) if m else None

    @staticmethod
    def _split_city_district(address_text: str | None) -> tuple[str | None, str | None]:
        if not address_text:
            return None, None
        cleaned = address_text.replace("Address:", "").strip()
        parts = [part.strip() for part in cleaned.split(",") if part.strip()]
        if len(parts) >= 2:
            return parts[0], parts[1]
        return (parts[0], None) if parts else (None, None)
