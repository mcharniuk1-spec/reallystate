from __future__ import annotations

import unittest
from pathlib import Path

from scripts.live_scraper import parse_listing_html


REPO = Path(__file__).resolve().parents[1]


class TestLiveScraperSourceParsers(unittest.TestCase):
    def _parse(self, source_name: str, raw_path: str, url: str) -> dict:
        html = (REPO / raw_path).read_text(encoding="utf-8", errors="ignore")
        parsed = parse_listing_html(html, url, source_name)
        self.assertIsNotNone(parsed, source_name)
        return parsed or {}

    def test_address_bg_parser_extracts_core_fields(self) -> None:
        parsed = self._parse(
            "Address.bg",
            "data/scraped/address_bg/raw/Address.bg_45556d0cad2d.html",
            "https://address.bg/sofia-bistrica-parcel-teren-offer626861",
        )
        self.assertEqual(parsed["price"], 425000.0)
        self.assertEqual(parsed["city"], "София")
        self.assertEqual(parsed["district"], "Бистрица")
        self.assertEqual(parsed["area_sqm"], 1000.0)
        self.assertGreater(len(parsed["phones"]), 0)

    def test_bulgarianproperties_parser_extracts_gallery_and_rooms(self) -> None:
        parsed = self._parse(
            "BulgarianProperties",
            "data/scraped/bulgarianproperties/raw/BulgarianProperties_ec4b0ae64e6c.html",
            "https://www.bulgarianproperties.com/1-bedroom_apartments_in_Bulgaria/AD86759BG_1-bedroom_apartment_for_sale_in_Sozopol.html",
        )
        self.assertEqual(parsed["price"], 120000.0)
        self.assertEqual(parsed["city"], "Sozopol")
        self.assertEqual(parsed["rooms"], 2.0)
        self.assertGreaterEqual(len(parsed["image_urls"]), 10)
        self.assertTrue(all("/big/" in url for url in parsed["image_urls"]))
        self.assertGreater(len(parsed["phones"]), 0)

    def test_luximmo_parser_extracts_city_rooms_and_gallery(self) -> None:
        parsed = self._parse(
            "LUXIMMO",
            "data/scraped/luximmo/raw/LUXIMMO_0c9fd22cfdbb.html",
            "https://www.luximmo.bg/bulgaria/oblast-sofia/borovets/luksozni-imoti-dvustayni-apartamenti/luksozen-imot-40091-dvustaen-apartament-za-prodajba-v-borovets.html",
        )
        self.assertEqual(parsed["city"], "Боровец")
        self.assertEqual(parsed["rooms"], 2.0)
        self.assertGreater(parsed["area_sqm"], 60.0)
        self.assertGreaterEqual(len(parsed["image_urls"]), 20)

    def test_olx_parser_extracts_area_rooms_and_location(self) -> None:
        parsed = self._parse(
            "OLX.bg",
            "data/scraped/olx_bg/raw/OLX.bg_147540772.html",
            "https://www.olx.bg/d/ad/dvustaen-ap-pod-naem-v-kv-lyulin-5-CID368-ID9Z45S.html",
        )
        self.assertEqual(parsed["city"], "София")
        self.assertEqual(parsed["district"], "Люлин 5")
        self.assertEqual(parsed["rooms"], 2.0)
        self.assertEqual(parsed["area_sqm"], 50.0)

    def test_property_bg_parser_extracts_price_and_gallery(self) -> None:
        parsed = self._parse(
            "property.bg",
            "data/scraped/property_bg/raw/property.bg_c6be6a6838ca.html",
            "https://www.property.bg/property-117962-two-room-maisonette-quotturnkeyquot-in-the-luxury-complex-7-angels/",
        )
        self.assertEqual(parsed["price"], 235600.0)
        self.assertEqual(parsed["city"], "Borovets")
        self.assertEqual(parsed["rooms"], 2.0)
        self.assertGreaterEqual(len(parsed["image_urls"]), 20)

    def test_suprimmo_parser_extracts_price_and_district(self) -> None:
        parsed = self._parse(
            "SUPRIMMO",
            "data/scraped/suprimmo/raw/SUPRIMMO_STO-132154.html",
            "https://www.suprimmo.bg/imot-132154-yujen-dvustaen-apartament-s-otdelna-kuhnya-v-spokoen-i-zelen-rayon/",
        )
        self.assertEqual(parsed["price"], 175000.0)
        self.assertEqual(parsed["city"], "София")
        self.assertEqual(parsed["district"], "Сухата река")
        self.assertEqual(parsed["rooms"], 2.0)
        self.assertGreaterEqual(len(parsed["image_urls"]), 20)

    def test_bazar_parser_extracts_location_area_and_rooms(self) -> None:
        parsed = self._parse(
            "Bazar.bg",
            "data/scraped/bazar_bg/raw/Bazar.bg_53706749.html",
            "https://bazar.bg/obiava-53706749/prodava-4-staen-gr-sofiya-krastova-vada",
        )
        self.assertEqual(parsed["city"], "София")
        self.assertEqual(parsed["district"], "Кръстова вада")
        self.assertEqual(parsed["rooms"], 4.0)
        self.assertEqual(parsed["area_sqm"], 167.0)

    def test_yavlena_parser_extracts_payload_details_and_gallery(self) -> None:
        parsed = self._parse(
            "Yavlena",
            "data/scraped/yavlena/raw/Yavlena_acbef70866cf.html",
            "https://www.yavlena.com/168366",
        )
        self.assertEqual(parsed["city"], "София")
        self.assertEqual(parsed["district"], "Надежда")
        self.assertEqual(parsed["rooms"], 3.0)
        self.assertEqual(parsed["area_sqm"], 124.0)
        self.assertEqual(len(parsed["image_urls"]), 1)
        self.assertEqual(parsed["phones"], ["+359 892 538 721", "+359 888 109 040"])
        self.assertGreater(len(parsed["description"]), 100)


if __name__ == "__main__":
    unittest.main()
