"""Unit tests for vntd.mixin.user — get_user integration with mocked HTTP."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.client import Client
from vntd.model.enums import Sort
from vntd.model.search import Search
from vntd.model.user import User

from tests.helpers import _mock_response, _sample_ad_search_raw, _sample_user_raw


class TestGetUserIntegration(unittest.TestCase):
    """Test get_user() end-to-end with mocked HTTP."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")

    def test_get_user_returns_user_object(self):
        self.mock_session.request.return_value = _mock_response(
            json_data={"user": _sample_user_raw()}
        )
        user = self.client.get_user(123)
        self.assertIsInstance(user, User)
        self.assertEqual(user.id, 123)
        self.assertEqual(user.login, "testuser")

    def test_get_user_calls_correct_endpoint(self):
        self.mock_session.request.return_value = _mock_response(
            json_data={"user": _sample_user_raw()}
        )
        self.client.get_user(42)
        url = self.mock_session.request.call_args.kwargs["url"]
        self.assertEqual(url, "https://www.vinted.fr/api/v2/users/42")


class TestGetUserAds(unittest.TestCase):
    """Test get_user_ads() end-to-end with mocked HTTP."""

    def setUp(self):
        patcher = patch("curl_cffi.requests.Session")
        self.mock_session_cls = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_session = MagicMock()
        self.mock_session.headers = {}
        self.mock_session_cls.return_value = self.mock_session
        self.mock_session.get.return_value = _mock_response()
        self.client = Client(base_url="https://www.vinted.fr")
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

    def test_returns_search_with_ads(self):
        result = self.client.get_user_ads(42)
        self.assertIsInstance(result, Search)
        self.assertEqual(result.total, 1)
        self.assertEqual(len(result.ads), 1)

    def test_calls_wardrobe_endpoint_with_params(self):
        self.client.get_user_ads(42, page=2, limit=10, sort=Sort.PRICE_LOW_TO_HIGH)
        kwargs = self.mock_session.request.call_args.kwargs
        self.assertEqual(kwargs["url"], "https://www.vinted.fr/api/v2/wardrobe/42/items")
        self.assertEqual(
            kwargs["params"],
            {"page": 2, "per_page": 10, "order": "price_low_to_high"},
        )


if __name__ == "__main__":
    unittest.main()
