"""Shared test helpers for vntd unit tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock data constants
# ---------------------------------------------------------------------------

def _mock_ad_html(item_id: int = 12345678, **item_overrides) -> str:
    """Return an item page whose data sits in `self.__next_f` chunks, like Vinted's."""
    item = {
        "id": str(item_id),
        "seller_id": "67890",
        "price": {"amount": "35", "currency_code": "EUR"},
        "title": "Test Vintage Jacket",
        "photos": [
            {"url": "https://example.com/img1.jpg"},
            {"url": "https://example.com/img2.jpg"},
        ],
        "can_buy": True,
        "is_reserved": False,
    }
    item.update(item_overrides)
    attributes = [
        {"code": "brand", "data": {"title": "Marque", "value": "Nike"}},
        {"code": "size_familiar", "data": {"title": "Taille", "value": "M"}},
        {"code": "status", "data": {"title": "État", "value": "Très bon état"}},
        {"code": "color", "data": {"title": "Couleur", "value": "Bleu"}},
    ]
    objects = [
        item,
        {"attributes": attributes, "item_id": str(item_id)},
        {"description": 'A "beautiful" vintage jacket', "item_id": str(item_id)},
        {"favourite_count": 7, "item_id": str(item_id)},
        {
            "breadcrumbs": [
                {"title": "Femmes", "url": "/catalog/1904-women"},
                {"title": "Vestes", "url": "/catalog/10-jackets"},
                {"title": "Nike Vestes", "url": "/catalog/10-jackets/brand/53-nike"},
            ]
        },
    ]
    payload = "\n".join(json.dumps(o, separators=(",", ":")) for o in objects)
    return (
        "<html><body><script>"
        f"self.__next_f.push([1,{json.dumps(payload)}])"
        "</script></body></html>"
    )


# ---------------------------------------------------------------------------
# Mock factories
# ---------------------------------------------------------------------------


def _mock_response(
    status_code: int = 200,
    json_data=None,
    text_data: str = "",
    headers: dict | None = None,
    cookies: dict | None = None,
):
    """Return a mock curl_cffi.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = text_data
    resp.headers = headers or {}
    resp.cookies = cookies or {}
    return resp


def _empty_search_response() -> dict:
    return {
        "items": [],
        "pagination": {
            "current_page": 1,
            "total_pages": 0,
            "total_entries": 0,
            "per_page": 24,
        },
    }


def _sample_user_raw() -> dict:
    return {
        "id": 123,
        "login": "testuser",
        "profile_url": "https://www.vinted.fr/member/123",
        "business": False,
        "feedback_count": 10,
        "feedback_reputation": 4.5,
        "item_count": 42,
        "total_items_count": 100,
        "followers_count": 5,
        "following_count": 3,
        "country_code": "FR",
        "city": "Paris",
        "about": "Hello!",
        "photo": {"url": "https://example.com/photo.jpg"},
    }


def _sample_ad_search_raw() -> dict:
    return {
        "id": 999,
        "title": "Blue Jeans",
        "price": {"amount": "19.99", "currency_code": "EUR"},
        "photos": [{"url": "https://example.com/jeans.jpg"}],
        "item_box": {
            "first_line": "Levi's",
            "second_line": "M · Très bon état",
            "accessibility_label": (
                "Blue Jeans, Marque: Levi's, État: Très bon état, Taille: M, "
                "19.99 €, 21.00 €"
            ),
        },
        "url": "/items/999-blue-jeans",
        "favourite_count": 5,
        "view_count": 120,
        "user": {"id": 42},
    }
