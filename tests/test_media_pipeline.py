"""Tests for the image download, storage, and proxy pipeline."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))


class TestImageDownloadService(unittest.TestCase):
    """Test services.media download and storage utilities."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="media_test_")
        os.environ["MEDIA_STORAGE_PATH"] = self.tmpdir
        import bgrealestate.services.media as media_mod
        media_mod.MEDIA_ROOT = Path(self.tmpdir)
        self.media_mod = media_mod

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_download_image_success(self):
        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        mock_response = MagicMock()
        mock_response.content = fake_jpeg
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        result = self.media_mod.download_image(
            "https://example.com/photo1.jpg",
            reference_id="test-ref-001",
            ordering=0,
            client=mock_client,
        )

        self.assertEqual(result.status, "downloaded")
        self.assertTrue(result.storage_key.startswith("test-ref-001/"))
        self.assertTrue(result.storage_key.endswith(".jpg"))
        self.assertGreater(result.file_size, 0)
        self.assertEqual(result.mime_type, "image/jpeg")
        self.assertIsNotNone(result.content_hash)
        self.assertIsNotNone(result.local_path)
        self.assertTrue(result.local_path.exists())

    def test_download_image_http_error(self):
        import httpx
        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock(status_code=404)
        )

        result = self.media_mod.download_image(
            "https://example.com/missing.jpg",
            reference_id="test-ref-002",
            client=mock_client,
        )
        self.assertEqual(result.status, "failed")
        self.assertIn("HTTP error", result.error)

    def test_download_image_unsupported_content_type(self):
        mock_response = MagicMock()
        mock_response.content = b"<html>Not an image</html>"
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        result = self.media_mod.download_image(
            "https://example.com/page.html",
            reference_id="test-ref-003",
            client=mock_client,
        )
        self.assertEqual(result.status, "failed")
        self.assertIn("Unsupported content type", result.error)

    def test_download_image_empty_body(self):
        mock_response = MagicMock()
        mock_response.content = b""
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response

        result = self.media_mod.download_image(
            "https://example.com/empty.jpg",
            reference_id="test-ref-004",
            client=mock_client,
        )
        self.assertEqual(result.status, "failed")
        self.assertIn("Empty", result.error)

    def test_download_listing_images_multiple(self):
        fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        mock_response = MagicMock()
        mock_response.content = fake_png
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/png"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.close = MagicMock()

        results = self.media_mod.download_listing_images(
            ["https://example.com/1.png", "https://example.com/2.png"],
            reference_id="test-batch-001",
            client=mock_client,
        )
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.status == "downloaded" for r in results))
        self.assertTrue(all(r.storage_key.startswith("test-batch-001/") for r in results))

    def test_get_image_path_exists(self):
        listing_dir = Path(self.tmpdir) / "ref-xyz"
        listing_dir.mkdir()
        test_file = listing_dir / "0000_abcd1234.jpg"
        test_file.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 10)

        path = self.media_mod.get_image_path("ref-xyz/0000_abcd1234.jpg")
        self.assertIsNotNone(path)
        self.assertTrue(path.is_file())

    def test_get_image_path_not_found(self):
        path = self.media_mod.get_image_path("nonexistent/missing.jpg")
        self.assertIsNone(path)

    def test_guess_ext(self):
        self.assertEqual(self.media_mod._guess_ext("image/jpeg", "test.jpg"), ".jpg")
        self.assertEqual(self.media_mod._guess_ext("image/png", "test"), ".png")
        self.assertEqual(self.media_mod._guess_ext("image/webp", "test.webp"), ".webp")
        self.assertEqual(self.media_mod._guess_ext(None, "photo.png"), ".png")
        self.assertEqual(self.media_mod._guess_ext(None, "unknown"), ".jpg")


class TestListingMediaModel(unittest.TestCase):
    """Verify ListingMediaModel is importable and has correct attributes."""

    def test_model_attributes(self):
        from bgrealestate.db.models import ListingMediaModel
        self.assertEqual(ListingMediaModel.__tablename__, "listing_media")
        cols = {c.name for c in ListingMediaModel.__table__.columns}
        expected = {"media_id", "listing_reference_id", "url", "content_hash",
                    "caption", "ordering", "storage_key", "mime_type",
                    "width", "height", "file_size", "download_status"}
        self.assertTrue(expected.issubset(cols), f"Missing columns: {expected - cols}")


class TestProxiedImageUrls(unittest.TestCase):
    """Test the API listing serialization with proxied URLs."""

    def test_proxy_wraps_external_urls(self):
        from bgrealestate.api.routers.listings import _proxied_image_url
        result = _proxied_image_url("https://cdn.example.com/photo.jpg")
        self.assertTrue(result.startswith("/media/proxy?url="))
        self.assertIn("cdn.example.com", result)

    def test_proxy_leaves_internal_urls(self):
        from bgrealestate.api.routers.listings import _proxied_image_url
        self.assertEqual(_proxied_image_url("/api/placeholder/800/500"), "/api/placeholder/800/500")
        self.assertEqual(_proxied_image_url(""), "")

    def test_serialize_listing_proxies_images(self):
        from bgrealestate.api.routers.listings import _serialize_listing
        from unittest.mock import MagicMock

        m = MagicMock()
        m.reference_id = "ref-001"
        m.source_name = "Homes.bg"
        m.owner_group = "Test"
        m.listing_url = "https://example.com/1"
        m.external_id = "EXT-1"
        m.listing_intent = "sale"
        m.property_category = "apartment"
        m.city = "Sofia"
        m.district = None
        m.resort = None
        m.region = None
        m.address_text = None
        m.latitude = 42.7
        m.longitude = 23.3
        m.area_sqm = 80
        m.rooms = 2
        m.price = 100000
        m.currency = "EUR"
        m.description = "Test"
        m.image_urls = [
            "https://cdn.example.com/photo1.jpg",
            "https://cdn.example.com/photo2.jpg",
        ]
        m.first_seen = None
        m.last_seen = None
        m.last_changed_at = None
        m.removed_at = None
        m.parser_version = "v1"
        m.crawl_provenance = {}

        result = _serialize_listing(m)
        self.assertEqual(len(result["image_urls"]), 2)
        for url in result["image_urls"]:
            self.assertTrue(url.startswith("/media/proxy?url="))
        self.assertEqual(len(result["original_image_urls"]), 2)
        for url in result["original_image_urls"]:
            self.assertTrue(url.startswith("https://"))


class TestFrontendImageProxy(unittest.TestCase):
    """Verify the image-url utility module exists."""

    def test_utility_file_exists(self):
        util_path = REPO_ROOT / "lib" / "utils" / "image-url.ts"
        self.assertTrue(util_path.exists(), f"Missing: {util_path}")

    def test_next_api_route_exists(self):
        route_path = REPO_ROOT / "app" / "api" / "images" / "route.ts"
        self.assertTrue(route_path.exists(), f"Missing: {route_path}")


if __name__ == "__main__":
    unittest.main()
