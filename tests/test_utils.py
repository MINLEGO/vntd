"""Unit tests for vntd.utils — build_search_params, normalize_list, price validation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.exceptions import InvalidValue
from vntd.model.enums import SellerType, Sort
from vntd.utils import (
    _normalize_list,
    build_search_params_with_args,
    build_search_params_with_url,
)


# ---------------------------------------------------------------------------
# 3. Search Filter Tests (build_search_params_with_args)
# ---------------------------------------------------------------------------


class TestBuildSearchParamsWithArgs(unittest.TestCase):
    """Test build_search_params_with_args with various filter combinations."""

    def test_defaults_produce_page_and_per_page(self):
        params = build_search_params_with_args()
        self.assertEqual(params["page"], 1)
        self.assertEqual(params["per_page"], 24)
        self.assertNotIn("search_text", params)
        self.assertNotIn("price_from", params)

    def test_text_adds_search_text(self):
        params = build_search_params_with_args(text="sneakers")
        self.assertEqual(params["search_text"], "sneakers")

    def test_none_text_does_not_add_search_text(self):
        params = build_search_params_with_args(text=None)
        self.assertNotIn("search_text", params)

    def test_price_range_adds_from_and_to(self):
        params = build_search_params_with_args(price=(10, 50))
        self.assertEqual(params["price_from"], 10)
        self.assertEqual(params["price_to"], 50)

    def test_price_with_none_min_omits_from(self):
        params = build_search_params_with_args(price=(None, 100))
        self.assertNotIn("price_from", params)
        self.assertEqual(params["price_to"], 100)

    def test_price_with_none_max_omits_to(self):
        params = build_search_params_with_args(price=(5, None))
        self.assertEqual(params["price_from"], 5)
        self.assertNotIn("price_to", params)

    def test_seller_type_business_sets_is_business_1(self):
        params = build_search_params_with_args(seller_type=SellerType.BUSINESS)
        self.assertEqual(params["is_business"], 1)

    def test_seller_type_individual_sets_is_business_0(self):
        params = build_search_params_with_args(seller_type=SellerType.INDIVIDUAL)
        self.assertEqual(params["is_business"], 0)

    def test_seller_type_all_omits_is_business(self):
        params = build_search_params_with_args(seller_type=SellerType.ALL)
        self.assertNotIn("is_business", params)

    def test_user_id_adds_param(self):
        params = build_search_params_with_args(user_id=123)
        self.assertEqual(params["user_id"], 123)

    def test_user_id_none_omits_param(self):
        params = build_search_params_with_args(user_id=None)
        self.assertNotIn("user_id", params)

    def test_sort_sets_order_value(self):
        params = build_search_params_with_args(sort=Sort.PRICE_LOW_TO_HIGH)
        self.assertEqual(params["order"], "price_low_to_high")

    def test_sort_newest(self):
        params = build_search_params_with_args(sort=Sort.NEWEST)
        self.assertEqual(params["order"], "newest_first")

    def test_catalog_ids_normalized_from_list(self):
        params = build_search_params_with_args(catalog_ids=[1, 2, 3])
        self.assertEqual(params["catalog_ids"], "1,2,3")

    def test_color_ids_normalized_from_list(self):
        params = build_search_params_with_args(color_ids=[10, 20])
        self.assertEqual(params["color_ids"], "10,20")

    def test_brand_ids_normalized_from_list(self):
        params = build_search_params_with_args(brand_ids=[100])
        self.assertEqual(params["brand_ids"], "100")

    def test_size_ids_normalized_from_tuple(self):
        params = build_search_params_with_args(size_ids=(5, 6, 7))
        self.assertEqual(params["size_ids"], "5,6,7")

    def test_none_filter_value_is_omitted(self):
        params = build_search_params_with_args(catalog_ids=None)
        self.assertNotIn("catalog_ids", params)

    def test_multiple_filters_combined(self):
        params = build_search_params_with_args(
            text="dress",
            price=(10, 100),
            seller_type=SellerType.BUSINESS,
            sort=Sort.PRICE_HIGH_TO_LOW,
            user_id=42,
            catalog_ids=[1, 2],
            color_ids=[3],
        )
        self.assertEqual(params["search_text"], "dress")
        self.assertEqual(params["price_from"], 10)
        self.assertEqual(params["price_to"], 100)
        self.assertEqual(params["is_business"], 1)
        self.assertEqual(params["order"], "price_high_to_low")
        self.assertEqual(params["user_id"], 42)
        self.assertEqual(params["catalog_ids"], "1,2")
        self.assertEqual(params["color_ids"], "3")


class TestBuildSearchParamsWithUrl(unittest.TestCase):
    """Test build_search_params_with_url parses Vinted search URLs."""

    def test_basic_url_extraction(self):
        url = (
            "https://www.vinted.fr/catalog"
            "?search_text=robe&order=newest_first&price_from=5&price_to=20"
        )
        params = build_search_params_with_url(url, limit=10, page=2)
        self.assertEqual(params["search_text"], "robe")
        self.assertEqual(params["order"], "newest_first")
        self.assertEqual(params["price_from"], "5")
        self.assertEqual(params["price_to"], "20")
        self.assertEqual(params["page"], 2)
        self.assertEqual(params["per_page"], 10)

    def test_url_with_multiple_values_for_same_key(self):
        url = "https://www.vinted.fr/catalog?color_ids=1&color_ids=2&color_ids=3"
        params = build_search_params_with_url(url)
        # Multiple values for the same key are joined with commas
        self.assertEqual(params["color_ids"], "1,2,3")


# ---------------------------------------------------------------------------
# 7. _normalize_list utility
# ---------------------------------------------------------------------------


class TestNormalizeList(unittest.TestCase):
    """Test _normalize_list with various input types."""

    def test_list_joined_with_commas(self):
        self.assertEqual(_normalize_list([1, 2, 3]), "1,2,3")

    def test_tuple_joined_with_commas(self):
        self.assertEqual(_normalize_list((4, 5)), "4,5")

    def test_single_int_as_string(self):
        self.assertEqual(_normalize_list(42), "42")

    def test_single_string_returned_unchanged(self):
        self.assertEqual(_normalize_list("hello"), "hello")

    def test_empty_list_returns_empty_string(self):
        self.assertEqual(_normalize_list([]), "")

    def test_single_element_list(self):
        self.assertEqual(_normalize_list([99]), "99")

    def test_set_elements_present_in_output(self):
        result = _normalize_list({1, 2})
        # Sets are unordered, so check membership
        parts = set(result.split(","))
        self.assertEqual(parts, {"1", "2"})


# ---------------------------------------------------------------------------
# Price Validation Tests
# ---------------------------------------------------------------------------


class TestPriceValidation(unittest.TestCase):
    """Verify build_search_params_with_args rejects malformed price inputs."""

    def test_price_as_string_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            build_search_params_with_args(price="cheap")

    def test_price_as_three_tuple_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            build_search_params_with_args(price=(10, 20, 30))

    def test_price_as_single_int_raises_invalid_value(self):
        with self.assertRaises(InvalidValue):
            build_search_params_with_args(price=50)


if __name__ == "__main__":
    unittest.main()
