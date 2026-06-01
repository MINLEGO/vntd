"""Unit tests for vntd.model.enums — Sort and SellerType enum values."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.model.enums import SellerType, Sort


class TestEnums(unittest.TestCase):
    """Verify enum values match expected Vinted API strings."""

    def test_sort_relevance_value(self):
        self.assertEqual(Sort.RELEVANCE.value, "relevance")

    def test_sort_newest_value(self):
        self.assertEqual(Sort.NEWEST.value, "newest_first")

    def test_sort_price_low_to_high_value(self):
        self.assertEqual(Sort.PRICE_LOW_TO_HIGH.value, "price_low_to_high")

    def test_sort_price_high_to_low_value(self):
        self.assertEqual(Sort.PRICE_HIGH_TO_LOW.value, "price_high_to_low")

    def test_seller_type_business_value(self):
        self.assertEqual(SellerType.BUSINESS.value, "business")

    def test_seller_type_individual_value(self):
        self.assertEqual(SellerType.INDIVIDUAL.value, "individual")

    def test_seller_type_all_value(self):
        self.assertEqual(SellerType.ALL.value, "all")


if __name__ == "__main__":
    unittest.main()
