"""Shared test helpers for vntd unit tests."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock data constants
# ---------------------------------------------------------------------------

MOCK_AD_JSON_LD = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Test Vintage Jacket",
        "description": "A beautiful vintage jacket",
        "image": [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg",
        ],
        "brand": {"@type": "Brand", "name": "Nike"},
        "offers": {
            "@type": "Offer",
            "price": "35.00",
            "priceCurrency": "EUR",
            "itemCondition": "Used",
        },
        "category": "Clothing",
        "color": "Blue",
    }
)

MOCK_AD_HTML = (
    "<html><head>"
    f'<script type="application/ld+json">{MOCK_AD_JSON_LD}</script>'
    "</head>"
    '<body>\\"seller_id\\":67890</body></html>'
)


# ---------------------------------------------------------------------------
# Mock factories
# ---------------------------------------------------------------------------


def _mock_response(status_code: int = 200, json_data=None, text_data: str = ""):
    """Return a mock curl_cffi.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = 200 <= status_code < 300
    resp.json.return_value = json_data if json_data is not None else {}
    resp.text = text_data
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
        "brand_title": "Levi's",
        "size_title": "M",
        "status": "good",
        "url": "https://www.vinted.fr/items/999",
        "favourite_count": 5,
        "view_count": 120,
        "user": {"id": 42},
    }
