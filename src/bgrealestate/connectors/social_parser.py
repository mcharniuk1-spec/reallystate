"""Minimal regex-based NLP extractor for social overlay messages (Telegram, etc.).

This is intentionally lightweight — production enrichment will use LLM pipelines.
The parser must never access the network; it operates on pre-redacted text only.
"""

from __future__ import annotations

import re
from typing import Any

_SALE_KW = re.compile(r"продава[мш]?|продажба|for\s+sale", re.IGNORECASE)
_RENT_KW = re.compile(r"отдава[мш]?|наем|под\s+наем|for\s+rent", re.IGNORECASE)

_APARTMENT_KW = re.compile(
    r"апартамент|студио|едностаен|двустаен|тристаен|многостаен|apartment|studio",
    re.IGNORECASE,
)
_HOUSE_KW = re.compile(r"къща|вила|house|villa", re.IGNORECASE)
_LAND_KW = re.compile(r"парцел|земя|земеделска|land|plot", re.IGNORECASE)

_PRICE_RE = re.compile(r"(\d[\d\s]*\d)\s*(EUR|BGN|лв\.?|€|\$)", re.IGNORECASE)

_CITY_PATTERNS: list[tuple[str, str]] = [
    ("Варна", "Варна"),
    ("Varna", "Варна"),
    ("София", "София"),
    ("Sofia", "София"),
    ("Бургас", "Бургас"),
    ("Burgas", "Бургас"),
    ("Пловдив", "Пловдив"),
    ("Plovdiv", "Пловдив"),
]

_DISTRICT_RE = re.compile(
    r"(?:кв\.|квартал|район|ж\.?к\.?)\s*([А-Яа-яA-Za-z\s\-]+)",
    re.IGNORECASE,
)


def extract_social_lead(raw: dict[str, Any]) -> dict[str, Any]:
    """Parse a social overlay fixture/message and return structured lead fields."""
    text = raw.get("raw_text", "")

    intent = None
    if _SALE_KW.search(text):
        intent = "sale"
    elif _RENT_KW.search(text):
        intent = "long_term_rent"

    prop_type = None
    if _APARTMENT_KW.search(text):
        prop_type = "apartment"
    elif _HOUSE_KW.search(text):
        prop_type = "house"
    elif _LAND_KW.search(text):
        prop_type = "land"

    price = None
    currency = None
    price_m = _PRICE_RE.search(text)
    if price_m:
        digits = price_m.group(1).replace(" ", "")
        price = int(digits)
        cur = price_m.group(2).upper()
        if cur in ("ЛВ", "ЛВ.", "BGN"):
            currency = "BGN"
        elif cur in ("EUR", "€"):
            currency = "EUR"
        elif cur == "$":
            currency = "USD"
        else:
            currency = cur

    city = None
    for needle, canonical in _CITY_PATTERNS:
        if needle in text:
            city = canonical
            break

    district = None
    dist_m = _DISTRICT_RE.search(text)
    if dist_m:
        district = dist_m.group(1).strip()
    elif city:
        for known in ("Чайка", "Бриз", "Лозенец", "Младост", "Каменица", "Сарафово", "Левски"):
            if known in text:
                district = known
                break

    is_noise = intent is None and prop_type is None and price is None

    return {
        "intent": intent,
        "property_type": prop_type,
        "city": city,
        "district": district,
        "price": price,
        "currency": currency,
        "phones": [],
        "is_noise": is_noise,
    }
