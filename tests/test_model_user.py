"""Unit tests for vntd.model.user — User dataclass properties."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vntd.model.user import User

from tests.helpers import _sample_user_raw


class TestUserModel(unittest.TestCase):
    """Test User dataclass properties."""

    def _make_user(self, **overrides) -> User:
        defaults = {
            "id": 1,
            "login": "alice",
            "profile_url": None,
            "business": False,
            "feedback_count": None,
            "feedback_reputation": None,
            "item_count": None,
            "total_items_count": None,
            "followers_count": None,
            "following_count": None,
            "country_code": None,
            "city": None,
            "about": None,
            "photo_url": None,
        }
        defaults.update(overrides)
        return User(**defaults)

    def test_name_returns_login(self):
        user = self._make_user(login="bob")
        self.assertEqual(user.name, "bob")

    def test_is_pro_true_when_business(self):
        user = self._make_user(business=True)
        self.assertTrue(user.is_pro)

    def test_is_pro_false_when_not_business(self):
        user = self._make_user(business=False)
        self.assertFalse(user.is_pro)

    def test_feedback_score_multiplied_by_5(self):
        user = self._make_user(feedback_reputation=4.2)
        self.assertAlmostEqual(user.feedback_score, 21.0)

    def test_feedback_score_none_when_reputation_is_none(self):
        user = self._make_user(feedback_reputation=None)
        self.assertIsNone(user.feedback_score)

    def test_feedback_score_none_when_reputation_is_zero(self):
        user = self._make_user(feedback_reputation=0.0)
        # 0.0 is falsy, so feedback_score returns None
        self.assertIsNone(user.feedback_score)

    def test_build_from_raw(self):
        raw = _sample_user_raw()
        user = User._build(raw)
        self.assertEqual(user.id, 123)
        self.assertEqual(user.login, "testuser")
        self.assertEqual(user.profile_url, "https://www.vinted.fr/member/123")
        self.assertFalse(user.business)
        self.assertEqual(user.feedback_count, 10)
        self.assertAlmostEqual(user.feedback_reputation, 4.5)
        self.assertEqual(user.item_count, 42)
        self.assertEqual(user.photo_url, "https://example.com/photo.jpg")

    def test_build_from_raw_with_missing_photo(self):
        raw = {"id": 1, "login": "u"}
        user = User._build(raw)
        self.assertIsNone(user.photo_url)

    def test_build_from_raw_with_business_true(self):
        raw = {"id": 1, "login": "shop", "business": True}
        user = User._build(raw)
        self.assertTrue(user.is_pro)


if __name__ == "__main__":
    unittest.main()
