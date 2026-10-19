"""Unit tests for vntd.model.ad — Ad dataclass properties and builders."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.model.ad import Ad
from vntd.model.user import User

from tests.helpers import _sample_ad_search_raw


def _make_ad(**overrides) -> Ad:
    defaults = dict(
        id=1, title="T", description=None, price=10.0, currency="EUR",
        brand=None, size=None, status=None, condition=None, url="u", images=[],
        favorite_count=None, view_count=None, category=None, color=None, raw={},
        _client=MagicMock(), _user_id=None, _user=None,
    )
    defaults.update(overrides)
    return Ad(**defaults)


def _search_client() -> MagicMock:
    return MagicMock(base_url="https://www.vinted.fr")


def _item_page_raw(**item_overrides) -> dict:
    item = {
        "id": "123",
        "seller_id": "456",
        "price": {"amount": "35", "currency_code": "EUR"},
        "title": "Test Vintage Jacket",
        "photos": [{"url": "https://example.com/1.jpg"}, {"url": "https://example.com/2.jpg"}],
        "can_buy": True,
        "is_reserved": False,
    }
    item.update(item_overrides)
    return {
        "item": item,
        "attributes": {
            "brand": "Nike",
            "size_familiar": "M",
            "status": "Très bon état",
            "color": "Bleu",
        },
        "description": "A beautiful vintage jacket",
        "favourite_count": 7,
        "category": "Vestes",
    }


class TestAdModel(unittest.TestCase):
    """Test Ad dataclass properties and builders."""

    def test_subject_returns_title(self):
        self.assertEqual(_make_ad(title="Vintage Dress").subject, "Vintage Dress")

    def test_body_returns_description(self):
        self.assertEqual(_make_ad(description="Soft cotton").body, "Soft cotton")

    def test_favorites_returns_favorite_count(self):
        self.assertEqual(_make_ad(favorite_count=3).favorites, 3)

    def test_build_from_search(self):
        ad = Ad._build_from_search(raw=_sample_ad_search_raw(), client=_search_client())

        self.assertEqual(ad.id, 999)
        self.assertEqual(ad.title, "Blue Jeans")
        self.assertAlmostEqual(ad.price, 19.99)
        self.assertEqual(ad.currency, "EUR")
        self.assertEqual(ad.brand, "Levi's")
        self.assertEqual(ad.size, "M")
        self.assertEqual(ad.condition, "Très bon état")
        self.assertEqual(ad.status, "active")
        self.assertEqual(ad.url, "https://www.vinted.fr/items/999-blue-jeans")
        self.assertEqual(ad.images, ["https://example.com/jeans.jpg"])
        self.assertEqual(ad.favorite_count, 5)
        self.assertEqual(ad.view_count, 120)
        self.assertEqual(ad._user_id, 42)

    def test_build_from_search_keeps_raw(self):
        raw = _sample_ad_search_raw()
        self.assertIs(Ad._build_from_search(raw=raw, client=_search_client()).raw, raw)

    def test_build_from_item_page_keeps_raw(self):
        raw = _item_page_raw()
        ad = Ad._build_from_item_page(raw=raw, url="u", client=MagicMock())
        self.assertIs(ad.raw, raw)

    def test_build_from_search_without_brand_or_size(self):
        raw = _sample_ad_search_raw()
        raw["item_box"] = {
            "first_line": "Sac à main",
            "second_line": "Bon état",
            "accessibility_label": "Sac à main, État: Bon état, 3.00 €, 3.85 €",
        }
        ad = Ad._build_from_search(raw=raw, client=_search_client())
        self.assertIsNone(ad.brand)
        self.assertIsNone(ad.size)
        self.assertEqual(ad.condition, "Bon état")

    def test_build_from_search_brand_equal_to_title(self):
        raw = _sample_ad_search_raw()
        raw["title"] = "Lego"
        raw["item_box"] = {
            "first_line": "Lego",
            "second_line": "Neuf sans étiquette",
            "accessibility_label": "Lego, Marque: Lego, État: Neuf sans étiquette, 5.00 €",
        }
        self.assertEqual(
            Ad._build_from_search(raw=raw, client=_search_client()).brand, "Lego"
        )

    def test_build_from_search_title_equal_to_first_line_is_not_a_brand(self):
        raw = _sample_ad_search_raw()
        raw["title"] = "Lego"
        raw["item_box"] = {
            "first_line": "Lego",
            "second_line": "Très bon état",
            "accessibility_label": "Lego, État: Très bon état, 5.00 €",
        }
        self.assertIsNone(
            Ad._build_from_search(raw=raw, client=_search_client()).brand
        )

    def test_build_from_search_without_item_box(self):
        raw = {"id": 1, "title": "Hat", "price": {}, "photos": [], "user": {}}
        ad = Ad._build_from_search(raw=raw, client=_search_client())
        self.assertIsNone(ad.brand)
        self.assertIsNone(ad.size)
        self.assertIsNone(ad.condition)
        self.assertIsNone(ad.url)

    def test_build_from_search_with_no_photos_uses_photo_fallback(self):
        raw = {
            "id": 1,
            "title": "Hat",
            "price": {"amount": "10.00", "currency_code": "EUR"},
            "photo": {"url": "https://example.com/hat.jpg"},
            "user": {"id": 1},
        }
        ad = Ad._build_from_search(raw=raw, client=_search_client())
        self.assertEqual(ad.images, ["https://example.com/hat.jpg"])

    def test_build_from_search_with_no_price(self):
        raw = {"id": 1, "title": "Free Item", "price": {}, "photos": [], "user": {}}
        ad = Ad._build_from_search(raw=raw, client=_search_client())
        self.assertIsNone(ad.price)
        self.assertIsNone(ad._user_id)

    def test_build_from_item_page(self):
        ad = Ad._build_from_item_page(
            raw=_item_page_raw(), url="https://example.com/123", client=MagicMock()
        )
        self.assertEqual(ad.id, 123)
        self.assertEqual(ad.title, "Test Vintage Jacket")
        self.assertEqual(ad.description, "A beautiful vintage jacket")
        self.assertAlmostEqual(ad.price, 35.0)
        self.assertEqual(ad.currency, "EUR")
        self.assertEqual(ad.brand, "Nike")
        self.assertEqual(ad.size, "M")
        self.assertEqual(ad.condition, "Très bon état")
        self.assertEqual(ad.category, "Vestes")
        self.assertEqual(ad.color, "Bleu")
        self.assertEqual(ad.favorite_count, 7)
        self.assertEqual(ad.images, ["https://example.com/1.jpg", "https://example.com/2.jpg"])
        self.assertEqual(ad._user_id, 456)

    def test_build_from_item_page_status(self):
        def status(**item):
            return Ad._build_from_item_page(
                raw=_item_page_raw(**item), url="u", client=MagicMock()
            ).status

        self.assertEqual(status(can_buy=True, is_reserved=False), "active")
        self.assertEqual(status(can_buy=False, is_reserved=False), "sold")
        self.assertEqual(status(can_buy=False, is_reserved=True), "reserved")

    def test_build_from_item_page_without_seller_or_price(self):
        raw = _item_page_raw(seller_id=None, price=None)
        ad = Ad._build_from_item_page(raw=raw, url="u", client=MagicMock())
        self.assertIsNone(ad._user_id)
        self.assertIsNone(ad.price)


class TestAdUserProperty(unittest.TestCase):
    """Test the Ad.user property — cached user first, lazy load otherwise."""

    def _user(self) -> User:
        return User(
            id=42, login="seller", profile_url=None, business=False,
            feedback_count=None, feedback_reputation=None, item_count=None,
            total_items_count=None, followers_count=None, following_count=None,
            country_code=None, city=None, about=None, photo_url=None,
        )

    def test_user_returns_cached_user(self):
        mock_client = MagicMock()
        ad = _make_ad(_client=mock_client, _user_id=42, _user=self._user())
        self.assertEqual(ad.user.login, "seller")
        mock_client.get_user.assert_not_called()

    def test_user_returns_none_when_no_user_id(self):
        mock_client = MagicMock()
        ad = _make_ad(_client=mock_client, _user_id=None)
        self.assertIsNone(ad.user)
        mock_client.get_user.assert_not_called()

    def test_user_is_loaded_once_when_not_populated(self):
        mock_client = MagicMock()
        mock_client.get_user.return_value = self._user()
        ad = _make_ad(_client=mock_client, _user_id=42)
        self.assertEqual(ad.user.id, 42)
        self.assertEqual(ad.user.id, 42)
        mock_client.get_user.assert_called_once_with(user_id=42)


if __name__ == "__main__":
    unittest.main()
