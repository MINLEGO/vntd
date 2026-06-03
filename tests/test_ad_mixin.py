"""Unit tests for vntd.mixin.ad — URL extraction, ID validation, and get_ad integration."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.exceptions import InvalidValue, NotFoundError

from tests.helpers import MOCK_AD_HTML, _mock_response


# ---------------------------------------------------------------------------
# 4. URL Parsing Tests (AdMixin._extract_item_id)
# ---------------------------------------------------------------------------


class TestExtractItemId(unittest.TestCase):
    """Test _extract_item_id with various input formats."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        mock_session = MagicMock()
        self.mock_session_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")

    def test_full_url_extracts_id(self):
        item_id = self.client._extract_item_id(
            "https://www.vinted.fr/items/12345678-some-slug"
        )
        self.assertEqual(item_id, 12345678)

    def test_url_with_different_domain_extracts_id(self):
        item_id = self.client._extract_item_id(
            "https://www.vinted.de/items/99999"
        )
        self.assertEqual(item_id, 99999)

    def test_integer_id_returned_directly(self):
        self.assertEqual(self.client._extract_item_id(12345678), 12345678)

    def test_numeric_string_extracts_id(self):
        self.assertEqual(self.client._extract_item_id("55555"), 55555)

    def test_non_numeric_string_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            self.client._extract_item_id("abc-def")


# ---------------------------------------------------------------------------
# Ad ID Validation Tests
# ---------------------------------------------------------------------------


class TestAdIdValidation(unittest.TestCase):
    """Verify _extract_item_id rejects invalid inputs."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        mock_session = MagicMock()
        self.mock_session_cls.return_value = mock_session
        mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")

    def test_non_numeric_non_url_string_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            self.client._extract_item_id("not_a_valid_id")

    def test_empty_string_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            self.client._extract_item_id("")

    def test_partial_url_without_digits_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            self.client._extract_item_id("https://www.vinted.fr/items/")


# ---------------------------------------------------------------------------
# 9. get_ad integration (mocked HTTP)
# ---------------------------------------------------------------------------


class TestGetAdIntegration(unittest.TestCase):
    """Test get_ad() end-to-end with mocked HTTP."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")

    def test_get_ad_with_url_extracts_id_and_parses(self):
        self.mock_session.request.return_value = _mock_response(
            text_data=MOCK_AD_HTML
        )
        ad = self.client.get_ad("https://www.vinted.fr/items/12345678-some-slug")
        self.assertEqual(ad.id, 12345678)
        self.assertEqual(ad.title, "Test Vintage Jacket")

    def test_get_ad_with_integer_id(self):
        self.mock_session.request.return_value = _mock_response(
            text_data=MOCK_AD_HTML
        )
        ad = self.client.get_ad(99999)
        self.assertEqual(ad.id, 99999)
        self.assertAlmostEqual(ad.price, 35.0)

    def test_get_ad_extracts_seller_id(self):
        self.mock_session.request.return_value = _mock_response(
            text_data=MOCK_AD_HTML
        )
        ad = self.client.get_ad(12345)
        self.assertEqual(ad._user_id, 67890)

    def test_get_ad_raises_not_found_when_no_json_ld(self):
        self.mock_session.request.return_value = _mock_response(
            text_data="<html><body>No data</body></html>"
        )
        with self.assertRaises(NotFoundError):
            self.client.get_ad(12345)

    def test_get_ad_fetches_correct_url(self):
        self.mock_session.request.return_value = _mock_response(
            text_data=MOCK_AD_HTML
        )
        self.client.get_ad(42)
        url = self.mock_session.request.call_args.kwargs["url"]
        self.assertEqual(url, "https://www.vinted.fr/items/42")


if __name__ == "__main__":
    unittest.main()
