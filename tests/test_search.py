"""Unit tests for vntd.mixin.search — Search integration with mocked _fetch."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.model.enums import SellerType, Sort
from vntd.model.search import Search

from tests.helpers import _mock_response, _sample_ad_search_raw


class TestSearchIntegration(unittest.TestCase):
    """Test search() end-to-end with mocked _fetch."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session.headers = {}
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response(
            headers={"X-Anon-Id": "anon-123"},
            cookies={"access_token_web": "token-123"},
            text_data='<meta name="csrf-token" content="csrf-456">',
        )
        self.client = Client(base_url="https://www.vinted.fr")

    def _setup_search_response(self):
        self.mock_session.request.return_value = _mock_response(
            json_data={
                "items": [_sample_ad_search_raw()],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "total_entries": 1,
                    "per_page": 24,
                },
            }
        )

    def test_search_returns_search_object(self):
        self._setup_search_response()
        result = self.client.search(text="jeans")
        self.assertIsInstance(result, Search)
        self.assertEqual(len(result.ads), 1)
        self.assertEqual(result.ads[0].title, "Blue Jeans")

    def test_search_price_range_params(self):
        self._setup_search_response()
        self.client.search(price=(10, 50))
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["price_from"], 10)
        self.assertEqual(params["price_to"], 50)

    def test_search_seller_type_business_params(self):
        self._setup_search_response()
        self.client.search(seller_type=SellerType.BUSINESS)
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["is_business"], 1)

    def test_search_user_id_params(self):
        self._setup_search_response()
        self.client.search(user_id=123)
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["user_id"], 123)

    def test_search_sort_order_params(self):
        self._setup_search_response()
        self.client.search(sort=Sort.PRICE_LOW_TO_HIGH)
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["order"], "price_low_to_high")

    def test_search_catalog_ids_normalized(self):
        self._setup_search_response()
        self.client.search(catalog_ids=[1, 2, 3])
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["attribute_ids[catalog]"], "1,2,3")
        self.assertNotIn("catalog_ids", params)

    def test_search_color_ids_normalized(self):
        self._setup_search_response()
        self.client.search(color_ids=[10, 20])
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["color_ids"], "10,20")

    def test_search_brand_ids_normalized(self):
        self._setup_search_response()
        self.client.search(brand_ids=[100])
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["attribute_ids[brand]"], "100")

    def test_search_size_ids_normalized(self):
        self._setup_search_response()
        self.client.search(size_ids=(5, 6))
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["attribute_ids[size]"], "5,6")

    def test_search_maps_all_legacy_attribute_filters(self):
        self._setup_search_response()
        self.client.search(
            catalog_ids=[1],
            status_ids=[2],
            brand_ids=[3],
            size_ids=[4],
        )
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(
            {
                params["attribute_ids[catalog]"],
                params["attribute_ids[status]"],
                params["attribute_ids[brand]"],
                params["attribute_ids[size]"],
            },
            {"1", "2", "3", "4"},
        )
        for legacy_name in ("catalog_ids", "status_ids", "brand_ids", "size_ids"):
            self.assertNotIn(legacy_name, params)

    def test_search_url_delegates_to_url_builder(self):
        self._setup_search_response()
        self.client.search(
            url=(
                "https://www.vinted.fr/catalog"
                "?search_text=hat&order=newest_first&catalog_ids=1&catalog_ids=2"
            )
        )
        params = self.mock_session.request.call_args.kwargs["params"]
        self.assertEqual(params["search_text"], "hat")
        self.assertEqual(params["order"], "newest_first")
        self.assertEqual(params["attribute_ids[catalog]"], "1,2")

    def test_search_calls_correct_endpoint(self):
        self._setup_search_response()
        self.client.search(text="test")
        url = self.mock_session.request.call_args.kwargs["url"]
        self.assertEqual(url, "https://api.vinted.fr/svc-catalogue/items")

    def test_search_sends_bootstrapped_session_data(self):
        self._setup_search_response()
        self.client.search(text="test")
        headers = self.mock_session.request.call_args.kwargs["headers"]
        self.assertEqual(headers["X-Anon-Id"], "anon-123")
        self.assertEqual(headers["X-Csrf-Token"], "csrf-456")
        self.assertIn("access_token_web=token-123", headers["Cookie"])

    def test_search_preserves_custom_session_headers(self):
        custom_session = MagicMock()
        custom_session.headers = {
            "User-Agent": "custom-agent",
            "X-Anon-Id": "custom-anon",
            "Cookie": "access_token_web=custom-token",
        }
        custom_session.request.return_value = _mock_response(
            json_data={"items": [], "pagination": {}}
        )
        self.client.session = custom_session

        self.client.search(text="test")

        custom_session.request.assert_called_once()
        headers = custom_session.request.call_args.kwargs["headers"]
        self.assertEqual(headers["User-Agent"], "custom-agent")
        self.assertEqual(headers["X-Anon-Id"], "custom-anon")
        self.assertEqual(headers["Cookie"], "access_token_web=custom-token")

    def test_search_parses_new_endpoint_pagination(self):
        self.mock_session.request.return_value = _mock_response(
            json_data={
                "items": [],
                "pagination": {
                    "current_page": 2,
                    "total_pages": 4,
                    "total_entries": 100,
                    "per_page": 30,
                },
            }
        )

        result = self.client.search(text="nike", page=2, limit=30)

        self.assertEqual(result.pagination.current_page, 2)
        self.assertEqual(result.pagination.total_pages, 4)
        self.assertEqual(result.pagination.total_entries, 100)
        self.assertEqual(result.pagination.per_page, 30)


if __name__ == "__main__":
    unittest.main()
