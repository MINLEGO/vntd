"""Unit tests for vntd.mixin.ad — URL extraction, ID validation, and get_ad integration."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.exceptions import InvalidValue, NotFoundError, ParseError

from tests.helpers import _mock_ad_html, _mock_response


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

    def _serve(self, item_id: int, **item_overrides) -> None:
        self.mock_session.request.return_value = _mock_response(
            text_data=_mock_ad_html(item_id, **item_overrides)
        )

    def test_get_ad_with_url_extracts_id_and_parses(self):
        self._serve(12345678)
        ad = self.client.get_ad("https://www.vinted.fr/items/12345678-some-slug")
        self.assertEqual(ad.id, 12345678)
        self.assertEqual(ad.title, "Test Vintage Jacket")

    def test_get_ad_with_integer_id(self):
        self._serve(99999)
        ad = self.client.get_ad(99999)
        self.assertEqual(ad.id, 99999)
        self.assertAlmostEqual(ad.price, 35.0)

    def test_get_ad_extracts_seller_id(self):
        self._serve(12345)
        self.assertEqual(self.client.get_ad(12345)._user_id, 67890)

    def test_get_ad_extracts_page_fields(self):
        self._serve(12345)
        ad = self.client.get_ad(12345)
        self.assertEqual(ad.description, 'A "beautiful" vintage jacket')
        self.assertEqual(ad.brand, "Nike")
        self.assertEqual(ad.size, "M")
        self.assertEqual(ad.condition, "Très bon état")
        self.assertEqual(ad.color, "Bleu")
        self.assertEqual(ad.favorite_count, 7)
        self.assertEqual(ad.category, "Vestes")
        self.assertEqual(len(ad.images), 2)

    def test_get_ad_sold_item_does_not_raise(self):
        self._serve(12345, can_buy=False)
        self.assertEqual(self.client.get_ad(12345).status, "sold")

    def test_get_ad_ignores_data_of_other_items(self):
        self.mock_session.request.return_value = _mock_response(
            text_data=_mock_ad_html(777)
        )
        with self.assertRaises(ParseError):
            self.client.get_ad(12345)

    def test_get_ad_raises_parse_error_when_no_item_data(self):
        self.mock_session.request.return_value = _mock_response(
            text_data="<html><body>No data</body></html>"
        )
        with self.assertRaises(ParseError):
            self.client.get_ad(12345)

    def test_get_ad_raises_not_found_on_404(self):
        self.mock_session.request.return_value = _mock_response(status_code=404)
        with self.assertRaises(NotFoundError):
            self.client.get_ad(12345)

    def test_get_ad_raises_parse_error_on_undecodable_chunk(self):
        self.mock_session.request.return_value = _mock_response(
            text_data=r'<script>self.__next_f.push([1,"\x"])</script>'
        )
        with self.assertRaises(ParseError):
            self.client.get_ad(12345)

    def test_get_ad_exposes_raw(self):
        self._serve(12345)
        raw = self.client.get_ad(12345).raw
        self.assertEqual(raw["item"]["title"], "Test Vintage Jacket")
        self.assertEqual(raw["attributes"]["brand"], "Nike")

    def test_get_ad_fetches_correct_url(self):
        self._serve(42)
        self.client.get_ad(42)
        url = self.mock_session.request.call_args.kwargs["url"]
        self.assertEqual(url, "https://www.vinted.fr/items/42")


if __name__ == "__main__":
    unittest.main()
