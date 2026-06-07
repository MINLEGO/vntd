"""Unit tests for vntd.model.ad — Ad dataclass properties and builders."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.model.ad import Ad
from vntd.model.user import User

from tests.helpers import MOCK_AD_JSON_LD, _sample_ad_search_raw


class TestAdModel(unittest.TestCase):
    """Test Ad dataclass properties and builders."""

    def test_subject_returns_title(self):
        ad = Ad(
            id=1,
            title="Vintage Dress",
            description=None,
            price=25.0,
            currency="EUR",
            brand=None,
            size=None,
            status=None,
            url="https://example.com",
            images=[],
            favorite_count=None,
            view_count=None,
            category=None,
            color=None,
            _client=MagicMock(),
            _user_id=None,
        )
        self.assertEqual(ad.subject, "Vintage Dress")

    def test_build_from_search(self):
        client = MagicMock()
        raw = _sample_ad_search_raw()
        ad = Ad._build_from_search(raw=raw, client=client)

        self.assertEqual(ad.id, 999)
        self.assertEqual(ad.title, "Blue Jeans")
        self.assertAlmostEqual(ad.price, 19.99)
        self.assertEqual(ad.currency, "EUR")
        self.assertEqual(ad.brand, "Levi's")
        self.assertEqual(ad.size, "M")
        self.assertEqual(ad.url, "https://www.vinted.fr/items/999")
        self.assertEqual(ad.images, ["https://example.com/jeans.jpg"])
        self.assertEqual(ad.favorite_count, 5)
        self.assertEqual(ad.view_count, 120)
        self.assertEqual(ad._user_id, 42)

    def test_build_from_search_with_no_photos_uses_photo_fallback(self):
        raw = {
            "id": 1,
            "title": "Hat",
            "price": {"amount": "10.00", "currency_code": "EUR"},
            "photo": {"url": "https://example.com/hat.jpg"},
            "user": {"id": 1},
        }
        ad = Ad._build_from_search(raw=raw, client=MagicMock())
        self.assertEqual(ad.images, ["https://example.com/hat.jpg"])

    def test_build_from_search_with_no_price(self):
        raw = {
            "id": 1,
            "title": "Free Item",
            "price": {},
            "photos": [],
            "user": {},
        }
        ad = Ad._build_from_search(raw=raw, client=MagicMock())
        self.assertIsNone(ad.price)
        self.assertIsNone(ad._user_id)

    def test_build_from_item_page(self):
        client = MagicMock()
        raw = json.loads(MOCK_AD_JSON_LD)
        ad = Ad._build_from_item_page(
            raw=raw, item_id=123, url="https://example.com/123", seller_id=456, client=client
        )
        self.assertEqual(ad.id, 123)
        self.assertEqual(ad.title, "Test Vintage Jacket")
        self.assertEqual(ad.description, "A beautiful vintage jacket")
        self.assertAlmostEqual(ad.price, 35.0)
        self.assertEqual(ad.currency, "EUR")
        self.assertEqual(ad.brand, "Nike")
        self.assertEqual(ad.category, "Clothing")
        self.assertEqual(ad.color, "Blue")
        self.assertEqual(ad._user_id, 456)

    def test_build_from_item_page_with_string_image(self):
        raw = {"name": "Item", "image": "https://example.com/one.jpg", "offers": {}}
        ad = Ad._build_from_item_page(
            raw=raw, item_id=1, url="u", seller_id=None, client=MagicMock()
        )
        self.assertEqual(ad.images, ["https://example.com/one.jpg"])

    def test_build_from_item_page_with_list_brand(self):
        raw = {
            "name": "Item",
            "brand": [{"name": "Adidas"}],
            "offers": {"price": "10.00", "priceCurrency": "EUR"},
        }
        ad = Ad._build_from_item_page(
            raw=raw, item_id=1, url="u", seller_id=None, client=MagicMock()
        )
        self.assertEqual(ad.brand, "Adidas")

    def test_build_from_item_page_with_empty_list_brand(self):
        raw = {"name": "Item", "brand": [], "offers": {}}
        ad = Ad._build_from_item_page(
            raw=raw, item_id=1, url="u", seller_id=None, client=MagicMock()
        )
        self.assertIsNone(ad.brand)


class TestAdUserProperty(unittest.TestCase):
    """Test the Ad.user property — returns cached user without HTTP requests."""

    def test_user_returns_cached_user(self):
        cached_user = User(
            id=42, login="seller", profile_url=None, business=False,
            feedback_count=None, feedback_reputation=None, item_count=None,
            total_items_count=None, followers_count=None, following_count=None,
            country_code=None, city=None, about=None, photo_url=None,
        )
        mock_client = MagicMock()
        ad = Ad(
            id=1, title="T", description=None, price=10.0, currency="EUR",
            brand=None, size=None, status=None, url="u", images=[],
            favorite_count=None, view_count=None, category=None, color=None,
            _client=mock_client, _user_id=42, _user=cached_user,
        )
        user = ad.user
        self.assertEqual(user.id, 42)
        self.assertEqual(user.login, "seller")
        mock_client.get_user.assert_not_called()

    def test_user_returns_none_when_no_user_id(self):
        ad = Ad(
            id=1, title="T", description=None, price=10.0, currency="EUR",
            brand=None, size=None, status=None, url="u", images=[],
            favorite_count=None, view_count=None, category=None, color=None,
            _client=MagicMock(), _user_id=None, _user=None,
        )
        self.assertIsNone(ad.user)

    def test_user_returns_none_when_not_populated(self):
        mock_client = MagicMock()
        ad = Ad(
            id=1, title="T", description=None, price=10.0, currency="EUR",
            brand=None, size=None, status=None, url="u", images=[],
            favorite_count=None, view_count=None, category=None, color=None,
            _client=mock_client, _user_id=42, _user=None,
        )
        self.assertIsNone(ad.user)
        mock_client.get_user.assert_not_called()


if __name__ == "__main__":
    unittest.main()
