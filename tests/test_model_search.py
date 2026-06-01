"""Unit tests for vntd.model.search — Search dataclass and Pagination."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.model.search import Pagination, Search

from tests.helpers import _empty_search_response, _sample_ad_search_raw


class TestSearchModel(unittest.TestCase):
    """Test Search dataclass and Pagination."""

    def test_total_returns_total_entries(self):
        search = Search(
            pagination=Pagination(
                current_page=1, total_pages=5, total_entries=120, per_page=24
            ),
            ads=[],
        )
        self.assertEqual(search.total, 120)

    def test_build_from_raw(self):
        raw = {
            "items": [_sample_ad_search_raw()],
            "pagination": {
                "current_page": 1,
                "total_pages": 10,
                "total_entries": 100,
                "per_page": 24,
            },
        }
        search = Search._build(raw=raw, client=MagicMock())
        self.assertEqual(search.total, 100)
        self.assertEqual(len(search.ads), 1)
        self.assertEqual(search.ads[0].id, 999)
        self.assertEqual(search.pagination.current_page, 1)
        self.assertEqual(search.pagination.total_pages, 10)

    def test_build_from_raw_empty_items(self):
        raw = _empty_search_response()
        search = Search._build(raw=raw, client=MagicMock())
        self.assertEqual(search.total, 0)
        self.assertEqual(len(search.ads), 0)


if __name__ == "__main__":
    unittest.main()
